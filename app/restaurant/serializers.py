from rest_framework import serializers

from core.models import Restaurant, Menu, Meal, Drink, Ingredient


class DrinkSerializer(serializers.ModelSerializer):
    """Drink serializer"""

    class Meta:
        model = Drink
        fields = ('name', 'price')
        read_only_fields = ('name', 'price')


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""

    class Meta:
        model = Ingredient
        fields = ('name',)
        read_only_fields = ('name',)


class MealSerializer(serializers.ModelSerializer):
    """Meal serializer"""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tag = serializers.StringRelatedField()

    class Meta:
        model = Meal
        fields = ('name', 'tag', 'ingredients', 'price')
        read_only_fields = ('name', 'ingredients', 'price')


class MenuSerializer(serializers.ModelSerializer):
    """Menu serializer"""
    drinks = DrinkSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ('meals', 'drinks')
        read_only_fields = ('restaurant', 'meals', 'drinks')


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for restaurant model"""
    cuisine = serializers.StringRelatedField()

    class Meta:
        model = Restaurant
        fields = ('id', 'name', 'cuisine', 'city',
                  'address', 'phone', 'delivery_price',
                  'avg_delivery_time'
                  )
        read_only_fields = ('id',)


class RestaurantDetailSerializer(RestaurantSerializer):
    """Serializer for restaurant detail"""
    menu = serializers.SerializerMethodField()

    class Meta(RestaurantSerializer.Meta):
        fields = ('name', 'city', 'country', 'address',
                  'post_code', 'phone', 'cuisine', 'menu',
                  'delivery_price', 'avg_delivery_time',
                  )

    def get_menu(self, obj):
        menu = Menu.objects.filter(restaurant=obj)
        return MenuSerializer(menu, many=True).data
