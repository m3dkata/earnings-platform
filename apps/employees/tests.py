from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.employees.models import Employee, Workshop


class EmployeeStatsViewTest(TestCase):
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

        self.stats_url = reverse("employee_stats")

    def test_stats_view_staff_access(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_stats.html")
        self.assertTrue("employees" in response.context)
        self.assertTrue("selected_employee" in response.context)
        self.assertTrue("operations" in response.context)
        self.assertTrue("reports" in response.context)

    def test_stats_view_employee_access(self):
        self.client.login(username="employee", password="StrongPass123!")
        response = self.client.get(self.stats_url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, "employees/employee_stats.html")
        self.assertIsNone(response.context["employees"])
        self.assertEqual(response.context["selected_employee"], self.employee)

    def test_stats_view_period_filter(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(f"{self.stats_url}?period=month")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["period"], "month")

    def test_stats_view_employee_filter(self):
        self.client.login(username="staffuser", password="StrongPass123!")
        response = self.client.get(f"{self.stats_url}?employee={self.employee.id}")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context["selected_employee"], self.employee)
