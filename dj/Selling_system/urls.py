from django.urls import path, include
# from rest_framework.routers import DefaultRouter
from rest_framework_nested import routers
from .views import *

router = routers.DefaultRouter()

router.register('products', Products_View_Set)
router.register('customers', Customers_View_Set)
router.register('payments', Payments_View_Set)
router.register('sales', Sales_View_Set)
router.register('saleitems', SaleItems_View_Set)
router.register('statistics', Statistics_View_Set, basename='statistics')

urlpatterns = [
    path('', include(router.urls)),
]
