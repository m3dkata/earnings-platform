from django.db import models
from math import ceil
from apps.accounts.models import CustomUser
from django.core.validators import MaxValueValidator, MinValueValidator

class Workshop(models.Model):
    WORKSHOP_CHOICES = [
        ('ASSEMBLY', 'Assembly Line'),
        ('WELDING', 'Welding Shop'),
        ('PAINTING', 'Paint Shop'),
        ('QUALITY', 'Quality Control'),
        ('MAINTENANCE', 'Maintenance'),
        ('LOGISTICS', 'Logistics'),
        ('TOOLROOM', 'Tool Room'),
    ]
    
    name = models.CharField(max_length=100, choices=WORKSHOP_CHOICES)
    
    def __str__(self):
        return self.name

class Employee(models.Model):
    POSITION_CHOICES = [
        ('OPERATOR', 'Machine Operator'),
        ('TECHNICIAN', 'Technician'),
        ('SUPERVISOR', 'Supervisor'),
        ('ENGINEER', 'Engineer'),
        ('MANAGER', 'Manager'),
        ('INSPECTOR', 'Quality Inspector'),
        ('MECHANIC', 'Mechanic'),
        ('ELECTRICIAN', 'Electrician'),
        ('LOGISTICS', 'Logistics Specialist'),
        ('TOOLMAKER', 'Tool Maker'),
    ]

    user = models.OneToOneField(CustomUser, on_delete=models.CASCADE, related_name='employee_profile')
    number = models.IntegerField(
        unique=True, 
        verbose_name='ID',
        validators=[MinValueValidator(1), MaxValueValidator(9999)],
        db_index=True
    )
    position = models.CharField(max_length=100, choices=POSITION_CHOICES, verbose_name='Position')
    workshop = models.ForeignKey(Workshop, on_delete=models.PROTECT, verbose_name='Workshop')
    is_online = models.BooleanField(default=False, db_index=True)
    
    class Meta:
        ordering = ['number']
        unique_together = ('number', 'workshop')
        
    def __str__(self):
        return f"{self.number} - {self.user.get_full_name()}"

class Leave(models.Model):
    LEAVE_TYPES = [
        ('VACATION', 'Vacation Leave'),
        ('SICK', 'Sick Leave'),
    ]
    
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected'),
    ]
    
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, related_name='leaves')
    leave_type = models.CharField(max_length=20, choices=LEAVE_TYPES)
    start_datetime = models.DateTimeField()
    end_datetime = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')
    reason = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.employee.user.get_full_name()} - {self.leave_type} / {self.status}"
    
    def duration_in_hours(self):
        duration = self.end_datetime - self.start_datetime
        total_hours = duration.total_seconds() / 3600
        hours = int(total_hours)
        minutes = int((total_hours - hours) * 60)
        return f"{hours:02d}:{minutes:02d}"
        
    def duration_in_days(self):
        duration = self.end_datetime - self.start_datetime
        hours = duration.total_seconds() / 3600
        
        if hours < 8:
            return 0
        return max(1, int(hours / 24))
        
    def save(self, *args, **kwargs):
        is_new = not self.pk
        super().save(*args, **kwargs)
        
        if is_new:
            from apps.notifications.services import NotificationService
            NotificationService.notify_leave_request(self)
            
    class Meta:        
        permissions = [
                ("can_approve_leave", "Can approve leave requests"),
                ("can_reject_leave", "Can reject leave requests"),
            ]        