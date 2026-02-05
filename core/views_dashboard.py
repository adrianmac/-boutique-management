from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Sum, Count, Q
from .models import Rental, Event, InventoryItem, SeamstressJob, Invoice, RentalItem
from datetime import date, timedelta
import calendar as cal_module
import json

@login_required
def dashboard(request):
    today = date.today()

    # Action Items
    actions = {
        'rentals_start': Rental.objects.filter(rental_date=today, status='RESERVED'),
        'rentals_return': Rental.objects.filter(return_date=today, status='PICKED_UP'),
        'jobs_due': SeamstressJob.objects.filter(due_date=today).exclude(status='COMPLETED'),
        'events_today': Event.objects.filter(date=today),
    }

    context = {
        'actions': actions,
        'recent_events': Event.objects.filter(date__gte=today).order_by('date')[:5],
        'active_rentals': Rental.objects.filter(status__in=['RESERVED', 'PICKED_UP']).order_by('rental_date')[:5],
        'pending_jobs': SeamstressJob.objects.filter(status__in=['PENDING', 'IN_PROGRESS']).order_by('due_date')[:5],
        'overdue_invoices': Invoice.objects.filter(status='UNPAID', date_created__lt=today).count(),
    }
    return render(request, 'core/dashboard.html', context)

@login_required
def calendar_view(request):
    today = date.today()
    year = int(request.GET.get('year', today.year))
    month = int(request.GET.get('month', today.month))

    cal = cal_module.Calendar()
    month_days = cal.monthdatescalendar(year, month)

    start_date = month_days[0][0]
    end_date = month_days[-1][-1]

    events = Event.objects.filter(date__range=(start_date, end_date))
    rentals = Rental.objects.filter(rental_date__range=(start_date, end_date))

    calendar_data = []
    for week in month_days:
        week_data = []
        for day in week:
            day_events = events.filter(date=day)
            day_rentals = rentals.filter(rental_date=day)

            is_today = (day == today)
            is_current_month = (day.month == month)

            week_data.append({
                'date': day,
                'events': day_events,
                'rentals': day_rentals,
                'is_today': is_today,
                'is_current_month': is_current_month
            })
        calendar_data.append(week_data)

    prev_month = month - 1 if month > 1 else 12
    prev_year = year if month > 1 else year - 1
    next_month = month + 1 if month < 12 else 1
    next_year = year if month < 12 else year + 1

    return render(request, 'core/calendar.html', {
        'calendar': calendar_data,
        'current_month': date(year, month, 1),
        'prev_year': prev_year, 'prev_month': prev_month,
        'next_year': next_year, 'next_month': next_month
    })

@login_required
def reports_view(request):
    today = date.today()

    # 1. Monthly Revenue
    revenue_labels = []
    revenue_data = []

    for i in range(5, -1, -1):
        if today.month - i < 1:
             m = 12 + (today.month - i)
             y = today.year - 1
        else:
             m = today.month - i
             y = today.year
        month_start = date(y, m, 1)
        next_month = (month_start + timedelta(days=32)).replace(day=1)

        total = Invoice.objects.filter(
            date_created__gte=month_start,
            date_created__lt=next_month,
            status='PAID'
        ).aggregate(Sum('total_amount'))['total_amount__sum'] or 0

        revenue_labels.append(month_start.strftime("%B"))
        revenue_data.append(float(total))

    # 2. Top Items
    top_items = RentalItem.objects.values('inventory_item__name').annotate(
        total_qty=Sum('quantity')
    ).order_by('-total_qty')[:5]

    item_labels = [x['inventory_item__name'] for x in top_items]
    item_data = [x['total_qty'] for x in top_items]

    # 3. Revenue by Event Type
    event_revenue = Invoice.objects.filter(
        event__isnull=False,
        status='PAID'
    ).values('event__event_type').annotate(
        total=Sum('total_amount')
    ).order_by('-total')

    event_type_display = dict(Event.EVENT_TYPE_CHOICES)

    event_type_labels = [event_type_display.get(x['event__event_type'], x['event__event_type']) for x in event_revenue]
    event_type_data = [float(x['total']) for x in event_revenue]

    return render(request, 'core/reports.html', {
        'revenue_labels': json.dumps(revenue_labels),
        'revenue_data': json.dumps(revenue_data),
        'item_labels': json.dumps(item_labels),
        'item_data': json.dumps(item_data),
        'event_type_labels': json.dumps(event_type_labels),
        'event_type_data': json.dumps(event_type_data),
    })
