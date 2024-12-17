from django.contrib import admin
from apps.accounts.admin import admin_site
from .models import Rate, Operation
from import_export import resources
from import_export.admin import ImportExportMixin

class RateResource(resources.ModelResource):
    class Meta:
        model = Rate
        fields = ('category', 'price')

class OperationResource(resources.ModelResource):
    class Meta:
        model = Operation
        fields = ('code', 'name', 'time', 'price', 'category__category', 'date_added')

@admin.register(Rate)
class RateAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = RateResource
    list_display = ("category", "price")
    search_fields = ("category",)

@admin.register(Operation)
class OperationAdmin(ImportExportMixin, admin.ModelAdmin):
    resource_class = OperationResource
    list_display = ("code", "name", "time", "price", "category", "date_added")
    list_filter = ("category__category", "date_added")
    search_fields = ("code", "name")
    ordering = ("code",)

admin_site.register(Rate, RateAdmin)
admin_site.register(Operation, OperationAdmin)
