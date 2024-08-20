from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import views
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response

from api.serializers import FeatureDetailedSerializer
from api.serializers import FeatureGeoJSONSerializer
from api.serializers import FeatureListSerializer
from api.serializers import FeatureTypeListSerializer
from api.utils.filters import FeatureTypeFilter
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project


User = get_user_model()


class FeatureViewDeprecated(
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
    
    @swagger_auto_schema(
        operation_summary="List features",
        tags=["[deprecated] features"],
        deprecated=True
    )
    def list(self, request):
        response = {}
        queryset = self.get_queryset()
        count = queryset.count()
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
                'count': count,
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
        tags=["[deprecated] features"],
        deprecated=True
    )
    def retrieve(self, request, *args, **kwargs):
        """
        Retrieves the details of a specific feature.
        """
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a feature",
        tags=["[deprecated] features"],
        deprecated=True
    )
    def create(self, request, *args, **kwargs):
        """
        Creates a new feature.
        """
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update a feature",
        tags=["[deprecated] features"],
        deprecated=True
    )
    def update(self, request, *args, **kwargs):
        """
        Updates an existing feature.
        """
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a feature",
        tags=["[deprecated] features"],
        deprecated=True
    )
    def partial_update(self, request, *args, **kwargs):
        """
        Partially updates an existing feature.
        """
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete a feature",
        tags=["[deprecated] features"],
        deprecated=True
    )
    def destroy(self, request, *args, **kwargs):
        """
        Marks a feature as deleted by setting its deletion_on field to the current date.
        """
        feature = self.get_object()
        feature.deletion_on = date.today()
        feature.save()
        message = {"message": "Le signalement a été supprimé"}
        return Response(message)


class FeatureTypeViewDeprecated(
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

    @swagger_auto_schema(
        operation_summary="List feature types",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve feature type",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create feature type",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Update feature type",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Partially update a feature type",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Delete feature type",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class ProjectFeatureTypesDeprecated(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    @swagger_auto_schema(
        operation_summary="Retrieve feature type from a project",
        tags=["[deprecated] feature types"],
        deprecated=True
    )
    def get(self, request, slug):
        feature_types = FeatureType.objects.filter(project__slug=slug).order_by("title")
        serializers = FeatureTypeListSerializer(feature_types, many=True)
        data = {
            'feature_types': serializers.data,
        }
        return Response(data, status=200)


class ProjectFeatureDeprecated(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    @swagger_auto_schema(
        operation_summary="Retrieve feature from a project",
        tags=["[deprecated] features"],
        deprecated=True
    )
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