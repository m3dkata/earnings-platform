from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import OvertimeRequest
from import_export import resources, fields
from import_export.admin import ImportExportMixin

class OvertimeRequestResource(resources.ModelResource):
    employee_name = fields.Field(
        column_name='Employee',
        attribute='employee',
    )
    
    def dehydrate_employee_name(self, leave):
        return f"{leave.employee.user.first_name} {leave.employee.user.last_name}"
    class Meta:
        model = OvertimeRequest
        fields = ('employee_name', 'date', 'start_time', 'end_time', 
                 'hours', 'rate', 'status', 'description')

@admin.register(OvertimeRequest)
class OvertimeRequestAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OvertimeRequestResource
    list_display = ('employee', 'date', 'start_time', 'end_time', 'status', 'rate')
    list_filter = ('status', 'employee__workshop', 'date', 'created_at')
    search_fields = ('employee__user__first_name', 'employee__user__last_name', 'employee__number')
    ordering = ('-date', '-created_at')
    readonly_fields = ('created_at', 'updated_at')
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('employee__user', 'employee__workshop')

admin_site.register(OvertimeRequest, OvertimeRequestAdmin)
