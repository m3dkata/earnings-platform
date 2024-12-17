from rest_framework import serializers
from apps.reports.models import Report, ReportOperation
from apps.operations.models import Operation
from apps.employees.models import Employee


class ReportEmployeeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Employee
        fields = ["id", "number", "position", "user"]
        read_only_fields = ["id"]


class ReportOperationDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Operation
        fields = ["id", "code", "name", "time", "price"]
        read_only_fields = ["id"]


class ReportOperationSerializer(serializers.ModelSerializer):
    operation = ReportOperationDetailSerializer(read_only=True)
    operation_id = serializers.PrimaryKeyRelatedField(
        queryset=Operation.objects.all(), source="operation", write_only=True
    )

    class Meta:
        model = ReportOperation
        fields = ["id", "operation", "operation_id", "quantity", "percent", "sum"]
        read_only_fields = ["id", "percent", "sum"]


class ReportSerializer(serializers.ModelSerializer):
    employee = ReportEmployeeSerializer(read_only=True)
    employee_id = serializers.PrimaryKeyRelatedField(
        queryset=Employee.objects.all(),
        source="employee",
        write_only=True,
        required=False,
    )
    operations = ReportOperationSerializer(many=True, source="reportoperation_set")

    def create(self, validated_data):
        operations_data = validated_data.pop("reportoperation_set")
        report = Report(**validated_data)
        report.save()

        for operation_data in operations_data:
            ReportOperation.objects.create(report=report, **operation_data)

        return report

    class Meta:
        model = Report
        fields = [
            "id",
            "employee",
            "employee_id",
            "date",
            "status",
            "created_at",
            "updated_at",
            "total_percent",
            "total_sum",
            "operations",
        ]
        read_only_fields = [
            "id",
            "created_at",
            "updated_at",
            "total_percent",
            "total_sum",
        ]
