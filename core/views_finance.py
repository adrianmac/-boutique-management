from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import Invoice, Payment
from .forms import PaymentForm

@login_required
def invoice_list(request):
    invoices = Invoice.objects.all().order_by('-date_created')
    return render(request, 'core/invoice_list.html', {'invoices': invoices})

@login_required
def invoice_detail(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)

    if request.method == 'POST':
        form = PaymentForm(request.POST)
        if form.is_valid():
            payment = form.save(commit=False)
            payment.invoice = invoice
            payment.save()
            return redirect('invoice_detail', pk=pk)
    else:
        form = PaymentForm()

    return render(request, 'core/invoice_detail.html', {'invoice': invoice, 'form': form})

@login_required
def invoice_print(request, pk):
    invoice = get_object_or_404(Invoice, pk=pk)
    return render(request, 'core/invoice_print.html', {'invoice': invoice})
