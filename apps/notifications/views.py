from django.views.generic import ListView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.shortcuts import redirect
from django.views.decorators.http import require_POST
from .models import Notification

class NotificationListView(LoginRequiredMixin, ListView):
    model = Notification
    template_name = 'notifications/notification_list.html'
    context_object_name = 'notifications'
    paginate_by = 10
    
    def get_queryset(self):
        queryset = Notification.objects.filter(recipient=self.request.user)
        
        # Type filter
        notification_type = self.request.GET.get('type')
        if notification_type:
            queryset = queryset.filter(notification_type=notification_type)
            
        # Date range filter
        date_from = self.request.GET.get('date_from')
        date_to = self.request.GET.get('date_to')
        if date_from:
            queryset = queryset.filter(created_at__gte=date_from)
        if date_to:
            queryset = queryset.filter(created_at__lte=date_to)
            
        # Read status filter
        read_status = self.request.GET.get('read_status')
        if read_status == 'read':
            queryset = queryset.filter(is_read=True)
        elif read_status == 'unread':
            queryset = queryset.filter(is_read=False)
            
        return queryset.order_by('-created_at')


@require_POST
def mark_as_read(request, pk):
    notification = Notification.objects.get(pk=pk)
    notification.is_read = True
    notification.save()
    
    if notification.notification_type == 'report_status' or notification.notification_type == 'report_submission' and notification.report:
        return redirect('report-update', pk=notification.report.pk)
    elif notification.notification_type == 'registration':
        return redirect('inactive_employees')
    return redirect('notification_list')

