from django.urls import path, include

from rest_framework.routers import DefaultRouter

from . import views

router = DefaultRouter()
router.register('', views.OrderViewSet)

app_name = 'order'

urlpatterns = [
    path('create/', views.OrderCreateView.as_view(), name='order-create'),
    path('', include(router.urls)),
]
