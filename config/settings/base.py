"""
Django settings for exam_project project.
"""

from datetime import timedelta
from pathlib import Path
import environ
import os

# Build paths inside the project like this: BASE_DIR / 'subdir'.
BASE_DIR = Path(__file__).resolve().parent.parent.parent

env = environ.Env(
    DEBUG=(bool, False)
)
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

DEBUG = env('DEBUG', default=False)
BUILD_ENVIRONMENT = env('BUILD_ENVIRONMENT')
ALLOWED_HOSTS = env.list('ALLOWED_HOSTS')
CORS_ALLOWED_ORIGINS = env.list('CORS_ALLOWED_ORIGINS')	
CSRF_TRUSTED_ORIGINS = env.list('CSRF_TRUSTED_ORIGINS')
INTERNAL_IPS = env.list('INTERNAL_IPS')

# SECURITY WARNING: keep the secret key used in production secret!
SECRET_KEY = env('SECRET_KEY')
if os.name == 'nt':
    NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"
else:
    NPM_BIN_PATH = 'npm'
# Tailwind App Name
TAILWIND_APP_NAME='theme'

# Application definition
INSTALLED_APPS = [
    'jazzmin',
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'tailwind',
    'theme',
    'django_otp',
    'django_otp.plugins.otp_totp',
    'apps.accounts.apps.AccountsConfig',
    'apps.employees.apps.EmployeesConfig',
    'apps.operations.apps.OperationsConfig',
    'apps.overtime.apps.OvertimeConfig',
    'apps.reports.apps.ReportsConfig',
    'apps.payrolls.apps.PayrollsConfig',
    'apps.api.apps.ApiConfig',
    'apps.notifications.apps.NotificationsConfig',
    'apps.ai.apps.AiConfig',
    'channels',
    'channels_redis',
    'rest_framework',
    'rest_framework_simplejwt',
    'rest_framework_simplejwt.token_blacklist',
    'drf_spectacular',
    'widget_tweaks',
    'django_htmx',
    "corsheaders",
    'import_export',
    'django_browser_reload',
]

MIDDLEWARE = [
    'django.middleware.security.SecurityMiddleware',
    'django.contrib.sessions.middleware.SessionMiddleware',
    "whitenoise.middleware.WhiteNoiseMiddleware",
    'django.middleware.common.CommonMiddleware',
    'django.middleware.csrf.CsrfViewMiddleware',
    'django.contrib.auth.middleware.AuthenticationMiddleware',
    'django_otp.middleware.OTPMiddleware',
    'apps.employees.middleware.LeaveCheckMiddleware',
    'django.contrib.messages.middleware.MessageMiddleware',
    'django.middleware.clickjacking.XFrameOptionsMiddleware',
    'django_htmx.middleware.HtmxMiddleware',
    "corsheaders.middleware.CorsMiddleware",
    "django_browser_reload.middleware.BrowserReloadMiddleware",
]

if env('BUILD_ENVIRONMENT') == 'development':
    INSTALLED_APPS += ['debug_toolbar']
    MIDDLEWARE += ['debug_toolbar.middleware.DebugToolbarMiddleware']
    
AUTH_USER_MODEL = 'accounts.CustomUser'

ROOT_URLCONF = 'config.urls'

ASGI_APPLICATION = 'config.asgi.application'

CHANNEL_LAYERS = {
    'default': {
        'BACKEND': 'channels_redis.core.RedisChannelLayer',
        'CONFIG': {
            "hosts": [(env('REDIS_HOST'), 6379)],
        },
    },
}
TEMPLATES = [
    {
        'BACKEND': 'django.template.backends.django.DjangoTemplates',
        'DIRS': [
            BASE_DIR / 'templates'
        ],
        'APP_DIRS': True,
        'OPTIONS': {
            'context_processors': [
                'django.template.context_processors.debug',
                'django.template.context_processors.request',
                'django.contrib.auth.context_processors.auth',
                'django.contrib.messages.context_processors.messages',
                'config.context_processors.report_context',
                'config.context_processors.employee_status_context',
            ],
        },
    },
]

WSGI_APPLICATION = 'config.wsgi.application'

# Database
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': env('DB_NAME'),
        'USER': env('DB_USER'),
        'PASSWORD': env('DB_PASSWORD'),
        'HOST': env('DB_HOST'),
        'PORT': env('DB_PORT'),
        'OPTIONS': {
            'client_encoding': 'UTF8',
            'sslmode': 'disable'
        }
    }
}

# REST Framework settings
REST_FRAMEWORK = {
    'DEFAULT_PERMISSION_CLASSES': [
        'rest_framework.permissions.IsAuthenticated',
    ],
    'DEFAULT_SCHEMA_CLASS': 'drf_spectacular.openapi.AutoSchema',
    'DEFAULT_AUTHENTICATION_CLASSES': [
        'rest_framework_simplejwt.authentication.JWTAuthentication',
        'rest_framework.authentication.SessionAuthentication',
        'rest_framework.authentication.BasicAuthentication',
    ],
    'DEFAULT_PAGINATION_CLASS': 'rest_framework.pagination.PageNumberPagination',
    'PAGE_SIZE': 10
}

SPECTACULAR_SETTINGS = {
    'TITLE': 'EARNINGS Platfform API',
    'DESCRIPTION': 'Track employees earnings and payrolls',
    'VERSION': '1.0.0',
    'SERVE_INCLUDE_SCHEMA': False,
    'SWAGGER_UI_SETTINGS': {
        'persistAuthorization': True,
    },
}

SIMPLE_JWT = {
    'ACCESS_TOKEN_LIFETIME': timedelta(minutes=5),
    'REFRESH_TOKEN_LIFETIME': timedelta(days=1),
    'ROTATE_REFRESH_TOKENS': True,
    'BLACKLIST_AFTER_ROTATION': True,
    'UPDATE_LAST_LOGIN': True,
    'ALGORITHM': 'HS256',
    'SIGNING_KEY': SECRET_KEY,
    'VERIFYING_KEY': None,
    'AUTH_HEADER_TYPES': ('Bearer',),
}

CACHES = {
    "default": {
        "BACKEND": "django_redis.cache.RedisCache",
        "LOCATION": env('REDIS_URL'),
        "OPTIONS": {
            "CLIENT_CLASS": "django_redis.client.DefaultClient"
        }
    }
}
# Logging configuration
LOGGING = {
    'version': 1,
    'disable_existing_loggers': False,
    'handlers': {
        'file': {
            'level': 'ERROR',
            'class': 'logging.FileHandler',
            'filename': 'debug.log',
        },
    },
    'loggers': {
        'accounts': {
            'handlers': ['file'],
            'level': 'ERROR',
            'propagate': True,
        },
    },
}

# Password validation
AUTH_PASSWORD_VALIDATORS = [
    {
        'NAME': 'django.contrib.auth.password_validation.UserAttributeSimilarityValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.MinimumLengthValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.CommonPasswordValidator',
    },
    {
        'NAME': 'django.contrib.auth.password_validation.NumericPasswordValidator',
    },
]

# Internationalization
LANGUAGE_CODE = 'en-us'
TIME_ZONE = 'Europe/Sofia'
USE_I18N = True
USE_TZ = True

# Static files settings
STATIC_URL = 'static/'
STATIC_ROOT = BASE_DIR / 'staticfiles'

STATICFILES_DIRS = (
    BASE_DIR / 'static',
)
WHITENOISE_USE_FINDERS = True

# Create static directory if it doesn't exist
if not (BASE_DIR / 'static').exists():
    (BASE_DIR / 'static').mkdir()

# Media files
MEDIA_URL = '/media/'
MEDIA_ROOT = BASE_DIR / 'media'

# Default primary key field type
DEFAULT_AUTO_FIELD = 'django.db.models.BigAutoField'

# Celery Configuration
CELERY_BROKER_URL = env('CELERY_URL')
CELERY_RESULT_BACKEND = env('CELERY_URL')
CELERY_ACCEPT_CONTENT = ['json']
CELERY_TASK_SERIALIZER = 'json'
CELERY_RESULT_SERIALIZER = 'json'
CELERY_TIMEZONE = TIME_ZONE
CELERY_BROKER_CONNECTION_RETRY_ON_STARTUP = True

# Email Configuration
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = 'smtp.gmail.com'
EMAIL_PORT = 587
EMAIL_USE_TLS = True
EMAIL_HOST_USER = env('EMAIL_HOST_USER')
EMAIL_HOST_PASSWORD = env('EMAIL_HOST_PASSWORD')
DEFAULT_FROM_EMAIL = env('EMAIL_HOST_USER')
EMAIL_USE_LOCALTIME = True
EMAIL_TIMEOUT = 300
EMAIL_USE_SSL = False

# Authentication settings
LOGIN_REDIRECT_URL = 'dashboard'
LOGOUT_REDIRECT_URL = 'home'

# OTP Configuration settings
OTP_LENGTH = 6
PAGINATION_SIZE = 10
EMAIL_TEMPLATE_PATH = 'email_templates/'
MAX_LOGIN_ATTEMPTS = 5
CACHE_TIMEOUT = 300

# Site settings
PROTOCOL = env('PROTOCOL')
DOMAIN = env('DOMAIN')

JAZZMIN_SETTINGS = {
    "site_title": "EARNINGS Platform",
    "site_header": "EARNINGS",
    "site_brand": "EARNINGS",
    "site_logo": "img/logo.png",
    "login_logo": "img/logo.png",
    "login_logo_dark": "img/logo.png",
    "site_logo_classes": "img-circle",
    "site_icon": "img/logo.png",
    "welcome_sign": "Welcome to EARNINGS Platform",
    "copyright": "EARNINGS Platform",
    "search_model": "employees.Employee",
    "search_fields": ["number", "position", "workshop__name", "user__first_name", "user__last_name", "user__username", "user__email"],
    "user_avatar": "profile_image",
    "topmenu_links": [
        {"name": "Dashboard", "url": "admin:index"},
        {"app": "accounts"},
        {"app": "employees"},
        {"app": "payrolls"},
        {"app": "operations"},
        {"app": "overtime"},
        {"app": "reports"},
        {"app": "notifications"},
        {"name": "API", "url": "/api/schema/redoc/", "new_window": True},
    ],
    "usermenu_links": [
        {"name": "View Site", "url": "/", "new_window": True}
    ],
    "show_sidebar": True,
    "navigation_expanded": False,
    "hide_apps": [],
    "hide_models": [],
    "order_with_respect_to": [
        "accounts",
        "employees",
        "reports",
        "payrolls",
        "operations",
        "overtime",
    ],
    "icons": {
        # Main apps
        "accounts": "fas fa-users-cog",
        "accounts.CustomUser": "fas fa-user",
        "accounts.ArchivedUser": "fas fa-user-slash",
        "accounts.EmployeeUser": "fas fa-user-tie",
        "accounts.FaceDescriptor": "fas fa-id-card",
        "accounts.PendingUser": "fas fa-user-clock",
        
        # Workshops
        "employees": "fas fa-industry",
        "employees.Workshop": "fas fa-building",
        "employees.Leave": "fas fa-calendar-minus",
        
        # Operations
        "operations": "fas fa-cogs",
        "operations.Operation": "fas fa-tasks",
        "operations.Rate": "fas fa-dollar-sign",
        
        # Overtime
        "overtime": "fas fa-business-time",
        "overtime.OvertimeRequest": "fas fa-clock",
        
        # Payrolls
        "payrolls": "fas fa-money-check-alt",
        "payrolls.Payroll": "fas fa-money-bill-wave",
        
        # Reports
        "reports": "fas fa-chart-bar",
        "reports.Report": "fas fa-file-alt",
        
        # Auth and Security
        "auth": "fas fa-shield-alt",
        "auth.Group": "fas fa-users",
        "otp_totp": "fas fa-lock",
        "otp_totp.TOTPDevice": "fas fa-mobile-alt",
        
        # Notifications
        "notifications": "fas fa-bell"
    },
    "default_icon_parents": "fas fa-folder",
    "default_icon_children": "fas fa-file",
    "related_modal_active": True,
    "custom_css": None,
    "custom_js": None,
    "use_google_fonts_cdn": True,
    "show_ui_builder": True,
    "changeform_format": "horizontal_tabs",
    "changeform_format_overrides": {
        "accounts.CustomUser": "collapsible",
        "employees.Employee": "horizontal_tabs",
        "payrolls.Payroll": "vertical_tabs"
    }
}

# Additional Jazzmin UI customization
JAZZMIN_UI_TWEAKS = {
    "navbar_small_text": True,
    "footer_small_text": True,
    "body_small_text": True,
    "brand_small_text": False,
    "brand_colour": "navbar-primary",
    "accent": "accent-primary",
    "navbar": "navbar-dark",
    "no_navbar_border": False,
    "navbar_fixed": True,
    "layout_boxed": False,
    "footer_fixed": False,
    "sidebar_fixed": True,
    "sidebar": "sidebar-dark-primary",
    "sidebar_nav_small_text": True,
    "sidebar_disable_expand": False,
    "sidebar_nav_child_indent": True,
    "sidebar_nav_compact_style": True,
    "sidebar_nav_legacy_style": False,
    "sidebar_nav_flat_style": False,
    "theme": "default",
    "dark_mode_theme": "darkly",
    "button_classes": {
        "primary": "btn-primary",
        "secondary": "btn-secondary",
        "info": "btn-info",
        "warning": "btn-warning",
        "danger": "btn-danger",
        "success": "btn-success"
    }
}
