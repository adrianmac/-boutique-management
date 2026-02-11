from django.test import TestCase, Client
from django.urls import reverse
from .models import Customer, Service, InventoryItem
from decimal import Decimal
from django.contrib.auth.models import User

class EventWizardViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.customer = Customer.objects.create(name="Test Client")
        self.service1 = Service.objects.create(name="Service 1", base_price=Decimal("100.00"))
        self.service2 = Service.objects.create(name="Service 2", base_price=Decimal("200.00"))

        # Log in
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client.login(username='testuser', password='password')

    def test_event_wizard_confirm_context(self):
        # Set up session data
        session = self.client.session
        session['event_data'] = {
            'name': 'Test Event',
            'customer_id': self.customer.id,
            'date': '2023-12-25',
            'guest_count': 100,
            'event_type': 'WEDDING',
            'location': 'Test Location',
            'description': 'Test Description',
            'budget': '1000.00',
            'deposit_amount': '0'
        }
        session['event_items'] = {} # No items for this test
        session['event_services'] = {
            self.service1.id: True,
            self.service2.id: True
        }
        session.save()

        # Expected queries:
        # 1. Session lookup
        # 2. User lookup (auth)
        # 3. Customer lookup
        # 4. Service lookup (bulk)
        # 5. Session save?

        # Let's see what happens. I'll just assert success first.
        # But wait, assertNumQueries context manager.

        with self.assertNumQueries(6):
             response = self.client.get(reverse('event_wizard_confirm'))

        self.assertEqual(response.status_code, 200)

        # Check context
        self.assertIn('service_items', response.context)
        service_items = response.context['service_items']
        self.assertEqual(len(service_items), 2)

        # Check if services are correct
        ids = [s.id for s in service_items]
        self.assertIn(self.service1.id, ids)
        self.assertIn(self.service2.id, ids)

        # Check total
        self.assertIn('total', response.context)
        # Budget 1000 + Service1 100 + Service2 200 = 1300
        self.assertEqual(response.context['total'], Decimal('1300.00'))
