from celery import shared_task
from django.db import transaction
from datetime import datetime
from .models import Payroll
from django.core.exceptions import ObjectDoesNotExist


@shared_task
def generate_payroll(employee_id, report_date):
    from apps.employees.models import Employee

    try:
        with transaction.atomic():
            employee = Employee.objects.get(id=employee_id)
            month_date = datetime.strptime(report_date, "%Y-%m-%d").replace(day=1)

            payroll, _ = Payroll.objects.get_or_create(
                employee=employee, month=month_date
            )

            return f"Payroll updated for {employee} - {month_date.strftime('%B %Y')}"
    except ObjectDoesNotExist:
        return f"Employee with ID {employee_id} not found"
    except Exception as e:
        return f"Error generating payroll: {str(e)}"
