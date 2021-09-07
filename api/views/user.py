# from django.contrib.auth.models import User
from django.contrib.auth import get_user_model
from rest_framework import views
from rest_framework import viewsets
from rest_framework import permissions
from api.serializers import UserSerializer
from geocontrib.models import Authorization
from geocontrib.models import Project
from rest_framework.response import Response

User = get_user_model()


class UserViewSet(viewsets.ModelViewSet):
    """
    API endpoint that allows users to be viewed or edited.
    """
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

class UserLevelProjectView(views.APIView):
    permission_classes = [
        permissions.AllowAny,
        # permissions.IsAuthenticated,
    ]

    def get(self, request):
        try:
            user_level_projects = Authorization.get_user_level_projects(request.user)
        except Exception:
            user_level_projects = {}

        return Response(data=user_level_projects, status=200)


class UserPermissionsView(views.APIView):
    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request):
        data = {}
        user = request.user
        for project in Project.objects.all():
            data[project.slug] = Authorization.all_permissions(user, project)
        return Response(data=data, status=200)
