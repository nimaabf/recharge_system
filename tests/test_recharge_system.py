import os
import django
from decimal import Decimal
from concurrent.futures import ThreadPoolExecutor

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'recharge_system.settings')
django.setup()

from django.test import TestCase, TransactionTestCase
from django.db import transaction
from app.models import Seller, CreditRequest, CreditTransaction, PhoneNumber, RechargeSale, CreditRequestStatus, TransactionType
from app.services.credit_service import CreditService, SellerNotFoundError
from app.services.charge_service import ChargeService


class RechargeSystemTestCase(TransactionTestCase):
    
    def setUp(self):
        # create 2 sellers
        self.seller1 = Seller.objects.create(name="Seller 1", balance=Decimal('0.00'))
        self.seller2 = Seller.objects.create(name="Seller 2", balance=Decimal('0.00'))
        
        # create phone numbers
        self.phone_numbers = []
        for i in range(10):
            phone = PhoneNumber.objects.create(
                phone_number=f"0912345678{i}",
                is_active=True
            )
            self.phone_numbers.append(phone)
    
    def test_credit_increase_only_charges_once(self):
        # create credit request
        request = CreditService.create_credit_request(
            seller_id=self.seller1.id,
            amount=Decimal('100000.00')
        )
        self.assertEqual(request.status, CreditRequestStatus.PENDING)
        
        approved = CreditService.approve_credit_request(request.id)
        self.assertEqual(approved.status, CreditRequestStatus.APPROVED)
        
        with self.assertRaises(Exception):
            CreditService.approve_credit_request(request.id)
        
        # verify balance increased only once
        seller1 = Seller.objects.get(id=self.seller1.id)
        self.assertEqual(seller1.balance, Decimal('100000.00'))
    
    def test_comprehensive_scenario(self):
        credit_requests = []
        for i in range(10):
            request = CreditService.create_credit_request(
                seller_id=self.seller1.id,
                amount=Decimal('100000.00')
            )
            credit_requests.append(request)
        
        for request in credit_requests:
            CreditService.approve_credit_request(request.id)
        
        seller1 = Seller.objects.get(id=self.seller1.id)
        self.assertEqual(seller1.balance, Decimal('1000000.00'))
        
        for i in range(5):
            request = CreditService.create_credit_request(
                seller_id=self.seller2.id,
                amount=Decimal('200000.00')
            )
            CreditService.approve_credit_request(request.id)
        
        
        seller2 = Seller.objects.get(id=self.seller2.id)
        self.assertEqual(seller2.balance, Decimal('1000000.00'))
        
        # perform 1000 recharge sales 500 for each seller
        recharge_amount = Decimal('5000.00')
        
        for i in range(500):
            phone = self.phone_numbers[i % len(self.phone_numbers)]
            ChargeService.charge_phone(
                seller_id=self.seller1.id,
                phone_number_id=phone.id,
                amount=recharge_amount
            )
        
        for i in range(500):
            phone = self.phone_numbers[i % len(self.phone_numbers)]
            ChargeService.charge_phone(
                seller_id=self.seller2.id,
                phone_number_id=phone.id,
                amount=recharge_amount
            )
        
        # verify final balances
        seller1.refresh_from_db()
        seller2.refresh_from_db()
        
        expected_balance_seller1 = Decimal('1000000.00') - (Decimal('500') * Decimal('5000.00'))
        self.assertEqual(seller1.balance, expected_balance_seller1)
        
        expected_balance_seller2 = Decimal('1000000.00') - (Decimal('500') * Decimal('5000.00'))
        self.assertEqual(seller2.balance, expected_balance_seller2)
        
        result1 = CreditService.verify_accounting_integrity(self.seller1.id)
        self.assertTrue(result1['is_match'], 
                       f"Seller1 accounting mismatch: current={result1['current_balance']}, calculated={result1['calculated_balance']}")
        
        result2 = CreditService.verify_accounting_integrity(self.seller2.id)
        self.assertTrue(result2['is_match'],
                       f"Seller2 accounting mismatch: current={result2['current_balance']}, calculated={result2['calculated_balance']}")
    
    def test_balance_never_goes_negative(self):
        # give seller some credit
        request = CreditService.create_credit_request(
            seller_id=self.seller1.id,
            amount=Decimal('10000.00')
        )
        CreditService.approve_credit_request(request.id)
        
        with self.assertRaises(Exception):
            ChargeService.charge_phone(
                seller_id=self.seller1.id,
                phone_number_id=self.phone_numbers[0].id,
                amount=Decimal('20000.00')
            )
        
        seller1 = Seller.objects.get(id=self.seller1.id)
        self.assertGreaterEqual(seller1.balance, Decimal('0.00'))


class ParallelLoadTestCase(TransactionTestCase):
    
    def setUp(self):
        self.seller = Seller.objects.create(name="Test Seller", balance=Decimal('1000000.00'))
        self.phone = PhoneNumber.objects.create(phone_number="09123456789", is_active=True)
    
    def test_parallel_recharge_sales(self):
        def make_recharge(seller_id, phone_id, amount):
            try:
                ChargeService.charge_phone(seller_id, phone_id, amount)
                return True
            except Exception as e:
                return str(e)
        
        with ThreadPoolExecutor(max_workers=20) as executor:
            futures = [
                executor.submit(
                    make_recharge,
                    self.seller.id,
                    self.phone.id,
                    Decimal('1000.00')
                )
                for _ in range(100)
            ]
            results = [f.result() for f in futures]
        
        # verify balance
        self.seller.refresh_from_db()
        expected_balance = Decimal('1000000.00') - (Decimal('100') * Decimal('1000.00'))
        self.assertEqual(self.seller.balance, expected_balance)
        
        result = CreditService.verify_accounting_integrity(self.seller.id)
        self.assertTrue(result['is_match'],
                       f"Accounting mismatch: current={result['current_balance']}, calculated={result['calculated_balance']}")
    
    def test_parallel_credit_approvals(self):
        # create multiple credit requests
        requests = []
        for i in range(5):
            req = CreditService.create_credit_request(
                seller_id=self.seller.id,
                amount=Decimal('10000.00')
            )
            requests.append(req)
        
        # try to approve all in parallel
        def approve_request(request_id):
            try:
                CreditService.approve_credit_request(request_id)
                return True
            except Exception as e:
                return str(e)
        
        with ThreadPoolExecutor(max_workers=5) as executor:
            futures = [
                executor.submit(approve_request, req.id)
                for req in requests
            ]
            results = [f.result() for f in futures]
        
        self.seller.refresh_from_db()
        expected_balance = Decimal('1000000.00') + (Decimal('5') * Decimal('10000.00'))
        self.assertEqual(self.seller.balance, expected_balance)
        
        result = CreditService.verify_accounting_integrity(self.seller.id)
        self.assertTrue(result['is_match'])


if __name__ == '__main__':
    import unittest
    unittest.main()
