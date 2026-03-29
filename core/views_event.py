from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Q
from django.core.paginator import Paginator
from .models import Customer, InventoryItem, Event, Rental, RentalItem, Service, EventService
from .forms import EventStep1Form
from .services import get_available_quantity, create_invoice_for_event
from decimal import Decimal

@login_required
def event_list(request):
    events = Event.objects.all().order_by('-date')

    query = request.GET.get('q')
    if query:
        events = events.filter(
            Q(name__icontains=query) |
            Q(customer__name__icontains=query) |
            Q(location__icontains=query)
        )

    event_type = request.GET.get('type')
    if event_type:
        events = events.filter(event_type=event_type)

    paginator = Paginator(events, 25)
    page = request.GET.get('page')
    events = paginator.get_page(page)

    return render(request, 'core/event_list.html', {
        'events': events,
        'query': query,
        'event_type': event_type,
        'event_types': Event.EVENT_TYPE_CHOICES,
    })

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
                'event_type': form.cleaned_data['event_type'],
                'location': form.cleaned_data['location'],
                'description': form.cleaned_data['description'],
                'budget': float(form.cleaned_data['budget']),
                'deposit_amount': float(form.cleaned_data.get('deposit_amount') or 0),
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
    items = InventoryItem.objects.all()
    available_items = []

    for item in items:
        avail = get_available_quantity(item, event_date, event_date)
        if avail > 0:
            available_items.append({'item': item, 'avail': avail})

    if request.method == 'POST':
        if 'skip' in request.POST:
            request.session['event_items'] = {}
            return redirect('event_wizard_step3')

        selected_items = {}
        for key, value in request.POST.items():
            if key.startswith('qty_') and value:
                try:
                    qty = int(value)
                except ValueError:
                    continue
                if qty > 0:
                    item_id = int(key.split('_')[1])
                    selected_items[item_id] = qty

        request.session['event_items'] = selected_items
        return redirect('event_wizard_step3')

    return render(request, 'core/event_wizard_step2.html', {'items': available_items})

@login_required
def event_wizard_step3(request):
    """Step 3: Select Services (DJ, etc.)"""
    if not request.session.get('event_data'):
        return redirect('event_wizard_step1')

    services = Service.objects.all()

    if request.method == 'POST':
        if 'skip' in request.POST:
            request.session['event_services'] = {}
            return redirect('event_wizard_confirm')

        selected_services = {}
        for key, value in request.POST.items():
            if key.startswith('srv_') and value == 'on':
                srv_id = int(key.split('_')[1])
                selected_services[srv_id] = True

        request.session['event_services'] = selected_services
        return redirect('event_wizard_confirm')

    return render(request, 'core/event_wizard_step3.html', {'services': services})

@login_required
def event_wizard_confirm(request):
    """Step 4: Confirmation"""
    data = request.session.get('event_data')
    items_data = request.session.get('event_items', {})
    services_data = request.session.get('event_services', {})

    if not data:
        return redirect('event_wizard_step1')

    customer = Customer.objects.get(id=data['customer_id'])
    budget = Decimal(str(data['budget']))

    decor_items = []
    decor_total = Decimal('0.00')

    if items_data:
        for item_id_str, qty in items_data.items():
            item = InventoryItem.objects.get(id=int(item_id_str))
            line_total = item.rental_price * qty
            decor_total += line_total
            decor_items.append({'item': item, 'qty': qty, 'total': line_total})

    service_items = []
    service_total = Decimal('0.00')

    if services_data:
        for srv_id_str in services_data.keys():
            srv = Service.objects.get(id=int(srv_id_str))
            service_total += srv.base_price
            service_items.append(srv)

    total_est = budget + decor_total + service_total

    if request.method == 'POST':
        event = Event.objects.create(
            name=data['name'],
            customer=customer,
            date=data['date'],
            guest_count=data['guest_count'],
            event_type=data.get('event_type', 'OTHER'),
            location=data['location'],
            description=data['description'],
            budget=budget,
            deposit_amount=Decimal(str(data.get('deposit_amount', 0)))
        )

        if items_data:
            rental = Rental.objects.create(
                customer=customer,
                event=event,
                rental_date=data['date'],
                return_date=data['date'],
                status='RESERVED'
            )
            for item_id_str, qty in items_data.items():
                inv_item = InventoryItem.objects.get(id=int(item_id_str))
                RentalItem.objects.create(
                    rental=rental,
                    inventory_item=inv_item,
                    quantity=qty,
                    price_at_booking=inv_item.rental_price
                )

        if services_data:
            for srv_id_str in services_data.keys():
                srv = Service.objects.get(id=int(srv_id_str))
                EventService.objects.create(
                    event=event,
                    service=srv,
                    price=srv.base_price
                )

        create_invoice_for_event(event)

        del request.session['event_data']
        if 'event_items' in request.session: del request.session['event_items']
        if 'event_services' in request.session: del request.session['event_services']

        messages.success(request, "Event created successfully!")
        return redirect('event_detail', pk=event.pk)

    return render(request, 'core/event_wizard_confirm.html', {
        'data': data,
        'customer': customer,
        'decor_items': decor_items,
        'service_items': service_items,
        'budget': budget,
        'total': total_est
    })
