from django.db import models
from django.conf import settings

from apps.reports.models import Report

class Notification(models.Model):
    NOTIFICATION_TYPES = (
        ('registration', 'New User Registration'),
        ('report_submission', 'Report Submission'),
        ('report_status', 'Report Status Change'),
    )

    recipient = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    notification_type = models.CharField(max_length=20, choices=NOTIFICATION_TYPES)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)
    report = models.ForeignKey(Report, on_delete=models.CASCADE, null=True, blank=True)

    class Meta:
        ordering = ['-created_at']