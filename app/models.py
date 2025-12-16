from django.db import models
from django.validators import MinValueValidator
from decimal import Decimal


class CreditRequestStatus(models.TextChoices):
    PENDING = "pending", "Pending"
    APPROVED = "approved", "Approved"
    REJECTED = "rejected", "Rejected"

class Seller(models.Model):
    name = models.CharField(max_length=100)
    balance=models.DecimalField(max_digits=15, decimal_places=2, default=Decimal('0.00'),validators=[MinValueValidator(Decimal('0.00'))])
    created_at=models.DateTimeField(auto_now_add=True)



    class Meta:
        db_table="seller"
        indexes=[models.Index(fields=['name'])]

        constraints=[models.CheckConstraint(check=models.Q(balance__gte=0), name='check_balance_positive')
        ]


    def __str__(self):
        return f"seller: {self.id}: {self.name}"

class CreditRequest(models.Model):
    seller=models.ForeignKey(Seller, on_delete=models.CASCADE,related_name='credit_requests',db_index=True)
    amount=models.DecimalField(max_digits=15, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    status=model.CharField(max_length=20,choices=CreditRequestStatus.choices,default=CreditRequestStatus.PENDING,db_index=True)
    created_at=models.DateTimeField(auto_now_add=True)
    approved_at=models.DateTimeField(null=True,blank=True)


    class Meta:
        db_table="credit_requests"
        indexs=[
            models.Index(fields=['seller',status])
        ]

    def __str__(self):
        return f"credit request {self.id}:{self.seller.id} - {self.amount} ({self.status})"


    