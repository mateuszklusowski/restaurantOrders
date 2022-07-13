from rest_framework import serializers

from core.models import Restaurant, Menu, Meal, Drink, Ingredient


class DrinkSerializer(serializers.ModelSerializer):
    """Drink serializer"""

    class Meta:
        model = Drink
        fields = ('id', 'name', 'price')


class IngredientSerializer(serializers.ModelSerializer):
    """Ingredient serializer"""

    class Meta:
        model = Ingredient
        fields = ('name',)


class MealSerializer(serializers.ModelSerializer):
    """Meal serializer"""
    ingredients = serializers.SerializerMethodField()
    tag = serializers.StringRelatedField()

    class Meta:
        model = Meal
        fields = ('id', 'name', 'tag', 'ingredients', 'price')

    def get_ingredients(self, obj):
        return obj.ingredients.values_list('name', flat=True)


class MenuSerializer(serializers.ModelSerializer):
    """Menu serializer"""
    drinks = DrinkSerializer(many=True, read_only=True)
    meals = MealSerializer(many=True, read_only=True)

    class Meta:
        model = Menu
        fields = ('meals', 'drinks')


class RestaurantSerializer(serializers.ModelSerializer):
    """Serializer for restaurant model"""
    cuisine = serializers.StringRelatedField()

    class Meta:
        model = Restaurant
        fields = ('id', 'slug', 'name', 'cuisine', 'city',
                  'address', 'phone', 'delivery_price',
                  'avg_delivery_time'
                  )


class RestaurantDetailSerializer(RestaurantSerializer):
    """Serializer for restaurant detail"""
    menu = serializers.SerializerMethodField()

    class Meta(RestaurantSerializer.Meta):
        fields = ('id', 'name', 'city', 'country', 'address',
                  'post_code', 'phone', 'cuisine', 'menu',
                  'delivery_price', 'avg_delivery_time',
                  )
        lookup_field = 'slug'

    def get_menu(self, obj):
        menu = Menu.objects.get(restaurant=obj)
        return MenuSerializer(menu, many=True).data
