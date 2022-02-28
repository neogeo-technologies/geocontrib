from django.conf import settings
from django.contrib.auth import get_user_model
from django.db.models import Q
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import Http404
from django.conf import settings
from rest_framework import filters
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import mixins

from api.serializers import ProjectDetailedSerializer
from api.serializers.project import ProjectCreationSerializer
from api.serializers.project import ProjectAuthorizationSerializer
from api.utils.permissions import ProjectThumbnailPermission
from api.utils.validators import validate_image_file
from api.utils.filters import AuthorizationLevelCodenameFilter
from api.utils.filters import ProjectsModerationFilter
from api.utils.filters import ProjectsAccessLevelFilter
from api.utils.filters import ProjectsUserAccessLevelFilter
from api.utils.filters import ProjectsUserAccessibleFilter
from api.utils.paginations import SimplePagination
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import Subscription
from geocontrib.models import FeatureType
from geocontrib.models import BaseMap


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
        ProjectsModerationFilter,
        ProjectsAccessLevelFilter,
        ProjectsUserAccessLevelFilter,
        ProjectsUserAccessibleFilter
    ]
    search_fields = [
        'slug',
        'title',
    ]

    def filter_queryset(self, queryset):
        myaccount = self.request.query_params.get('myaccount', None)
        user = self.request.user
        if myaccount and user :
            project_authorized = Authorization.objects.filter(user=user
            ).filter(
                level__rank__gte=2
            ).values_list('project__pk', flat=True)
            queryset = queryset.filter(Q(pk__in=project_authorized) | Q(creator=user))
        return queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return ProjectDetailedSerializer
        if self.action == 'create':
            return ProjectCreationSerializer
        if self.action in ['update', 'partial_update'] :
            return ProjectCreationSerializer
        return ProjectDetailedSerializer

    def get_permissions(self):
        if self.action == 'list':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ProjectTypesView(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    Get all project-types
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    queryset = Project.objects.filter(is_project_type=True).order_by('-created_on')

    serializer_class = ProjectDetailedSerializer


class ProjectDuplicate(APIView):
    http_method_names = ['post', ]
    serializer_class = ProjectCreationSerializer

    PROJECT_COPY_RELATED = getattr(settings, 'PROJECT_COPY_RELATED', {})

    def post(self, request, slug):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        if serializer.is_valid():
            project_template = Project.objects.filter(slug=slug).first()
            instance = serializer.save(creator=request.user)

            self._set_thumbnail(instance, serializer, project_template)
            self._set_creator(instance)
            self._duplicate_project_related_sets(instance, project_template)
            self._duplicate_project_base_map(instance, project_template)
            self._duplicate_project_authorization(instance, project_template)
            serializer.save()

            data = serializer.data
            status = 201
        else:
            data = serializer.errors
            status = 400
        return Response(data=data, status=status)

    def _duplicate_project_related_sets(self, instance, project_template):
        copy_feature_types = self.PROJECT_COPY_RELATED.get('FEATURE_TYPE', False)
        if project_template and isinstance(project_template, Project) and copy_feature_types:
            for feature_type in project_template.featuretype_set.all():
                # Pour manipuler une copie immuable
                legit_feature_type = FeatureType.objects.get(pk=feature_type.pk)
                feature_type.pk = None
                feature_type.project = instance
                feature_type.save()
                for custom_field in legit_feature_type.customfield_set.all():
                    custom_field.pk = None
                    custom_field.feature_type = feature_type
                    custom_field.save()

    def _duplicate_project_base_map(self, instance, project_template):
        copy_related = self.PROJECT_COPY_RELATED.get('BASE_MAP', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for base_map in project_template.basemap_set.all():
                legit_base_map = BaseMap.objects.get(pk=base_map.pk)
                base_map.pk = None
                base_map.project = instance
                base_map.save()
                for ctx_layer in legit_base_map.contextlayer_set.all():
                    ctx_layer.pk = None
                    ctx_layer.base_map = base_map
                    ctx_layer.save()

    def _duplicate_project_authorization(self, instance, project_template):
        """
        Un signale est deja en place pour appliquer les permissions initiales
        à la creation d'un projet:
        - createur = rank 4
        - autres = rank 1
        Ici on ecrase ces permissions initiales avec celles du projet type parent
        à l'exclusion de la permission relative au créateur de l'instance courante
        """
        copy_related = self.PROJECT_COPY_RELATED.get('AUTHORIZATION', False)
        if project_template and isinstance(project_template, Project) and copy_related:
            for auth in instance.authorization_set.exclude(user=instance.creator):
                auth.level = Authorization.objects.get(
                    user=auth.user, project=project_template).level
                auth.save()

    def _set_thumbnail(self, instance, form, project_template):
        copy_related = self.PROJECT_COPY_RELATED.get('THUMBNAIL', False)
        if hasattr(project_template, 'thumbnail') and copy_related:
            instance.thumbnail = project_template.thumbnail

    def _set_creator(self, instance):
        instance.creator = self.request.user
        return instance


class ProjectThumbnailView(APIView):
    parser_classes = [
        MultiPartParser,
        FormParser
    ]

    permission_classes = [
        ProjectThumbnailPermission,
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

    def get_object(self, *args, **kwargs):
        instance = get_object_or_404(Project, slug=self.kwargs.get('project__slug'))
        return instance

    def get_queryset(self, *args, **kwargs):
        instance = self.get_object()
        return self.queryset.filter(project=instance)

    def put(self, request, *args, **kwargs):
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
