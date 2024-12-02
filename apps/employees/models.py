from django.db import models

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

    class Meta:
        ordering = ['number']
        unique_together = ('number', 'workshop')
        
    def __str__(self):
        return f"{self.number} - {self.user.get_full_name()}"

