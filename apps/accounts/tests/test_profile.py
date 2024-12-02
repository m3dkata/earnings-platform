from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model

class ProfileViewTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_active=True
        )
        self.client.login(username='testuser', password='testpass123')

    def test_profile_update(self):
        url = reverse('update_profile')
        data = {
            'first_name': 'Updated',
            'last_name': 'Name',
            'phone_number': '+123456789000'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Updated')
