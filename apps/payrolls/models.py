from decimal import Decimal
from django.db import models
from django.db.models import Avg, Sum, Count
from apps.employees.models import Employee
from apps.reports.models import Report


class Payroll(models.Model):
    LEAVE_RATES = {"VACATION": 30, "SICK": 20}

    employee = models.ForeignKey(Employee, on_delete=models.CASCADE)
    month = models.DateField()
    work_days = models.IntegerField(default=0)
    percent = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    earnings = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    attendance_bonus = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    vacation_days = models.IntegerField(default=0)
    vacation_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    sick_days = models.IntegerField(default=0)
    sick_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    bank_transfer = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    cash_payment = models.DecimalField(max_digits=10, decimal_places=2, default=0)

    def calculate_from_reports(self):
        reports = Report.objects.filter(
            employee=self.employee,
            date__month=self.month.month,
            date__year=self.month.year,
            status="APPROVED",
        )

        aggregates = reports.aggregate(
            total_sum=Sum("total_sum"),
            avg_percent=Avg("total_percent"),
            days_count=Count("id"),
        )

        self.earnings = aggregates["total_sum"] or Decimal("0")
        self.percent = aggregates["avg_percent"] or Decimal("0")
        self.work_days = aggregates["days_count"] or 0
        self.attendance_bonus = self.earnings * Decimal("0.1")

    def calculate_leave_amounts(self):
        self.vacation_amount = self.vacation_days * self.LEAVE_RATES["VACATION"]
        self.sick_amount = self.sick_days * self.LEAVE_RATES["SICK"]

    def calculate_total(self):
        self.total = (
            self.earnings
            + self.attendance_bonus
            + self.vacation_amount
            + self.sick_amount
        )
        self.cash_payment = self.total - self.bank_transfer

    def save(self, *args, **kwargs):
        self.calculate_from_reports()
        self.calculate_leave_amounts()
        self.calculate_total()
        super().save(*args, **kwargs)

    def __str__(self):
        return f"Payroll for {self.employee} in {self.month.strftime('%B %Y')}"

    class Meta:
        unique_together = ["employee", "month"]
        ordering = ["-month", "employee"]
