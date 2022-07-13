from rest_framework import generics, viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from .serializers import (
                          OrderSerializer,
                          OrderCreateSerializer,
                          OrderDetailSerializer
                        )
from core.models import Order


class OrderViewSet(viewsets.GenericViewSet,
                   mixins.ListModelMixin,
                   mixins.RetrieveModelMixin):
    """Retrieve orders list"""
    serializer_class = OrderSerializer
    permission_classers = (IsAuthenticated,)
    queryset = Order.objects.all()
    lookup_field = 'id'

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return OrderDetailSerializer
        
        return self.serializer_class


class OrderCreateView(generics.CreateAPIView):
    """Order create view"""
    serializer_class = OrderCreateSerializer
    authentication_classes = (TokenAuthentication,)
    permission_classes = (IsAuthenticated,)

    def perform_create(self, serializer):
        """Create a new order for authenticated user"""
        serializer.save(user=self.request.user)
