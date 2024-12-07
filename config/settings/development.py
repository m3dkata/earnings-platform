from .base import *

if os.name == 'nt':
    NPM_BIN_PATH = r"C:\\Program Files\\nodejs\\npm.cmd"
else:
    NPM_BIN_PATH = 'npm'

CSRF_COOKIE_SECURE = False
SESSION_COOKIE_SECURE = False
CSRF_COOKIE_DOMAIN = None

STORAGES = {
    'default': {
        'BACKEND': 'django.core.files.storage.FileSystemStorage',
    },
    "staticfiles": {
        "BACKEND": "whitenoise.storage.CompressedStaticFilesStorage",
    },
}
