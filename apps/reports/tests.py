from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.employees.models import Employee, Workshop
from apps.reports.models import Report, ReportOperation
from apps.operations.models import Operation, Rate


class ReportTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.workshop = Workshop.objects.create(name="ASSEMBLY")

        self.staff_user = get_user_model().objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="StrongPass123!",
            is_staff=True,
        )

        self.employee_user = get_user_model().objects.create_user(
            username="employee", email="employee@test.com", password="StrongPass123!"
        )

        self.employee = Employee.objects.create(
            user=self.employee_user,
            number=1001,
            position="OPERATOR",
            workshop=self.workshop,
        )

        self.rate = Rate.objects.create(category="BASIC", price=100.00)

        self.operation = Operation.objects.create(
            code=1001, name="Test Operation", time=1.5, category=self.rate
        )

        self.workday = timezone.now()

        self.report = Report.objects.create(
            number=1, employee=self.employee, date=self.workday.date(), status="DRAFT"
        )

        self.report_operation = ReportOperation.objects.create(
            report=self.report, operation=self.operation, quantity=1
        )

    def test_report_list_staff_view(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(reverse("report-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/admin_report_list.html")

    def test_report_list_employee_view(self):
        self.client.login(username="employee", password="StrongPass123!")
        response = self.client.get(reverse("report-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "reports/employee_report_list.html")

    def test_report_calculations(self):
        self.report_operation.quantity = 2
        self.report_operation.save()
        self.report.refresh_from_db()
        self.assertEqual(float(self.report.total_sum), float(self.report_operation.sum))
        self.assertAlmostEqual(
            float(self.report.total_percent),
            float(self.report_operation.percent),
            places=2,
        )
