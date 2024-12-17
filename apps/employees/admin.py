from django.contrib import admin
from .models import Workshop, Leave
from apps.accounts.admin import admin_site


@admin.register(Workshop)
class WorkshopAdmin(admin.ModelAdmin):
    list_display = ["name"]
    search_fields = ["name"]


admin_site.register(Workshop, WorkshopAdmin)
admin_site.register(Leave)
