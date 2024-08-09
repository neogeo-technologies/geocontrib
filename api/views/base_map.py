import requests
import logging
import json

from rest_framework.views import APIView
from rest_framework.response import Response
from django.http import HttpResponse
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions

from api.serializers import BaseMapSerializer
from api.serializers import LayerSerializer
from geocontrib.models import BaseMap
from geocontrib.models import Layer

logger = logging.getLogger(__name__)

class GetFeatureInfo(APIView):

    http_method_names = ['get', ]
    def get(self, request):
        payload = {}

        url = request.GET.get('url', '')
        params = [
            'request',
            'service',
            'srs',
            'version',
            'bbox',
            'height',
            'width',
            'layers',
            'query_layers',
            'info_format',
        ]
        for param in params:
            payload[param] = request.GET.get(param, '')

        coords = [
            'x',
            'y',
            'i',
            'j'
        ]
        for coord in coords:
            val = request.GET.get(coord)
            if val:
                payload[coord] = val
        try:
            response = requests.get(url, params=payload, timeout=60)
            data = response.json()
            code = response.status_code
            if code != 200 or not data.get('type', '') == 'FeatureCollection':
                data = "Les données ne sont pas au format geoJSON"
            return Response(data=data, status=code)
        except json.decoder.JSONDecodeError as e:
            logger.error(f"Failed to decode JSON from response: {response.content}")
            logger.exception(e)
            return HttpResponse(response.content, status=response.status_code, content_type=response.headers.get('Content-Type'))
        except Exception as e:
            logger.error(f"An unexpected error occurred: {e}")
            logger.exception(e)
            return Response(data="Les données sont inaccessibles", status=502)

class BaseMapViewset(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly,
    ]

    queryset = BaseMap.objects.all()

    serializer_class = BaseMapSerializer

    def get_queryset(self):
        """
        Optionally restricts the returned base maps to a given project
        by filtering against a `project__slug` query parameter in the URL.
        """
        queryset = super().get_queryset()

        project_slug = self.request.query_params.get('project__slug')
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)

        return queryset

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Retrieve a list of base maps"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Retrieve a specific base map"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Create a new base map"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Update a specific base map"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Partially update a specific base map"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["base-maps"],
        operation_summary="Delete a specific base map"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class LayerViewset(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    API endpoint that allows layers to be viewed.
    """

    permission_classes = [
        permissions.AllowAny,
    ]

    queryset = Layer.objects.all()

    serializer_class = LayerSerializer

    @swagger_auto_schema(
        operation_summary="List layers",
        tags=["base-maps"]
    )
    def list(self, request, *args, **kwargs):
        """
        Retrieve a list of all layers.
        """
        return super().list(request, *args, **kwargs)