from django.db import models
from django.contrib.auth.models import User
from  django.conf import settings
from django.db.models import Sum
from decimal import Decimal

class Products(models.Model):

    name = models.CharField(max_length=100, unique=True)
    cost_price = models.DecimalField(max_digits=10, decimal_places=2)
    selling_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.PositiveIntegerField()

    def __str__(self):
        return self.name

class Customers(models.Model):

    name = models.CharField(max_length=100)

    def __str__(self):
        return self.name



    @property
    def total_debt(self):
        result = self.sales.filter(
            payment_type__iexact='debt'
        ).aggregate(
            total=Sum('items__total_price')
        )['total']
        
        return result if result is not None else Decimal('0.00')

    @property
    def total_paid(self):
        result = self.payments.aggregate(
            total=Sum('amount')
        )['total']
        
        return result if result is not None else Decimal('0.00')
    
    @property
    def total_remaining(self):

        g = self.total_debt - self.total_paid
        return g if g is not None else Decimal('0.00')
    
class Payments(models.Model):

    customer = models.ForeignKey(Customers, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    date = models.DateTimeField(auto_now_add=True)

class Sales(models.Model):

    x = (
        ('cash', 'Cash'),
        ('card', 'Card'),
        ('debt', 'Debt'),
        ('transfer', 'Transfer'),
    )

    customer = models.ForeignKey(Customers, on_delete=models.SET_NULL, null=True, blank=True, related_name='sales')
    payment_type = models.CharField(max_length=10, choices=x)
    status = models.BooleanField(default=True)
    date_created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return str(self.id)

    @property
    def big_total(self):
        result = self.items.aggregate(
            total=Sum('total_price')
        )['total']
        
        return result if result is not None else Decimal('0.00')

class SaleItems(models.Model):

    sale = models.ForeignKey(Sales, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Products, on_delete=models.SET_NULL, null=True, blank=True, related_name='saleitems')
    quantity = models.PositiveIntegerField()
    price_at_sale = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)



    def __str__(self):
        return str(self.id)
