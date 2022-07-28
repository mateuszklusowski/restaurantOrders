from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from .serializers import RestaurantSerializer, RestaurantDetailSerializer

from core.models import Restaurant


class RestaurantViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """Retrieve restaurant list"""
    serializer_class = RestaurantSerializer
    permission_classes = (AllowAny,)
    queryset = Restaurant.objects.all()
    lookup_field = 'slug'

    def get_queryset(self):
        """Return filetered queryset"""
        queryset = self.queryset
        cuisine = str(self.request.query_params.get('cuisine', '')).title()
        city = str(self.request.query_params.get('city', '')).title()

        if city != '':
            queryset = queryset.filter(city=city)

        if cuisine != '':
            queryset = queryset.filter(cuisine__name=cuisine)

        return queryset

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return RestaurantDetailSerializer

        return self.serializer_class
