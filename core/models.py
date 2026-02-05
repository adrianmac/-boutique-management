from django.db import models
from django.contrib.auth.models import User
from decimal import Decimal

class Customer(models.Model):
    STATUS_CHOICES = [
        ('ACTIVE', 'Active'),
        ('VIP', 'VIP'),
        ('INACTIVE', 'Inactive'),
    ]
    name = models.CharField(max_length=100)
    email = models.EmailField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    address = models.TextField(blank=True, null=True)

    # New Fields
    birthday = models.DateField(blank=True, null=True)
    notes = models.TextField(blank=True, null=True)
    bust = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Bust measurement (inches)")
    waist = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Waist measurement (inches)")
    hips = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Hips measurement (inches)")
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='ACTIVE')

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

class InventoryItem(models.Model):
    CATEGORY_CHOICES = [
        ('DRESS', 'Dress'),
        ('SHOES', 'Shoes'),
        ('ACCESSORY', 'Accessory'),
        ('LINENS', 'Linens'),
        ('CHAIR_COVER', 'Chair Cover'),
        ('TABLECLOTH', 'Tablecloth'),
        ('FURNITURE', 'Furniture'),
        ('DECOR', 'Other Decor (Vase, etc.)'),
    ]
    name = models.CharField(max_length=100)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='DRESS')
    description = models.TextField(blank=True, null=True)
    sku = models.CharField(max_length=50, unique=True, blank=True, null=True, help_text="Stock Keeping Unit / Barcode")
    total_quantity = models.PositiveIntegerField(default=1)
    rental_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    condition = models.CharField(max_length=100, default='Good')
    last_cleaned_date = models.DateField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.get_category_display()})"

class InventoryLog(models.Model):
    item = models.ForeignKey(InventoryItem, on_delete=models.CASCADE, related_name='logs')
    action = models.CharField(max_length=50) # Restock, Damaged, Lost
    quantity_changed = models.IntegerField()
    timestamp = models.DateTimeField(auto_now_add=True)
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)

class Event(models.Model):
    EVENT_TYPE_CHOICES = [
        ('WEDDING', 'Wedding'),
        ('SWEET16', 'Sweet 16'),
        ('QUINCE', 'Quinceanera'),
        ('OTHER', 'Other'),
    ]
    name = models.CharField(max_length=200)
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    date = models.DateField()
    guest_count = models.PositiveIntegerField(default=0)
    event_type = models.CharField(max_length=20, choices=EVENT_TYPE_CHOICES, default='OTHER')
    location = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True, help_text="Event details")

    # Pricing
    budget = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.name} - {self.date}"

class Rental(models.Model):
    STATUS_CHOICES = [
        ('RESERVED', 'Reserved'),
        ('PICKED_UP', 'Picked Up'),
        ('RETURNED', 'Returned'),
        ('CANCELLED', 'Cancelled'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    event = models.ForeignKey(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='rentals')
    rental_date = models.DateField()
    return_date = models.DateField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='RESERVED')
    created_at = models.DateTimeField(auto_now_add=True)

    # Pricing
    deposit_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    deposit_returned = models.BooleanField(default=False)

    def __str__(self):
        return f"Rental #{self.id} for {self.customer.name}"

class RentalItem(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='items')
    inventory_item = models.ForeignKey(InventoryItem, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price_at_booking = models.DecimalField(max_digits=10, decimal_places=2)

    def save(self, *args, **kwargs):
        if not self.price_at_booking:
            self.price_at_booking = self.inventory_item.rental_price
        super().save(*args, **kwargs)

class SeamstressJob(models.Model):
    STATUS_CHOICES = [
        ('PENDING', 'Pending'),
        ('IN_PROGRESS', 'In Progress'),
        ('READY', 'Ready for Pickup'),
        ('COMPLETED', 'Completed'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    rental = models.ForeignKey(Rental, on_delete=models.SET_NULL, null=True, blank=True, related_name='alterations')
    description = models.TextField(help_text="Measurements and required alterations")
    due_date = models.DateField()
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='PENDING')

    def __str__(self):
        return f"Alteration for {self.customer.name}"

class Invoice(models.Model):
    STATUS_CHOICES = [
        ('UNPAID', 'Unpaid'),
        ('PARTIAL', 'Partially Paid'),
        ('PAID', 'Paid'),
    ]
    customer = models.ForeignKey(Customer, on_delete=models.CASCADE)
    event = models.OneToOneField(Event, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    rental = models.OneToOneField(Rental, on_delete=models.SET_NULL, null=True, blank=True, related_name='invoice')
    date_created = models.DateTimeField(auto_now_add=True)
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, default=0.00)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='UNPAID')

    def update_status(self):
        paid = self.payments.aggregate(total=models.Sum('amount'))['total'] or Decimal('0.00')
        if paid >= self.total_amount:
            self.status = 'PAID'
        elif paid > 0:
            self.status = 'PARTIAL'
        else:
            self.status = 'UNPAID'
        self.save()

class Payment(models.Model):
    invoice = models.ForeignKey(Invoice, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateField(auto_now_add=True)
    method = models.CharField(max_length=50, default='Cash') # Cash, Card, Transfer

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)
        self.invoice.update_status()
