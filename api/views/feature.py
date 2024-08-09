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
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import status
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
from api.serializers import BboxSerializer
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
    """
    A viewset that provides the standard actions for the Feature model, 
    including listing, retrieving, creating, updating, and deleting features.
    """

    # The field used for lookups in this viewset
    lookup_field = 'feature_id'

    # The queryset that retrieves all Feature objects
    queryset = Feature.objects.all()

    # The serializer used to serialize Feature objects
    serializer_class = FeatureGeoJSONSerializer

    # Permissions for this viewset: authenticated users can create, update, and delete; everyone can read
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_queryset(self):
        """
        Returns the queryset of features filtered by various query parameters.
        """
        # Start with the base queryset
        queryset = super().get_queryset()

        # Filter by project slug if provided
        project_slug = self.request.query_params.get('project__slug')
        if project_slug:
            project = get_object_or_404(Project, slug=project_slug)
            queryset = Feature.handy.availables(self.request.user, project)

        # Filter by feature type slug if provided
        feature_type_slug = self.request.query_params.get('feature_type__slug')
        if feature_type_slug:
            project = get_object_or_404(FeatureType, slug=feature_type_slug).project
            queryset = Feature.handy.availables(self.request.user, project)
            queryset = queryset.filter(feature_type__slug=feature_type_slug)

        # Raise an error if neither project_slug nor feature_type_slug is provided
        if not feature_type_slug and not project_slug:
            raise ValidationError(detail="Must provide parameter project__slug or feature_type__slug")

        # Filter by a date range if 'from_date' is provided
        from_date = self.request.query_params.get('from_date')
        if from_date:
            try:
                parsed_date = datetime.strptime(from_date, '%Y-%m-%dT%H:%M:%S')
            except ValueError:
                try:
                    parsed_date = datetime.strptime(from_date, '%Y-%m-%d')
                except ValueError:
                    raise ValidationError(detail=f"Invalid 'from_date' format. Use YYYY-MM-DD or YYYY-MM-DDTHH:MM:SS")
            queryset = queryset.filter(
                Q(created_on__gte=parsed_date) | 
                Q(updated_on__gte=parsed_date) | 
                Q(deletion_on__gte=parsed_date)
            )
        else:
            # Exclude deleted features if no date range is provided
            queryset = queryset.filter(deletion_on__isnull=True)

        # Filter by title if 'title__contains' or 'title__icontains' is provided
        title_contains = self.request.query_params.get('title__contains')
        if title_contains:
            queryset = queryset.filter(title__contains=title_contains)

        title_icontains = self.request.query_params.get('title__icontains')
        if title_icontains:
            queryset = queryset.filter(title__icontains=title_icontains)

        # Order the queryset if 'ordering' is provided
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Limit the queryset if 'limit' is provided
        limit = self.request.query_params.get('limit')
        if limit:
            queryset = queryset[:int(limit)]

        # Filter by ID if 'id' is provided
        _id = self.request.query_params.get('id')
        if _id:
            queryset = queryset.filter(pk=_id)

        return queryset

    @swagger_auto_schema(
        operation_summary="List features",
        tags=["features"]
    )
    def list(self, request):
        """
        Lists features based on the filters applied in the queryset.
        Supports output formats 'geojson' and 'list'.
        """
        response = {}
        queryset = self.get_queryset()
        format = self.request.query_params.get('output')
        
        # Output the response in the requested format
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

    @swagger_auto_schema(
        operation_summary="Retrieve a feature",
        tags=["features"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a feature",
        tags=["features"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a feature",
        tags=["features"]
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a feature",
        tags=["features"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a feature",
        tags=["features"]
    )
    def destroy(self, request, *args, **kwargs):
        """
        Marks a feature as deleted by setting its deletion_on field to the current date.
        """
        feature = self.get_object()
        feature.deletion_on = date.today()
        feature.save()
        message = {"message": "Le signalement a été supprimé"}
        return Response(message, status=status.HTTP_200_OK)


class FeatureTypeView(
        mixins.ListModelMixin,
        mixins.RetrieveModelMixin,
        mixins.CreateModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
    ):
    """
    View to manage feature types, allowing listing, retrieval, creation, updating, and deletion of feature types.

    * Uses 'slug' as the lookup field.
    * Requires authentication for modifications.
    """
    lookup_field = 'slug'
    queryset = FeatureType.objects.all()
    serializer_class = FeatureTypeListSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    filter_backends = [FeatureTypeFilter]

    @swagger_auto_schema(
        operation_summary="List feature types",
        tags=["feature types"],
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve feature type",
        tags=["feature types"],
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create feature type",
        tags=["feature types"],
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update feature type",
        tags=["feature types"],
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a feature type",
        tags=["feature types"],
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete feature type",
        tags=["feature types"],
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProjectFeaturePaginated(generics.ListAPIView):
    """
    Provide a paginated list of features for a specific project.
    """
    
    queryset = Project.objects.all()
    pagination_class = CustomPagination
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        """
        Customize filtering based on query parameters like status, feature type, and title.
        """
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
        Dynamically select the serializer class based on the output format.
        """
        format = self.request.query_params.get('output')
        if format and format == 'geojson':
            if self.request.user.is_authenticated:
                return FeatureDetailedAuthenticatedSerializer
            return FeatureDetailedSerializer
        return FeatureListSerializer

    def get_queryset(self):
        """
        Provide a customized queryset for the view based on the project slug.
        """
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)

        queryset = Feature.handy.availables(user=self.request.user, project=project)
        ordering = self.request.query_params.get('ordering')
        if ordering:
            queryset = queryset.order_by(ordering)

        # Optimize query performance with select_related
        queryset = queryset.select_related('creator', 'feature_type', 'project')
        return queryset

    @swagger_auto_schema(
        operation_summary="List features for a project",
        tags=["features"]
    )
    def get(self, request, *args, **kwargs):
        """
        Override get method to provide a list of features for a project.
        """
        return super().get(request, *args, **kwargs)


class ProjectFeaturePositionInList(views.APIView):
    """
    Retrieve the position of a feature in an ordered list within a project.
    """

    http_method_names = ['get', ]

    @swagger_auto_schema(
        operation_summary="Get feature position in list",
        responses={
            200: openapi.Response(
                description="Feature position in the list",
                schema=openapi.Schema(
                    type=openapi.TYPE_INTEGER,
                    description="Position of the feature in the list"
                ),
            ),
            404: openapi.Response(
                description="Not Found",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={"detail": no_data_msg}
                ),
            ),
            204: openapi.Response(description="No Content"),
        },
        tags=["features"],
    )
    def get(self, request, slug, feature_id):
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
                position = list(queryset).index(instance)
                return Response(data=position, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Exception as e:
            logger.exception("Error occurred while fetching the feature position: %s", e)
            return Response(data={"detail": no_data_msg}, status=status.HTTP_404_NOT_FOUND)

class ProjectFeatureBbox(generics.GenericAPIView):
    """
    Provides the bounding box (bbox) of features within a project, filtered by query parameters.
    """
    lookup_field = 'slug'
    http_method_names = ['get']
    serializer_class = BboxSerializer

    def filter_queryset(self, queryset):
        status_values = self.request.query_params.get('status__value', '')
        feature_type_slugs = self.request.query_params.get('feature_type_slug', '')
        title = self.request.query_params.get('title')

        status_list = [value.strip() for value in status_values.split(',') if value.strip()]
        feature_type_slug_list = [slug.strip() for slug in feature_type_slugs.split(',') if slug.strip()]

        queryset = queryset.filter(deletion_on__isnull=True)

        if status_list:
            queryset = queryset.filter(status__in=status_list)
        if feature_type_slug_list:
            queryset = queryset.filter(feature_type__slug__in=feature_type_slug_list)
        if title:
            queryset = queryset.filter(title__icontains=title)

        return queryset

    def get_queryset(self):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)
        queryset = Feature.handy.availables(user=self.request.user, project=project)
        return queryset.select_related('creator', 'feature_type', 'project')

    @swagger_auto_schema(
        operation_summary="Get Bounding Box of Features",
        tags=["features"],
        manual_parameters=[
            openapi.Parameter(
                name='status__value',
                in_=openapi.IN_QUERY,
                description="Comma-separated list of status values to filter features.",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='feature_type_slug',
                in_=openapi.IN_QUERY,
                description="Comma-separated list of feature type slugs to filter features.",
                type=openapi.TYPE_STRING,
                required=False
            ),
            openapi.Parameter(
                name='title',
                in_=openapi.IN_QUERY,
                description="Substring to filter features by title.",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="Bounding box of the filtered features.",
                schema=BboxSerializer()
            ),
            204: openapi.Response(
                description="No Content - No features found matching the filters."
            ),
            404: openapi.Response(
                description="Not Found - Project not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
                    },
                    example={"detail": "Project not found."}
                ),
            ),
        }
    )
    def get(self, request, *args, **kwargs):
        try:
            queryset = self.filter_queryset(self.get_queryset())
            aggregated_data = queryset.aggregate(geom_extent=Extent('geom'))
            geom_extent = aggregated_data.get('geom_extent')

            if geom_extent and all(geom_extent):
                bbox_data = {
                    'minLon': geom_extent[0],
                    'minLat': geom_extent[1],
                    'maxLon': geom_extent[2],
                    'maxLat': geom_extent[3]
                }
                serializer = self.get_serializer(data=bbox_data)
                serializer.is_valid(raise_exception=True)
                return Response(serializer.data, status=status.HTTP_200_OK)
            else:
                return Response(status=status.HTTP_204_NO_CONTENT)
        except Project.DoesNotExist:
            logger.error("Project with slug '%s' not found.", self.kwargs.get('slug'))
            return Response(
                {"detail": "Project not found."},
                status=status.HTTP_404_NOT_FOUND
            )
        except Exception as e:
            logger.exception("An unexpected error occurred: %s", str(e))
            return Response(
                {"detail": "An unexpected error occurred."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class ExportFeatureList(views.APIView):
    """
    Export feature data for a project in JSON, GeoJSON, or CSV format.
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

    @swagger_auto_schema(
        operation_summary="Export features in JSON, GeoJSON, or CSV",
        tags=["features"],
        responses={
            200: openapi.Response(
                description="Successful export of features.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "type": openapi.Schema(type=openapi.TYPE_STRING, example="FeatureCollection"),
                        "features": openapi.Schema(
                            type=openapi.TYPE_ARRAY,
                            items=openapi.Schema(
                                type=openapi.TYPE_OBJECT,
                                properties={
                                    "id": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_UUID, example="4770f587-a509-4afe-adaa-b29987809519"),
                                    "type": openapi.Schema(type=openapi.TYPE_STRING, example="Feature"),
                                    "geometry": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "type": openapi.Schema(type=openapi.TYPE_STRING, example="Point"),
                                            "coordinates": openapi.Schema(
                                                type=openapi.TYPE_ARRAY,
                                                items=openapi.Schema(type=openapi.TYPE_NUMBER, format=openapi.FORMAT_FLOAT),
                                                example=[1.568015747070313, 43.64026371612965]
                                            ),
                                        }
                                    ),
                                    "properties": openapi.Schema(
                                        type=openapi.TYPE_OBJECT,
                                        properties={
                                            "title": openapi.Schema(type=openapi.TYPE_STRING, example="Signalement1"),
                                            "description": openapi.Schema(type=openapi.TYPE_STRING, example=""),
                                            "status": openapi.Schema(type=openapi.TYPE_STRING, example="draft"),
                                            "created_on": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example="2024-05-14T16:38:48.100784+02:00"),
                                            "updated_on": openapi.Schema(type=openapi.TYPE_STRING, format=openapi.FORMAT_DATETIME, example="2024-05-14T16:38:48.100810+02:00"),
                                            "deletion_on": openapi.Schema(type=openapi.TYPE_STRING, example=None),
                                            "feature_type": openapi.Schema(type=openapi.TYPE_STRING, example="1-type-signalement1"),
                                            "project": openapi.Schema(type=openapi.TYPE_STRING, example="1-projet1"),
                                            "display_creator": openapi.Schema(type=openapi.TYPE_STRING, example="user1"),
                                            "display_last_editor": openapi.Schema(type=openapi.TYPE_STRING, example="user1"),
                                            "creator": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                                        }
                                    ),
                                }
                            )
                        ),
                    }
                ),
            ),
            400: openapi.Response(
                description="Invalid format provided.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, example="Le format d'export spécifié est invalide. Doit être parmi: 'json', 'geojson', 'csv'.")
                    }
                ),
            ),
            404: openapi.Response(
                description="Project or Feature Type not found.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "detail": openapi.Schema(type=openapi.TYPE_STRING, example="Le projet ou type de signalement n'a pas été trouvé.")
                    }
                ),
            ),
            500: openapi.Response(
                description="Internal Server Error",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "error": openapi.Schema(type=openapi.TYPE_STRING, example="An unexpected error occurred during export.")
                    }
                ),
            ),
        }
    )
    def get(self, request, slug, feature_type_slug):
        # Try to retrieve the project
        try:
            project = Project.objects.get(slug=slug)
        except Project.DoesNotExist:
            return Response({"detail": "Le projet n'a pas été trouvé."}, status=status.HTTP_404_NOT_FOUND)

        # Try to retrieve the feature type
        try:
            feature_type = FeatureType.objects.get(slug=feature_type_slug)
        except FeatureType.DoesNotExist:
            return Response({"detail": "Le type de signalement n'a pas été trouvé."}, status=status.HTTP_404_NOT_FOUND)

        features = Feature.handy.availables(request.user, project).filter(
            feature_type=feature_type,
            # filter out features with a deletion date, since deleted features are not anymore deleted directly from database (https://redmine.neogeo.fr/issues/16246)
            deletion_on__isnull=True
        ).order_by("created_on")

        format = request.GET.get('format_export', 'geojson')

        if format == 'json':
            serializer = FeatureJSONSerializer(features, many=True, context={'request': request})
            response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export_projet.json'

        elif format == 'geojson':
            serializer = FeatureGeoJSONSerializer(features, many=True, context={'request': request})
            response = HttpResponse(json.dumps(serializer.data), content_type='application/json')
            response['Content-Disposition'] = 'attachment; filename=export_projet.geojson'

        elif format == 'csv':
            serializer = FeatureCSVSerializer(features, many=True, context={'request': request})
            response = HttpResponse(content_type='text/csv')
            response['Content-Disposition'] = 'attachment; filename=export_projet.csv'

            # Prepare CSV headers and initialize a CSV writer
            writer = csv.DictWriter(response, fieldnames=self.get_csv_headers(serializer, feature_type))
            writer.writeheader()

            # Write each feature to the CSV file
            for row in serializer.data:
                writer.writerow(self.prepare_csv_row(row, feature_type))
        else:
            return Response(
                {"error": "Le format d'export spécifié est invalide. Doit être parmi: 'json', 'geojson', 'csv'."},
                status=status.HTTP_400_BAD_REQUEST
            )

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
    @swagger_auto_schema(
        operation_summary= 'Retrieve a list of custom field types available',
        responses={
            200: openapi.Response(
                description="A list of custom field types.",
                examples={
                    "application/json": [
                        {"type": "boolean", "label": "Booléen"},
                    ]
                },
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            'type': openapi.Schema(type=openapi.TYPE_STRING),
                            'label': openapi.Schema(type=openapi.TYPE_STRING),
                        }
                    )
                )
            ),
        },
        tags=["feature types"]
    )
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
