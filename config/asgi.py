"""
ASGI config for config project.

It exposes the ASGI callable as a module-level variable named ``application``.

For more information on this file, see
https://docs.djangoproject.com/en/5.1/howto/deployment/asgi/
"""

import os
import sys
import environ
from .settings.base import BASE_DIR

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
env = environ.Env()
environ.Env.read_env(os.path.join(BASE_DIR, '.env'))

from config.settings import development
from config.settings import production
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.security.websocket import AllowedHostsOriginValidator
from channels.auth import AuthMiddlewareStack
from apps.notifications.routing import websocket_urlpatterns as notification_websocket_urlpatterns
from apps.employees.routing import websocket_urlpatterns as employee_websocket_urlpatterns

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env("BUILD_ENVIRONMENT")}')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AllowedHostsOriginValidator(
        AuthMiddlewareStack(
            URLRouter(
                notification_websocket_urlpatterns +
                employee_websocket_urlpatterns
            )
        )
    ),
})