from django.contrib import admin
from .models import Products, Customers, Payments, Sales, SaleItems


admin.site.register(Products)
admin.site.register(Customers)
admin.site.register(Payments)
admin.site.register(Sales)
admin.site.register(SaleItems)
