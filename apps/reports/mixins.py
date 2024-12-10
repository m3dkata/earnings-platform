from django.utils import timezone
from django.shortcuts import redirect
from django.contrib import messages
from datetime import time
from django.views.generic import CreateView
from apps.employees.models import Leave

class WorkHourRestrictionMixin:
    def dispatch(self, request, *args, **kwargs):
        if hasattr(self, 'get_object') and not isinstance(self, CreateView):
            report = self.get_object()
            if report.status == 'APPROVED':
                return super().dispatch(request, *args, **kwargs)
        
        current_time = timezone.localtime().time()
        workday_start = time(6, 0)
        workday_end = time(23, 0)
        
        if current_time < workday_start or current_time > workday_end:
            messages.error(request, "You cannot add/edit Report outside worktime!")
            return redirect('report-list')
            
        return super().dispatch(request, *args, **kwargs)