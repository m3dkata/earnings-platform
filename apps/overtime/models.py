from django.db import models
from apps.employees.models import Employee
from django.urls import reverse
from django.db.models.signals import post_save
from django.dispatch import receiver
from apps.notifications.services import NotificationService

class OvertimeRequest(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    hours = models.DecimalField(max_digits=4, decimal_places=2)
    rate = models.DecimalField(max_digits=5, decimal_places=2, default=10.00)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    description = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    approved_by = models.ForeignKey(
        'accounts.CustomUser',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='approved_overtime_requests'
    )

    def get_absolute_url(self):
        return reverse('overtime:detail', kwargs={'pk': self.pk})

    def calculate_amount(self):
        return self.hours * self.rate

    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)

        if is_new:
            NotificationService.notify_overtime_request(self)
        elif self.status in ['approved', 'rejected']:
            NotificationService.notify_overtime_status_change(self)

    class Meta:
        permissions = [
            ('can_approve_overtime', 'Can approve overtime requests'),
            ('can_reject_overtime', 'Can reject overtime requests'),
        ]
