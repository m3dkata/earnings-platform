from django.db import models
from django.utils import timezone
from apps.operations.models import Operation
from apps.employees.models import Employee

class Report(models.Model):
    STATUS_CHOICES = [
        ('DRAFT', 'Draft'),
        ('SUBMITTED', 'Submitted'),
        ('APPROVED', 'Approved'),
        ('REJECTED', 'Rejected')
    ]
    employee = models.ForeignKey(Employee, on_delete=models.CASCADE, verbose_name='Employee')
    date = models.DateField(default=timezone.now, verbose_name='Date')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='DRAFT')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    total_percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total_sum = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def update_totals(self):
        operations = ReportOperation.objects.filter(report=self)
        if operations:
            self.total_percent = sum(op.percent for op in operations) / operations.count()
            self.total_sum = sum(op.sum for op in operations)
            self.save()

    def __str__(self):
        return f"Report #{self.pk} - {self.employee}"

    @property
    def total_working_time(self):
        return sum(op.total_time for op in self.reportoperation_set.all())
    
    class Meta:
        ordering = ['-date', '-id']
        verbose_name = 'Report'
        verbose_name_plural = 'Reports'
        constraints = [
            models.UniqueConstraint(
                fields=['employee', 'date'], 
                name='unique_employee_date'
            )
        ]

class ReportOperation(models.Model):
    report = models.ForeignKey(Report, on_delete=models.CASCADE)
    operation = models.ForeignKey(Operation, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)
    percent = models.DecimalField(max_digits=10, decimal_places=2)
    sum = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        self.percent = ((float(self.operation.time) * int(self.quantity)) / 470) * 100
        self.sum = float(self.operation.price) * float(self.quantity)
        super().save(*args, **kwargs)
        self.report.update_totals()

    def __str__(self):
        return f"{self.operation.code} - {self.operation.name} (x{self.quantity})"
    
    @property
    def total_time(self):
        return float(self.operation.time) * int(self.quantity)

    class Meta:
        verbose_name = 'Report Operation'
        verbose_name_plural = 'Report Operations'
