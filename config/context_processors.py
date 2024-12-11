from datetime import date
from apps.employees.models import Employee
from apps.reports.models import Report

def report_context(request):
    context = {'has_today_report': True}
    
    if request.user.is_authenticated and request.user.is_employee:
        try:
            employee = Employee.objects.select_related('user').get(user=request.user)
            context['has_today_report'] = Report.objects.select_related('employee').filter(
                employee=employee,
                date=date.today()
            ).exists()
        except Employee.DoesNotExist:
            pass
            
    return context

def employee_status_context(request):
    if request.user.is_authenticated and request.user.is_staff:
        total_active = Employee.objects.filter(user__is_active=True).count()
        working_now = Employee.objects.filter(user__is_active=True, is_online=True).count()
        return {
            'active_employees_count': total_active,
            'working_employees_count': working_now
        }
    return {}