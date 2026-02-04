from decimal import Decimal
from django.db.models import Sum, Q
from .models import Rental, RentalItem, Invoice, InventoryLog

def get_available_quantity(inventory_item, start_date, end_date):
    """
    Calculates the available quantity of an item for a given date range.
    """
    # Find rentals that overlap with the requested range
    # Overlap logic: Rental Start <= Requested End AND Rental End >= Requested Start
    overlapping_rentals = Rental.objects.filter(
        Q(status='RESERVED') | Q(status='PICKED_UP'),
        rental_date__lte=end_date,
        return_date__gte=start_date
    )

    # Sum the quantity of the specific item in those rentals
    rented_quantity = RentalItem.objects.filter(
        rental__in=overlapping_rentals,
        inventory_item=inventory_item
    ).aggregate(total=Sum('quantity'))['total'] or 0

    return inventory_item.total_quantity - rented_quantity

def calculate_rental_total(rental):
    """
    Calculates the total cost of a rental, including items and seamstress jobs.
    Returns Decimal.
    """
    item_total = Decimal('0.00')
    for item in rental.items.all():
        item_total += item.price_at_booking * item.quantity

    seamstress_total = Decimal('0.00')
    # Use related_name 'alterations' from SeamstressJob model
    for job in rental.alterations.all():
        seamstress_total += job.price

    return item_total + seamstress_total

def calculate_event_total(event):
    """
    Calculates the total cost of an event.
    Base Cost + (Cost Per Guest * Guests) + Linked Decor Rentals
    """
    base_cost = event.base_cost
    guest_cost = event.cost_per_guest * event.guest_count

    decor_total = Decimal('0.00')
    for rental in event.rentals.all():
        decor_total += calculate_rental_total(rental)

    return base_cost + guest_cost + decor_total

def create_invoice_for_rental(rental):
    """
    Creates or updates an invoice for a Rental.
    If the rental belongs to an Event, delegate to Event invoice.
    """
    if rental.event:
        return create_invoice_for_event(rental.event)

    total = calculate_rental_total(rental)

    invoice, created = Invoice.objects.get_or_create(
        rental=rental,
        defaults={
            'customer': rental.customer,
            'total_amount': total,
            'status': 'UNPAID'
        }
    )

    if not created:
        invoice.total_amount = total
        invoice.save()
        invoice.update_status() # Re-check status based on payments

    return invoice

def create_invoice_for_event(event):
    """
    Creates or updates an invoice for an Event.
    """
    total = calculate_event_total(event)

    invoice, created = Invoice.objects.get_or_create(
        event=event,
        defaults={
            'customer': event.customer,
            'total_amount': total,
            'status': 'UNPAID'
        }
    )

    if not created:
        invoice.total_amount = total
        invoice.save()
        invoice.update_status()

    return invoice
