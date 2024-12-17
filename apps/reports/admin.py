from django.contrib import admin
from .models import Report, ReportOperation
from apps.accounts.admin import admin_site


class ReportOperationInline(admin.TabularInline):
    model = ReportOperation
    extra = 0


@admin.register(Report)
class ReportAdmin(admin.ModelAdmin):
    list_display = ("id", "employee", "date", "status", "total_percent", "total_sum")
    list_filter = ("status", "date", "employee__workshop__name")
    search_fields = ("employee__user__first_name", "employee__user__last_name")
    readonly_fields = ("id", "created_at", "updated_at", "total_percent", "total_sum")
    inlines = [ReportOperationInline]
    date_hierarchy = "date"
    ordering = ("-date", "-id")


# @admin.register(ReportOperation)
# class ReportOperationAdmin(admin.ModelAdmin):
#     list_display = ('report', 'operation', 'quantity', 'percent', 'sum')
#     list_filter = ('operation', 'report__status')
#     search_fields = ('report__number', 'operation__name', 'operation__code')
#     readonly_fields = ('percent', 'sum')

admin_site.register(Report, ReportAdmin)
# admin_site.register(ReportOperation, ReportOperationAdmin)
