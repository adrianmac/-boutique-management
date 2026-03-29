from django.contrib import admin
from .models import (
    Customer, InventoryItem, InventoryLog, Event, Rental,
    RentalItem, SeamstressJob, Invoice, Payment, Service, EventService,
)


class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1


class RentalAdmin(admin.ModelAdmin):
    inlines = [RentalItemInline]
    list_display = ('id', 'customer', 'rental_date', 'return_date', 'status')
    list_filter = ('status',)


class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0


class InvoiceAdmin(admin.ModelAdmin):
    inlines = [PaymentInline]
    list_display = ('id', 'customer', 'status', 'total_amount', 'date_created')
    list_filter = ('status',)


class EventAdmin(admin.ModelAdmin):
    list_display = ('name', 'customer', 'date', 'event_type', 'guest_count')
    list_filter = ('event_type',)


class CustomerAdmin(admin.ModelAdmin):
    list_display = ('name', 'email', 'phone', 'status', 'created_at')
    list_filter = ('status',)
    search_fields = ('name', 'email', 'phone')


class SeamstressJobAdmin(admin.ModelAdmin):
    list_display = ('customer', 'due_date', 'status', 'price')
    list_filter = ('status',)


admin.site.register(Customer, CustomerAdmin)
admin.site.register(InventoryItem)
admin.site.register(InventoryLog)
admin.site.register(Event, EventAdmin)
admin.site.register(Rental, RentalAdmin)
admin.site.register(SeamstressJob, SeamstressJobAdmin)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Payment)
admin.site.register(Service)
admin.site.register(EventService)
