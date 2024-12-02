from django.test import TestCase
from django.contrib.auth import get_user_model
from ..forms import CustomUserCreationForm

class FormsTest(TestCase):
    def test_user_creation_form(self):
        form_data = {
            'username': 'testuser',
            'email': 'test@example.com',
            'password1': 'StrongPass123!',
            'password2': 'StrongPass123!',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+12345678901'
        }
        form = CustomUserCreationForm(data=form_data)
        self.assertTrue(form.is_valid())
