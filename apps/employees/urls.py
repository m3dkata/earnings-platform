from django.urls import path
from apps.accounts.views import ActiveEmployeeListView, InactiveEmployeeListView, ArchivedEmployeeListView, toggle_employee_status
from .views import EmployeeStatsView

urlpatterns = [
    path('', ActiveEmployeeListView.as_view(), name='active_employees'),
    path('inactive/', InactiveEmployeeListView.as_view(), name='inactive_employees'),
    path('archived/', ArchivedEmployeeListView.as_view(), name='archived_employees'),
    path('toggle-status/<int:employee_id>/', toggle_employee_status, name='toggle_employee_status'),

    path('stats/', EmployeeStatsView.as_view(), name='employee_stats'),
]
