from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.RestaurantViewSet)

app_name = 'restaurant'

urlpatterns = [
    path('', include(router.urls)),
]
