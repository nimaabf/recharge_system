from django.urls import path
from .views import (
    CreateCreditRequestView,
    ApproveCreditRequestView,
    ChargePhoneView,
    SellerBalanceView,
    TransactionHistoryView,
    VerifyAccountingView
)

urlpatterns = [
    path('sellers/<int:seller_id>/credit-request/', CreateCreditRequestView.as_view(), name='create-credit-request'),
    path('admin/credit-requests/<int:request_id>/approve/', ApproveCreditRequestView.as_view(), name='approve-credit-request'),
    path('sellers/<int:seller_id>/charge/', ChargePhoneView.as_view(), name='charge-phone'),
    path('sellers/<int:seller_id>/balance/', SellerBalanceView.as_view(), name='seller-balance'),
    path('sellers/<int:seller_id>/transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('sellers/<int:seller_id>/verify-accounting/', VerifyAccountingView.as_view(), name='verify-accounting'),
]

