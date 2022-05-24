from rest_framework import viewsets, mixins
from rest_framework.permissions import AllowAny

from django_filters.rest_framework import DjangoFilterBackend

from .serializers import RestaurantSerializer, RestaurantDetailSerializer

from core.models import Restaurant


class RestaurantViewSet(viewsets.GenericViewSet,
                        mixins.ListModelMixin,
                        mixins.RetrieveModelMixin):
    """Retrieve restaurant list"""
    serializer_class = RestaurantSerializer
    permission_classers = (AllowAny,)
    queryset = Restaurant.objects.all()
    filter_backends = (DjangoFilterBackend,)
    filterset_fields = ('city', 'cuisine')

    def get_serializer_class(self):
        """Return appropriate serializer class"""
        if self.action == 'retrieve':
            return RestaurantDetailSerializer

        return self.serializer_class
