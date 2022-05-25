from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from order import serializers as order_serializers
from core.models import Order, Tag, Meal, Drink, Ingredient, Restaurant, Cuisine

ORDERS_URL = reverse('order:order-list')


def detail_url(order_id):
    return reverse('order:order-detail', args=[order_id])


def create_user(**params):
    return get_user_model().objects.create_user(**params)


def sample_restaurant(restaurant_name):
    """Sample restaurant for testing"""
    return Restaurant.objects.create(
        name=restaurant_name,
        city='Warsaw',
        country='Poland',
        address='Prosta 48',
        post_code='00-000',
        phone='phone number',
        cuisine=Cuisine.objects.create(name='Vegan'),
        delivery_price=12.00,
        avg_delivery_time=60
    )


def sample_ingredient(ingredient_name):
    """Sample ingredient for testing"""
    return Ingredient.objects.create(name=ingredient_name)


def sample_tag(tag_name):
    """Sample tag for testing"""
    return Tag.objects.create(name=tag_name)


def sample_meal(**params):
    """Sample meal for testing"""
    default = {
        'price': 10.00,
        'tag': sample_tag('Vegan'),
    }
    default.update(**params)
    meal = Meal.objects.create(**default)
    meal.ingredients.set([sample_ingredient('Potatoes'), sample_ingredient('Tomatoes')])
    return meal


def sample_drink(**params):
    """Sample drink for testing"""
    default = {'price': 2.50}
    default.update(**params)
    return Drink.objects.create(**default)


def sample_order(**params):
    """Sample order for testing"""
    default = {
        'restaurant': sample_restaurant('restaurant1'),
        'order_time': '2019-01-01 00:00:00',
        'delivery_address': 'some address',
        'delivery_city': 'some city',
        'delivery_post_code': 'some post code',
        'delivery_phone': 'some phone',
        'delivery_phone': 'some phone'
    }
    meals = params['meals']
    drinks = params['drinks']

    params.pop('drinks', None)
    params.pop('meals', None)
    default.update(**params)

    order = Order.objects.create(**default)
    order.meals.set(meals)
    order.drinks.set(drinks)

    return order


class PublicOrderApiTests(TestCase):
    """Test unauthenticated order API access"""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test that login is required"""
        res = self.client.get(ORDERS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateOrderApiTests(TestCase):
    """Test authenticated order API access"""

    def setUp(self):
        self.user = create_user(
            email='test@test.com',
            password='testpass',
            name='Test name'
        )

        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_retrieve_orders(self):
        """Test retrieving orders"""
        sample_order(
            user=self.user,
            meals=[sample_meal(name='meal1',), sample_meal(name='meal2')],
            drinks=[sample_drink(name='drink3'), sample_drink(name='drink4')]
        )
        sample_order(
            user=self.user,
            meals=[sample_meal(name='meal3', price=20.00), sample_meal(name='meal4')],
            drinks=[sample_drink(name='drink1'), sample_drink(name='drink2')]
        )

        res = self.client.get(ORDERS_URL)

        orders = Order.objects.all()
        serializer = order_serializers.OrderSerializer(orders, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_orders_limited_to_user(self):
        """Test retrieving orders for authenticated user"""
        user2 = create_user(
            email='other@user.com',
            password='testpass',
            name='Other name'
        )
        sample_order(
            user=user2,
            meals=[sample_meal(name='meal1'), sample_meal(name='meal2')],
            drinks=[sample_drink(name='drink1'), sample_drink(name='drink2')]
        )
        sample_order(
            user=self.user,
            meals=[sample_meal(name='meal3', price=20.00), sample_meal(name='meal4')],
            drinks=[sample_drink(name='drink1'), sample_drink(name='drink2')]
        )

        res = self.client.get(ORDERS_URL)

        orders = Order.objects.filter(user=self.user)
        serializer = order_serializers.OrderSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)