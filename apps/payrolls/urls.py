from django.urls import path
from .views import (
    PayrollListView,
    PayrollCreateView,
    PayrollPDFView,
    PayrollUpdateView,
    PayrollDeleteView,
)

urlpatterns = [
    path("", PayrollListView.as_view(), name="payroll-list"),
    path("create/", PayrollCreateView.as_view(), name="payroll-create"),
    path("<int:pk>/update/", PayrollUpdateView.as_view(), name="payroll-update"),
    path("<int:pk>/delete/", PayrollDeleteView.as_view(), name="payroll-delete"),
    path("<int:pk>/pdf/", PayrollPDFView.as_view(), name="payroll-pdf"),
]
