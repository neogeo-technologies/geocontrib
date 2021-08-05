from django.db.models import F
from django.contrib.auth import get_user_model

from rest_framework.permissions import IsAuthenticated
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework.views import APIView
from rest_framework.response import Response

from api.serializers import ProjectSerializer
from api.serializers.project import ProjectCreationSerializer
from api.serializers import ProjectDetailedSerializer
from geocontrib.models import Authorization
from geocontrib.models import Project

User = get_user_model()


class ProjectView(mixins.ListModelMixin, mixins.CreateModelMixin, mixins.DestroyModelMixin, viewsets.GenericViewSet):

    queryset = Project.objects.all()
    serializer_class = ProjectDetailedSerializer
    permission_classes = [
        # permissions.IsAuthenticated,
        permissions.AllowAny,
    ]
    http_method_names = ['get', 'delete', 'post']
    lookup_field = 'slug'



class ProjectDetails(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Project.objects.all()
    serializer_class = ProjectCreationSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(creator=self.request.user)


class ProjectData(APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        projet = Project.objects.filter(slug=slug).values()
        data = { 'project_data': list(projet) }

        return Response(data=data, status=200)


class Projects(APIView):
    queryset = Project.objects.all()
    serializer_class = ProjectDetailedSerializer
    http_method_names = ['get', ]

    def get(self, request):
        projets = Project.objects.all()
        data = { 'projects': projets }

        return Response(data=data, status=200)


class ProjectDatas(APIView):
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
