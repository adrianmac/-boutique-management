from django.contrib.auth.decorators import login_required
from django.shortcuts import render, get_object_or_404, redirect
from .models import SeamstressJob, Customer
from .forms import SeamstressJobForm, CustomerForm

@login_required
def seamstress_list(request):
    jobs = SeamstressJob.objects.all().order_by('due_date')
    return render(request, 'core/seamstress_list.html', {'jobs': jobs})

@login_required
def seamstress_detail(request, pk):
    job = get_object_or_404(SeamstressJob, pk=pk)
    return render(request, 'core/seamstress_detail.html', {'job': job})

@login_required
def seamstress_create_standalone(request):
    """Create a job without a rental"""
    # Simple 2-step: Select Customer -> Enter Job Details (Or simple 1 page if customer exists)
    # For MVP, let's assume we select customer first or create new.
    # To keep it simple, I'll use a form that only handles job details and requires a customer ID in URL or select from list.
    pass
    # Actually, let's just make a generic create view where you select customer.

    if request.method == 'POST':
        form = SeamstressJobForm(request.POST)
        customer_id = request.POST.get('customer')
        if form.is_valid() and customer_id:
            job = form.save(commit=False)
            job.customer_id = customer_id
            job.save()
            return redirect('seamstress_detail', pk=job.pk)
    else:
        form = SeamstressJobForm()

    customers = Customer.objects.all()
    return render(request, 'core/seamstress_form.html', {'form': form, 'customers': customers})

@login_required
def seamstress_update_status(request, pk):
    job = get_object_or_404(SeamstressJob, pk=pk)
    if request.method == 'POST':
        status = request.POST.get('status')
        if status in dict(SeamstressJob.STATUS_CHOICES):
            job.status = status
            job.save()
    return redirect('seamstress_detail', pk=pk)
