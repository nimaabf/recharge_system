from django.core.management.base import BaseCommand
from decimal import Decimal
from app.models import Seller, PhoneNumber


class Command(BaseCommand):
    help = 'Creates sample data for testing API endpoints'

    def handle(self, *args, **options):
        self.stdout.write('Creating sample data...')
        
        # Create sample sellers
        seller1, created = Seller.objects.get_or_create(
            name="Seller 1",
            defaults={'balance': Decimal('1000000.00')}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created seller: {seller1.name} (ID: {seller1.id}) with balance: {seller1.balance}'))
        else:
            self.stdout.write(self.style.WARNING(f'Seller already exists: {seller1.name} (ID: {seller1.id})'))
        
        seller2, created = Seller.objects.get_or_create(
            name="Seller 2",
            defaults={'balance': Decimal('500000.00')}
        )
        if created:
            self.stdout.write(self.style.SUCCESS(f'Created seller: {seller2.name} (ID: {seller2.id}) with balance: {seller2.balance}'))
        else:
            self.stdout.write(self.style.WARNING(f'Seller already exists: {seller2.name} (ID: {seller2.id})'))
        
        # Create sample phone numbers
        phone_numbers = [
            "09123456789",
            "09123456790",
            "09123456791",
            "09123456792",
            "09123456793",
        ]
        
        created_count = 0
        for phone_num in phone_numbers:
            phone, created = PhoneNumber.objects.get_or_create(
                phone_number=phone_num,
                defaults={'is_active': True}
            )
            if created:
                created_count += 1
                self.stdout.write(self.style.SUCCESS(f'Created phone number: {phone.phone_number} (ID: {phone.id})'))
        
        if created_count == 0:
            self.stdout.write(self.style.WARNING('All phone numbers already exist'))
        
        self.stdout.write(self.style.SUCCESS('\nSample data created successfully!'))
        self.stdout.write('\nYou can now test the API endpoints:')
        self.stdout.write(f'  - Seller 1 ID: {seller1.id}')
        self.stdout.write(f'  - Seller 2 ID: {seller2.id}')
        self.stdout.write(f'  - Phone number IDs: {", ".join([str(p.id) for p in PhoneNumber.objects.all()[:5]])}')
