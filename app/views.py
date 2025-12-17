from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.exceptions import NotFound, ValidationError


from app.models import Seller, CreditTransaction
from app.serializers import (
    CreditRequestCreateSerializer,
    CreditRequestSerializer,
    RechargeChargeRequestSerializer,
    RechargeSaleSerializer,
    BalanceSerializer,
    TransactionHistorySerializer,
    CreditTransactionSerializer
)
from app.services.credit_service import (
    CreditService,
    SellerNotFoundError,
    CreditRequestNotFoundError,
    InvalidCreditRequestError
)
from app.services.charge_service import (
    ChargeService,
    PhoneNumberNotFoundError,
    PhoneNumberInactiveError,
    InsufficientBalanceError
)

class CreateCreditRequestView(APIView):
    def post(self, request, seller_id):
        serializer = CreditRequestCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            credit_request = CreditService.create_credit_request(
                seller_id=seller_id,
                amount=serializer.validated_data['amount']
            )
            return Response(
                CreditRequestSerializer(credit_request).data,
                status=status.HTTP_201_CREATED
            )
        except SellerNotFoundError as e:
            raise NotFound(str(e))
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ApproveCreditRequestView(APIView):
    def post(self, request, request_id):
        try:
            credit_request = CreditService.approve_credit_request(request_id)
            return Response(CreditRequestSerializer(credit_request).data)
        except CreditRequestNotFoundError as e:
            raise NotFound(str(e))
        except InvalidCreditRequestError as e:
            raise ValidationError(str(e))
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ChargePhoneView(APIView):
    def post(self, request, seller_id):
        serializer = RechargeChargeRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        try:
            recharge_sale = ChargeService.charge_phone(
                seller_id=seller_id,
                phone_number_id=serializer.validated_data['phone_number_id'],
                amount=serializer.validated_data['amount']
            )
            return Response(
                RechargeSaleSerializer(recharge_sale).data,
                status=status.HTTP_201_CREATED
            )
        except (SellerNotFoundError, PhoneNumberNotFoundError) as e:
            raise NotFound(str(e))
        except (PhoneNumberInactiveError, InsufficientBalanceError) as e:
            raise ValidationError(str(e))
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class SellerBalanceView(APIView):
    def get(self, request, seller_id):
        balance = CreditService.get_seller_balance(seller_id)
        if balance is None:
            raise NotFound(f"Seller with ID {seller_id} not found")
        
        try:
            seller = Seller.objects.get(id=seller_id)
            return Response(BalanceSerializer({
                'seller_id': seller_id,
                'current_balance': balance,
                'seller_name': seller.name
            }).data)
        except Seller.DoesNotExist:
            raise NotFound(f"Seller with ID {seller_id} not found")


class TransactionHistoryView(APIView):
    def get(self, request, seller_id):
        try:
            seller = Seller.objects.get(id=seller_id)
        except Seller.DoesNotExist:
            raise NotFound(f"Seller with ID {seller_id} not found")
        
        transactions = CreditTransaction.objects.filter(
            seller_id=seller_id
        ).order_by('created_at')
        
        transaction_data = CreditTransactionSerializer(transactions, many=True).data
        
        return Response(TransactionHistorySerializer({
            'seller_id': seller_id,
            'current_balance': seller.balance,
            'transactions': transaction_data,
            'total_count': len(transaction_data)
        }).data)


class VerifyAccountingView(APIView):
    def get(self, request, seller_id):
        try:
            result = CreditService.verify_accounting_integrity(seller_id)
            return Response(result)
        except SellerNotFoundError as e:
            raise NotFound(str(e))
        except Exception as e:
            return Response(
                {'detail': str(e)},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

