from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import Rate, Operation


@admin.register(Rate)
class RateAdmin(admin.ModelAdmin):
    list_display = ("category", "price")
    search_fields = ("category",)


@admin.register(Operation)
class OperationAdmin(admin.ModelAdmin):
    list_display = ("code", "name", "time", "price", "category", "date_added")
    list_filter = ("category__category", "date_added")
    search_fields = ("code", "name")
    ordering = ("code",)


admin_site.register(Rate, RateAdmin)
admin_site.register(Operation, OperationAdmin)
