from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.conf import settings
import threading

def send_notification_email(customer, subject, template_name, context):
    """
    Sends an email to the customer.
    Uses threading to avoid blocking the request.
    """
    if not customer.email:
        print(f"Skipping email for {customer.name}: No email address.")
        return

    html_message = render_to_string(f'core/emails/{template_name}', context)
    plain_message = html_message # Simplified for MVP

    def _send():
        try:
            send_mail(
                subject=subject,
                message=plain_message,
                from_email=getattr(settings, 'DEFAULT_FROM_EMAIL', 'noreply@boutique.com'),
                recipient_list=[customer.email],
                html_message=html_message,
                fail_silently=False,
            )
            print(f"Email sent to {customer.email}: {subject}")
        except Exception as e:
            print(f"Failed to send email to {customer.email}: {e}")

    # Fire and forget
    threading.Thread(target=_send).start()
