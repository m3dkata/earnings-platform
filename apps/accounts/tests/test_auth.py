from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model


class AuthenticationTest(TestCase):
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

    def test_signup_view(self):
        url = reverse('signup')
        data = {
            'username': 'newuser',
            'email': 'new@example.com', 
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'New',
            'last_name': 'User',
            'phone_number': '+12345678901'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        
    def test_login_with_2fa(self):
        self.user.is_2fa_enabled = True
        self.user.save()
        
        response = self.client.post(reverse('login'), {
            'username': 'testuser',
            'password': 'testpass123'
        })
        self.assertRedirects(response, reverse('verify_login_2fa'))
