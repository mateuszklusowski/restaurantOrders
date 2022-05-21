from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from .serializers import RestaurantSerializer, RestaurantDetailSerializer

from core.models import Restaurant


class RestaurantViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """Retrieve restaurant list"""
    serializer_class = RestaurantSerializer
    permission_classers = (AllowAny,)
    queryset = Restaurant.objects.all()

    def get_queryset(self):
        """Return restaurant with given cuisine or name"""
        queryset = self.queryset
        cuisine = self.request.query_params.get('cuisine', None)
        name = self.request.query_params.get('name', None)

        if cuisine is not None:
            queryset = queryset.filter(cuisine__name=cuisine)
        if name is not None:
            queryset = queryset.filter(name=name)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return RestaurantDetailSerializer

        return self.serializer_class
