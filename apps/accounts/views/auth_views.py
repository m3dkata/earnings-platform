from django.contrib.auth.views import (
    LoginView,
    PasswordResetView,
    PasswordResetConfirmView,
)
from django.views.generic.edit import CreateView
from django_otp.plugins.otp_totp.models import TOTPDevice
from django.conf import settings
from django.shortcuts import redirect, render
from django.contrib.auth import login
from django.urls import reverse_lazy
from django.contrib import messages
from django.db.transaction import on_commit
from ..forms import CustomUserCreationForm, CustomLoginForm, PasswordResetForm
from ..models import CustomUser, EmailVerification
from ..utils import (
    send_otp_email,
    send_welcome_email,
    send_password_reset_email,
    generate_otp,
    rate_limit,
)
from ..services import AuthenticationService
from apps.notifications.services import NotificationService

auth_service = AuthenticationService()


class SignUpView(CreateView):
    form_class = CustomUserCreationForm
    template_name = "accounts/signup.html"

    def form_valid(self, form):
        try:
            user = form.save(commit=False)
            user.is_active = False
            user.save()
            NotificationService.notify_staff_new_registration(user)
            send_welcome_email(user)
            messages.info(
                self.request,
                "Your account has been created and is pending admin approval",
            )
            return redirect("login")
        except Exception:
            messages.error(self.request, "An error occurred during signup")
            return self.form_invalid(form)

    def form_invalid(self, form):
        for field, errors in form.errors.items():
            for error in errors:
                messages.error(self.request, error)
        return super().form_invalid(form)


class CustomLoginView(LoginView):
    form_class = CustomLoginForm
    template_name = "accounts/login.html"

    @rate_limit("login_attempt", limit=settings.MAX_LOGIN_ATTEMPTS, timeout=300)
    def form_valid(self, form):
        try:
            user = form.get_user()
            if not user.is_active:
                messages.error(self.request, "Account not activated by Administrators")
                return self.form_invalid(form)

            self.request.session["user_id"] = user.id

            if user.is_2fa_enabled or user.is_email_otp_enabled:
                if user.is_email_otp_enabled:
                    otp = generate_otp()
                    EmailVerification.objects.update_or_create(
                        user=user, defaults={"otp": otp}
                    )
                    on_commit(lambda: send_otp_email(user, otp))
                    messages.info(
                        self.request, "Please check your email for verification code"
                    )

                if user.is_2fa_enabled:
                    messages.info(
                        self.request, "Or enter your 2FA code from authenticator app."
                    )

                return redirect(
                    "verify_login_email"
                    if user.is_email_otp_enabled
                    else "verify_login_2fa"
                )

            login(self.request, user)
            messages.success(self.request, f"Welcome back, {user.get_full_name()}")
            return super().form_valid(form)
        except Exception as e:
            messages.error(self.request, f"An error occurred during login- {str(e)}")
            return self.form_invalid(form)


class CustomPasswordResetView(PasswordResetView):
    template_name = "accounts/password_reset.html"
    html_email_template_name = "email_templates/password_reset.html"
    email_template_name = "email_templates/password_reset.html"
    subject_template_name = "email_templates/password_reset_subject.txt"
    success_url = reverse_lazy("password_reset_done")
    form_class = PasswordResetForm

    def send_email(self, *args, **kwargs):
        """Override to use custom email sending"""
        user = kwargs.get("user")
        reset_url = kwargs.get("reset_url")
        send_password_reset_email(user, reset_url)


class CustomPasswordResetConfirmView(PasswordResetConfirmView):
    template_name = "accounts/password_reset_confirm.html"
    success_url = reverse_lazy("password_reset_complete")
    post_reset_login = True

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["validlink"] = self.validlink
        return context

    def form_valid(self, form):
        user = form.save()
        messages.success(self.request, "Your password has been reset successfully!")
        return super().form_valid(form)


@rate_limit("login", limit=settings.MAX_LOGIN_ATTEMPTS, timeout=300)
def verify_email(request, user_id):
    try:
        verification = EmailVerification.objects.get(user_id=user_id)
    except EmailVerification.DoesNotExist:
        messages.error(request, "Invalid verification link")
        return redirect("login")
    except Exception:
        messages.error(request, "System error occurred")
        return redirect("login")

    if request.method == "POST":
        if verification.otp == request.POST.get("otp"):
            user = verification.user
            user.is_active = True
            user.save()
            verification.delete()
            messages.success(request, "Email verified successfully. You can now login.")
            return redirect("login")
        messages.error(request, "Invalid verification code")
    return render(request, "accounts/verify_email.html")


@rate_limit("login", limit=settings.MAX_LOGIN_ATTEMPTS, timeout=300)
def verify_login_2fa(request):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            messages.error(request, "Invalid session. Please login again.")
            return redirect("login")

        if request.method == "POST":
            user = auth_service.verify_user(user_id)
            if not user:
                messages.error(request, "User not found")
                return redirect("login")

            device = TOTPDevice.objects.get(user=user)
            if device.verify_token(request.POST.get("otp_code")):
                login(request, user)
                del request.session["user_id"]
                messages.success(request, f"Welcome back, {user.get_full_name()}")
                return redirect("dashboard")
            messages.error(request, "Invalid 2FA code")
    except Exception:
        messages.error(request, "Authentication failed")
        return redirect("login")

    return render(request, "accounts/verify_login_2fa.html")


@rate_limit("login", limit=settings.MAX_LOGIN_ATTEMPTS, timeout=300)
def verify_login_email(request):
    try:
        user_id = request.session.get("user_id")
        if not user_id:
            messages.error(request, "Invalid session. Please login again.")
            return redirect("login")

        if request.method == "POST":
            user = auth_service.verify_user(user_id)
            if not user:
                messages.error(request, "User not found")
                return redirect("login")

            otp_code = request.POST.get("otp_code")

            if user.is_2fa_enabled:
                device = TOTPDevice.objects.get(user=user)
                if device.verify_token(otp_code):
                    login(request, user)
                    del request.session["user_id"]
                    messages.success(request, f"Welcome back, {user.get_full_name()}")
                    return redirect("dashboard")

            if user.is_email_otp_enabled:
                verification = EmailVerification.objects.get(user=user)
                if verification.otp == otp_code:
                    login(request, user)
                    verification.delete()
                    del request.session["user_id"]
                    messages.success(request, f"Welcome back, {user.get_full_name()}")
                    return redirect("dashboard")

            messages.error(request, "Invalid verification code")
    except Exception:
        messages.error(request, "Authentication failed")
        return redirect("login")

    return render(
        request,
        "accounts/verify_login_email.html",
        {
            "user_has_2fa": CustomUser.objects.get(id=user_id).is_2fa_enabled,
            "user_has_email_otp": CustomUser.objects.get(
                id=user_id
            ).is_email_otp_enabled,
        },
    )
