from django.core.management.base import BaseCommand
from core.models import Rental
from core.utils_email import send_notification_email
from datetime import date, timedelta

class Command(BaseCommand):
    help = 'Send reminders for rentals returning tomorrow'

    def handle(self, *args, **kwargs):
        tomorrow = date.today() + timedelta(days=1)
        rentals = Rental.objects.filter(return_date=tomorrow, status='PICKED_UP')

        count = 0
        for rental in rentals:
            send_notification_email(
                rental.customer,
                "Reminder: Rental Due Tomorrow",
                "email_reminder.html",
                {"rental": rental}
            )
            count += 1

        self.stdout.write(self.style.SUCCESS(f'Sent {count} reminders.'))
