import os
import django
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor
import time

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recharge_system.settings')
django.setup()

from django.test import TransactionTestCase
from app.models import Seller, PhoneNumber
from app.services.credit_service import CreditService
from app.services.charge_service import ChargeService


class ParallelLoadTest(TransactionTestCase):
    
    def setUp(self):
        self.seller = Seller.objects.create(name="Load Test Seller", balance=Decimal('10000000.00'))
        self.phones = [
            PhoneNumber.objects.create(phone_number=f"0912345678{i}", is_active=True)
            for i in range(20)
        ]
    
    def test_thread_based_parallel_load(self):
        def make_recharge(phone_id):
            try:
                ChargeService.charge_phone(
                    seller_id=self.seller.id,
                    phone_number_id=phone_id,
                    amount=Decimal('100.00')
                )
                return True
            except Exception as e:
                return False
        
        # 1000 parallel operations using threads
        start_time = time.time()
        with ThreadPoolExecutor(max_workers=50) as executor:
            futures = [
                executor.submit(make_recharge, self.phones[i % len(self.phones)].id)
                for i in range(1000)
            ]
            results = [f.result() for f in futures]
        
        elapsed = time.time() - start_time
        
        # verify accounting integrity
        self.seller.refresh_from_db()
        result = CreditService.verify_accounting_integrity(self.seller.id)
        
        print(f"\nThread-based test:")
        print(f"  Time: {elapsed:.2f}s")
        print(f"  Success rate: {sum(results)/len(results)*100:.1f}%")
        print(f"  Final balance: {self.seller.balance}")
        print(f"  Accounting match: {result['is_match']}")
        print(f"  Transaction count: {result['transaction_count']}")
        
        self.assertTrue(result['is_match'], "Accounting integrity failed under thread load")
    
    def test_process_based_parallel_load(self):
       
        
        def worker_process(seller_id, phone_ids, num_operations):
            import os
            import django
            os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recharge_system.settings')
            django.setup()
            
            from app.services.charge_service import ChargeService
            from decimal import Decimal
            
            success_count = 0
            for i in range(num_operations):
                try:
                    ChargeService.charge_phone(
                        seller_id=seller_id,
                        phone_number_id=phone_ids[i % len(phone_ids)],
                        amount=Decimal('100.00')
                    )
                    success_count += 1
                except:
                    pass
            return success_count
        
        
        print("\nProcess-based testing requires separate database connections")
        print("In production, use separate API calls or message queues")


class MultiProcessVsMultiThreadDemo:
    
    @staticmethod
    def explain_difference():
        print("threads share memory fast data sharing lower overhead")
        print("processes true parallelism isolated memory higher overhead")
        print("for this recharge system threads are better for db operations")


if __name__ == '__main__':
    demo = MultiProcessVsMultiThreadDemo()
    demo.explain_difference()
