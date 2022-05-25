from rest_framework import serializers

from core.models import Order, Meal
from restaurant.serializers import DrinkSerializer


class OrderMealSerializer(serializers.ModelSerializer):
    """Meal serializer for order"""
    tag = serializers.StringRelatedField()

    class Meta:
        model = Meal
        fields = ('name', 'tag', 'price')
        read_only_fields = ('name', 'tag', 'price')


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""

    total_price = serializers.DecimalField(max_digits=5, decimal_places=2, source='get_total_price')
    restaurant = serializers.StringRelatedField()
    order_time = serializers.DateTimeField(format='%Y-%m-%d %H:%m')

    class Meta:
        model = Order
        fields = ('id', 'restaurant', 'order_time', 'total_price')


class OrderDetailSerializer(OrderSerializer):
    """Order detail serializer"""
    meals = OrderMealSerializer(many=True, read_only=True)
    drinks = DrinkSerializer(many=True, read_only=True)
    user = serializers.StringRelatedField()

    class Meta(OrderSerializer.Meta):
        fields = '__all__'


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order create serializer"""
    class Meta:
        model = Order
        exclude = ('order_time',)