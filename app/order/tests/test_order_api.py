from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from order import serializers as order_serializers
from core.models import (Order,
                         Tag,
                         Meal,
                         Drink,
                         Ingredient,
                         Restaurant,
                         Cuisine,
                         OrderDrink,
                         OrderMeal,
                         Menu)


ORDERS_URL = reverse('order:order-list')
ORDER_CREATE_URL = reverse('order:order-create')


def detail_url(order_id):
    """Return order detail url"""
    return reverse('order:order-detail', args=[order_id])


def create_user(**params):
    """Sample user for testing"""
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
    default = {'price': 2.50, 'tag': sample_tag('water')}
    default.update(**params)
    return Drink.objects.create(**default)


def sample_order(**params):
    """Sample order for testing"""
    default = {
        'restaurant': sample_restaurant('restaurant1'),
        'order_time': '2019-01-01 00:00:00',
        'delivery_address': 'some address',
        'delivery_city': 'some city',
        'delivery_post_code': '01-100',
        'delivery_phone': 'some phone',
        'delivery_phone': 'some phone'
    }
    default.update(**params)

    return Order.objects.create(**default)


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
        sample_order(user=self.user)
        sample_order(user=self.user)

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
        sample_order(user=self.user)
        sample_order(user=user2)

        res = self.client.get(ORDERS_URL)

        orders = Order.objects.filter(user=self.user)
        serializer = order_serializers.OrderSerializer(orders, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)

    def test_retrieve_detail_order(self):
        """Test retrieving detail order"""
        order = sample_order(user=self.user, restaurant=sample_restaurant('rest2'))
        order2 = sample_order(user=self.user)

        url = detail_url(order.id)
        res = self.client.get(url)

        serializer1 = order_serializers.OrderDetailSerializer(order)
        serializer2 = order_serializers.OrderDetailSerializer(order2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer1.data)
        self.assertNotEqual(res.data, serializer2.data)

    def test_create_order(self):
        """Test create an order"""

        restaurant = sample_restaurant('restaurant1')
        meal1 = sample_meal(name="meal1")
        meal2 = sample_meal(name="meal2")
        drink1 = sample_drink(name="drink1")
        drink2 = sample_drink(name="drink2")

        menu = Menu.objects.create(restaurant=restaurant)
        menu.meals.set([meal1, meal2])
        menu.drinks.set([drink1, drink2])

        payload = {
            "restaurant": restaurant.id,
            "meals": [
                {"meal": meal1.id, "quantity": 10},
                {"meal": meal2.id, "quantity": 10}
            ],
            "drinks": [
                {"drink": drink1.id, "quantity": 10},
                {"drink": drink2.id, "quantity": 10}
            ],
            "delivery_city": "some city",
            "delivery_address": "some address",
            "delivery_country": "some country",
            "delivery_post_code": "01-223",
            "delivery_phone": "some phone"
        }

        res = self.client.post(ORDER_CREATE_URL, payload, format='json')

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        order = Order.objects.get(id=res.data['id'])

        bad_assertion_keys = ['restaurant', 'meals', 'drinks']

        for key in payload.keys():
            if key in bad_assertion_keys:
                continue
            self.assertEqual(payload[key], getattr(order, key))

        self.assertEqual(payload['restaurant'], order.restaurant.id)

        for meal in payload['meals']:
            order_meal = OrderMeal.objects.get(id=meal['meal'])
            self.assertEqual(order_meal.order.id, order.id)

        for drink in payload['drinks']:
            order_drink = OrderDrink.objects.get(id=drink['drink'])
            self.assertEqual(order_drink.order.id, order.id)
