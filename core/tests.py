from django.test import TestCase
from decimal import Decimal
from datetime import date, timedelta
from .models import Customer, InventoryItem, Event, Rental, RentalItem, SeamstressJob, Invoice
from .services import get_available_quantity, calculate_rental_total, calculate_event_total, create_invoice_for_rental, create_invoice_for_event

class ServiceTests(TestCase):
    def setUp(self):
        self.customer = Customer.objects.create(name="Test Client")
        self.dress = InventoryItem.objects.create(
            name="Red Dress",
            category="DRESS",
            total_quantity=5,
            rental_price=Decimal('100.00')
        )
        self.decor = InventoryItem.objects.create(
            name="Vase",
            category="DECOR",
            total_quantity=10,
            rental_price=Decimal('10.00')
        )

    def test_availability(self):
        # Rent 2 dresses for tomorrow
        today = date.today()
        tomorrow = today + timedelta(days=1)

        rental = Rental.objects.create(
            customer=self.customer,
            rental_date=today,
            return_date=tomorrow
        )
        RentalItem.objects.create(rental=rental, inventory_item=self.dress, quantity=2, price_at_booking=100)

        # Check availability for same dates
        avail = get_available_quantity(self.dress, today, tomorrow)
        self.assertEqual(avail, 3) # 5 total - 2 rented = 3

    def test_rental_calculation(self):
        rental = Rental.objects.create(
            customer=self.customer,
            rental_date=date.today(),
            return_date=date.today()
        )
        RentalItem.objects.create(rental=rental, inventory_item=self.dress, quantity=1, price_at_booking=100)
        SeamstressJob.objects.create(customer=self.customer, rental=rental, description="Hem", due_date=date.today(), price=Decimal('20.00'))

        total = calculate_rental_total(rental)
        self.assertEqual(total, Decimal('120.00'))

    def test_event_calculation_and_invoice(self):
        event = Event.objects.create(
            name="Wedding",
            customer=self.customer,
            date=date.today(),
            guest_count=50,
            event_type='WEDDING',
            budget=Decimal('5000.00')
        )
        # Add Decor Rental linked to Event
        rental = Rental.objects.create(
            customer=self.customer,
            event=event,
            rental_date=date.today(),
            return_date=date.today()
        )
        RentalItem.objects.create(rental=rental, inventory_item=self.decor, quantity=10, price_at_booking=10) # 10 * 10 = 100

        # Expected: 5000 (Budget) + 100 (Decor) = 5100
        total = calculate_event_total(event)
        self.assertEqual(total, Decimal('5100.00'))

        invoice = create_invoice_for_event(event)
        self.assertEqual(invoice.total_amount, Decimal('5100.00'))

from django.test import Client
from django.contrib.auth.models import User
from django.urls import reverse

class SeamstressViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.force_login(self.user)

        # Create 10 customers and 10 jobs
        for i in range(10):
            customer = Customer.objects.create(name=f"Customer {i}")
            SeamstressJob.objects.create(
                customer=customer,
                due_date=date.today() + timedelta(days=i),
                description=f"Job {i}"
            )

    def test_seamstress_list_queries(self):
        url = reverse('seamstress_list')

        # We expect 5 queries:
        # 1. Session
        # 2. User
        # 3. Permissions (User)
        # 4. Permissions (Group)
        # 5. SeamstressJob list with Customer join
        with self.assertNumQueries(5):
            response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
