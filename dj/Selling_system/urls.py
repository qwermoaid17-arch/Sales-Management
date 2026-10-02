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
    # مسارات الواجهة (Web UI)
    path('login/', login_view, name='login'),
    path('logout/', logout_view, name='logout'),
    path('dashboard/', dashboard_view, name='dashboard'),
    path('products-page/', products_page, name='products_page'),
    path('customers-page/', customers_page, name='customers_page'),
    path('sales-page/', sales_page, name='sales_page'),
    path('payments-page/', payments_page, name='payments_page'),
    path('register/', register_view, name='register'),

    # مسارات الـ REST API
    path('', include(router.urls)),
]