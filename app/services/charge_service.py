from django.db import transaction
from decimal import Decimal

from app.models import Seller,PhoneNumber,RechargeSale,CreditTransaction,TransactionType

from app.services.credit_service import SellerNotFoundError,CreditServiceError,InsufficientBalanceError


class PhoneNumberNotFoundError(CreditServiceError):
   pass

class PhoneNumberInactiveError(CreditServiceError):
   pass


class ChargeService:

    @staticmethod
    def charge_phone(seller_id:int,phone_number_id:int,amount:Decimal)-> RechargeSale:
        # check phone number
        try:
            phone_number = PhoneNumber.objects.get(id=phone_number_id)
        except PhoneNumber.DoesNotExist:
            raise PhoneNumberNotFoundError(f"Phone number with ID {phone_number_id} not found")

        if not phone_number.is_active:
            raise PhoneNumberInactiveError(f"Phone number {phone_number.phone_number} is not active")

        # lock seller to prevent race conditions
        try:
            seller = Seller.objects.select_for_update().get(id=seller_id)
        except Seller.DoesNotExist:
            raise SellerNotFoundError(f"Seller with ID {seller_id} not found")

        # check balance
        current_balance = Decimal(str(seller.balance))
        charge_amount = Decimal(str(amount))

        if current_balance < charge_amount:
            raise InsufficientBalanceError(
                f"Insufficient balance. Current: {current_balance}, Required: {charge_amount}"
            )

        try:
            with transaction.atomic():
                new_balance = current_balance - charge_amount
                seller.balance = new_balance
                seller.save()

                recharge_sale = RechargeSale(
                    seller=seller,
                    phone_number=phone_number,
                    amount=charge_amount,
                    status="completed"
                )
                recharge_sale.save()

                # record transaction for accounting (- for deduction)
                credit_transaction = CreditTransaction(
                    seller=seller,
                    amount=-charge_amount,
                    transaction_type=TransactionType.RECHARGE_SALE,
                    reference_id=recharge_sale.id,
                    balance_after=new_balance
                )
                credit_transaction.save()

                recharge_sale.refresh_from_db()
                seller.refresh_from_db()

                return recharge_sale

        except Exception as e:
            raise CreditServiceError(f"Failed to process charge: {str(e)}")

    @staticmethod
    def get_recharge_history(seller_id: int, limit: int = 100) -> list:
        recharge_sales = RechargeSale.objects.filter(
            seller_id=seller_id
        ).order_by('-created_at')[:limit]

        return list(recharge_sales)   