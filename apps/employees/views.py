from django.views.generic import TemplateView, View, ListView
from django.views.generic.edit import CreateView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from django.urls import reverse_lazy
from apps.reports.models import Report, ReportOperation
from apps.employees.models import Employee, Leave
from django.shortcuts import get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .forms import LeaveRequestForm
from datetime import datetime
from .forms import LeaveFilterForm
from apps.notifications.services import NotificationService

def get_base_context(request):
    if request.user.is_authenticated and request.user.is_staff:
        total_active = Employee.objects.filter(user__is_active=True).count()
        working_now = Employee.objects.filter(user__is_active=True, is_online=True).count()
        return {
            'active_employees_count': total_active,
            'working_employees_count': working_now
        }
    return {}

class LeaveRequestView(LoginRequiredMixin, CreateView):
    model = Leave
    form_class = LeaveRequestForm
    template_name = 'employees/leave_request.html'
    success_url = reverse_lazy('leave_list')
    
    def form_valid(self, form):
        form.instance.employee = self.request.user.employee_profile
        messages.success(self.request, 'Leave request submitted successfully')
        return super().form_valid(form)

class ApproveLeaveView(PermissionRequiredMixin, View):
    permission_required = 'employees.can_approve_leave'
    raise_exception = True
    
    def post(self, request, leave_id):
        leave = get_object_or_404(Leave, id=leave_id)
        leave.status = 'APPROVED'
        leave.save()
        
        from apps.payrolls.models import Payroll
        payroll, created = Payroll.objects.get_or_create(
            employee=leave.employee,
            month=leave.start_datetime.date().replace(day=1)
        )
        
        days = leave.duration_in_days()
        if days > 0:
            if leave.leave_type == 'VACATION':
                payroll.vacation_days += days
            else:
                payroll.sick_days += days
            payroll.save()
        
        NotificationService.notify_leave_status(leave)
        messages.success(request, f'Leave request for {leave.employee} has been approved')
        return HttpResponse(status=204)

class RejectLeaveView(PermissionRequiredMixin, View):
    permission_required = 'employees.can_reject_leave'
    raise_exception = True
    
    def post(self, request, leave_id):
        leave = get_object_or_404(Leave, id=leave_id)
        leave.status = 'REJECTED'
        leave.save()
        
        NotificationService.notify_leave_status(leave)
        messages.success(request, f'Leave request for {leave.employee} has been rejected')
        return HttpResponse(status=204)

class LeaveListView(LoginRequiredMixin, ListView):
    model = Leave
    template_name = 'employees/leave_list.html'
    context_object_name = 'leaves'
    
    def get_queryset(self):
        queryset = Leave.objects.select_related('employee__user').order_by('-created_at')
        
        month = self.request.GET.get('month')
        if month:
            date = datetime.strptime(month, '%Y-%m')
            queryset = queryset.filter(
                created_at__year=date.year,
                created_at__month=date.month
            )
        
        if not self.request.user.has_perm('employees.can_approve_leave'):
            queryset = queryset.filter(employee__user=self.request.user)
        else:
            employee_id = self.request.GET.get('employee')
            if employee_id:
                queryset = queryset.filter(employee_id=employee_id)
                
        return queryset
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter_form'] = LeaveFilterForm(self.request.GET)
        if self.request.user.has_perm('employees.can_approve_leave'):
            context['employees'] = Employee.objects.select_related('user').all()
        return context

class EmployeeStatsView(LoginRequiredMixin, TemplateView):
    template_name = 'employees/employee_stats.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        
        period = self.request.GET.get('period', 'week')
        employee_id = self.request.GET.get('employee')
        
        if self.request.user.is_staff:
            employees = Employee.objects.select_related('user').all()
            if employee_id:
                employee = employees.get(id=employee_id)
            else:
                employee = employees.first()
        else:
            employee = Employee.objects.select_related('user').get(user=self.request.user)
            employees = None
            
        today = timezone.now()
        if period == 'week':
            start_date = today - timedelta(days=7)
        elif period == 'month':
            start_date = today - timedelta(days=30)
        elif period == 'year':
            start_date = today - timedelta(days=365)
        else:
            start_date = today - timedelta(days=7)

        operations = ReportOperation.objects.select_related(
            'operation',
            'report',
            'report__employee'
        ).filter(
            report__employee=employee,
            report__date__gte=start_date
        )

        reports = Report.objects.select_related('employee').filter(
            employee=employee,
            date__gte=start_date
        )

        chart_data = []
        for operation in operations:
            chart_data.append({
                'date': operation.report.date.strftime('%Y-%m-%d'),
                'operation_code': operation.operation.code,
                'quantity': operation.quantity,
                'percent': float(operation.percent),
                'sum': float(operation.sum)
            })

        context.update({
            'period': period,
            'employees': employees,
            'selected_employee': employee,
            'operations': operations,
            'reports': reports,
            'chart_data': chart_data,
            'total_operations': operations.count(),
            'total_reports': reports.count(),
        })
        
        return context
