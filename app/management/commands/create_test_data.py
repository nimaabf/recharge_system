from django.core.management.base import BaseCommand
from app.models import Seller, PhoneNumber
from decimal import Decimal


class Command(BaseCommand):
    help = 'Create test data: sellers and phone numbers'

    def handle(self, *args, **options):
        # create sellers
        seller1, created1 = Seller.objects.get_or_create(
            name="Seller 1",
            defaults={'balance': Decimal('1000000.00')}
        )
        seller2, created2 = Seller.objects.get_or_create(
            name="Seller 2",
            defaults={'balance': Decimal('500000.00')}
        )
        
        # create phone numbers
        phones = []
        for i in range(10):
            phone, _ = PhoneNumber.objects.get_or_create(
                phone_number=f"0912345678{i}",
                defaults={'is_active': True}
            )
            phones.append(phone)
        
        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created:\n'
                f'  - Seller 1 (ID: {seller1.id}, Balance: {seller1.balance})\n'
                f'  - Seller 2 (ID: {seller2.id}, Balance: {seller2.balance})\n'
                f'  - {len(phones)} phone numbers (IDs: {phones[0].id}-{phones[-1].id})'
            )
        )
