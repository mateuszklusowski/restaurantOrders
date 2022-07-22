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

        for key in params.keys():
            if key == 'password':
                self.assertTrue(user.check_password(params['password']))
                continue
            self.assertEqual(params[key], getattr(user, key))

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

        for key in params.keys():
            self.assertEqual(params[key], getattr(restaurant, key))

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

        for key in params.keys():
            self.assertEqual(params[key], getattr(meal, key))

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

        for key in params.keys():
            self.assertEqual(params[key], getattr(drink, key))

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

        for key in params.keys():
            if key == 'order_time':
                continue
            self.assertEqual(params[key], getattr(order, key))

        self.assertEqual(order.order_time.day, params['order_time'].day)
        self.assertEqual(order.order_time.hour, params['order_time'].hour)
        self.assertEqual(order.order_time.minute, params['order_time'].minute)

    def test_order_meal_model(self):
        """Test order meal model"""
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

        order_params = {
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
        order = models.Order.objects.create(**order_params)

        meal = sample_meal(name='test meal', price=1.00, tag=sample_tag('tag'))
        order_meal = models.OrderMeal.objects.create(
            order=order,
            meal=meal,
            quantity=2
        )

        self.assertEqual(order_meal.order, order)
        self.assertEqual(order_meal.meal, meal)
        self.assertEqual(order_meal.quantity, 2)

    def test_order_drink_model(self):
        """Test order drink model"""
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

        order_params = {
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
        order = models.Order.objects.create(**order_params)

        drink = sample_drink(name='test drink', price=1.00, tag=sample_tag('tag'))
        order_drink = models.OrderDrink.objects.create(
            order=order,
            drink=drink,
            quantity=2
        )

        self.assertEqual(order_drink.order, order)
        self.assertEqual(order_drink.drink, drink)
        self.assertEqual(order_drink.quantity, 2)
