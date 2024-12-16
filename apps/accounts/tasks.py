from celery import shared_task
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.utils.html import strip_tags
from django.conf import settings


@shared_task
def send_email_task(email, template_name, context):
    html_content = render_to_string(f"email_templates/{template_name}", context)
    text_content = strip_tags(html_content)

    msg = EmailMultiAlternatives(
        subject=context["subject"],
        body=text_content,
        from_email=settings.DEFAULT_FROM_EMAIL,
        to=[email],
    )
    msg.attach_alternative(html_content, "text/html")
    return msg.send()


@shared_task
def send_otp_email_task(email, user_data, otp):
    context = {"user": user_data, "otp": otp, "subject": "Verify You!"}
    return send_email_task(email, "otp_verification.html", context)


@shared_task
def send_welcome_email_task(email, user_data):
    context = {
        "user": user_data,
        "login_url": settings.LOGIN_URL,
        "subject": "Welcome to EARNINGS Platform",
        "PROTOCOL": settings.PROTOCOL,
        "DOMAIN": settings.DOMAIN,
    }
    return send_email_task(email, "welcome_email.html", context)


@shared_task
def send_password_reset_email_task(email, user_data, reset_url):
    context = {
        "user": user_data,
        "reset_url": reset_url,
        "subject": "Password Reset Request",
        "protocol": settings.PROTOCOL,
        "domain": settings.DOMAIN,
    }
    return send_email_task(email, "password_reset.html", context)
