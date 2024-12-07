from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
import json

class AIViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.staff_user = get_user_model().objects.create_user(
            username='staffuser',
            email='staff@test.com',
            password='StrongPass123!',
            is_staff=True,
            first_name='Staff',
            last_name='User'
        )
        self.regular_user = get_user_model().objects.create_user(
            username='regularuser',
            email='regular@test.com',
            password='StrongPass123!',
            first_name='Regular',
            last_name='User'
        )
        self.query_url = reverse('ai_query')

    def test_ai_query_staff_access(self):
        self.client.login(username='staffuser', password='StrongPass123!')
        response = self.client.get(self.query_url, {'query': 'select * from accounts_customuser'})
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue(any(key in content for key in ['data', 'error']))

    def test_ai_query_unauthorized_access(self):
        self.client.login(username='regularuser', password='StrongPass123!')
        response = self.client.get(self.query_url, {'query': 'show total users'})
        self.assertEqual(response.status_code, 302)

    def test_ai_query_unauthenticated_access(self):
        response = self.client.get(self.query_url, {'query': 'show total users'})
        self.assertEqual(response.status_code, 302)

    def test_ai_query_empty_query(self):
        self.client.login(username='staffuser', password='StrongPass123!')
        response = self.client.get(self.query_url, {'query': ''})
        self.assertEqual(response.status_code, 200)

    def test_ai_query_invalid_query(self):
        self.client.login(username='staffuser', password='StrongPass123!')
        response = self.client.get(self.query_url, {'query': '!@#$%^'})
        content = json.loads(response.content)
        self.assertEqual(response.status_code, 200)
        self.assertTrue('error' in content or 'data' in content)
