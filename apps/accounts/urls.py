from django.urls import path
from django.contrib.auth.views import LogoutView
from django.views.decorators.cache import cache_page
from django.conf import settings
from django.contrib.auth import views as auth_views

from .views.auth_views import (
    SignUpView,
    CustomLoginView,
    CustomPasswordResetView,
    CustomPasswordResetConfirmView,
    verify_email,
    verify_login_2fa,
    verify_login_email,
)
from .views.profile_views import (
    ProfileView,
    update_profile_image,
    update_profile,
    change_password,
    toggle_2fa,
    verify_2fa,
    toggle_email_otp,
)
from .views.face_auth_views import (
    face_training,
    save_face_descriptor,
    verify_face_login,
)

urlpatterns = [
    # Authentication URLs
    path("signup/", SignUpView.as_view(), name="signup"),
    path("login/", CustomLoginView.as_view(), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("verify-email/<int:user_id>/", verify_email, name="verify_email"),
    path("verify-login-2fa/", verify_login_2fa, name="verify_login_2fa"),
    path("verify-login-email/", verify_login_email, name="verify_login_email"),
    # Profile URLs
    path(
        "profile/",
        cache_page(settings.CACHE_TIMEOUT)(ProfileView.as_view()),
        name="profile",
    ),
    path("profile/update-image/", update_profile_image, name="update_profile_image"),
    path("profile/update/", update_profile, name="update_profile"),
    path("profile/change-password/", change_password, name="change_password"),
    path("profile/toggle-2fa/", toggle_2fa, name="toggle_2fa"),
    path("profile/verify-2fa/", verify_2fa, name="verify_2fa"),
    path("toggle-email-otp/", toggle_email_otp, name="toggle_email_otp"),
    # Password Reset URLs
    path("password-reset/", CustomPasswordResetView.as_view(), name="password_reset"),
    path(
        "password-reset/done/",
        auth_views.PasswordResetDoneView.as_view(
            template_name="accounts/password_reset_done.html"
        ),
        name="password_reset_done",
    ),
    path(
        "reset/<uidb64>/<token>/",
        CustomPasswordResetConfirmView.as_view(),
        name="password_reset_confirm",
    ),
    path(
        "reset/done/",
        auth_views.PasswordResetCompleteView.as_view(
            template_name="accounts/password_reset_complete.html"
        ),
        name="password_reset_complete",
    ),
    # Face Authentication URLs
    path("face/train/", face_training, name="face_training"),
    path("face/save-descriptor/", save_face_descriptor, name="save_face_descriptor"),
    path("face/verify/", verify_face_login, name="verify_face_login"),
]
