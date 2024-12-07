from django.views.generic import TemplateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.utils import timezone
from datetime import timedelta
from apps.reports.models import Report, ReportOperation
from apps.employees.models import Employee

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
