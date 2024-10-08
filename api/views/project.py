from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.base import ContentFile
from django.http import FileResponse
from django.http import JsonResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import Http404
from django.conf import settings
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import exceptions
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ProjectDetailedSerializer
from api.serializers import ProjectAttributeSerializer
from api.serializers import ProjectCreationSerializer
from api.serializers import ProjectAuthorizationSerializer
from api.utils.permissions import ProjectPermission
from api.utils.validators import validate_image_file
from api.utils.filters import AuthorizationLevelCodenameFilter
from api.utils.filters import ProjectsModerationFilter
from api.utils.filters import ProjectsAccessLevelFilter
from api.utils.filters import ProjectsTypeFilter
from api.utils.filters import ProjectsUserAccessLevelFilter
from api.utils.filters import ProjectsUserAccessibleFilter
from api.utils.filters import ProjectsUserAccountFilter
from api.utils.filters import ProjectsAttributeFilter
from api.utils.paginations import SimplePagination
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.models import FeatureType
from geocontrib.models import BaseMap
from geocontrib.models import ProjectAttribute


User = get_user_model()


class ProjectView(viewsets.ModelViewSet):
    """
    Get all project and can create one
    """
    lookup_field = 'slug'
    pagination_class = SimplePagination
    queryset = Project.objects.all().order_by('-created_on')

    filter_backends = [
        filters.SearchFilter,
        ProjectsTypeFilter,
        ProjectsModerationFilter,
        ProjectsAccessLevelFilter,
        ProjectsUserAccessLevelFilter,
        ProjectsUserAccessibleFilter,
        ProjectsUserAccountFilter,
        ProjectsAttributeFilter
    ]
    search_fields = [
        'slug',
        'title',
    ]

    def get_serializer_class(self):
        if self.action == 'list' or self.action == 'retrieve':
            return ProjectDetailedSerializer
        if self.action == 'create':
            return ProjectCreationSerializer
        if self.action in ['update', 'partial_update']:
            return ProjectCreationSerializer
        return ProjectDetailedSerializer

    def get_permissions(self):
        if self.action == 'list' or self.action == 'retrieve':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)

    @swagger_auto_schema(
        operation_summary="Delete project",
        tags=["projects"]
    )
    def destroy(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)
        perms = Authorization.all_permissions(self.request.user, project)
        if perms and (self.request.user.is_superuser or perms['is_project_administrator']):
            return super().destroy(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    @swagger_auto_schema(
        operation_summary="Update project",
        tags=["projects"]
    )
    def update(self, request, *args, **kwargs):
        slug = self.kwargs.get('slug')
        project = get_object_or_404(Project, slug=slug)
        perms = Authorization.all_permissions(self.request.user, project)
        if perms and (self.request.user.is_superuser or perms['is_project_administrator']):
            return super().update(request, *args, **kwargs)
        raise exceptions.PermissionDenied

    @swagger_auto_schema(
        operation_summary="Partially update a project",
        tags=["projects"]
    )
    def partial_update(self, request, *args, **kwargs):
        return self.update(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Create a project",
        tags=["projects"]
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List projects",
        tags=["projects"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="Retrieve project",
        tags=["projects"]
    )
    def retrieve(self, request, *args, **kwargs):
        response = super().retrieve(request, *args, **kwargs)
        # Add a CORS header to allow requesting a project from any other domain, like a web-component embed in another website
        response["Access-Control-Allow-Origin"] = "*"
        return response


class ProjectDuplicate(APIView):
    """
    Duplicate a project.

    This endpoint allows authenticated users to create a duplicate of an existing project,
    including related features such as thumbnails, base maps, and authorizations, depending
    on settings.
    """
    
    http_method_names = ['post']
    serializer_class = ProjectCreationSerializer
    permission_classes = (permissions.IsAuthenticated,)

    PROJECT_COPY_RELATED = getattr(settings, 'PROJECT_COPY_RELATED', {})

    @swagger_auto_schema(operation_summary="Duplicate an existing project")
    def post(self, request, slug):
        # Fetch the template project to be duplicated
        project_template = get_object_or_404(Project, slug=slug)

        # Validate and deserialize input data
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            # Save the new project instance
            instance = serializer.save(creator=request.user)

            # Duplicate related project data
            self._set_creator(instance)
            self._duplicate_project_thumbnail(instance, project_template)
            self._duplicate_project_related_sets(instance, project_template)
            self._duplicate_project_base_map(instance, project_template)
            self._duplicate_project_authorization(instance, project_template)
            serializer.save()

            data = serializer.data
            status = 201
        else:
            data = serializer.errors
            status = 400
        
        # Return the response with the appropriate status
        return Response(data=data, status=status)

    def _duplicate_project_related_sets(self, instance, project_template):
        copy_feature_types = self.PROJECT_COPY_RELATED.get('FEATURE_TYPE', False)
        if project_template and isinstance(project_template, Project) and copy_feature_types:
            for feature_type in project_template.featuretype_set.all():
                # Retrieve a fresh copy of the feature type
                legit_feature_type = FeatureType.objects.get(pk=feature_type.pk)
                feature_type.pk = None  # Clear the primary key to create a new instance
                feature_type.project = instance
                feature_type.save()
                for custom_field in legit_feature_type.customfield_set.all():
                    custom_field.pk = None  # Clear the primary key for the new custom field
                    custom_field.feature_type = feature_type
                    custom_field.save()

    def _duplicate_project_base_map(self, instance, project_template):
        copy_related = self.PROJECT_COPY_RELATED.get('BASE_MAP', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for base_map in project_template.basemap_set.all():
                legit_base_map = BaseMap.objects.get(pk=base_map.pk)
                base_map.pk = None  # Clear the primary key to create a new instance
                base_map.project = instance
                base_map.save()
                for ctx_layer in legit_base_map.contextlayer_set.all():
                    ctx_layer.pk = None  # Clear the primary key for the new context layer
                    ctx_layer.base_map = base_map
                    ctx_layer.save()

    def _duplicate_project_thumbnail(self, instance, project_template):
        copy_related = self.PROJECT_COPY_RELATED.get('THUMBNAIL', True)
        if project_template and isinstance(project_template, Project) and copy_related:
            original_thumbnail = project_template.thumbnail  # Get the original thumbnail object
            new_thumbnail_name = original_thumbnail.name.split('/')[-1]  # Extract the file name
            new_thumbnail_file = original_thumbnail.file.read()  # Copy the file content
            new_file = ContentFile(new_thumbnail_file, new_thumbnail_name)  # Create a new file object
            instance.thumbnail = new_file  # Assign the new thumbnail to the instance
            instance.save()

    def _duplicate_project_authorization(self, instance, project_template):
        """
        Duplicates the authorization levels from the original project to the new 
        project instance, except for the creator of the current instance.
        """
        copy_related = self.PROJECT_COPY_RELATED.get('AUTHORIZATION', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for auth in instance.authorization_set.exclude(user=instance.creator):
                auth.level = Authorization.objects.get(
                    user=auth.user, project=project_template).level
                auth.save()

    def _set_creator(self, instance):
        """
        Assigns the current user as the creator of the duplicated project.
        """
        instance.creator = self.request.user
        return instance


class ProjectThumbnailView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    permission_classes = [
        ProjectPermission,
    ]

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        try:
            response = FileResponse(open(project.thumbnail.path, 'rb'))
        except Exception:
            raise Http404
        return response

    def put(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        file_obj = request.data.get('file')
        # Pour ne pas bloqué l'install ideobfc:
        if getattr(settings, 'MAGIC_IS_AVAILABLE', False):
            validate_image_file(file_obj)
        project.thumbnail = file_obj
        project.save(update_fields=['thumbnail', ])
        data = ProjectDetailedSerializer(project).data
        return Response(data=data, status=200)


class ProjectAuthorizationView(generics.ListAPIView, generics.UpdateAPIView):

    queryset = Authorization.objects.select_related('user', 'level').all()

    serializer_class = ProjectAuthorizationSerializer

    lookup_field = 'project__slug'

    filter_backends = [
        AuthorizationLevelCodenameFilter,
    ]

    permission_classes = [
        ProjectPermission,
    ]

    def get_object(self, *args, **kwargs):
        instance = get_object_or_404(Project, slug=self.kwargs.get('project__slug'))
        return instance

    def get_queryset(self, *args, **kwargs):
        instance = self.get_object()
        return self.queryset.filter(project=instance)

    def put(self, request, *args, **kwargs):
        instance = self.get_object()
        self.check_object_permissions(self.request, instance)
        data = request.data
        serializer = ProjectAuthorizationSerializer(data=data, many=True)
        if serializer.is_valid():
            project = self.get_object()
            serializer.bulk_edit(project)
            data = serializer.data
            status = 200
        else:
            data = serializer.errors
            status = 400
        return Response(data=data, status=status)


class ProjectSubscription(APIView):

    permission_classes = (
        permissions.IsAuthenticated,
    )

    def get(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        data = {'is_suscriber': Subscription.is_suscriber(request.user, project)}
        return Response(data=data, status=200)

    def put(self, request, slug):
        project = get_object_or_404(Project, slug=slug)
        is_suscriber = request.data.get('is_suscriber', None)
        if is_suscriber is True:
            obj, _created = Subscription.objects.get_or_create(
                project=project,
            )
            obj.users.add(request.user)
            obj.save()
        if is_suscriber is False:
            try:
                obj = Subscription.objects.get(project=project)
            except Subscription.DoesNotExist:
                pass
            else:
                obj.users.remove(request.user)
                obj.save()
        data = {'is_suscriber': Subscription.is_suscriber(request.user, project)}
        return Response(data=data, status=200)


class ProjectAttributeListView(generics.ListAPIView):
    """
    View to list all project attributes.
    """

    queryset = ProjectAttribute.objects.all()
    serializer_class = ProjectAttributeSerializer

    @swagger_auto_schema(
        operation_summary="List all project attributes",
        tags=["projects"],
        manual_parameters=[
            openapi.Parameter(
                'project_id',
                openapi.IN_QUERY,
                description="Filter attributes by project ID",
                type=openapi.TYPE_INTEGER,
                required=False
            ),
            openapi.Parameter(
                'name',
                openapi.IN_QUERY,
                description="Filter attributes by name",
                type=openapi.TYPE_STRING,
                required=False
            ),
        ],
        responses={
            200: openapi.Response(
                description="A list of project attributes.",
                schema=openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=1),
                            "label": openapi.Schema(type=openapi.TYPE_STRING, example="Actif"),
                            "name": openapi.Schema(type=openapi.TYPE_STRING, example="active"),
                            "field_type": openapi.Schema(type=openapi.TYPE_STRING, example="boolean"),
                            "options": openapi.Schema(type=openapi.TYPE_STRING, nullable=True, example=None),
                            "default_value": openapi.Schema(type=openapi.TYPE_STRING, example="true"),
                            "display_filter": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                            "default_filter_enabled": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                            "default_filter_value": openapi.Schema(type=openapi.TYPE_STRING, example="false"),
                        }
                    )
                ),
                examples={
                    "application/json": [
                        {
                            "id": 1,
                            "label": "Actif",
                            "name": "active",
                            "field_type": "boolean",
                            "options": None,
                            "default_value": "true",
                            "display_filter": False,
                            "default_filter_enabled": False,
                            "default_filter_value": "false"
                        }
                    ]
                }
            ),
            400: openapi.Response(
                description="Bad Request",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Invalid request parameters."
                )
            )
        }
    )
    def get(self, request, *args, **kwargs):
        """
        Retrieve a list of project attributes, with optional filters by project ID and name.
        """
        return super().get(request, *args, **kwargs)