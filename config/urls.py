"""
URL configuration for exam_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.1/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
import os
from apps.accounts.admin import admin_site
from django.urls import path, include, re_path
from django.views.static import serve
from apps.accounts.views.dashboard_views import home, DashboardView
from django.conf import settings
from django.conf.urls.static import static
from django.urls import include, path
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('admin/', admin_site.urls),
    path('accounts/', include('apps.accounts.urls')),
    path('employees/', include('apps.employees.urls')),
    path('operations/', include('apps.operations.urls')),
    path('reports/', include('apps.reports.urls')),
    path('payrolls/', include('apps.payrolls.urls')),
    path('notifications/', include('apps.notifications.urls')),
    path('api/', include('apps.api.urls')),
    path('ai/', include('apps.ai.urls')),
    
    path('', home, name='home'),
    path('dashboard/', DashboardView.as_view(), name='dashboard'),
    
    path('api-auth/', include('rest_framework.urls')),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(
        template_name='accounts/password_reset_confirm.html'
    ), name='password_reset_confirm'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(
        template_name='accounts/password_reset_complete.html'
    ), name='password_reset_complete'),
    
    re_path(r'^media/(?P<path>.*)$',serve,{'document_root':settings.MEDIA_ROOT}),
]  + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'config.views.bad_request'
handler403 = 'config.views.permission_denied'
handler404 = 'config.views.page_not_found'
handler500 = 'config.views.server_error'
handler500 = 'config.views.csrf_failure'

if settings.BUILD_ENVIRONMENT == 'development':
    try:
        import debug_toolbar
        urlpatterns += [
            path('__debug__/', include(debug_toolbar.urls)),
        ]
    except ImportError:
        pass