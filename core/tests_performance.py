from django.test import TestCase, Client
from django.urls import reverse
from django.contrib.auth.models import User
from core.models import Customer, SeamstressJob, Rental, Event
from datetime import date, timedelta

class DashboardPerformanceTest(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='password')
        self.client = Client()
        self.client.login(username='testuser', password='password')

        today = date.today()

        # Create data to trigger all sections of the dashboard
        for i in range(10):
            c = Customer.objects.create(name=f"Customer {i}")

            # Pending Jobs (The reported issue)
            SeamstressJob.objects.create(customer=c, due_date=today, status='PENDING', description="Fix")

            # Active Rentals
            Rental.objects.create(customer=c, rental_date=today, return_date=today + timedelta(days=3), status='PICKED_UP')

            # Action Items: Rentals Start Today
            Rental.objects.create(customer=c, rental_date=today, return_date=today + timedelta(days=3), status='RESERVED')

            # Action Items: Rentals Return Today
            Rental.objects.create(customer=c, rental_date=today - timedelta(days=3), return_date=today, status='PICKED_UP')

            # Action Items: Jobs Due Today
            SeamstressJob.objects.create(customer=c, due_date=today, status='IN_PROGRESS', description="Due")

            # Events
            Event.objects.create(name=f"Event {i}", date=today, customer=c)

    def test_dashboard_query_count(self):
        # Access the dashboard
        # We expect a LOT of queries currently.
        # 1 for user
        # 1 for session
        # + Queries for each section.
        # Each section iterates ~5-10 items and hits the DB for 'customer' on each.

        with self.assertNumQueries(12):
            response = self.client.get(reverse('dashboard'))

        self.assertEqual(response.status_code, 200)
