from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import OvertimeRequest

@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(admin.ModelAdmin):
    list_display = ('employee', 'date', 'start_time', 'end_time', 'status', 'rate')
    list_filter = ('status', 'employee__workshop', 'date', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__number')
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user', 'employee__workshop')

admin_site.register(OvertimeRequest, OvertimeRequestAdmin)
