from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from .models import Customer, InventoryItem, Event, Rental, RentalItem
from .forms import EventStep1Form
from .services import get_available_quantity, create_invoice_for_event
from decimal import Decimal

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date')
    return render(request, 'core/event_list.html', {'events': events})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    return render(request, 'core/event_detail.html', {'event': event})

@login_required
def event_wizard_step1(request):
    """Step 1: Event Details"""
    if request.method == 'POST':
        form = EventStep1Form(request.POST)
        if form.is_valid():
            request.session['event_data'] = {
                'name': form.cleaned_data['name'],
                'customer_id': form.cleaned_data['customer'].id,
                'date': form.cleaned_data['date'].isoformat(),
                'guest_count': form.cleaned_data['guest_count'],
                'location': form.cleaned_data['location'],
                'description': form.cleaned_data['description'],
                'base_cost': float(form.cleaned_data['base_cost']),
                'cost_per_guest': float(form.cleaned_data['cost_per_guest']),
            }
            return redirect('event_wizard_step2')
    else:
        form = EventStep1Form()

    return render(request, 'core/event_wizard_step1.html', {'form': form})

@login_required
def event_wizard_step2(request):
    """Step 2: Select Decor (Inventory)"""
    data = request.session.get('event_data')
    if not data:
        return redirect('event_wizard_step1')

    event_date = data['date']

    # Filter for DECOR category only
    items = InventoryItem.objects.filter(category='DECOR')
    available_items = []

    for item in items:
        # Check availability for the single day
        avail = get_available_quantity(item, event_date, event_date)
        if avail > 0:
            available_items.append({'item': item, 'avail': avail})

    if request.method == 'POST':
        if 'skip' in request.POST:
            request.session['event_items'] = {}
            return redirect('event_wizard_confirm')

        selected_items = {}
        for key, value in request.POST.items():
            if key.startswith('qty_') and value and int(value) > 0:
                item_id = int(key.split('_')[1])
                selected_items[item_id] = int(value)

        request.session['event_items'] = selected_items
        return redirect('event_wizard_confirm')

    return render(request, 'core/event_wizard_step2.html', {'items': available_items})

@login_required
def event_wizard_confirm(request):
    """Step 3: Confirmation"""
    data = request.session.get('event_data')
    items_data = request.session.get('event_items')

    if not data:
        return redirect('event_wizard_step1')

    customer = Customer.objects.get(id=data['customer_id'])

    # Calculate costs
    base_cost = Decimal(data['base_cost'])
    guest_cost = Decimal(data['cost_per_guest']) * data['guest_count']

    decor_items = []
    decor_total = Decimal('0.00')

    if items_data:
        for item_id, qty in items_data.items():
            item = InventoryItem.objects.get(id=item_id)
            line_total = item.rental_price * qty
            decor_total += line_total
            decor_items.append({'item': item, 'qty': qty, 'total': line_total})

    total_est = base_cost + guest_cost + decor_total

    if request.method == 'POST':
        # Create Event
        event = Event.objects.create(
            name=data['name'],
            customer=customer,
            date=data['date'],
            guest_count=data['guest_count'],
            location=data['location'],
            description=data['description'],
            base_cost=base_cost,
            cost_per_guest=Decimal(data['cost_per_guest'])
        )

        # Create Rental for Decor if items selected
        if items_data:
            rental = Rental.objects.create(
                customer=customer,
                event=event,
                rental_date=data['date'],
                return_date=data['date'],
                status='RESERVED'
            )
            for item_id, qty in items_data.items():
                inv_item = InventoryItem.objects.get(id=item_id)
                RentalItem.objects.create(
                    rental=rental,
                    inventory_item=inv_item,
                    quantity=qty,
                    price_at_booking=inv_item.rental_price
                )

        # Generate Invoice
        create_invoice_for_event(event)

        # Clear session
        del request.session['event_data']
        if 'event_items' in request.session:
            del request.session['event_items']

        messages.success(request, "Event created successfully!")
        return redirect('event_detail', pk=event.pk)

    return render(request, 'core/event_wizard_confirm.html', {
        'data': data,
        'customer': customer,
        'decor_items': decor_items,
        'base_cost': base_cost,
        'guest_cost': guest_cost,
        'total': total_est
    })
