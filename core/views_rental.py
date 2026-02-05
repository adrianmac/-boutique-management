from .utils_email import send_notification_email
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import HttpResponse
from .models import Customer, InventoryItem, Rental, RentalItem, SeamstressJob
from .forms import RentalStep1Form, SeamstressJobForm
from .services import get_available_quantity, create_invoice_for_rental
from datetime import datetime
from decimal import Decimal

@login_required
def rental_list(request):
    rentals = Rental.objects.all().order_by('-rental_date')
    return render(request, 'core/rental_list.html', {'rentals': rentals})

@login_required
def rental_detail(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    return render(request, 'core/rental_detail.html', {'rental': rental})

@login_required
def rental_wizard_step1(request):
    """Step 1: Customer and Dates"""
    if request.method == 'POST':
        form = RentalStep1Form(request.POST)
        if form.is_valid():
            request.session['rental_data'] = {
                'customer_id': form.cleaned_data['customer'].id,
                'rental_date': form.cleaned_data['rental_date'].isoformat(),
                'return_date': form.cleaned_data['return_date'].isoformat(),
                'deposit': float(form.cleaned_data.get('deposit') or 0),
            }
            return redirect('rental_wizard_step2')
    else:
        form = RentalStep1Form()

    return render(request, 'core/rental_wizard_step1.html', {'form': form})

@login_required
def rental_wizard_step2(request):
    """Step 2: Select Items"""
    data = request.session.get('rental_data')
    if not data:
        return redirect('rental_wizard_step1')

    start_date = data['rental_date']
    end_date = data['return_date']

    items = InventoryItem.objects.all()
    available_items = []

    for item in items:
        avail = get_available_quantity(item, start_date, end_date)
        if avail > 0:
            available_items.append({'item': item, 'avail': avail})

    if request.method == 'POST':
        # Process selected items
        selected_items = {}
        for key, value in request.POST.items():
            if key.startswith('qty_') and value and int(value) > 0:
                item_id = int(key.split('_')[1])
                selected_items[item_id] = int(value)

        if not selected_items:
            messages.error(request, "Please select at least one item.")
            return render(request, 'core/rental_wizard_step2.html', {'items': available_items})

        request.session['rental_items'] = selected_items
        return redirect('rental_wizard_step3')

    return render(request, 'core/rental_wizard_step2.html', {'items': available_items})

@login_required
def rental_wizard_step3(request):
    """Step 3: Add Seamstress (Optional)"""
    if not request.session.get('rental_data'):
        return redirect('rental_wizard_step1')

    if request.method == 'POST':
        if 'skip' in request.POST:
            request.session['seamstress_data'] = None
            return redirect('rental_wizard_confirm')

        form = SeamstressJobForm(request.POST)
        if form.is_valid():
            request.session['seamstress_data'] = {
                'description': form.cleaned_data['description'],
                'due_date': form.cleaned_data['due_date'].isoformat(),
                'price': float(form.cleaned_data['price']),
            }
            return redirect('rental_wizard_confirm')
    else:
        form = SeamstressJobForm()

    return render(request, 'core/rental_wizard_step3.html', {'form': form})

@login_required
def rental_wizard_confirm(request):
    """Step 4: Confirmation"""
    data = request.session.get('rental_data')
    items_data = request.session.get('rental_items')
    seamstress_data = request.session.get('seamstress_data')

    if not data or not items_data:
        return redirect('rental_wizard_step1')

    customer = Customer.objects.get(id=data['customer_id'])

    # Prepare display data
    display_items = []
    total_est = Decimal('0.00')

    for item_id, qty in items_data.items():
        item = InventoryItem.objects.get(id=item_id)
        line_total = item.rental_price * qty
        total_est += line_total
        display_items.append({'item': item, 'qty': qty, 'total': line_total})

    seamstress_price = Decimal('0.00')
    if seamstress_data:
        seamstress_price = Decimal(seamstress_data['price'])
        total_est += seamstress_price

    deposit = Decimal(data.get('deposit', 0))

    if request.method == 'POST':
        # SAVE EVERYTHING
        rental = Rental.objects.create(
            customer=customer,
            rental_date=data['rental_date'],
            return_date=data['return_date'],
            status='RESERVED',
            deposit_amount=deposit
        )

        for item_id, qty in items_data.items():
            inv_item = InventoryItem.objects.get(id=item_id)
            RentalItem.objects.create(
                rental=rental,
                inventory_item=inv_item,
                quantity=qty,
                price_at_booking=inv_item.rental_price
            )

        if seamstress_data:
            SeamstressJob.objects.create(
                customer=customer,
                rental=rental,
                description=seamstress_data['description'],
                due_date=seamstress_data['due_date'],
                price=seamstress_data['price'],
                status='PENDING'
            )

        # Generate Invoice (Total does NOT include deposit usually, or does it?
        # Usually Invoice = Service Fees. Deposit is separate. But for simplicity, we invoice the TOTAL fees.)
        create_invoice_for_rental(rental)

        # Clear session
        del request.session['rental_data']
        del request.session['rental_items']
        if 'seamstress_data' in request.session:
            del request.session['seamstress_data']

        send_notification_email(customer, "Rental Confirmation", "email_rental_confirm.html", {"rental": rental})
        messages.success(request, "Rental booking created successfully!")
        return redirect('rental_detail', pk=rental.pk)

    return render(request, 'core/rental_wizard_confirm.html', {
        'customer': customer,
        'data': data,
        'items': display_items,
        'seamstress': seamstress_data,
        'total': total_est,
        'deposit': deposit
    })

@login_required
def contract_generate(request, pk):
    rental = get_object_or_404(Rental, pk=pk)
    # Simple HTML Contract
    return render(request, 'core/contract_template.html', {'rental': rental})
