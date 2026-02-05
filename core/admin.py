from django.contrib import admin
from .models import Customer, InventoryItem, InventoryLog, Event, Rental, RentalItem, SeamstressJob, Invoice, Payment

class RentalItemInline(admin.TabularInline):
    model = RentalItem
    extra = 1

class RentalAdmin(admin.ModelAdmin):
    inlines = [RentalItemInline]

class PaymentInline(admin.TabularInline):
    model = Payment
    extra = 0

class InvoiceAdmin(admin.ModelAdmin):
    inlines = [PaymentInline]
    list_display = ('id', 'customer', 'status', 'total_amount', 'date_created')

admin.site.register(Customer)
admin.site.register(InventoryItem)
admin.site.register(InventoryLog)
admin.site.register(Event)
admin.site.register(Rental, RentalAdmin)
admin.site.register(SeamstressJob)
admin.site.register(Invoice, InvoiceAdmin)
admin.site.register(Payment)
from .models import Service, EventService

admin.site.register(Service)
admin.site.register(EventService)
