from django.urls import path
from apps.accounts.views import (
    ActiveEmployeeListView,
    InactiveEmployeeListView,
    ArchivedEmployeeListView,
    toggle_employee_status,
)
from .views import (
    EmployeeStatsView,
    LeaveRequestView,
    LeaveListView,
    ApproveLeaveView,
    RejectLeaveView,
)

urlpatterns = [
    path("", ActiveEmployeeListView.as_view(), name="active_employees"),
    path("inactive/", InactiveEmployeeListView.as_view(), name="inactive_employees"),
    path("archived/", ArchivedEmployeeListView.as_view(), name="archived_employees"),
    path(
        "toggle-status/<int:employee_id>/",
        toggle_employee_status,
        name="toggle_employee_status",
    ),
    path("stats/", EmployeeStatsView.as_view(), name="employee_stats"),
    path("leaves/", LeaveListView.as_view(), name="leave_list"),
    path("leave/request/", LeaveRequestView.as_view(), name="leave_request"),
    path(
        "leave/<int:leave_id>/approve/",
        ApproveLeaveView.as_view(),
        name="approve_leave",
    ),
    path(
        "leave/<int:leave_id>/reject/", RejectLeaveView.as_view(), name="reject_leave"
    ),
]
