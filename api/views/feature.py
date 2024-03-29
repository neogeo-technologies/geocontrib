from datetime import datetime
import json
import requests
import csv
import collections
from datetime import date

from django.db.models import Q
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.gis.geos import Polygon
from django.contrib.gis.geos.error import GEOSException
from django.contrib.gis.db.models import Extent
from django.http import HttpResponse
from django.http import JsonResponse
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
from api.serializers import FeatureJSONSerializer
from api.serializers import FeatureGeoJSONSerializer
from api.serializers import FeatureCSVSerializer
from api.serializers import FeatureLinkSerializer
from api.serializers import FeatureListSerializer
from api.serializers import FeatureSearchSerializer
from api.serializers import FeatureTypeListSerializer
from api.serializers import FeatureEventSerializer
from api.utils.filters import FeatureTypeFilter
from api.utils.paginations import CustomPagination
from api.db_layer_utils import get_pre_recorded_values
from geocontrib.choices import TYPE_CHOICES
from geocontrib.models import CustomField
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import PreRecordedValues
from geocontrib.models import Project


User = get_user_model()
no_data_msg = "Les données sont inaccessibles"


class FeatureView(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):

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

        from_date = self.request.query_params.get('from_date')
        if from_date:
            try:
                parsed_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    parsed_date = datetime.strptime(from_date, '%Y-%m-%d')
                except ValueError:
                    raise ValidationError(detail=f"Invalid 'from_date' format."
                                          "Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
            queryset = queryset.filter(
                Q(created_on__gte=parsed_date) | 
                Q(updated_on__gte=parsed_date) | 
                Q(deletion_on__gte=parsed_date)
            )
        else:
            queryset = queryset.filter(deletion_on__isnull=True)

        title_contains = self.request.query_params.get('title__contains')
        if title_contains:
            queryset = queryset.filter(title__contains=title_contains)

        title_icontains = self.request.query_params.get('title__icontains')
        if title_icontains:
            queryset = queryset.filter(title__icontains=title_icontains)

        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]
        _id = self.request.query_params.get('id')
        if _id:
            queryset = queryset.filter(pk=_id)

        return queryset

    def list(self, request):
        response = {}
        queryset = self.get_queryset()
        format = self.request.query_params.get('output')
        if format and format == 'geojson':
            response = FeatureDetailedSerializer(
                queryset,
                is_authenticated=self.request.user.is_authenticated,
                many=True,
                context={"request": self.request},
            ).data
        elif format and format == 'list':
            serializers = FeatureListSerializer(
                queryset,
                many=True,
                context={"request": self.request},
            )
            response = {
                'features': serializers.data,
                'count': queryset.count(),
            }
        else:
            response = FeatureGeoJSONSerializer(
                queryset,
                many=True,
                context={'request': request}
            ).data

        return Response(response)

    def destroy(self, request, *args, **kwargs):
        feature = self.get_object()
        feature.deletion_on = date.today()
        feature.save()
        message = {"message": "Le signalement a été supprimé"}
        return Response(message)



class FeatureTypeView(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):

    lookup_field = 'slug'

    queryset = FeatureType.objects.all()

    serializer_class = FeatureTypeListSerializer

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]
    filter_backends = [
        FeatureTypeFilter
    ]

class ProjectFeaturePaginated(generics.ListAPIView):
    """
    API view to provide a paginated list of features for a specific project.

    This view extends the ListAPIView from Django Rest Framework to customize
    queryset filtering based on query parameters like status values, feature
    type slugs, and title. It also supports dynamic selection of serializer
    classes based on the requested output format.
    """
    
    queryset = Project.objects.all()
    pagination_class = CustomPagination
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        """
        Overrides the default ListModelMixin to provide customized filtering.

        This method allows filtering based on multiple values for certain fields
        by using the '__in' lookup in Django ORM. It is important to note that 
        the '__in' lookup is case-sensitive. However, in this implementation, 
        this behavior does not present an issue as the filter values are provided 
        by the application itself and are expected to match the case of the stored data.

        The 'getlist' method is used to retrieve multiple values for the same query 
        parameter, allowing for more flexible and inclusive filtering compared to 'get',
        which only retrieves a single value.

        Parameters:
        - queryset: The initial queryset to be filtered.

        Returns:
        - QuerySet: The filtered queryset based on the provided query parameters.
        """
        # Retrieve values from the query parameters. 
        status_values = self.request.query_params.get('status__value')
        feature_type_slugs = self.request.query_params.get('feature_type_slug')
        title = self.request.query_params.get('title')
        # Filter out features that have been marked as deleted
        queryset = queryset.filter(deletion_on__isnull=True)

        # Apply filters for status values, feature type slugs, and title
        if status_values:
            status_values_list = status_values.split(',')
            queryset = queryset.filter(status__in=status_values_list)
        if feature_type_slugs:
            feature_type_slug_list = feature_type_slugs.split(',')
            queryset = queryset.filter(feature_type__slug__in=feature_type_slug_list)
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_serializer_class(self):
        """
        Override get_serializer_class to dynamically select the serializer class based on
        the requested output format.

        Returns a detailed serializer for authenticated users requesting geojson format,
        otherwise returns a standard list serializer.
        """
        format = self.request.query_params.get('output')
        if format and format == 'geojson':
            if self.request.user.is_authenticated:
                return FeatureDetailedAuthenticatedSerializer
            return FeatureDetailedSerializer
        return FeatureListSerializer

    def get_queryset(self):
        """
        Override get_queryset to provide a customized queryset for the view.

        Retrieves the project based on the provided slug and returns a queryset
        of available features for the project, applying any specified ordering.
        """
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)

        queryset = Feature.handy.availables(user=self.request.user, project=project)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Optimize query performance with select_related
        queryset = queryset.select_related('creator')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        return queryset

class ProjectFeaturePositionInList(views.APIView):

    http_method_names = ['get', ]

    def get(self, request, slug, feature_id):
        """
            Vue de récupération de la position d'un signalement dans une liste ordonnée selon un tri et des filtres
        """
        project = get_object_or_404(Project, slug=slug)
        # Ordering :
        ordering = request.GET.get('ordering') or '-created_on'
        queryset = Feature.handy.availables(request.user, project).order_by(ordering)
        # Filters :
        feature_type_slug = request.GET.get('feature_type_slug')
        status__value = request.GET.get('status')
        title = request.GET.get('title')
        # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
        queryset = queryset.filter(deletion_on__isnull=True)

        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug__icontains=feature_type_slug)
        if status__value:
            queryset = queryset.filter(status__icontains=status__value)
        if title:
            queryset = queryset.filter(title__icontains=title)
        # Position :
        try:
            instance = queryset.filter(feature_id=feature_id).first()
            if instance:
                position = (*queryset,).index(instance)
                return Response(data=position, status=200)
            else:
                return Response(status=204)

        except Exception as e:
            logger.exception("%s %s", no_data_msg, e)
            return Response(data=no_data_msg, status=404)

class ProjectFeatureBbox(generics.ListAPIView):
    """
    API view that provides the bounding box (bbox) of features within a project.

    The view filters features based on specified query parameters, supporting
    'feature_type_slug' and 'status__value'. It calculates the bbox for the filtered
    features. The view interprets comma-separated string values in the query parameters
    as lists.

    Attributes:
        queryset: Default queryset for Project model.
        lookup_field: Field used for looking up a project.
        http_method_names: Allowed HTTP methods for this view.
    """
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        """
        Filters the queryset based on the query parameters.

        Processes 'status__value' and 'feature_type_slug' as comma-separated strings,
        converts them to lists, and applies filters accordingly. Also filters by 'title' if provided.

        Parameters:
            queryset: Initial queryset to apply filters on.

        Returns:
            Filtered queryset based on query parameters.
        """
        # Retrieve string parameters and convert them to lists
        status_values = self.request.query_params.get('status__value', '')
        feature_type_slugs = self.request.query_params.get('feature_type_slug', '')
        title = self.request.query_params.get('title')

        status_list = status_values.split(',') if status_values else []
        feature_type_slug_list = feature_type_slugs.split(',') if feature_type_slugs else []

        # Filter out features with a deletion date
        queryset = queryset.filter(deletion_on__isnull=True)

        # Apply filters if lists are not empty
        if status_list:
            queryset = queryset.filter(status__in=status_list)
        if feature_type_slug_list:
            queryset = queryset.filter(feature_type__slug__in=feature_type_slug_list)
        if title:
            queryset = queryset.filter(title__icontains=title)
        return queryset

    def get_queryset(self):
        """
        Provides a queryset of Feature objects for a specific project.

        Filters the features based on the project slug and applies select_related
        for related fields to optimize database queries.

        Returns:
            A queryset of Feature objects for the specified project.
        """
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)
        queryset = Feature.handy.availables(user=self.request.user, project=project)
        queryset = queryset.select_related('creator', 'feature_type', 'project')
        return queryset

    def list(self, request, *args, **kwargs):
        """
        Custom list method to return the bbox of filtered features.

        Aggregates the filtered features to calculate their geographic extent (bbox).
        If features exist, returns their bbox, otherwise returns None.

        Returns:
            Response with bbox of the filtered features or None if no features are found.
        """
        bbox = None
        queryset = self.filter_queryset(self.get_queryset()).aggregate(Extent('geom'))
        geom_extent = queryset['geom__extent']
        if geom_extent:
            bbox = {'minLon': geom_extent[0], 'minLat': geom_extent[1], 'maxLon': geom_extent[2], 'maxLat': geom_extent[3]}
        return Response(bbox)


class ExportFeatureList(views.APIView):
    """
    API view for exporting feature data related to a project in various formats such as JSON, GeoJSON, or CSV.
    """

    http_method_names = ['get', ]

    def get_csv_headers(self, serializer, feature_type):
        """
        Builds and returns headers for the CSV file.

        Parameters:
        - serializer: The serializer containing the feature data.
        - feature_type: The feature type object used to determine if additional geographical fields are needed.

        Returns:
        - List[str]: Column headers for the CSV file.
        """
        # Retrieve feature field names from the serializer data
        featureFieldNames = [*serializer.data[0].keys()]
        # Get custom field names from the FeatureType model
        customFieldNames = [custField.name for custField in CustomField.objects.filter(feature_type=feature_type)]
        # Combine feature field names and custom field names
        headers = [*featureFieldNames, *customFieldNames]
        # Remove 'feature_data' and 'geom' fields, as they are not needed in the CSV
        headers.remove('feature_data')
        headers.remove('geom')
        # Add latitude and longitude columns for geographical feature types
        if feature_type.geom_type != 'none':
            headers += ['lat', 'lon']
        return headers

    def prepare_csv_row(self, row, feature_type):
        """
        Prepares and returns a single row for the CSV file.

        Parameters:
        - row: Dict representing a single feature's data.
        - feature_type: The feature type object used to determine if geographical data conversion is necessary.

        Returns:
        - OrderedDict: A single row in the CSV file.
        """
        # Convert geom data to latitude and longitude if the feature type is geographical
        if feature_type.geom_type != 'none' and 'geom' in row:
            row['lon'] = row['geom']['coordinates'][0]
            row['lat'] = row['geom']['coordinates'][1]
        # Merge feature data with custom field data
        data = row['feature_data'].items() if row['feature_data'] else []
        full_row = collections.OrderedDict(list(row.items()) + list(data))
        # Remove 'geom' and 'feature_data' fields from the row
        full_row.pop('geom', None)
        full_row.pop('feature_data', None)
        return full_row

    def get(self, request, slug, feature_type_slug):
        """
        Handles GET request to export feature data.

        Parameters:
        - request: The incoming HTTP request.
        - slug: Slug of the project.
        - feature_type_slug: Slug of the feature type.

        Returns:
        - HttpResponse: Response with exported data in the requested format.
        """
        # Retrieve the project and features based on the provided slugs
        project = get_object_or_404(Project, slug=slug)
        features = Feature.handy.availables(request.user, project).filter(
            feature_type__slug=feature_type_slug,
            # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
            deletion_on__isnull=True
        ).order_by("created_on")

        # Determine the format for export
        format = request.GET.get('format_export')

        # Handling JSON export
        if format == 'json':
            serializer = FeatureJSONSerializer(features, many=True, context={'request': request})
            response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export_projet.json'

        # Handling GeoJSON export
        elif format == 'geojson':
            serializer = FeatureGeoJSONSerializer(features, many=True, context={'request': request})
            response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export_projet.json'

        # Handling CSV export
        elif format == 'csv':
            serializer = FeatureCSVSerializer(features, many=True, context={'request': request})
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export_projet.csv'

            feature_type = FeatureType.objects.get(slug=feature_type_slug)

            # Prepare CSV headers and initialize a CSV writer
            writer = csv.DictWriter(response, fieldnames=self.get_csv_headers(serializer, feature_type))
            writer.writeheader()

            # Write each feature to the CSV file
            for row in serializer.data:
                writer.writerow(self.prepare_csv_row(row, feature_type))

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
        # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
        queryset = queryset.filter(deletion_on__isnull=True)
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
        # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
        queryset = queryset.filter(deletion_on__isnull=True)
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
            logger.exception("%s %s", no_data_msg, e)
            return Response(data=no_data_msg, status=404)

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
            logger.exception("%s %s", no_data_msg, e)
            return Response(data=no_data_msg, status=404)


class PreRecordedValuesView(APIView):
    queryset = PreRecordedValues.objects.all()

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get(self, request, name=None):
        response=[]
        name = self.kwargs.get('name', None)
        pattern = self.request.query_params.get('pattern', '')
        limit = self.request.query_params.get('limit', '')

        if name:
            response = get_pre_recorded_values(name, pattern, limit)
        else:
            response = list(PreRecordedValues.objects.values("name"))
        status = 200
        return JsonResponse(response, safe=False, status=status)


class CustomFields(APIView):
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get(self, request):
        type_choices = [] 
        status = 200
        for x, y in TYPE_CHOICES:
            type_choices.append(
                {
                "type": x,
                "label":y
                }
            )
        return JsonResponse(type_choices, safe=False, status=status)
