from rest_framework import serializers
from .models import *
from django.db import transaction

class Product_admin_Serializer(serializers.ModelSerializer):

    class Meta:

        model = Products
        fields = ['id', 'name', 'cost_price', 'selling_price', 'quantity']
            

class Product_Serializer(serializers.ModelSerializer):

    class Meta:

        model = Products
        fields = ['id', 'name', 'selling_price', 'quantity']

class Customer_Serializer(serializers.ModelSerializer):

    total_debt = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_paid = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_remaining = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:

        model = Customers
        fields = ['id', 'name', 'total_debt', 'total_paid', 'total_remaining']

class Payment_Serializer(serializers.ModelSerializer):

    date = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)
    customer = serializers.SlugRelatedField(slug_field='name', queryset=Customers.objects.all(), required=False, allow_null=True)

    class Meta:

        model = Payments
        fields = ['id', 'customer', 'amount', 'date']

    def validate(self, attrs):
        customer = attrs.get('customer')
        amount = attrs.get('amount')

        if customer :
            remining_debt = customer.total_remaining

            if amount > remining_debt:
                raise serializers.ValidationError("Payment amount is greater than remaining debt.")

            if amount <= 0:
                raise serializers.ValidationError("Payment amount must be greater than zero.")

        return attrs

class SaleItem_Serializer(serializers.ModelSerializer):

    product = serializers.SlugRelatedField(slug_field='name', queryset=Products.objects.all())
    price_at_sale = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    total_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    sale = serializers.SlugRelatedField(slug_field='id', queryset=Sales.objects.all())

    class Meta:

        model = SaleItems
        fields = ['sale', 'id',  'product', 'quantity', 'price_at_sale', 'total_price']

    def create(self, validated_data):

        with transaction.atomic():

            product = validated_data['product']
            quantity = validated_data['quantity']

            if product.quantity < quantity: 
                raise serializers.ValidationError(f"Not enough quantity for product {product.name}. Available: {product.quantity}, Requested: {quantity}")
            if quantity <= 0:
                raise serializers.ValidationError(f"Quantity must be greater than zero for product {product.name}.")
            if Products.objects.filter(id=product.id).exists() == False:
                raise serializers.ValidationError(f"Product {product.name} does not exist.")
                

            product.quantity -= quantity           
            product.save()

            return SaleItems.objects.create(sale=validated_data['sale'], product=product, quantity=quantity, price_at_sale=product.selling_price, total_price=product.selling_price * quantity)
            

class Sale_Serializer(serializers.ModelSerializer):

    customer = serializers.SlugRelatedField(slug_field='name', queryset=Customers.objects.all(), required=False, allow_null=True)
    items = SaleItem_Serializer(many=True, read_only=True)
    status = serializers.SerializerMethodField()
    date_created = serializers.DateTimeField(format="%Y-%m-%d %H:%M:%S", read_only=True)

    def get_status(self, obj):
        if obj.payment_type != 'debt':

            return True

        elif obj.customer is not None:

            if obj.customer.total_remaining <= 0:

                return True

        else:

            return False
        
    class Meta:

        model = Sales
        fields = ['id', 'customer', 'payment_type', 'date_created', 'items', 'big_total', 'status']

    def validate(self, attrs):

        payment_type = attrs.get('payment_type')

        if payment_type == 'debt' and not attrs.get('customer'):
            raise serializers.ValidationError("Customer is required for debt payment type.")
        elif payment_type != 'debt' :
            attrs['customer'] = None

        return attrs

    def create(self, validated_data):

        items_data = validated_data.pop('items', [])
        sale = Sales.objects.create(**validated_data)

        for item_data in items_data:
            SaleItems.objects.create(sale=sale, product=item_data['product'], quantity=item_data['quantity'], price_at_sale=item_data['product'].selling_price, total_price=item_data['product'].selling_price * item_data['quantity'])

        return sale

class Cancel_Invoice_Serializer(serializers.ModelSerializer):

    Cancel_choice = (('canceled', 'Return to stock'),
                     ('DAMAGED', 'Damaged'))

    Choice_type = serializers.ChoiceField(choices=Cancel_choice)