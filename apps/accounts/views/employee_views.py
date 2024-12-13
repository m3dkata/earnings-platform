from django.views.generic import ListView
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.contrib import messages
from ..models import CustomUser
from apps.employees.models import Employee
from apps.employees.forms import EmployeeActivationForm
from django.contrib.auth.models import Group
from django.http import JsonResponse
from django.template.loader import render_to_string

class BaseEmployeeListView(ListView):
    model = Employee
    template_name = 'employees/employees.html'
    context_object_name = 'employees'
    status = ''
    status_class = ''

    def get_queryset(self):
        return super().get_queryset().select_related(
            'user',
            'workshop'
        ).prefetch_related(
            'user__groups'
        ).defer(
            'user__password',
            'user__last_login',
            'user__date_joined'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.update({
            'status': self.status,
            'status_class': self.status_class,
            'employees': self.get_queryset()
        })
        return context

class ActiveEmployeeListView(BaseEmployeeListView):
    status = 'Active'
    status_class = 'bg-green-100 text-green-800'

    def get_queryset(self):
        return Employee.objects.filter(
            user__is_active=True,
            user__is_archived=False
        ).select_related(
            'user',
            'workshop'
        ).order_by('number')

class InactiveEmployeeListView(BaseEmployeeListView):
    status = 'Inactive'
    status_class = 'bg-yellow-100 text-yellow-800'
    model = CustomUser

    def get_queryset(self):
        return CustomUser.objects.filter(
            is_active=False,
            is_archived=False,
            is_employee=True
        ).select_related(
            'employee_profile',
            'employee_profile__workshop'
        )

class ArchivedEmployeeListView(BaseEmployeeListView):
    status = 'Archived'
    status_class = 'bg-red-100 text-red-800'

    def get_queryset(self):
        return Employee.objects.filter(
            user__is_archived=True
        ).select_related(
            'user',
            'workshop'
        ).order_by('number')

    
@login_required
def toggle_employee_status(request, employee_id):
    user = get_object_or_404(CustomUser, id=employee_id)
    
    if request.method == 'GET':
        initial_data = {}
        if hasattr(user, 'employee_profile'):
            initial_data = {
                'number': user.employee_profile.number,
                'position': user.employee_profile.position,
                'workshop': user.employee_profile.workshop
            }
        form = EmployeeActivationForm(initial=initial_data)
        return render(request, 'employees/activate_modal.html', {'form': form, 'user': user})
    
    action = request.POST.get('action')
    if action == 'activate':
        instance = user.employee_profile if hasattr(user, 'employee_profile') else None
        form = EmployeeActivationForm(request.POST, instance=instance)
        if form.is_valid():
            employee = form.save(commit=False)
            employee.user = user
            employee.save()
            try:
                employee_group = Group.objects.get(name='employee')
                user.groups.add(employee_group)
            except Group.DoesNotExist:
                messages.warning(request, "Employee group not found. Please create the group.")
            user.is_active = True
            user.is_archived = False
            user.save()
            messages.success(request, f"Employee {user.get_full_name()} activated successfully")
            return redirect(request.META.get('HTTP_REFERER', 'employee_list'))
        else:
            return JsonResponse({
                'status': 'error',
                'html': render_to_string('employees/activate_modal.html', 
                                       {'form': form, 'user': user},
                                       request=request)
            })
    
    elif action == 'deactivate':
        user.is_active = False
        user.is_archived = False
    elif action == 'archive':
        user.is_archived = True
        user.is_active = False
    elif action == 'unarchive':
        user.is_archived = False
        user.is_active = False
    elif action == 'delete':
        if hasattr(user, 'employee_profile'):
            user.employee_profile.delete()
        user.delete()
        messages.success(request, f"Employee {user.get_full_name()} deleted successfully")
        return redirect('archived_employees')
        
    user.save()
    messages.success(request, f"Employee {user.get_full_name()} status updated successfully")
    return redirect(request.META.get('HTTP_REFERER', 'employee_list'))
