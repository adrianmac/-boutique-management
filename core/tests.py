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
            base_cost=Decimal('1000.00'),
            cost_per_guest=Decimal('10.00')
        )
        # Add Decor Rental linked to Event
        rental = Rental.objects.create(
            customer=self.customer,
            event=event,
            rental_date=date.today(),
            return_date=date.today()
        )
        RentalItem.objects.create(rental=rental, inventory_item=self.decor, quantity=10, price_at_booking=10) # 10 * 10 = 100

        # Expected: 1000 (Base) + 500 (Guests) + 100 (Decor) = 1600
        total = calculate_event_total(event)
        self.assertEqual(total, Decimal('1600.00'))

        invoice = create_invoice_for_event(event)
        self.assertEqual(invoice.total_amount, Decimal('1600.00'))
