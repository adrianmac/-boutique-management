from django.urls import path
from . import views_customer, views_inventory, views_rental, views_seamstress, views_event, views_finance, views_dashboard

urlpatterns = [
    # Dashboard
    path('', views_dashboard.dashboard, name='dashboard'),
    path('calendar/', views_dashboard.calendar_view, name='calendar'),
    path('reports/', views_dashboard.reports_view, name='reports'),

    # Customers
    path('customers/', views_customer.customer_list, name='customer_list'),
    path('customers/add/', views_customer.customer_create, name='customer_create'),
    path('customers/<int:pk>/', views_customer.customer_detail, name='customer_detail'),
    path('customers/<int:pk>/edit/', views_customer.customer_edit, name='customer_edit'),

    # Inventory
    path('inventory/', views_inventory.inventory_list, name='inventory_list'),
    path('inventory/add/', views_inventory.inventory_create, name='inventory_create'),
    path('inventory/labels/', views_inventory.inventory_labels, name='inventory_labels'),
    path('inventory/<int:pk>/', views_inventory.inventory_detail, name='inventory_detail'),
    path('inventory/<int:pk>/edit/', views_inventory.inventory_edit, name='inventory_edit'),

    # Rentals
    path('rentals/', views_rental.rental_list, name='rental_list'),
    path('rentals/wizard/step1/', views_rental.rental_wizard_step1, name='rental_wizard_step1'),
    path('rentals/wizard/step2/', views_rental.rental_wizard_step2, name='rental_wizard_step2'),
    path('rentals/wizard/step3/', views_rental.rental_wizard_step3, name='rental_wizard_step3'),
    path('rentals/wizard/confirm/', views_rental.rental_wizard_confirm, name='rental_wizard_confirm'),
    path('rentals/<int:pk>/', views_rental.rental_detail, name='rental_detail'),
    path('rentals/<int:pk>/status/', views_rental.rental_update_status, name='rental_update_status'),  # NEW
    path('rentals/<int:pk>/contract/', views_rental.contract_generate, name='contract_generate'),

    # Seamstress
    path('seamstress/', views_seamstress.seamstress_list, name='seamstress_list'),
    path('seamstress/add/', views_seamstress.seamstress_create_standalone, name='seamstress_create'),
    path('seamstress/<int:pk>/', views_seamstress.seamstress_detail, name='seamstress_detail'),
    path('seamstress/<int:pk>/update/', views_seamstress.seamstress_update_status, name='seamstress_update_status'),

    # Events
    path('events/', views_event.event_list, name='event_list'),
    path('events/plan/step1/', views_event.event_wizard_step1, name='event_wizard_step1'),
    path('events/plan/step2/', views_event.event_wizard_step2, name='event_wizard_step2'),
    path('events/plan/step3/', views_event.event_wizard_step3, name='event_wizard_step3'),
    path('events/plan/confirm/', views_event.event_wizard_confirm, name='event_wizard_confirm'),
    path('events/<int:pk>/', views_event.event_detail, name='event_detail'),

    # Finance
    path('invoices/', views_finance.invoice_list, name='invoice_list'),
    path('invoices/<int:pk>/', views_finance.invoice_detail, name='invoice_detail'),
    path('invoices/<int:pk>/print/', views_finance.invoice_print, name='invoice_print'),
]
