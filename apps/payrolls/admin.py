from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import Payroll
from import_export import resources, fields
from import_export.admin import ImportExportMixin

class PayrollResource(resources.ModelResource):
    employee_name = fields.Field(
        column_name='Employee',
        attribute='employee',
    )
    
    def dehydrate_employee_name(self, payroll):
        return f"{payroll.employee.user.first_name} {payroll.employee.user.last_name}"
    
    class Meta:
        model = Payroll
        fields = ('employee_name', 'month', 'work_days', 'percent', 'earnings', 
                 'attendance_bonus', 'vacation_days', 'vacation_amount',
                 'sick_days', 'sick_amount', 'total', 'bank_transfer', 'cash_payment')
        export_order = fields

@admin.register(Payroll)
class PayrollAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = PayrollResource
    list_display = ("employee", "month", "percent", "total")
    list_filter = ("month", "employee")
    search_fields = ("employee__user__first_name", "employee__user__last_name")
    ordering = ("-month",)

admin_site.register(Payroll, PayrollAdmin)
