from django.contrib.auth import get_user_model
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import Http404
from django.conf import settings
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import generics
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ProjectDetailedSerializer
from api.serializers.project import ProjectCreationSerializer
from api.serializers.project import ProjectAuthorizationSerializer
from api.utils.permissions import ProjectThumbnailPermission
from api.utils.validators import validate_image_file
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import Subscription

User = get_user_model()


class ProjectView(viewsets.ModelViewSet):
    """
    Get all project and can create one
    """
    lookup_field = 'slug'
    queryset = Project.objects.all()

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
