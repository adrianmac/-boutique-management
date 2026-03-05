@login_required
def rental_update_status(request, pk):
    """Update the status of a rental (Picked Up / Returned / Cancelled)."""
    rental = get_object_or_404(Rental, pk=pk)
    if request.method == 'POST':
        new_status = request.POST.get('status')
        valid_statuses = dict(Rental.STATUS_CHOICES)
        if new_status in valid_statuses:
            rental.status = new_status
            rental.save()
            messages.success(request, f"Rental #{rental.id} marked as {valid_statuses[new_status]}.")
        else:
            messages.error(request, "Invalid status.")
    return redirect('rental_detail', pk=pk)
