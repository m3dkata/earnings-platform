from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from django.utils import timezone
from apps.employees.models import Employee, Workshop
from apps.payrolls.models import Payroll
from apps.payrolls.tasks import generate_payroll


class PayrollTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.workshop = Workshop.objects.create(name="ASSEMBLY")

        self.staff_user = get_user_model().objects.create_user(
            username="staffuser",
            email="staff@test.com",
            password="StrongPass123!",
            is_staff=True,
            first_name="Staff",
            last_name="User",
        )

        self.employee_user = get_user_model().objects.create_user(
            username="employee",
            email="employee@test.com",
            password="StrongPass123!",
            first_name="Test",
            last_name="Employee",
        )

        self.employee = Employee.objects.create(
            user=self.employee_user,
            number=1001,
            position="OPERATOR",
            workshop=self.workshop,
        )

        self.payroll = Payroll.objects.create(
            employee=self.employee, month=timezone.now().date(), bank_transfer=1000
        )

    def test_payroll_list_staff_view(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(reverse("payroll-list"))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "payrolls/payroll_list.html")
        self.assertTrue("payrolls" in response.context)

    def test_payroll_list_employee_view(self):
        self.client.login(username="employee", password="StrongPass123!")
        response = self.client.get(reverse("payroll-list"))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["payrolls"]), 1)

    def test_payroll_pdf_view(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(
            reverse("payroll-pdf", kwargs={"pk": self.payroll.pk})
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response["Content-Type"], "application/pdf")

    def test_payroll_create_view(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        data = {
            "employee": self.employee.id,
            "month": "2024-01",
            "bank_transfer": 1500,
            "vacation_days": 0,
            "sick_days": 0,
        }
        response = self.client.post(reverse("payroll-create"), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(
            Payroll.objects.filter(employee=self.employee, bank_transfer=1500).exists()
        )

    def test_generate_payroll_task(self):
        date = timezone.now().strftime("%Y-%m-%d")
        result = generate_payroll(self.employee.id, date)
        self.assertIn("Payroll updated for", result)

    def test_unauthorized_access(self):
        self.client.login(username="employee", password="StrongPass123!")
        response = self.client.get(reverse("payroll-create"))
        self.assertEqual(response.status_code, 403)

    def test_payroll_filter(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        current_date = timezone.now()
        response = self.client.get(
            reverse("payroll-list"),
            {"month_year": f"{current_date.year}-{current_date.month:02d}"},
        )
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context["payrolls"]), 1)
