from django.test import TestCase
from apps.operations.forms import OperationForm, RateForm
from apps.operations.models import Rate

class OperationFormTest(TestCase):
    def setUp(self):
        self.rate = Rate.objects.create(
            category='BASIC',
            price=100.00
        )

    def test_valid_operation_form(self):
        form_data = {
            'code': 1001,
            'name': 'Test Operation',
            'time': 1.5,
            'category': self.rate.id
        }
        form = OperationForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_invalid_operation_form(self):
        form_data = {
            'code': -1,
            'name': 'Test Operation',
            'time': 0,
            'category': 999
        }
        form = OperationForm(data=form_data)
        self.assertFalse(form.is_valid())
        self.assertIn('code', form.errors)
        self.assertIn('time', form.errors)
        self.assertIn('category', form.errors)

class RateFormTest(TestCase):
    def setUp(self):
        self.rate = Rate.objects.create(
            category='BASIC',
            price=100.00
        )

    def test_valid_rate_form(self):
        form_data = {
            'category': 'ADVANCED',
            'price': 150.00
        }
        form = RateForm(data=form_data)
        self.assertTrue(form.is_valid())
        
    def test_duplicate_category(self):
        form_data = {
            'category': 'BASIC',
            'price': 150.00
        }
        form = RateForm(data=form_data)
        self.assertFalse(form.is_valid())
