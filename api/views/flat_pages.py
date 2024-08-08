
from django.contrib.flatpages.models import FlatPage
from rest_framework import permissions
from rest_framework.generics import ListAPIView
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from api.serializers import FlatPagesSerializer

class FlatPagesView(ListAPIView):
    """
    View to list all flat pages in the database.

    * Only the GET method is allowed.
    """
    queryset = FlatPage.objects.all()
    permission_classes = [
        permissions.AllowAny,
    ]
    serializer_class = FlatPagesSerializer
    http_method_names = ['get', ]

    @swagger_auto_schema(
        operation_summary="List flat pages",
        tags=["misc"],
    )
    def get(self, request, *args, **kwargs):
        return super().get(request, *args, **kwargs)