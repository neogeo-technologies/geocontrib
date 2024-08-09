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

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi


class GetFeatureInfo(APIView):
    """
    Proxy endpoint for retrieving feature information from an external WMS/WFS service.

    Forwards requests to a specified remote geospatial service (WMS/WFS) using the provided parameters (like bounding box, layers, and coordinates).
    It returns the service's response, typically in GeoJSON format, to the client.
    This proxy is useful for centralizing and controlling access to external geospatial data, especially in scenarios where direct client access is restricted or additional logging and security are required.
    """
    http_method_names = ['get', ]

    @swagger_auto_schema(
        operation_summary="Retrieve feature information from a remote service",
        tags=["misc"],
        manual_parameters=[
            openapi.Parameter(
                'url',
                openapi.IN_QUERY,
                description="The base URL of the WMS/WFS service.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'request',
                openapi.IN_QUERY,
                description="The type of request, e.g., GetFeatureInfo.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'service',
                openapi.IN_QUERY,
                description="The service type, usually WMS or WFS.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'srs',
                openapi.IN_QUERY,
                description="The spatial reference system, e.g., EPSG:4326.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'version',
                openapi.IN_QUERY,
                description="The service version, e.g., 1.3.0.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'bbox',
                openapi.IN_QUERY,
                description="The bounding box for the request, usually in the format 'minx,miny,maxx,maxy'.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'height',
                openapi.IN_QUERY,
                description="The height of the output image in pixels.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'width',
                openapi.IN_QUERY,
                description="The width of the output image in pixels.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'layers',
                openapi.IN_QUERY,
                description="The layers to query.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'query_layers',
                openapi.IN_QUERY,
                description="The layers to query for feature info.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'info_format',
                openapi.IN_QUERY,
                description="The format of the feature information returned, e.g., 'application/json'.",
                type=openapi.TYPE_STRING,
                required=True
            ),
            openapi.Parameter(
                'x',
                openapi.IN_QUERY,
                description="X coordinate for the query.",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'y',
                openapi.IN_QUERY,
                description="Y coordinate for the query.",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'i',
                openapi.IN_QUERY,
                description="I coordinate for the query (alternative to x).",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                'j',
                openapi.IN_QUERY,
                description="J coordinate for the query (alternative to y).",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Successfully retrieved feature information.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "type": openapi.Schema(type=openapi.TYPE_STRING, example="FeatureCollection"),
                        "features": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "type": openapi.Schema(type=openapi.TYPE_STRING, example="Feature"),
                                    "geometry": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "type": openapi.Schema(type=openapi.TYPE_STRING, example="Point"),
                                            "coordinates": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(type=openapi.TYPE_NUMBER),
                                                example=[102.0, 0.5]
                                            ),
                                        }
                                    ),
                                    "properties": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        example={"name": "Example"}
                                    )
                                }
                            )
                        ),
                    }
                ),
                examples={
                    "application/json": {
                        "type": "FeatureCollection",
                        "features": [
                            {
                                "type": "Feature",
                                "geometry": {
                                    "type": "Point",
                                    "coordinates": [102.0, 0.5]
                                },
                                "properties": {
                                    "name": "Example"
                                }
                            }
                        ]
                    }
                }
            ),
            502: openapi.Response(
                description="Failed to retrieve feature information or the data is inaccessible.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Les données sont inaccessibles"
                )
            ),
            400: openapi.Response(
                description="Bad request due to invalid input parameters.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Invalid parameters provided."
                )
            ),
        }
    )
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