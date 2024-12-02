from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.generic import TemplateView
from django.utils import timezone
from datetime import timedelta
from django.db.models import Count, Sum, Avg
from apps.reports.models import Report
from django.contrib import messages

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard.html'

    def get_base_query(self, date):
        return Report.objects.select_related(
            'employee__user'
        ).prefetch_related(
            'reportoperation_set'
        ).filter(
            date__year=date.year,
            date__month=date.month,
            status='APPROVED'
        )

    def get_monthly_stats(self, date, user):
        base_query = self.get_base_query(date)
        
        if not user.is_staff:
            base_query = base_query.filter(employee__user=user)
        
        stats = base_query.aggregate(
            total_operations=Count('reportoperation'),
            total_earnings=Sum('total_sum'),
            work_days=Count('date', distinct=True),
            avg_percent=Avg('total_percent'),
            employee_count=Count('employee', distinct=True)
        )
        
        employee_count = stats['employee_count'] or 1
        
        if user.is_staff:
            return {
                'operations': stats['total_operations'] / employee_count,
                'earnings': stats['total_earnings'] / employee_count if stats['total_earnings'] else 0,
                'work_days': stats['work_days'],
                'avg_percent': stats['avg_percent'] or 0
            }
        
        return {
            'operations': stats['total_operations'] or 0,
            'earnings': stats['total_earnings'] or 0,
            'work_days': stats['work_days'],
            'avg_percent': stats['avg_percent'] or 0
        }

    def get_chart_data(self):
        current_date = timezone.now()
        base_query = self.get_base_query(current_date)
        
        if not self.request.user.is_staff:
            base_query = base_query.filter(employee__user=self.request.user)
        
        daily_stats = base_query.values('date').annotate(
            daily_sum=Sum('total_sum'),
            daily_percent=Avg('total_percent'),
            employee_count=Count('employee', distinct=True)
        ).order_by('date')
            
        return {
            'dates': [stat['date'].strftime('%Y-%m-%d') for stat in daily_stats],
            'sums': [float(stat['daily_sum'] / stat['employee_count'] if self.request.user.is_staff else stat['daily_sum'] or 0) for stat in daily_stats],
            'percents': [float(stat['daily_percent'] or 0) for stat in daily_stats],
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        current_date = timezone.now()
        last_month = current_date.replace(day=1) - timedelta(days=1)
        
        current_stats = self.get_monthly_stats(current_date, self.request.user)
        last_month_stats = self.get_monthly_stats(last_month, self.request.user)
        
        recent_reports = self.get_base_query(current_date)
        if not self.request.user.is_staff:
            recent_reports = recent_reports.filter(employee__user=self.request.user)
        
        context.update({
            'total_operations': current_stats['operations'],
            'operations_change': current_stats['operations'] - last_month_stats['operations'] if last_month_stats['operations'] else 0,
            'total_earnings': current_stats['earnings'],
            'earnings_change': current_stats['earnings'] - last_month_stats['earnings'] if last_month_stats['earnings'] else 0,
            'work_days': current_stats['work_days'],
            'work_days_change': current_stats['work_days'] - last_month_stats['work_days'] if last_month_stats['work_days'] else 0,
            'avg_percent': current_stats['avg_percent'],
            'percent_change': ((current_stats['avg_percent'] - last_month_stats['avg_percent']) / last_month_stats['avg_percent'] * 100) if last_month_stats['avg_percent'] else 0,
            'recent_reports': recent_reports.order_by('-date')[:10],
            'chart_data': self.get_chart_data()
        })
        
        return context

def home(request):
    if request.user.is_authenticated:
        return redirect('dashboard')
    messages.info(request, "Please login to continue")
    return redirect('login')    