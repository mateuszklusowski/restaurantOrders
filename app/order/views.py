from rest_framework import generics
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import OrderSerializer, OrderDetailSerializer
from core.models import Order


class OrderListView(generics.ListAPIView):
    """Order list view"""
    serializer_class = OrderSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return order for logged user"""
        return Order.objects.filter(user=self.request.user)

    
class OrderDetailView(generics.RetrieveAPIView):
    """Order detail view"""
    serializer_class = OrderDetailSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_queryset(self):
        """Return order for logged user"""
        return Order.objects.filter(user=self.request.user)
