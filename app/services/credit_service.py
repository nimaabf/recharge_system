from django.db import transaction
from decimal import Decimal
from datetime import datetime
from typing import Optional


from app.models import Seller,CreditRequest,RechargeSale,CreditTransaction,CreditRequestStatus,TransactionType

class CreditServiceError(Exception):
    pass

class SellerNotFoundError(CreditServiceError):
    pass

class CreditRequestNotFoundError(CreditServiceError):
    pass

class InvalidCreditRequestError(CreditServiceError):
    pass

class InsufficientBalanceError(CreditServiceError):
    pass


class CreditService:
    @staticmethod
    def create_credit_request(seller_id:int,amount:Decimal)->CreditRequest:
        try:
            seller=Seller.objects.get(id=seller_id)
        except Seller.DoesNotExist:
            raise SellerNotFoundError(f"Seller with id {seller_id} not found")
        
        #now we need check for pending requests with this amount
        existing_request=CreditRequest.objects.filter(seller_id=seller_id,amount=amount,status=CreditRequestStatus.PENDING).first()
        if existing_request:
            return existing_request

        credit_request = CreditRequest(
            seller=seller,
            amount=amount,
            status=CreditRequestStatus.PENDING
        )
        credit_request.save()

        return credit_request
        
    @staticmethod
    def approve_credit_request(request_id:int)->CreditRequest:
        #prevent race condition 
        try:
            credit_request=CreditRequest.objects.select_for_update().get(id=request_id)
        except CreditRequest.DoesNotExists:
            raise SellerNotFoundError(f"Credit request with ID {request_id} not found")
        #if process still pending
        if credit_request.status!=CreditRequestStatus.PENDING:
            raise InvalidRequestError(f"Credit request {request_id} is already {credit_request.status}. Cannot approve.")

        
     # lock seller too to prevent concurrent balance updates
        try:
            seller=Seller.objects.select_for_update().get(id=credit_request.seller_id)
        except Seller.DoesNotExist:
            raise SellerNotFoundError(f"Seller with ID {credit_request.seller_id} not found")

        try:
            with transaction.atomic():
                new_balance=seller.balance+credit_request.amount

                credit_request.status=CreditRequestStatus.APPROVED
                credit_request.approved_at=datetime.now()
                credit_request.save()

                seller.balance=new_balance
                seller.save()

                # record transaction for accounting
                credit_transaction = CreditTransaction(
                    seller=seller,
                    amount=credit_request.amount,
                    transaction_type=TransactionType.CREDIT_INCREASE,
                    reference_id=credit_request.id,
                    balance_after=new_balance
                )
                credit_transaction.save()

                credit_request.refresh_from_db()
                seller.refresh_from_db()

                return credit_request

        except Exception as e:
            raise InvalidCreditRequestError(f"Failed to approve credit request: {str(e)}")

    @staticmethod
    def get_seller_balance(seller_id: int) -> Optional[Decimal]:
        try:
            seller=seller.objects.get(id=seller_id)
            return seller.balance
        except Seller.DoesNotExists:
            return None

    # @staticmethod
    