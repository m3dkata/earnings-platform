from django.urls import path
from apps.api.views.accounts import (
    UserLoginAPIView,
    UserLogoutAPIView,
    UserSignupAPIView,
    VerifyOTPAPIView,
)
from apps.api.views.notifications import NotificationViewSet
from apps.api.views.operations import (
    OperationDetailAPIView,
    OperationListCreateAPIView,
    RateDetailAPIView,
    RateListCreateAPIView,
)
from apps.api.views.payrolls import PayrollDetailAPIView, PayrollListCreateAPIView
from apps.api.views.reports import ReportDetailAPIView, ReportListCreateAPIView
from drf_spectacular.views import (
    SpectacularAPIView,
    SpectacularSwaggerView,
    SpectacularRedocView,
)
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

urlpatterns = [
    path(
        "notifications/",
        NotificationViewSet.as_view({"get": "list"}),
        name="notification",
    ),
    # Authentication endpoints
    path("auth/signup/", UserSignupAPIView.as_view(), name="api_signup"),
    path("auth/login/", UserLoginAPIView.as_view(), name="api_login"),
    path("auth/logout/", UserLogoutAPIView.as_view(), name="api_logout"),
    path("auth/verify-otp/", VerifyOTPAPIView.as_view(), name="api_verify_otp"),
    # Operations and Rates endpoints
    path("operations/", OperationListCreateAPIView.as_view(), name="api_operations"),
    path(
        "operations/<int:pk>/",
        OperationDetailAPIView.as_view(),
        name="api_operation_detail",
    ),
    path("rates/", RateListCreateAPIView.as_view(), name="api_rates"),
    path("rates/<int:pk>/", RateDetailAPIView.as_view(), name="api_rate_detail"),
    # Reports endpoints
    path("reports/", ReportListCreateAPIView.as_view(), name="api_reports"),
    path("reports/<int:pk>/", ReportDetailAPIView.as_view(), name="api_report_detail"),
    # Payroll endpoints
    path("payrolls/", PayrollListCreateAPIView.as_view(), name="api_payrolls"),
    path(
        "payrolls/<int:pk>/", PayrollDetailAPIView.as_view(), name="api_payroll_detail"
    ),
    # JWT endpoints
    path("token/", TokenObtainPairView.as_view(), name="token_obtain_pair"),
    path("token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    # Spectacular endpoints
    path("schema/", SpectacularAPIView.as_view(), name="schema"),
    path("", SpectacularSwaggerView.as_view(url_name="schema"), name="swagger-ui"),
    path(
        "schema/redoc/", SpectacularRedocView.as_view(url_name="schema"), name="redoc"
    ),
]
