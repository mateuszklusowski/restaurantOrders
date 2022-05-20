from django.test import TestCase
from django.contrib.auth import get_user_model
from core import models


def sample_restaurant():
    return models.Restaurant.objects.create(
        name='test restaurant',
        city='Warsaw',
        country='Poland',
        address='Prosta 48',
        post_code='00-000',
        phone='phone number',
        cuisine=models.Cuisine.objects.create(name='cuisine'),
        delivery_price=7.50,
        avg_delivery_time=60
    )


def sample_user(email='test@test.com', password='testpassword'):
    return get_user_model().objects.create_user(email, password)


def sample_meal(name='Fish and chips', price=12.50, tag=None):
    return models.Meal.objects.create(name=name, price=price, tag=tag)


def sample_drink(name='coca-cola', price=3.50):
    return models.Drink.objects.create(name=name, price=price)


class ModelTests(TestCase):

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""
        email = 'test@test.com'
        name = 'test'
        password = 'testpassword'
        user = get_user_model().objects.create_user(
            email=email,
            name=name,
            password=password
        )

        self.assertEqual(user.name, name)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_normalized_email(self):
        """Test the email for a new user is normalized"""
        email = 'test@TEST.com'
        user = get_user_model().objects.create_user(
            email,
            'testpassword'
        )
        self.assertEqual(user.email, email.lower())

    def test_invalid_email(self):
        """Test creating user with invalid email"""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'testpassword')

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
        cuisine = models.Cuisine.objects.create(name=name)

        self.assertEqual(str(cuisine), name)

    def test_restaurant_model(self):
        """Test restaurant model"""
        name = 'test restaurant name'
        city = 'London'
        country = 'UK'
        address = 'test address'
        post_code = 'test post_code'
        phone = 'test phone'
        cuisine = models.Cuisine.objects.create(
            name='Japanese'
        )
        delivery_price = 7.50
        avg_delivery_time = 60
        restaurant = models.Restaurant.objects.create(
            name=name,
            city=city,
            country=country,
            address=address,
            post_code=post_code,
            phone=phone,
            cuisine=cuisine,
            delivery_price=delivery_price,
            avg_delivery_time=avg_delivery_time
        )

        self.assertEqual(str(restaurant), name)
        self.assertEqual(restaurant.city, city)
        self.assertEqual(restaurant.country, country)
        self.assertEqual(restaurant.address, address)
        self.assertEqual(restaurant.post_code, post_code)
        self.assertEqual(restaurant.phone, phone)
        self.assertEqual(restaurant.cuisine, cuisine)
        self.assertEqual(restaurant.delivery_price, delivery_price)
        self.assertEqual(restaurant.avg_delivery_time, avg_delivery_time)

    def test_tag_model(self):
        """Test tag model"""
        name = 'test tag name'
        tag = models.Tag.objects.create(
            name=name,
        )

        self.assertEqual(str(tag), name)

    def test_ingredient_model(self):
        """Test ingredient model"""
        name = 'test ingredient name'
        ingredient = models.Ingredient.objects.create(name=name)

        self.assertEqual(str(ingredient), name)

    def test_meal_model(self):
        """Test meal model"""
        name = 'test meal name'
        price = 32.50
        ingredient1 = models.Ingredient.objects.create(name='test ingredient1')
        ingredient2 = models.Ingredient.objects.create(name='test ingredient2')
        ingredient3 = models.Ingredient.objects.create(name='test ingredient3')
        ingredients = [ingredient1, ingredient2, ingredient3]
        tag = models.Tag.objects.create(name='test tag')
        meal = models.Meal.objects.create(
            name=name,
            price=price,
            tag=tag
        )
        meal.ingredients.set(ingredients)

        self.assertEqual(str(meal), name)
        self.assertIn(ingredient1, meal.ingredients.all())
        self.assertIn(ingredient2, meal.ingredients.all())
        self.assertIn(ingredient3, meal.ingredients.all())
        self.assertEqual(meal.tag, tag)
        self.assertEqual(meal.price, price)

    def test_drink_model(self):
        """Test drink model"""
        name = 'coca-cola'
        price = 2.50
        drink = models.Drink.objects.create(
            name=name,
            price=price
        )

        self.assertEqual(str(drink), name)
        self.assertEqual(drink.price, price)

    def test_menu_model(self):
        """Test menu model"""
        restaurant = sample_restaurant()
        tag = models.Tag.objects.create(name='test tag')
        ingredient1 = models.Ingredient.objects.create(name='Fish')
        ingredient2 = models.Ingredient.objects.create(name='Potatoes')

        drink1 = sample_drink('pepsi', 2.50)
        drink2 = sample_drink()

        meal1 = sample_meal(tag=tag)
        meal1.ingredients.set([ingredient1, ingredient2])
        meal2 = sample_meal(name='Fish', tag=tag)
        meal2.ingredients.set([ingredient1])

        menu = models.Menu.objects.create(restaurant=restaurant)
        menu.meals.set([meal1, meal2])
        menu.drinks.set([drink1, drink2])

        self.assertEqual(str(menu), f'{restaurant.name} menu')
        self.assertIn(ingredient1, menu.meals.all()[0].ingredients.all())
        self.assertIn(ingredient2, menu.meals.all()[0].ingredients.all())
        self.assertIn(ingredient1, menu.meals.all()[1].ingredients.all())
        self.assertIn(drink1, menu.drinks.all())

    def test_order_model(self):
        """Test order model"""
        user = sample_user()
        restaurant = sample_restaurant()
        tag = models.Tag.objects.create(name='test tag')
        ingredient1 = models.Ingredient.objects.create(name='Fish')
        ingredient2 = models.Ingredient.objects.create(name='Potatoes')

        drink1 = sample_drink('pepsi')
        drink2 = sample_drink()

        meal1 = sample_meal(tag=tag)
        meal1.ingredients.set([ingredient1, ingredient2])
        meal2 = sample_meal('Fish', tag=tag)
        meal2.ingredients.set([ingredient1])

        order = models.Order.objects.create(
            user=user,
            restaurant=restaurant,
        )
        order.meals.set([meal1, meal2])
        order.drinks.set([drink1, drink2])

        self.assertEqual(str(order), f'Order: {user} - {order.id} from {order.restaurant}')
        self.assertIn(meal1, order.meals.all())
        self.assertIn(meal2, order.meals.all())
        self.assertIn(drink1, order.drinks.all())
        self.assertIn(drink2, order.drinks.all())
        self.assertEqual(order.get_total_price, 32.00)
