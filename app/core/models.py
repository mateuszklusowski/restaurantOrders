from django.db import models
from django.utils.text import slugify
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin
)

from decimal import Decimal


class UserManager(BaseUserManager):
    """Create and save a new user and superuser"""

    def create_user(self, email, password=None, **extra_fields):
        """Create and save a new user"""
        if not email:
            raise ValueError('User must have an email address')

        user = self.model(email=self.normalize_email(email), **extra_fields)
        user.set_password(password)
        user.save(using=self._db)

        return user

    def create_superuser(self, email, password):
        """Create and save a new superuser"""
        super_user = self.create_user(email, password)
        super_user.is_staff = True
        super_user.is_superuser = True
        super_user.save(using=self._db)

        return super_user


class User(AbstractBaseUser, PermissionsMixin):
    """Custom user that uses email instead of username"""
    email = models.EmailField(max_length=255, unique=True, blank=False)
    name = models.CharField(max_length=255, unique=True, blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    objects = UserManager()

    USERNAME_FIELD = 'email'


class Cuisine(models.Model):
    """Cuisine model"""
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name


class Restaurant(models.Model):
    """Restaurant model"""
    name = models.CharField(max_length=255, blank=False)
    slug = models.SlugField(max_length=255, blank=True)
    city = models.CharField(max_length=255, blank=False)
    country = models.CharField(max_length=255, blank=False)
    address = models.CharField(max_length=255, blank=False)
    post_code = models.CharField(max_length=7, blank=False)
    phone = models.CharField(max_length=255, blank=False)
    cuisine = models.ForeignKey(Cuisine, on_delete=models.CASCADE)
    delivery_price = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    avg_delivery_time = models.PositiveSmallIntegerField(blank=False)

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        self.slug = slugify(self.name)
        super().save(*args, **kwargs)


class Tag(models.Model):
    """Tag model"""
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Ingredient model"""
    name = models.CharField(max_length=255, blank=False)

    def __str__(self):
        return self.name


class Meal(models.Model):
    """Meal model"""
    name = models.CharField(max_length=255, blank=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False)
    ingredients = models.ManyToManyField(Ingredient)
    tag = models.ForeignKey(Tag, on_delete=models.CASCADE)

    def __str__(self):
        return self.name


class Drink(models.Model):
    """Drink model"""
    name = models.CharField(max_length=255, blank=False)
    price = models.DecimalField(max_digits=5, decimal_places=2, blank=False)

    def __str__(self):
        return self.name


class Menu(models.Model):
    """Menu model"""
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal)
    drinks = models.ManyToManyField(Drink)

    def __str__(self):
        return f'{self.restaurant.name} menu'


class Order(models.Model):
    """Order model"""
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    restaurant = models.ForeignKey(Restaurant, on_delete=models.CASCADE)
    meals = models.ManyToManyField(Meal)
    drinks = models.ManyToManyField(Drink)
    delivery_address = models.CharField(max_length=255, blank=False)
    delivery_city = models.CharField(max_length=255, blank=False)
    delivery_country = models.CharField(max_length=255, blank=False)
    delivery_post_code = models.CharField(max_length=7, blank=False)
    delivery_phone = models.CharField(max_length=255, blank=False)
    order_time = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Order: {self.user} - {self.id} from {self.restaurant}'

    @property
    def get_total_price(self):
        """Return total price of order"""
        total_price = Decimal(0)
        total_price += Decimal(self.restaurant.delivery_price)

        for meal in self.meals.all():
            total_price += Decimal(meal.price)
        for drink in self.drinks.all():
            total_price += Decimal(drink.price)

        return total_price
