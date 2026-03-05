from django.contrib.auth.decorators import login_required
import qrcode
import io
import base64
from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Q
from django.core.paginator import Paginator
from .models import InventoryItem
from .forms import InventoryItemForm

@login_required
def inventory_list(request):
    query = request.GET.get('q')
    category = request.GET.get('category')
    items = InventoryItem.objects.all().order_by('name')

    if query:
        items = items.filter(
            Q(name__icontains=query) |
            Q(sku__icontains=query) |
            Q(description__icontains=query)
        )

    if category:
        items = items.filter(category=category)

    paginator = Paginator(items, 24)
    page = request.GET.get('page')
    items = paginator.get_page(page)

    return render(request, 'core/inventory_list.html', {
        'items': items,
        'query': query,
        'category': category,
        'categories': InventoryItem.CATEGORY_CHOICES
    })

@login_required
def inventory_detail(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)

    # Generate QR Code
    qr_data = f"ITEM-{item.id}-{item.sku}"
    qr = qrcode.QRCode(version=1, box_size=10, border=5)
    qr.add_data(qr_data)
    qr.make(fit=True)
    img = qr.make_image(fill_color="black", back_color="white")

    buffer = io.BytesIO()
    img.save(buffer, format="PNG")
    qr_code_base64 = base64.b64encode(buffer.getvalue()).decode()

    return render(request, 'core/inventory_detail.html', {
        'item': item,
        'qr_code': qr_code_base64
    })

@login_required
def inventory_create(request):
    if request.method == 'POST':
        form = InventoryItemForm(request.POST)
        if form.is_valid():
            item = form.save()
            return redirect('inventory_detail', pk=item.pk)
    else:
        form = InventoryItemForm()
    return render(request, 'core/inventory_form.html', {'form': form, 'title': 'Add Inventory Item'})

@login_required
def inventory_edit(request, pk):
    item = get_object_or_404(InventoryItem, pk=pk)
    if request.method == 'POST':
        form = InventoryItemForm(request.POST, instance=item)
        if form.is_valid():
            form.save()
            return redirect('inventory_detail', pk=item.pk)
    else:
        form = InventoryItemForm(instance=item)
    return render(request, 'core/inventory_form.html', {'form': form, 'title': 'Edit Inventory Item'})

@login_required
def inventory_labels(request):
    """Printable view of QR codes for all items"""
    items = InventoryItem.objects.all()
    labels = []

    for item in items:
        qr_data = f"ITEM-{item.id}-{item.sku}"
        qr = qrcode.QRCode(version=1, box_size=5, border=2)
        qr.add_data(qr_data)
        qr.make(fit=True)
        img = qr.make_image(fill_color="black", back_color="white")

        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        labels.append({
            'item': item,
            'qr': base64.b64encode(buffer.getvalue()).decode()
        })

    return render(request, 'core/inventory_labels.html', {'labels': labels})
