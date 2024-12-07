from django.apps import apps
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.utils.decorators import method_decorator
from django.views.decorators.cache import never_cache
from django.views.decorators.csrf import csrf_protect
from apps.accounts.services import ActivityLogService
from ..mixins import PaginationMixin
from .base_views import BaseTemplateView
from django.contrib.admin.models import LogEntry
from ..services import ActivityLogService, AuthenticationService
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.core.paginator import Paginator
from ..models import ActivityLog
from django.conf import settings
from .. utils import rate_limit
from django.contrib import messages
from django.shortcuts import redirect, render
from django.contrib.auth import update_session_auth_hash
import qrcode
import base64
from io import BytesIO

auth_service = AuthenticationService()

@method_decorator(never_cache, name='dispatch')
class ProfileView(LoginRequiredMixin, PaginationMixin, BaseTemplateView):
    template_name = 'accounts/profile.html'
    activity_service = ActivityLogService()

    def get_user_content_types(self):
        return [perm.split('.')[1].split('_')[1] 
                for perm in self.request.user.get_all_permissions()]

    def get_activity_logs(self):
        if self.request.user.is_staff:
            content_types = self.get_user_content_types()
            logs = LogEntry.objects.filter(
                content_type__model__in=content_types
            ).select_related('content_type', 'user').order_by('-action_time')[:100]
        else:
            logs = ActivityLog.objects.filter(
                user=self.request.user
            ).select_related('user').order_by('-timestamp')[:100]
        
        return [self.activity_service.format_log_entry(log) for log in logs]

    def get_models_data(self):
        models_data = []
        for app_config in apps.get_app_configs():
            if not app_config.name.startswith('django.'):
                for model in app_config.get_models():
                    models_data.append({
                        'name': model._meta.verbose_name.capitalize(),
                        'app_label': model._meta.app_label,
                        'model_name': model._meta.model_name,
                        'permissions': auth_service.get_user_permissions(self.request.user)
                    })
        return models_data

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_tab = self.request.GET.get('tab', 'activities')
        page_number = self.request.GET.get('page', 1)
        
        if current_tab == 'activities':
            activity_logs = self.get_activity_logs()
            paginator = Paginator(activity_logs, settings.PAGINATION_SIZE)
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'activity_logs': page_obj.object_list,
                'page_obj': page_obj,
                'current_tab': current_tab,
                'is_staff_view': self.request.user.is_staff
            })
        else:
            models_data = self.get_models_data()
            paginator = Paginator(models_data, settings.PAGINATION_SIZE)
            page_obj = paginator.get_page(page_number)
            
            context.update({
                'models': page_obj.object_list,
                'page_obj': page_obj,
                'current_tab': current_tab
            })
        
        return context


@login_required
@require_POST
@rate_limit('profile_update', limit=10, timeout=60)
def update_profile_image(request):
    try:
        if 'profile_image' in request.FILES:
            request.user.profile_image = request.FILES['profile_image']
            request.user.save()
            messages.success(request, 'Profile image updated successfully')
        else:
            messages.error(request, 'No image file provided')
    except Exception as e:
        messages.error(request, 'Error updating profile image')
    return redirect('profile')

@login_required
@require_POST
@rate_limit('profile_update', limit=10, timeout=60)
def update_profile(request):
    try:
        if not request.POST.get('first_name'):
            messages.error(request, 'First name is required')
            return redirect('profile')
        if not request.POST.get('last_name'):
            messages.error(request, 'Last name is required')
            return redirect('profile')
        
        request.user.first_name = request.POST.get('first_name')
        request.user.last_name = request.POST.get('last_name')
        request.user.phone_number = request.POST.get('phone_number')
        request.user.save()
        messages.success(request, 'Profile updated successfully')
    except Exception as e:
        messages.error(request, 'Error updating profile')
    return redirect('profile')

@login_required
@require_POST
@rate_limit('security', limit=3, timeout=3600)
def change_password(request):
    try:
        old_password = request.POST.get('old_password')
        new_password = request.POST.get('new_password')
        
        if request.user.is_2fa_enabled:
            otp_code = request.POST.get('otp_code')
            device = TOTPDevice.objects.get(user=request.user)
            if not device.verify_token(otp_code):
                messages.error(request, 'Invalid 2FA code')
                return redirect('profile')
        
        if request.user.check_password(old_password):
            request.user.set_password(new_password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, 'Password changed successfully')
        else:
            messages.error(request, 'Current password is incorrect')
    except Exception as e:
        messages.error(request, 'Error changing password')
    return redirect('profile')

@login_required
@require_POST
@rate_limit('security', limit=5, timeout=3600)
def toggle_2fa(request):
    try:
        if request.user.is_2fa_enabled:
            device = TOTPDevice.objects.get(user=request.user)
            device.delete()
            request.user.is_2fa_enabled = False
            request.user.save()
            messages.success(request, '2FA has been disabled')
            return redirect('profile')
        else:
            device = TOTPDevice.objects.create(user=request.user, name=f"2FA for {request.user.username}")
            
            qr = qrcode.QRCode(version=1, box_size=10, border=5)
            qr.add_data(device.config_url)
            qr.make(fit=True)
            img = qr.make_image(fill_color="black", back_color="white")
            
            buffer = BytesIO()
            img.save(buffer, format='PNG')
            qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()
            
            return render(request, 'accounts/setup_2fa.html', {
                'device': device,
                'qr_code': f"data:image/png;base64,{qr_code_base64}"
            })
    except Exception as e:
        messages.error(request, 'Error updating 2FA settings')
        return redirect('profile')

@login_required
@require_POST
@csrf_protect
@rate_limit('verify_2fa', limit=5, timeout=300)
def verify_2fa(request):
    try:
        device = TOTPDevice.objects.filter(user=request.user).order_by('-id').first()
        
        if not device:
            messages.error(request, 'No 2FA device found')
            return redirect('profile')
            
        if device.verify_token(request.POST.get('otp_code')):
            device.confirmed = True
            device.save()
            request.user.is_2fa_enabled = True
            request.user.save()
            
            TOTPDevice.objects.filter(user=request.user).exclude(id=device.id).delete()
            messages.success(request, '2FA has been enabled successfully')
        else:
            device.delete()
            messages.error(request, 'Invalid verification code')
    except Exception as e:
        messages.error(request, 'Error verifying 2FA')
    return redirect('profile')

@login_required
@require_POST
@csrf_protect
@rate_limit('security', limit=5, timeout=3600)
def toggle_email_otp(request):
    try:
        request.user.is_email_otp_enabled = not request.user.is_email_otp_enabled
        request.user.save()
        messages.success(request, 'Email OTP has been ' + ('enabled' if request.user.is_email_otp_enabled else 'disabled'))
    except Exception as e:
        messages.error(request, 'Error updating Email OTP settings')
    return redirect('profile')
