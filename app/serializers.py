from rest_framework import serializers
from decimal import Decimal
from .models import (Seller, CreditRequest, CreditTransaction, PhoneNumber, RechargeSale,
    CreditRequestStatus, TransactionType)

class CreditRequestCreateSerializer(serializers.Serializer):
    amount=serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))

class CreditRequestSerializer(serializers.ModelSerializer):
   seller_id=serializers.IntegerField(source='seller.id',read_only=True)

   class Meta:
    model=CreditRequest
    fields=['id','seller_id','amount','status','created_at','approved_at']

class RechargeChargeRequestSerializer(serializers.Serializer):
    phone_number_id=serializers.IntegerField()
    amount=serializers.DecimalField(max_digits=15, decimal_places=2, min_value=Decimal('0.01'))


class RechargeSaleSerializer(serializers.ModelSerializer):
    seller_id=serializers.IntegerField(source='seller.id',read_only=True)
    phone_number_id=serializers.IntegerField(source='phone_number.id',read_only=True)

    class Meta:
        model=RechargeSale
        fields=['id','seller_id','phone_number_id','amount','status','created_at']

class BalanceSerializer(serializers.Serializer):
    seller_id=serializers.IntegerField()
    current_balance=serializers.DecimalField(max_digits=15, decimal_places=2)
    seller_name=serializers.CharField()

class CreditTransactionSerializer(serializers.ModelSerializer):
    seller_id=serializers.IntegerField(source='seller.id',read_only=True)
    transaction_type=serializers.CharField()

    class Meta:
        model=CreditTransaction
        fields=['id','seller_id','amount','transaction_type','reference_id','balance_after','created_at']

class TransactionHistorySerializer(serializers.Serializer):
    seller_id=serializers.IntegerField()
    current_balance=serializers.DecimalField(max_digits=15, decimal_places=2)
    transactions=CreditTransactionSerializer(many=True)
    total_count=serializers.IntegerField()