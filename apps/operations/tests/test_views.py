from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth import get_user_model
from apps.operations.models import Operation, Rate

class OperationViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='StrongPass123!'
        )
        self.client.login(username='admin', password='StrongPass123!')
        
        self.rate = Rate.objects.create(
            category='BASIC',
            price=100.00
        )
        
        self.operation = Operation.objects.create(
            code=1001,
            name='Test Operation',
            time=1.5,
            category=self.rate
        )
        
    def test_operation_list_view(self):
        response = self.client.get(reverse('operations_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'operations/operation_list.html')
        self.assertTrue('operations' in response.context)
        
    def test_operation_search(self):
        response = self.client.get(reverse('operations_list'), {'search': 'Test'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.context['operations']), 1)
        
    def test_operation_create(self):
        data = {
            'code': 1002,
            'name': 'New Operation',
            'time': 2.0,
            'category': self.rate.id
        }
        response = self.client.post(reverse('operation_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Operation.objects.filter(code=1002).exists())
        
    def test_operation_update(self):
        data = {
            'code': self.operation.code,
            'name': 'Updated Operation',
            'time': 2.5,
            'category': self.rate.id
        }
        response = self.client.post(
            reverse('operation_edit', kwargs={'pk': self.operation.pk}),
            data
        )
        self.assertEqual(response.status_code, 302)
        self.operation.refresh_from_db()
        self.assertEqual(self.operation.name, 'Updated Operation')

class RateViewsTest(TestCase):
    def setUp(self):
        self.client = Client()
        self.user = get_user_model().objects.create_superuser(
            username='admin',
            email='admin@test.com',
            password='StrongPass123!'
        )
        self.client.login(username='admin', password='StrongPass123!')
        self.rate = Rate.objects.create(
            category='BASIC',
            price=100.00
        )
        
    def test_rate_list_view(self):
        response = self.client.get(reverse('rates_list'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'operations/rate_list.html')
        
    def test_rate_create(self):
        data = {
            'category': 'ADVANCED',
            'price': 150.00
        }
        response = self.client.post(reverse('rate_create'), data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(Rate.objects.filter(category='ADVANCED').exists())
