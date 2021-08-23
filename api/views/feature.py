import json

from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.error import GEOSException
from django.db.models import query
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from api import serializers
from rest_framework import generics
from rest_framework import permissions
from rest_framework import views
from rest_framework import viewsets
from rest_framework.pagination import LimitOffsetPagination
from rest_framework.response import Response

from api import logger
from api.serializers import FeatureGeoJSONSerializer
from api.serializers import FeatureSearchSerializer
from api.serializers.feature import FeatureListSerializer
from api.serializers import FeatureTypeListSerializer
from geocontrib.models import Feature, feature
from geocontrib.models import FeatureType
from geocontrib.models import Project


User = get_user_model()


class FeatureTypeView(viewsets.ModelViewSet):
    """
    Get all features and can create one
    """
    lookup_field = 'slug'
    queryset = FeatureType.objects.all()
    serializer_class = FeatureTypeListSerializer
    
    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    def get_object(self):
        slug = self.kwargs.get('slug') or None
        obj = get_object_or_404(FeatureType, slug=self.kwargs.get('slug'))
        return obj


class ProjectFeatureTypes(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        feature_types = FeatureType.objects.filter(project__slug=slug)
        serializers = FeatureTypeListSerializer(feature_types, many=True)
        data = {
            'feature_types': serializers.data,
        }
        return Response(data, status=200)


class ProjectFeature(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        feature_types = Feature.objects.filter(project__slug=slug)
        serializers = FeatureListSerializer(feature_types, many=True)
        data = {
            'features': serializers.data,
        }
        return Response(data, status=200)


class CustomPagination(LimitOffsetPagination):
    default_limit = 25


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


class FeatureSearch(generics.ListAPIView):

    queryset = Feature.objects.all()

    serializer_class = FeatureSearchSerializer

    pagination_class = CustomPagination

    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        """
        Surchargeant ListModelMixin
        """
        geom = self.request.query_params.get('geom')
        status = self.request.query_params.get('status')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        title = self.request.query_params.get('title')
        feature_id = self.request.query_params.get('feature_id')
        exclude_feature_id = self.request.query_params.get('exclude_feature_id')
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

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)

        # queryset = self.queryset.filter(project=project)
        queryset = Feature.handy.availables(user=self.request.user, project=project)

        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        # NB filter_queryset() bien appelé par ListModelMixin
        return queryset
