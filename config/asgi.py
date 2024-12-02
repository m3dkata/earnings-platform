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

from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from channels.auth import AuthMiddlewareStack
from apps.notifications.routing import websocket_urlpatterns
from config.settings import development
from config.settings import production

os.environ.setdefault('DJANGO_SETTINGS_MODULE', f'config.settings.{env("BUILD_ENVIRONMENT")}')

application = ProtocolTypeRouter({
    "http": get_asgi_application(),
    "websocket": AuthMiddlewareStack(
        URLRouter(
            websocket_urlpatterns
        )
    ),
})
