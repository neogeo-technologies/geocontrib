
from django.contrib.flatpages.models import FlatPage
from rest_framework import permissions
from rest_framework.generics import ListAPIView

from api.serializers import FlatPagesSerializer

class FlatPagesView(ListAPIView):
    queryset = FlatPage.objects.all()
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = FlatPagesSerializer
    http_method_names = ['get', ]

