from django.contrib import admin
from .models import Workshop, Leave
from apps.accounts.admin import admin_site
from import_export import resources, fields
from import_export.admin import ImportExportMixin

class WorkshopResource(resources.ModelResource):
    class Meta:
        model = Workshop
        fields = ('name',)

class LeaveResource(resources.ModelResource):
    employee_name = fields.Field(
        column_name='Employee',
        attribute='employee',
    )
    
    def dehydrate_employee_name(self, leave):
        return f"{leave.employee.user.first_name} {leave.employee.user.last_name}"
    
    class Meta:
        model = Leave
        fields = ('employee_name', 'leave_type', 'start_datetime', 
                 'end_datetime', 'status', 'reason')
        export_order = fields

@admin.register(Workshop)
class WorkshopAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = WorkshopResource
    list_display = ["name"]
    search_fields = ["name"]

@admin.register(Leave)
class LeaveAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = LeaveResource
    list_display = ["employee", "leave_type", "status"]

admin_site.register(Workshop, WorkshopAdmin)
admin_site.register(Leave, LeaveAdmin)
