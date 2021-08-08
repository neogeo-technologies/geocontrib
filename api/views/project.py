from django.db.models import F
from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404

from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from rest_framework.views import APIView

from api.serializers.project import ProjectCreationSerializer
from api.serializers import ProjectDetailedSerializer
from geocontrib.models import Authorization
from geocontrib.models import Project

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
    """
    Update thumbnail of a project
    """
    lookup_field = 'slug'
    queryset = Project.objects.all()
    http_method_names = ['put',]
    serializer = ProjectDetailedSerializer

    parser_classes = [MultiPartParser, FormParser]

    def put(self, request, slug):
        file_obj = request.data['file']
        project = get_object_or_404(Project, slug=slug)

        project.thumbnail = file_obj
        project.save()

        return Response(data=ProjectDetailedSerializer(project).data,
                        status=200)

class ProjectData(APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        projet = Project.objects.filter(slug=slug).values()
        data = { 'project_data': list(projet) }

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
