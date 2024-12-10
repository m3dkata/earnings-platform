from django.urls import re_path
from . import consumers

websocket_urlpatterns = [
    re_path(r'ws/user_activity/$', consumers.UserActivityConsumer.as_asgi()),
]