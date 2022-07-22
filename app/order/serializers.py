from rest_framework import serializers

from django.utils.translation import gettext_lazy as _

from decimal import Decimal

from core.models import Order, OrderMeal, OrderDrink, Menu


class OrderMealSerializer(serializers.ModelSerializer):
    """Meal serializer for order"""
    total_price = serializers.DecimalField(max_digits=5, decimal_places=2, source='get_total_meal_price', read_only=True)
    price = serializers.DecimalField(max_digits=5, decimal_places=2, source='meal.price', read_only=True)

    class Meta:
        model = OrderMeal
        fields = ('meal', 'quantity', 'price', 'total_price')


class OrderDetailMealSerializer(OrderMealSerializer):
    """Meal detail serializer"""
    meal = serializers.StringRelatedField()


class OrderDrinkSerializer(serializers.ModelSerializer):
    """Drink serializer for order"""
    total_price = serializers.DecimalField(max_digits=5, decimal_places=2, source='get_total_drink_price', read_only=True)
    price = serializers.DecimalField(max_digits=5, decimal_places=2, source='drink.price', read_only=True)

    class Meta:
        model = OrderDrink
        fields = ('drink', 'quantity', 'price', 'total_price')


class OrderDetailDrinkSerializer(OrderDrinkSerializer):
    """Meal detail serializer"""
    drink = serializers.StringRelatedField()


class OrderSerializer(serializers.ModelSerializer):
    """Order serializer"""

    total_price = serializers.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    restaurant = serializers.StringRelatedField()
    order_time = serializers.DateTimeField(format='%Y-%m-%d %H:%m')

    class Meta:
        model = Order
        fields = (
            'id',
            'total_price',
            'restaurant',
            'is_ordered',
            'delivery_address',
            'delivery_city',
            'delivery_phone',
            'order_time'
        )


class OrderDetailSerializer(OrderSerializer):
    """Order detail serializer"""
    meals = serializers.SerializerMethodField()
    drinks = serializers.SerializerMethodField()

    class Meta(OrderSerializer.Meta):
        fields = (
            'total_price',
            'restaurant',
            'meals',
            'drinks',
            'is_ordered',
            'delivery_address',
            'delivery_city',
            'delivery_phone',
            'order_time'
        )

    def get_meals(self, obj):
        meals = OrderMeal.objects.filter(order=obj)
        return OrderDetailMealSerializer(meals, many=True).data

    def get_drinks(self, obj):
        drinks = OrderDrink.objects.filter(order=obj)
        return OrderDetailDrinkSerializer(drinks, many=True).data


class OrderCreateSerializer(serializers.ModelSerializer):
    """Order create serializer"""
    meals = OrderMealSerializer(many=True, write_only=True)
    drinks = OrderDrinkSerializer(many=True, write_only=True)
    order_time = serializers.DateTimeField(format='%Y-%m-%d %H:%m', read_only=True)
    total_price = serializers.DecimalField(max_digits=5, decimal_places=2, read_only=True)

    class Meta:
        model = Order
        fields = (
            'id',
            'restaurant',
            'meals',
            'drinks',
            'delivery_city',
            'delivery_address',
            'delivery_country',
            'delivery_post_code',
            'delivery_phone',
            'total_price',
            'order_time'
        )

    def validate(self, attr):
        """Validate that meals and drinks come from right restaurant"""
        restaurant = attr.get('restaurant')
        meals = attr.get('meals')
        drinks = attr.get('drinks')

        calculated_meals = []
        calculated_drinks = []

        """Raise error for empty order"""
        if not meals:
            msg = _("Cannot order nothing")
            raise serializers.ValidationError({'meal': msg}, code='nothing')

        """Raise error for wrong meal and counting the number of the same meals"""
        for meal_data in meals:
            if not Menu.objects.filter(restaurant=restaurant, meals=meal_data['meal'].id).exists():
                msg = _("Some meal doesn't come from restaurant menu")
                raise serializers.ValidationError({'wrong meal': msg}, code='meal')

            if not calculated_meals:
                calculated_meals.append({'meal': meal_data['meal'], 'quantity': meal_data['quantity']})
                continue

            for meal in calculated_meals:
                if meal_data['meal'].id == meal['meal'].id:
                    meal['quantity'] += meal_data['quantity']
                    break
                else:
                    calculated_meals.append({'meal': meal_data['meal'], 'quantity': meal_data['quantity']})
                    break

        """Raise error for wrong drink and counting the number of the same drinks"""
        for drink_data in drinks:
            if not Menu.objects.filter(restaurant=restaurant, drinks=drink_data['drink'].id).exists():
                msg = _("Some drink doesn't come from restaurant menu")
                raise serializers.ValidationError({'wrong drink': msg}, code='drink')

            if not calculated_drinks:
                calculated_drinks.append({'drink': drink_data['drink'], 'quantity': drink_data['quantity']})
                continue

            for drink in calculated_drinks:
                if drink_data['drink'].id == drink['drink'].id:
                    drink['quantity'] += drink_data['quantity']
                    break
                else:
                    calculated_drinks.pop()
                    calculated_drinks.append({'drink': drink_data['drink'], 'quantity': drink_data['quantity']})
                    break

        attr['meals'] = calculated_meals
        attr['drinks'] = calculated_drinks

        return attr

    def create(self, validated_data):
        """Create meals and drink models for order"""
        meals = validated_data.pop('meals')
        drinks = validated_data.pop('drinks')
        order = Order.objects.create(**validated_data)
        total = Decimal(0)

        for meal_data in meals:
            OrderMeal.objects.create(order=order, **meal_data)

        for drink_data in drinks:
            OrderDrink.objects.create(order=order, **drink_data)

        meals = OrderMeal.objects.filter(order=order)
        drinks = OrderDrink.objects.filter(order=order)

        total += Decimal(sum([meal.get_total_meal_price for meal in meals]))
        total += Decimal(sum([drink.get_total_drink_price for drink in drinks]))

        order.total_price = total
        order.save()

        return order
