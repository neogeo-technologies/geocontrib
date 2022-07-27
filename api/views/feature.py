from email import header
import json
import requests
import csv
import collections

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.error import GEOSException
from django.contrib.gis.db.models import Extent
from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import views
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework_mvt.views import BaseMVTView
from rest_framework.views import APIView

from api import logger
from api.serializers.feature import FeatureDetailedAuthenticatedSerializer
from api.serializers import FeatureDetailedSerializer
from api.serializers import FeatureGeoJSONSerializer
from api.serializers import FeatureCSVSerializer
from api.serializers import FeatureLinkSerializer
from api.serializers import FeatureListSerializer
from api.serializers import FeatureSearchSerializer
from api.serializers import FeatureTypeListSerializer
from api.serializers import FeatureEventSerializer
from api.serializers import PreRecordedValuesSerializer
from api.utils.paginations import CustomPagination
from api.db_layer_utils import get_values_pre_enregistrés
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import PreRecordedValues
from geocontrib.models import Project


User = get_user_model()


class FeatureView(
            mixins.ListModelMixin,
            mixins.RetrieveModelMixin,
            mixins.CreateModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin,
            viewsets.GenericViewSet):

    lookup_field = 'feature_id'

    queryset = Feature.objects.all()

    serializer_class = FeatureGeoJSONSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        queryset = super().get_queryset()

        project_slug = self.request.query_params.get('project__slug')
        if project_slug:
            project = get_object_or_404(Project, slug=project_slug)
            queryset = Feature.handy.availables(self.request.user, project)

        feature_type_slug = self.request.query_params.get('feature_type__slug')
        if feature_type_slug:
            project = get_object_or_404(FeatureType, slug=feature_type_slug).project
            queryset = Feature.handy.availables(self.request.user, project)
            queryset = queryset.filter(feature_type__slug=feature_type_slug)

        if not feature_type_slug and not project_slug:
            raise ValidationError(detail="Must provide parameter project__slug "
                                         "or feature_type__slug")

        title_contains = self.request.query_params.get('title__contains')
        if title_contains:
            queryset = queryset.filter(title__contains=title_contains)

        title_icontains = self.request.query_params.get('title__icontains')
        if title_icontains:
            queryset = queryset.filter(title__icontains=title_icontains)

        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)
        return queryset


class FeatureTypeView(
            mixins.ListModelMixin,
            mixins.RetrieveModelMixin,
            mixins.CreateModelMixin,
            mixins.UpdateModelMixin,
            mixins.DestroyModelMixin,
            viewsets.GenericViewSet):

    lookup_field = 'slug'

    queryset = FeatureType.objects.all()

    serializer_class = FeatureTypeListSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]


class ProjectFeatureTypes(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        feature_types = FeatureType.objects.filter(project__slug=slug).order_by("title")
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
        project = get_object_or_404(Project, slug=slug)
        features = Feature.handy.availables(request.user, project)
        title_contains = self.request.query_params.get('title__contains')
        if title_contains:
            features = features.filter(title__contains=title_contains)

        title_icontains = self.request.query_params.get('title__icontains')
        if title_icontains:
            features = features.filter(title__icontains=title_icontains)

        feature_type__slug = self.request.query_params.get('feature_type__slug')
        if feature_type__slug:
            features = features.filter(feature_type__slug=feature_type__slug)

        feature_id = self.request.query_params.get('feature_id')
        if feature_id:
            features = features.filter(feature_id=feature_id)
        count = features.count()
        ordering = self.request.query_params.get('ordering')
        if ordering:
            features = features.order_by(ordering)
        limit = self.request.query_params.get('limit')
        if limit:
            features = features[:int(limit)]

        _id = self.request.query_params.get('id')
        if _id:
            features = features.filter(pk=_id)


        format = request.query_params.get('output')
        if format and format == 'geojson':
            data = FeatureDetailedSerializer(
                features,
                is_authenticated=request.user.is_authenticated,
                many=True,
                context={"request": request},
            ).data
        else:
            serializers = FeatureListSerializer(
                features,
                many=True,
                context={"request": request},
            )
            data = {
                'features': serializers.data,
                'count': count,
            }
        return Response(data, status=200)


class ProjectFeaturePaginated(generics.ListAPIView):
    queryset = Project.objects.all()
    pagination_class = CustomPagination
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        """
        Surchargeant ListModelMixin
        """
        status__value = self.request.query_params.get('status__value')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        title = self.request.query_params.get('title')

        if status__value:
            queryset = queryset.filter(status__icontains=status__value)
        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug__icontains=feature_type_slug)
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset
        
    def get_serializer_class(self):
        format = self.request.query_params.get('output')
        if format and format == 'geojson':
            if self.request.user.is_authenticated:
                return FeatureDetailedAuthenticatedSerializer
            return FeatureDetailedSerializer
        return FeatureListSerializer

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)

        queryset = Feature.handy.availables(user=self.request.user, project=project)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        return queryset

class ProjectFeatureBbox(generics.ListAPIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]


    def filter_queryset(self, queryset):
        """
        Surchargeant ListModelMixin
        """
        status__value = self.request.query_params.get('status__value')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        title = self.request.query_params.get('title')

        if status__value:
            queryset = queryset.filter(status__icontains=status__value)
        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug__icontains=feature_type_slug)
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)

        queryset = Feature.handy.availables(user=self.request.user, project=project)

        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        return queryset

    def list(self, request, *args, **kwargs):
        bbox = None
        queryset = self.filter_queryset(self.get_queryset()).aggregate(Extent('geom'))
        geom = queryset['geom__extent'];
        if geom :
            bbox = {'minLon': geom[0], 'minLat': geom[1], 'maxLon' : geom[2], 'maxLat': geom[3] }
        return Response(bbox)

class ExportFeatureList(views.APIView):

    http_method_names = ['get', ]

    def get(self, request, slug, feature_type_slug):
        """
            Vue de téléchargement des signalements lié à un projet.
        """
        project = get_object_or_404(Project, slug=slug)
        features = Feature.handy.availables(request.user, project).filter( feature_type__slug=feature_type_slug).order_by("created_on")
        format = request.GET.get('format_export')
        if format == 'geojson':
            serializer = FeatureGeoJSONSerializer(features, many=True, context={'request': request})
            response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export_projet.json'
        elif format == 'csv':
            serializer = FeatureCSVSerializer(features, many=True, context={'request': request})
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export_projet.csv'
            headers = [*serializer.data[0].keys()]
            headers.remove('geom')
            headers.remove('feature_data')
            headers.append('lat')
            headers.append('lon')
            feature_data = serializer.data[0]['feature_data']
            headers.extend(feature_data.keys() if feature_data else [])
            writer = csv.DictWriter(response, fieldnames=headers)
            writer.writeheader()
            for row in serializer.data:
                row['lon'] = row['geom']['coordinates'][0]
                row['lat'] = row['geom']['coordinates'][1]
                data = row['feature_data'].items() if row['feature_data'] else []
                full_row = collections.OrderedDict(list(row.items()) +
                                                   list(data))
                del full_row['geom']
                del full_row['feature_data']
                writer.writerow(full_row)
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

        queryset = Feature.handy.availables(user=self.request.user, project=project)

        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        # NB filter_queryset() bien appelé par ListModelMixin
        return queryset


class FeatureLinkView(generics.ListAPIView, generics.UpdateAPIView):

    parent_model = Feature

    queryset = FeatureLink.objects.all()

    serializer_class = FeatureLinkSerializer

    lookup_field = 'feature_id'

    def get_object(self, *args, **kwargs):
        lookup = {self.lookup_field: self.kwargs.get(self.lookup_field)}
        instance = get_object_or_404(self.parent_model, **lookup)
        return instance

    def get_queryset(self, *args, **kwargs):
        instance = self.get_object()
        return self.queryset.select_related(
            'feature_to', 'feature_from'
        ).filter(feature_from=instance)

    def put(self, request, *args, **kwargs):
        feature_from = self.get_object()
        serializer = FeatureLinkSerializer(feature_from, data=request.data, many=True)
        serializer.is_valid(raise_exception=True)
        serializer.bulk_create(feature_from)
        data = FeatureLinkSerializer(self.get_queryset(), many=True).data
        return Response(data)


class FeatureEventView(views.APIView):

    http_method_names = ['get', ]

    def get(self, request, feature_id):
        events = Event.objects.select_related('user').filter(
            feature_id=feature_id
        ).order_by('created_on')
        data = FeatureEventSerializer(events, many=True).data
        return Response(data, status=200)


class FeatureMVTView(BaseMVTView):
    model = Feature
    geom_col = "geom"

    def get(self, request, *args, **kwargs):

        project_slug = self.request.query_params.get('project__slug')
        project_id = self.request.query_params.get('project_id')
        if project_slug or project_id:
            qs_kwargs = dict()
            if project_slug:
                qs_kwargs["slug"] = project_slug

            if project_id:
                qs_kwargs["id"] = project_id

            project = get_object_or_404(Project, **qs_kwargs)
            queryset = Feature.handy.availables(self.request.user, project)

        feature_type_slug = self.request.query_params.get('feature_type__slug')
        featuretype_id = self.request.query_params.get('featuretype_id')
        if feature_type_slug or featuretype_id:
            project = get_object_or_404(FeatureType,
                                        slug=feature_type_slug,
                                        pk=featuretype_id).project
            queryset = Feature.handy.availables(self.request.user, project)
            queryset = queryset.filter(feature_type__slug=feature_type_slug, pk=featuretype_id)

        if not any([feature_type_slug, project_slug, project_id, featuretype_id]):
            raise ValidationError(detail="Must provide one of the parameters:"
                                  "project_id, project__slug, featuretype_id or feature_type__slug")

        if not request.GET._mutable:
            request.GET._mutable = True
        request.GET["pk__in"] = queryset.order_by("created_on").values_list("pk", flat=True)
        return super().get( request, *args, **kwargs)


class GetIdgoCatalogView(views.APIView):
    http_method_names = ['get', ]

    def get(self, request):
        url = settings.IDGO_URL
        user = request.query_params.get('user')
        if user:
            url += user

        try:
            response = requests.get(url, timeout=60, auth=(settings.IDGO_LOGIN, settings.IDGO_PASSWORD), verify=settings.IDGO_VERIFY_CERTIFICATE)
            data = response.json()
            code = response.status_code
            return Response(data=data, status=code)
        except Exception as e:
            logger.exception("Les données sont inaccessibles %s", e)
            return Response(data="Les données sont inaccessibles", status=404)

class GetExternalGeojsonView(views.APIView):
    http_method_names = ['get', ]

    def get(self, request):
        payload = {}
        url = settings.MAPSERVER_URL
        organization_slug = request.GET.get('organization_slug', '')
        if organization_slug:
            url += organization_slug

        payload["service"] = "WFS"
        payload["request"] = "GetFeature"
        payload["version"] = "2.0.0"
        payload["outputFormat"] = "geojson"
        typename = request.GET.get('typename', '')
        if typename:
            payload["typename"] = typename

        try:
            response = requests.get(url, params=payload, timeout=60, verify=settings.IDGO_VERIFY_CERTIFICATE)
            data = response.json()
            code = response.status_code
            if code != 200 or not data.get('type', '') == 'FeatureCollection':
                data = "Les données ne sont pas au format geoJSON"
            return Response(data=data, status=code)
        except Exception as e:
            logger.exception("Les données sont inaccessibles %s", e)
            return Response(data="Les données sont inaccessibles", status=404)


class PreRecordedValuesView(
        APIView
        ):
    queryset = PreRecordedValues.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get(self, request, name):
        from django.http import JsonResponse
        response = []
        name = self.kwargs.get('name')
        pattern = self.request.query_params.get('pattern')
        if name and pattern:
            data = get_values_pre_enregistrés(name, pattern)
            for da in data:
                response.append(da['values'])
        return JsonResponse(response, safe=False, status=200)