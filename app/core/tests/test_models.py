from django.test import TestCase
from django.contrib.auth import get_user_model

import datetime

from core import models


def sample_tag(tag_name):
    """Sample tag for testing"""
    return models.Tag.objects.create(name=tag_name)


def sample_restaurant(**params):
    """Sample restaurant for testing"""
    return models.Restaurant.objects.create(**params)


def sample_ingredient(ingredient_name):
    """Sample ingredient for testing"""
    return models.Ingredient.objects.create(name=ingredient_name)


def sample_cuisine(cuisine_name):
    """Sample cuisine for testing"""
    return models.Cuisine.objects.create(name=cuisine_name)


def sample_user(**params):
    """Sample user for testing"""
    return get_user_model().objects.create_user(**params)


def sample_meal(**params):
    """Sample meal for testing"""
    return models.Meal.objects.create(**params)


def sample_drink(**params):
    return models.Drink.objects.create(**params)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        params = {
            'email': 'test@test.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**params)

        self.assertEqual(user.name, params['name'])
        self.assertEqual(user.email, params['email'])
        self.assertTrue(user.check_password(params['password']))

    def test_normalized_email(self):
        """Test the email for a new user is normalized"""
        params = {
            'email': 'test@TEST.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**params)

        self.assertEqual(user.email, params['email'].lower())

    def test_invalid_email(self):
        """Test creating user with invalid email"""
        with self.assertRaises(ValueError):
            sample_user(email=None, password='testpassword')

    def test_create_superuser(self):
        """Test creating a new superuser"""
        super_user = get_user_model().objects.create_superuser(
            'test@test.com',
            'testpassword'
        )

        self.assertTrue(super_user.is_staff)
        self.assertTrue(super_user.is_superuser)

    def test_cuisine_model(self):
        """Test cuisine model"""
        name = 'Indian'
        cuisine = sample_cuisine(name)

        self.assertEqual(str(cuisine), name)

    def test_restaurant_model(self):
        """Test restaurant model"""
        params = {
            'name': 'Test name',
            'city': 'Warsaw',
            'country': 'Poland',
            'address': 'tes_address',
            'post_code': '11-111',
            'phone': 'test phone',
            'cuisine': sample_cuisine('Indian'),
            'delivery_price': 7.50,
            'avg_delivery_time': 60
        }
        restaurant = sample_restaurant(**params)

        self.assertEqual(str(restaurant), params['name'])
        self.assertEqual(restaurant.city, params['city'])
        self.assertEqual(restaurant.country, params['country'])
        self.assertEqual(restaurant.address, params['address'])
        self.assertEqual(restaurant.post_code, params['post_code'])
        self.assertEqual(restaurant.phone, params['phone'])
        self.assertEqual(restaurant.cuisine, params['cuisine'])
        self.assertEqual(restaurant.delivery_price, params['delivery_price'])
        self.assertEqual(restaurant.avg_delivery_time, params['avg_delivery_time'])

    def test_tag_model(self):
        """Test tag model"""
        name = 'Water'
        tag = sample_tag(name)

        self.assertEqual(str(tag), name)

    def test_ingredient_model(self):
        """Test ingredient model"""
        name = 'Test ingredient name'
        ingredient = sample_ingredient(name)

        self.assertEqual(str(ingredient), name)

    def test_meal_model(self):
        """Test meal model"""
        params = {
            'name': 'Test meal name',
            'price': 5.50,
            'tag': sample_tag('test meal tag')
        }
        ingredients = [sample_ingredient(f'ingredient{i}') for i in range(3)]

        meal = models.Meal.objects.create(**params)
        meal.ingredients.set(ingredients)

        self.assertEqual(str(meal), params['name'])
        self.assertEqual(meal.tag, params['tag'])
        self.assertEqual(meal.price, params['price'])
        for ingredient in ingredients:
            self.assertIn(ingredient, meal.ingredients.all())

    def test_drink_model(self):
        """Test drink model"""
        params = {
            'name': 'Coca-cola',
            'price': 3.50,
            'tag': sample_tag('fizzy drink')
        }
        drink = sample_drink(**params)

        self.assertEqual(str(drink), params['name'])
        self.assertEqual(drink.price, params['price'])
        self.assertEqual(drink.tag, params['tag'])

    def test_menu_model(self):
        """Test menu model"""
        restaurant_params = {
            'name': 'Test name',
            'city': 'Warsaw',
            'country': 'Poland',
            'address': 'tes_address',
            'post_code': '11-111',
            'phone': 'test phone',
            'cuisine': sample_cuisine('Indian'),
            'delivery_price': 7.50,
            'avg_delivery_time': 60
        }
        restaurant = sample_restaurant(**restaurant_params)

        ingredients = [sample_ingredient(f'ingredient{i}') for i in range(3)]
        meals = [
            sample_meal(
                name=f'test meal {i}',
                price=4.50,
                tag=sample_tag('meal tag')
            )
            for i in range(3)
        ]
        for meal in meals:
            meal.ingredients.set(ingredients)

        drinks = [
            sample_drink(
                name=f'test drink{i}',
                price=3.40,
                tag=sample_tag('Water')
            )
            for i in range(3)
        ]

        menu = models.Menu.objects.create(restaurant=restaurant)
        menu.meals.set(meals)
        menu.drinks.set(drinks)

        self.assertEqual(str(menu), f'{restaurant.name} menu')
        for meal in meals:
            self.assertIn(meal, menu.meals.all())
        for drink in drinks:
            self.assertIn(drink, menu.drinks.all())

    def test_order_model(self):
        """Test order model"""
        user_params = {
            'email': 'test@test.com',
            'name': 'test',
            'password': 'testpassword'
        }
        user = sample_user(**user_params)

        restaurant_params = {
            'name': 'Test name',
            'city': 'Warsaw',
            'country': 'Poland',
            'address': 'tes_address',
            'post_code': '11-111',
            'phone': 'test phone',
            'cuisine': sample_cuisine('Indian'),
            'delivery_price': 7.50,
            'avg_delivery_time': 60
        }
        restaurant = sample_restaurant(**restaurant_params)

        params = {
            'user': user,
            'restaurant': restaurant,
            'is_ordered': False,
            'delivery_address': 'test address',
            'delivery_city': 'Warsaw',
            'delivery_country': 'Poland',
            'delivery_post_code': '11-111',
            'delivery_phone': 'test phone',
            'order_time': datetime.datetime.now()
        }
        order = models.Order.objects.create(**params)

        self.assertEqual(order.user, params['user'])
        self.assertEqual(order.restaurant, params['restaurant'])
        self.assertEqual(order.is_ordered, params['is_ordered'])
        self.assertEqual(order.delivery_address, params['delivery_address'])
        self.assertEqual(order.delivery_country, params['delivery_country'])
        self.assertEqual(order.delivery_city, params['delivery_city'])
        self.assertEqual(order.delivery_phone, params['delivery_phone'])
        self.assertEqual(order.delivery_post_code, params['delivery_post_code'])
        self.assertEqual(order.order_time.day, params['order_time'].day)
        self.assertEqual(order.order_time.hour, params['order_time'].hour)
        self.assertEqual(order.order_time.minute, params['order_time'].minute)
