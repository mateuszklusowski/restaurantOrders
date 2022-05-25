from django.urls import path
from . import views

app_name = 'order'

urlpatterns = [
    path('', views.OrderListView.as_view(), name='order-list'),
    path('order-detail/<int:pk>', views.OrderDetailView.as_view(), name='order-detail'),
]
