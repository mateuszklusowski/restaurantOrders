from django.test import TestCase
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

from restaurant.serializers import RestaurantSerializer, RestaurantDetailSerializer

from core.models import Restaurant, Cuisine


RESTAURANTS_URL = reverse("restaurant:restaurant-list")


def sample_cuisine(cuisine_name):
    """Sample cuisine for testing"""
    return Cuisine.objects.create(name=cuisine_name)


def detail_url(restaurant_name):
    """Return restaurants detail URL"""
    return reverse('restaurant:restaurant-detail', args=[restaurant_name])


def sample_restaurant(name):
    return Restaurant.objects.create(
        name=name,
        city='Warsaw',
        country='Poland',
        address='Prosta 48',
        post_code='00-000',
        phone='phone number',
        cuisine=sample_cuisine('Indian'),
        delivery_price=7.50,
        avg_delivery_time=60
    )


class GetRestaurantListTest(TestCase):
    """Test get restaurant list"""

    def setUp(self):
        self.client = APIClient()

    def test_retrieve_restaurant_list(self):
        """Test retrieving restaurant list"""
        sample_restaurant(name='restaurant1')
        sample_restaurant(name='restaurant2')

        res = self.client.get(RESTAURANTS_URL)
        restaurants = Restaurant.objects.all().order_by('id')
        serializer = RestaurantSerializer(restaurants, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_view_restaurant_detail(self):
        """Test viewing a restaurant detail"""
        restaurant = sample_restaurant(name='restaurant2')

        url = detail_url(restaurant.id)

        res = self.client.get(url)
        serializer = RestaurantDetailSerializer(restaurant)
        self.assertEqual(res.data, serializer.data)

    def test_search_by_name(self):
        """Test restaurant filtering by name"""
        restaurant = sample_restaurant(name='Restaurant1')
        restaurant2 = sample_restaurant(name='Restaurant2')

        payload = {"name": "restaurant1"}

        res = self.client.get(RESTAURANTS_URL, payload)
        serializer = RestaurantSerializer(restaurant)
        serializer2 = RestaurantSerializer(restaurant2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_search_by_cuisine(self):
        """Test restaurant filtering by cuisine"""
        cuisine1 = sample_cuisine('Indian')
        cuisine2 = sample_cuisine('Italian')

        restaurant = sample_restaurant(name='restaurant1')
        restaurant.cuisine = cuisine1
        restaurant2 = sample_restaurant(name='restaurant2')
        restaurant2.cuisine = cuisine2

        payload = {'cuisine': 'indian'}
        res = self.client.get(RESTAURANTS_URL, payload)

        serializer = RestaurantSerializer(restaurant)
        serializer2 = RestaurantSerializer(restaurant2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_search_by_city(self):
        """Test restaurant filtering by cuisine"""
        restaurant = sample_restaurant(name='restaurant1')
        restaurant.city = 'Poznan'
        restaurant.save()
        restaurant2 = sample_restaurant(name='restaurant2')

        payload = {'city': 'poznan'}
        res = self.client.get(RESTAURANTS_URL, payload)

        serializer = RestaurantSerializer(restaurant)
        serializer2 = RestaurantSerializer(restaurant2)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn(serializer.data, res.data)
        self.assertNotIn(serializer2.data, res.data)