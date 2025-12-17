from django.contrib import admin
from .models import Seller, CreditRequest, CreditTransaction, PhoneNumber, RechargeSale


@admin.register(Seller)
class SellerAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'balance', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name']
    readonly_fields = ['created_at']


@admin.register(CreditRequest)
class CreditRequestAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'amount', 'status', 'created_at', 'approved_at']
    list_filter = ['status', 'created_at']
    search_fields = ['seller__name']
    readonly_fields = ['created_at', 'approved_at']
    date_hierarchy = 'created_at'


@admin.register(CreditTransaction)
class CreditTransactionAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'amount', 'transaction_type', 'balance_after', 'created_at']
    list_filter = ['transaction_type', 'created_at']
    search_fields = ['seller__name']
    readonly_fields = ['created_at']
    date_hierarchy = 'created_at'


@admin.register(PhoneNumber)
class PhoneNumberAdmin(admin.ModelAdmin):
    list_display = ['id', 'phone_number', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['phone_number']


@admin.register(RechargeSale)
class RechargeSaleAdmin(admin.ModelAdmin):
    list_display = ['id', 'seller', 'phone_number', 'amount', 'status', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['seller__name', 'phone_number__phone_number']
    date_hierarchy = 'created_at'
