from rest_framework import serializers
from apps.payrolls.models import Payroll
from apps.employees.models import Employee


class EmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "number", "position", "user"]
        read_only_fields = ["id"]


class PayrollSerializer(serializers.ModelSerializer):
    employee = EmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(), source="employee", write_only=True
    )

    class Meta:
        model = Payroll
        fields = [
            "id",
            "employee",
            "employee_id",
            "month",
            "work_days",
            "percent",
            "earnings",
            "attendance_bonus",
            "vacation_days",
            "vacation_amount",
            "sick_days",
            "sick_amount",
            "total",
            "bank_transfer",
            "cash_payment",
        ]
        read_only_fields = [
            "id",
            "work_days",
            "percent",
            "earnings",
            "attendance_bonus",
            "vacation_amount",
            "sick_amount",
            "total",
            "cash_payment",
        ]
