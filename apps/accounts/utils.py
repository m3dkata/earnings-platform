import logging
import random
import string
from django.conf import settings
from django.core.cache import cache
from django.contrib import messages
from django.shortcuts import redirect
from .tasks import send_otp_email_task, send_welcome_email_task, send_password_reset_email_task

logger = logging.getLogger(__name__)

def generate_otp():
    return ''.join(random.choices(string.digits, k=settings.OTP_LENGTH))

def send_otp_email(user, otp):
    user_data = {'username': user.username, 'email': user.email}
    send_otp_email_task.delay(user.email, user_data, otp)

def send_welcome_email(user):
    user_data = {'username': user.username, 'email': user.email}
    send_welcome_email_task.delay(user.email, user_data)

def send_password_reset_email(user, reset_url):
    user_data = {'username': user.username, 'email': user.email}
    send_password_reset_email_task.delay(user.email, user_data, reset_url)

def rate_limit(key_prefix, limit=5, timeout=60):
    def decorator(view_func):
        def wrapped_view(request_or_self, *args, **kwargs):
            request = request_or_self.request if hasattr(request_or_self, 'request') else request_or_self
            cache_key = f"{key_prefix}:{request.META.get('REMOTE_ADDR')}"
            requests = cache.get(cache_key, 0)
            
            if requests >= limit:
                messages.error(request, "Too many attempts. Please try again later.")
                return redirect('login')
                
            cache.set(cache_key, requests + 1, timeout)
            return view_func(request_or_self, *args, **kwargs)
        return wrapped_view
    return decorator