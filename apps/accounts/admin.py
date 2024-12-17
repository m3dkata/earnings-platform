from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.shortcuts import redirect
from apps.accounts.forms import CustomLoginForm
from .models import (
    CustomUser,
    EmailVerification,
    EmployeeUser,
    FaceDescriptor,
    PendingUser,
    ArchivedUser,
)
from .utils import send_otp_email, generate_otp
from django.db.transaction import on_commit
from apps.employees.models import Employee
from django.contrib.auth.models import Group
from django_otp.plugins.otp_totp.models import TOTPDevice
from import_export import resources
from import_export.admin import ImportExportMixin

class CustomUserResource(resources.ModelResource):
    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 
                 'is_active', 'is_employee', 'is_staff', 'phone_number')
        export_order = fields

class CustomAdminSite(admin.AdminSite):
    login_form = CustomLoginForm
    login_template = "accounts/login.html"

    def login(self, request, extra_context=None):
        if request.method == "POST":
            login_form = self.login_form(request, data=request.POST)
            if login_form.is_valid():
                user = login_form.get_user()
                if user.is_2fa_enabled or user.is_email_otp_enabled:
                    request.session["user_id"] = user.id
                    if user.is_email_otp_enabled:
                        otp = generate_otp()
                        EmailVerification.objects.update_or_create(
                            user=user, defaults={"otp": otp}
                        )
                        on_commit(lambda: send_otp_email(user, otp))
                        return redirect("verify_login_email")
                    return redirect("verify_login_2fa")
        return super().login(request, extra_context)


class CustomUserAdmin(ImportExportMixin, UserAdmin):
    resource_class = CustomUserResource
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_employee",
        "is_staff",
        "is_superuser",
    )
    list_filter = ("last_login", "is_active", "is_employee", "is_staff", "is_superuser")

    fieldsets = UserAdmin.fieldsets + (
        (
            "Security",
            {
                "fields": (
                    "is_2fa_enabled",
                    "is_email_otp_enabled",
                )
            },
        ),
        (
            "Employee Status",
            {
                "fields": (
                    "is_employee",
                    "is_archived",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_superuser=True)


class EmployeeInline(admin.StackedInline):
    model = Employee
    show_change_link = True
    verbose_name = "Employee Info"
    verbose_name_plural = "Employees Info"
    extra = 0


class EmployeeAccount(ImportExportMixin, UserAdmin):
    resource_class = CustomUserResource
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_employee",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_staff",
        "groups",
        "employee_profile__workshop__name",
        "employee_profile__position",
    )
    inlines = [EmployeeInline]

    def get_fieldsets(self, request, obj=None):
        employee_status = (
            (
                "Employee Status",
                {
                    "fields": (
                        "is_employee",
                        "is_archived",
                    )
                },
            ),
        )
        return employee_status + UserAdmin.fieldsets

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .select_related("employee_profile", "employee_profile__workshop")
            .filter(is_active=True, is_employee=True, is_archived=False)
        )


class PendingAccount(ImportExportMixin, UserAdmin):
    resource_class = CustomUserResource
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_employee",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_staff",
        "groups",
        "employee_profile__workshop__name",
        "employee_profile__position",
    )
    inlines = [EmployeeInline]

    fieldsets = (
        (
            "Employee Status",
            {
                "fields": (
                    "is_active",
                    "is_employee",
                    "is_archived",
                )
            },
        ),
    )

    def get_queryset(self, request):
        return (
            super()
            .get_queryset(request)
            .filter(is_active=False, is_employee=True, is_archived=False)
        )


class ArchivedAccount(ImportExportMixin, UserAdmin):
    resource_class = CustomUserResource
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_active",
        "is_employee",
        "is_staff",
        "is_superuser",
    )
    list_filter = (
        "is_staff",
        "groups",
        "employee_profile__workshop__name",
        "employee_profile__position",
    )
    inlines = [EmployeeInline]

    def get_fieldsets(self, request, obj=None):
        employee_status = (
            (
                "Employee Status",
                {
                    "fields": (
                        "is_archived",
                        "is_employee",
                    )
                },
            ),
        )
        return employee_status + UserAdmin.fieldsets

    def get_queryset(self, request):
        return super().get_queryset(request).filter(is_archived=True)


class GroupAdmin(admin.ModelAdmin):
    list_display = ("name",)


admin_site = CustomAdminSite()
admin_site.site_header = "EARNINGS Platform"
admin_site.site_title = "Earnings"
admin_site.index_title = "Management"
admin_site.register(TOTPDevice)
admin_site.register(CustomUser, CustomUserAdmin)
admin_site.register(EmployeeUser, EmployeeAccount)
admin_site.register(PendingUser, PendingAccount)
admin_site.register(ArchivedUser, ArchivedAccount)
admin_site.register(Group, GroupAdmin)
admin_site.register(FaceDescriptor)
