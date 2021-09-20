from django.contrib.auth import get_user_model
from django.db.models import F
from django.http import FileResponse
from django.shortcuts import get_object_or_404
from django.shortcuts import Http404
from django.conf import settings
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers import ProjectDetailedSerializer
from api.serializers.project import ProjectCreationSerializer
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


class ProjectAuthorization(APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):

        members = Authorization.objects.filter(project__slug=slug).annotate(
            user_pk=F('user__pk'),
            email=F('user__email'),
            username=F('user__username'),
            first_name=F('user__first_name'),
            last_name=F('user__last_name'),
        ).values(
            'user_pk', 'email', 'username', 'first_name', 'last_name',
        )

        others = User.objects.filter(
            is_active=True
        ).exclude(
            pk__in=[mem.get('user_pk') for mem in members]
        ).values(
            'pk', 'email', 'username', 'first_name', 'last_name'
        )
        data = {
            'members': list(members),
            'others': list(others),
        }
        return Response(data=data, status=200)


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
