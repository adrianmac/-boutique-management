from django import forms
from .models import Customer, InventoryItem, Event, Rental, SeamstressJob, Payment

class CustomerForm(forms.ModelForm):
    class Meta:
        model = Customer
        fields = ['name', 'email', 'phone', 'address']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'phone': forms.TextInput(attrs={'class': 'form-control'}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class InventoryItemForm(forms.ModelForm):
    class Meta:
        model = InventoryItem
        fields = ['name', 'category', 'description', 'sku', 'total_quantity', 'rental_price', 'condition', 'last_cleaned_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'category': forms.Select(attrs={'class': 'form-select'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 2}),
            'sku': forms.TextInput(attrs={'class': 'form-control'}),
            'total_quantity': forms.NumberInput(attrs={'class': 'form-control'}),
            'rental_price': forms.NumberInput(attrs={'class': 'form-control'}),
            'condition': forms.TextInput(attrs={'class': 'form-control'}),
            'last_cleaned_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }

class RentalStep1Form(forms.Form):
    customer = forms.ModelChoiceField(queryset=Customer.objects.all(), widget=forms.Select(attrs={'class': 'form-select'}))
    rental_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))
    return_date = forms.DateField(widget=forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}))

class SeamstressJobForm(forms.ModelForm):
    class Meta:
        model = SeamstressJob
        fields = ['description', 'due_date', 'price', 'status']
        widgets = {
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'due_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'price': forms.NumberInput(attrs={'class': 'form-control'}),
            'status': forms.Select(attrs={'class': 'form-select'}),
        }

class EventStep1Form(forms.ModelForm):
    # Field to trigger "Add New Customer" logic if needed, though usually handled by JS/Link
    class Meta:
        model = Event
        fields = ['name', 'customer', 'date', 'guest_count', 'event_type', 'location', 'description', 'budget']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'customer': forms.Select(attrs={'class': 'form-select'}),
            'date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'guest_count': forms.NumberInput(attrs={'class': 'form-control'}),
            'event_type': forms.Select(attrs={'class': 'form-select'}),
            'location': forms.TextInput(attrs={'class': 'form-control'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'budget': forms.NumberInput(attrs={'class': 'form-control'}),
        }

class PaymentForm(forms.ModelForm):
    class Meta:
        model = Payment
        fields = ['amount', 'method']
        widgets = {
            'amount': forms.NumberInput(attrs={'class': 'form-control'}),
            'method': forms.Select(choices=[('Cash', 'Cash'), ('Card', 'Card'), ('Transfer', 'Transfer')], attrs={'class': 'form-select'}),
        }
