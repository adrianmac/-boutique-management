from django.core.management.base import BaseCommand
from django.contrib.auth.models import Group, Permission
from django.contrib.contenttypes.models import ContentType
from core.models import Customer, InventoryItem, Event, Rental, SeamstressJob, Invoice

class Command(BaseCommand):
    help = 'Setup user roles and permissions'

    def handle(self, *args, **kwargs):
        # Create Groups
        manager_group, _ = Group.objects.get_or_create(name='Manager')
        sales_group, _ = Group.objects.get_or_create(name='Sales')
        seamstress_group, _ = Group.objects.get_or_create(name='Seamstress')

        # Models
        models = [Customer, InventoryItem, Event, Rental, SeamstressJob, Invoice]

        # Helper to get perms
        def get_perms(model, perms):
            ct = ContentType.objects.get_for_model(model)
            return Permission.objects.filter(content_type=ct, codename__in=[f'{p}_{model._meta.model_name}' for p in perms])

        # Sales Permissions
        sales_perms = []
        for model in models:
            sales_perms.extend(get_perms(model, ['view', 'add', 'change']))
        sales_group.permissions.set(sales_perms)

        # Seamstress Permissions
        seamstress_perms = []
        seamstress_perms.extend(get_perms(SeamstressJob, ['view', 'change']))
        seamstress_perms.extend(get_perms(Customer, ['view'])) # Need to see customer name
        seamstress_group.permissions.set(seamstress_perms)

        self.stdout.write(self.style.SUCCESS('Successfully setup roles.'))
