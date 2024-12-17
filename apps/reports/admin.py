from django.contrib import admin
from .models import Report, ReportOperation
from apps.accounts.admin import admin_site
from import_export import resources, fields
from import_export.admin import ImportExportMixin

class ReportOperationInline(admin.TabularInline):
    model = ReportOperation
    extra = 0

class ReportResource(resources.ModelResource):
    employee_name = fields.Field(
        column_name='Employee',
        attribute='employee',
    )
    
    def dehydrate_employee_name(self, report):
        return f"{report.employee.user.first_name} {report.employee.user.last_name}"
    
    class Meta:
        model = Report
        fields = ('employee_name', 'date', 'status', 'total_percent', 
                 'total_sum', 'created_at', 'updated_at')
        export_order = fields

@admin.register(Report)
class ReportAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = ReportResource
    list_display = ("id", "employee", "date", "status", "total_percent", "total_sum")
    list_filter = ("status", "date", "employee__workshop__name")
    search_fields = ("employee__user__first_name", "employee__user__last_name")
    readonly_fields = ("id", "created_at", "updated_at", "total_percent", "total_sum")
    inlines = [ReportOperationInline]
    date_hierarchy = "date"
    ordering = ("-date", "-id")

admin_site.register(Report, ReportAdmin)
