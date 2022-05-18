import requests

from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import permissions

from api.serializers import BaseMapSerializer
from api.serializers import LayerSerializer
from geocontrib.models import BaseMap
from geocontrib.models import Layer


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
        except Exception:
            return Response(data="Les données sont inaccessibles", status=404)

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
        queryset = super().get_queryset()

        project_slug = self.request.query_params.get('project__slug')
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)

        return queryset


class LayerViewset(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    permission_classes = [
        permissions.AllowAny,
    ]

    queryset = Layer.objects.all()

    serializer_class = LayerSerializer
