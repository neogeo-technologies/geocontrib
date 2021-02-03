import json
import logging

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.error import GEOSException
from django.http import Http404
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
# from rest_framework import status
from rest_framework import views
from rest_framework import permissions
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api.serializers import FeatureGeoJSONSerializer
from api.serializers import FeatureSerializer
from api.serializers import FeatureDetailedSerializer
from api.serializers import FeatureSearchSerializer
from geocontrib.models import Feature
from geocontrib.models import Project

logger = logging.getLogger(__name__)

User = get_user_model()


class CustomPagination(LimitOffsetPagination):
    default_limit = 3


class ExportFeatureList(views.APIView):

    http_method_names = ['get', ]

    def get(self, request, slug, feature_type_slug):
        """
            Vue de téléchargement des signalements lié à un projet.
        """
        features = Feature.objects.filter(
            status="published", project__slug=slug, feature_type__slug=feature_type_slug)
        serializer = FeatureGeoJSONSerializer(features, many=True, context={'request': request})
        response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
        response['Content-Disposition'] = 'attachment; filename=export_projet.json'
        return response


class AvailablesFeatureLinkList(views.APIView):

    http_method_names = ['get', ]

    def get(self, request, slug, feature_type_slug):
        """
            Vue retournant un abstract des signalements d'un type donnée,
            permettant de rechercher les signalements liés
        """
        features = Feature.objects.filter(
            status="published", project__slug=slug, feature_type__slug=feature_type_slug)
        serializer = FeatureSerializer(features, many=True, context={'request': request})
        return Response(serializer.data)


class FeatureSearch(generics.ListAPIView):

    # permission_classes = [
    #     permissions.IsAuthenticated,
    # ]

    queryset = Feature.objects.all()

    serializer_class = FeatureSearchSerializer

    pagination_class = LimitOffsetPagination

    http_method_names = ['get', ]

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)
        geom = self.request.query_params.get('geom')
        status = self.request.query_params.get('status')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        title = self.request.query_params.get('title')
        feature_id = self.request.query_params.get('feature_id')
        exclude_feature_id = self.request.query_params.get('exclude_feature_id')

        # queryset = self.queryset.filter(project=project)
        queryset = Feature.handy.availables(user=self.request.user, project=project)
        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')

        if geom:
            try:
                queryset = queryset.filter(geom__intersects=Polygon.from_bbox(geom.split(',')))
            except (GEOSException, ValueError):
                logger.exception("Api FeatureSearch geom error")
        if status:
            queryset = queryset.filter(status__icontains=status)
        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug__icontains=feature_type_slug)
        if title:
            queryset = queryset.filter(title__icontains=title)
        if feature_id:
            queryset = queryset.filter(feature_id=feature_id)
        if exclude_feature_id:
            queryset = queryset.exclude(feature_id=exclude_feature_id)

        return queryset

    # def get(self, request, slug):
    #
    #     queryset = self.get_queryset()
    #     try:
    #         data = self.get_serializer(
    #             queryset,
    #             many=True
    #         ).data
    #     except Exception:
    #         logger.exception('API FeatureView error')
    #         raise Http404
    #     return Response(data=data, status=status.HTTP_200_OK)
