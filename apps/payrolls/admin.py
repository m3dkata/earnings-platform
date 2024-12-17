from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import Payroll


@admin.register(Payroll)
class PayrollAdmin(admin.ModelAdmin):
    list_display = ("employee", "month", "percent", "total")
    list_filter = ("month", "employee")
    search_fields = ("employee__user__first_name", "employee__user__last_name")
    ordering = ("-month",)


admin_site.register(Payroll, PayrollAdmin)
