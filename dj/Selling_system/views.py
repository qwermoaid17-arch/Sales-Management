from django.shortcuts import render, get_object_or_404 
from rest_framework.decorators import api_view, action
from rest_framework.response import Response
from rest_framework.status import HTTP_204_NO_CONTENT, HTTP_201_CREATED, HTTP_200_OK, HTTP_400_BAD_REQUEST
from rest_framework.views import APIView
from rest_framework.generics import ListCreateAPIView, RetrieveUpdateDestroyAPIView
from rest_framework.viewsets import ModelViewSet, GenericViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, DestroyModelMixin
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from rest_framework.pagination import PageNumberPagination
from .serializers import *
from .serializers import SaleItem_Serializer
from .models import *
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticated, IsAdminUser
from rest_framework.exceptions import ValidationError, MethodNotAllowed
from django.db import transaction
from rest_framework import viewsets
from django.utils import timezone
from datetime import timedelta
from django.db.models import Sum, F, Count
import json
from django.db.models.functions import ExtractHour, ExtractWeekDay
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib.auth import login, logout, authenticate
from django.contrib import messages
from .models import Products, Customers, Sales, Payments
from django.http import JsonResponse
from django.contrib.auth import authenticate, login
from django.views.decorators.csrf import csrf_exempt
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User

class pageNumberPagination(PageNumberPagination):
    def get_page_size(self, request):
        return request.query_params.get('page_size', 1)
class Products_View_Set(ModelViewSet):

    queryset = Products.objects.all()
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):

        user = self.request.user
        if user.is_staff:
            return Product_admin_Serializer
        return Product_Serializer

class Customers_View_Set(ModelViewSet):

    queryset = Customers.objects.all()
    serializer_class = Customer_Serializer
    permission_classes = [IsAuthenticated]

    def get_view_name(self):
        return "Customer"

class Payments_View_Set(ModelViewSet):

    queryset = Payments.objects.all()
    serializer_class = Payment_Serializer
    permission_classes = [IsAuthenticated]


class Sales_View_Set(ModelViewSet):

    queryset = Sales.objects.all()
    serializer_class = Sale_Serializer
    permission_classes = [IsAuthenticated]
    pagination_class = pageNumberPagination

    def destroy(self, request, *args, **kwargs):
        # الحذف المباشر يتجاوز إرجاع المخزون وفحص الديون، فالإلغاء يتم فقط عبر /cancel/
        raise MethodNotAllowed('DELETE', detail='لا يمكن حذف الفاتورة مباشرة، استخدم إلغاء الفاتورة.')

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_sales(self, request, pk=None):
        sale = self.get_object()
        cancel_type = request.data.get('cancel_type')

        if cancel_type not in ['canceled', 'DAMAGED']:
            raise ValidationError({'cancel_type': 'Invalid cancel type'})

        with transaction.atomic():

            # منع الإلغاء إذا كان العميل قد سدد أكثر من الدين الذي سيبقى بعد الإلغاء
            if sale.payment_type == 'debt' and sale.customer:
                customer = sale.customer
                debt_after = customer.total_debt - sale.big_total
                if customer.total_paid > debt_after:
                    raise ValidationError({
                        'detail': (
                            f'لا يمكن إلغاء الفاتورة: العميل سدد {customer.total_paid}$ '
                            f'والدين بعد الإلغاء سيصبح {debt_after}$. '
                            'عالج الدفعات الزائدة أولاً.'
                        )
                    })

            if cancel_type == 'canceled':
                for item in sale.items.all():
                    if item.product_id:   # المنتج قد يكون محذوفاً (SET_NULL)
                        Products.objects.filter(pk=item.product_id).update(
                            quantity=F('quantity') + item.quantity
                        )

            sale.delete()

        return Response({'message': 'Sale canceled successfully'}, status=HTTP_200_OK)

class SaleItems_View_Set(ModelViewSet):

    queryset = SaleItems.objects.all()
    serializer_class = SaleItem_Serializer
    permission_classes = [IsAuthenticated]

class Statistics_View_Set(viewsets.ViewSet):

    permission_classes = [IsAuthenticated]

    def list(self, request):
        data = {
            'total_products': Products.objects.count(),
            'total_customers': Customers.objects.count(),
        }

        # الأرقام المالية للمسؤول فقط
        if request.user.is_staff:
            today = timezone.now().date()
            data['total_remaining_debts'] = float(sum(c.total_remaining for c in Customers.objects.all()))
            data['today_sales'] = float(sum(
                s.big_total for s in Sales.objects.filter(date_created__date=today, status=True)
            ))
            data['endpoints'] = {
                'earnings': 'http://127.0.0.1:8000/selling_system/statistics/earnings_statistics/',
                'sales': 'http://127.0.0.1:8000/selling_system/statistics/sales_statistics/',
                'products': 'http://127.0.0.1:8000/selling_system/statistics/products_statistics/',
                'debt': 'http://127.0.0.1:8000/selling_system/statistics/debt_statistics/',
                'peak_times': 'http://127.0.0.1:8000/selling_system/statistics/peak_times_statistics/',
            }

        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='earnings_statistics', permission_classes=[IsAdminUser])
    def earnings_statistics(self, request):

        all_total = Sales.objects.exclude(status=False).all()

        all_total_earnings = sum(sale.big_total for sale in all_total )

        a = SaleItems.objects.filter(sale__status=True).aggregate(
        profit=Sum(F('total_price') - (F('quantity') * F('product__cost_price')))
        )['profit'] or 0.00


        today = timezone.now().date()

        today_total = Sales.objects.filter(date_created__date=today, status=True).all()

        today_total_earnings = sum(sale.big_total for sale in today_total)

        b = SaleItems.objects.filter(sale__date_created__date=today, sale__status=True).aggregate(
        profit=Sum(F('total_price') - (F('quantity') * F('product__cost_price')))
        )['profit'] or 0.00


        week = timezone.now().date() - timedelta(days=7)

        week_total = Sales.objects.filter(date_created__date__gte=week, status=True).all()

        week_total_earnings = sum(sale.big_total for sale in week_total)

        c = SaleItems.objects.filter(sale__date_created__date__gte=week, sale__status=True).aggregate(
        profit=Sum(F('total_price') - (F('quantity') * F('product__cost_price')))
        )['profit'] or 0.00


        month = timezone.now().date() - timedelta(days=30)

        month_total = Sales.objects.filter(date_created__gte=month, status=True).all()

        month_total_earnings = sum(sale.big_total for sale in month_total)

        d = SaleItems.objects.filter(sale__date_created__date__gte=month, sale__status=True).aggregate(
        profit=Sum(F('total_price') - (F('quantity') * F('product__cost_price')))
        )['profit'] or 0.00


        year = timezone.now().date() - timedelta(days=365)

        year_total = Sales.objects.filter(date_created__gte=year, status=True).all()

        year_total_earnings = sum(sale.big_total for sale in year_total)

        e = SaleItems.objects.filter(sale__date_created__date__gte=year, sale__status=True).aggregate(
        profit=Sum(F('total_price') - (F('quantity') * F('product__cost_price')))
        )['profit'] or 0.00


        data = {
            'all_time' : {'total_earnings': all_total_earnings,
            'Total net profit': a},
            'today' : {'total_earnings': today_total_earnings,
            'Total net profit today': b},
            'week' :{'total_earnings': week_total_earnings,
            'Total net profit this week': c},
            'month' :{'total_earnings': month_total_earnings,
            'Total net profit this month': d},
            'year' :{'total_earnings': year_total_earnings,
            'Total net profit this year': e}
        }

        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='sales_statistics')
    def Sales_statistics(self, request):

        top_sales = Products.objects.filter(saleitems__sale__status=True).annotate(total_quantity=Sum('saleitems__quantity')).order_by('-total_quantity')[:5]

        data = [{
            'id': n.id,
            'name': n.name,
            'quantity': n.total_quantity
        } for n in top_sales]
            
        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='debt_statistics', permission_classes=[IsAdminUser])
    def debt_statistics(self, request):

        custom = list(Customers.objects.all())

        total_debt = sum(customer.total_remaining for customer in custom)

        top_debt = sorted([customer for customer in custom if customer.total_remaining and customer.total_remaining > 0], key=lambda x: x.total_remaining, reverse=True)[:5]

        data = {
            'total_debt': total_debt,
            'top_debt': [{
                'id': c.id,
                'name': c.name,
                'total_remaining': c.total_remaining
            } for c in top_debt]
        }

        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='products_statistics')
    def products_statistics(self, request):

        top_products = Products.objects.filter(quantity__lte=10).order_by('quantity')[:5]

        data = [{
            'id': n.id,
            'name': n.name,
            'quantity': n.quantity
        } for n in top_products]
            
        return Response(data, status=HTTP_200_OK)

    @action(detail=False, methods=['get'], url_path='peak_times_statistics')
    def Peak_times_statistics(self, request):

        best_hour = Sales.objects.filter(status=True).annotate(hour=ExtractHour('date_created')).values('hour').annotate(total_orders=Count('id')).order_by('-total_orders')[:1]

        best_day = Sales.objects.filter(status=True).annotate(day=ExtractWeekDay('date_created')).values('day').annotate(total_orders=Count('id')).order_by('-total_orders')[:1]

        week_day = {
            1: 'Sunday',
            2: 'Monday',
            3: 'Tuesday',
            4: 'Wednesday',
            5: 'Thursday',
            6: 'Friday',
            7: 'Saturday'
        }

        data = {
            'peak_hour': [{
                'hour':f"{item['hour']:02d}:00",
                'total_orders': item['total_orders']
                }
                          for item in best_hour],
            'peak_day': [{
                'day': week_day.get(item['day']),
                'total_orders': item['total_orders']
                }
                          for item in best_day]
        }

        return Response(data, status=HTTP_200_OK)
    


def login_view(request):
    if request.method == 'POST':
        # قراءة البيانات سواء كانت مرسلة كـ JSON من Fetch أو Form عادي
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')

        user = authenticate(request, username=username, password=password)

        if user is not None:
            # 1. إنشاء Session في المتصفح لفتح صفحات الواجهات
            login(request, user)

            # 2. توليد توكنات JWT للـ API
            refresh = RefreshToken.for_user(user)

            # تحديد رابط التوجيه المطلوب
            redirect_url = request.GET.get('next') or '/selling_system/dashboard/'

            if request.content_type == 'application/json':
                return JsonResponse({
                    'success': True,
                    'access': str(refresh.access_token),
                    'refresh': str(refresh),
                    'redirect_url': redirect_url
                })
            return redirect(redirect_url)

        else:
            if request.content_type == 'application/json':
                return JsonResponse({'detail': 'اسم المستخدم أو كلمة المرور غير صحيحة'}, status=400)
            return render(request, 'login.html', {'error': 'اسم المستخدم أو كلمة المرور غير صحيحة'})

    return render(request, 'login.html')

@login_required
def dashboard_view(request):
    return render(request, 'dashboard.html')

def logout_view(request):
    logout(request)
    return redirect('login')

@login_required
def products_page(request):
    return render(request, 'products.html')

@login_required
def customers_page(request):
    return render(request, 'customers.html')

@login_required
def sales_page(request):
    return render(request, 'sales.html')

@login_required
def payments_page(request):
    return render(request, 'payments.html')

@csrf_exempt
def register_view(request):
    if request.method == 'POST':
        if request.content_type == 'application/json':
            data = json.loads(request.body)
            username = data.get('username')
            password = data.get('password')
            email = data.get('email', '')
        else:
            username = request.POST.get('username')
            password = request.POST.get('password')
            email = request.POST.get('email', '')

        if User.objects.filter(username=username).exists():
            msg = 'اسم المستخدم مُستخدم بالفعل، يرجى اختيار اسم آخر'
            if request.content_type == 'application/json':
                return JsonResponse({'detail': msg}, status=400)
            return render(request, 'register.html', {'error': msg})

        # إنشاء المستخدم الجديد
        user = User.objects.create_user(username=username, password=password, email=email)
        
        # تسجيل الدخول تلقائياً (Session + JWT)
        login(request, user)
        refresh = RefreshToken.for_user(user)

        if request.content_type == 'application/json':
            return JsonResponse({
                'success': True,
                'access': str(refresh.access_token),
                'refresh': str(refresh),
                'redirect_url': '/selling_system/dashboard/'
            })
        return redirect('dashboard')

    return render(request, 'register.html')