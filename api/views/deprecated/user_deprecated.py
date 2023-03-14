import logging
import uuid

from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import mixins
from rest_framework import views
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from api.serializers import UserSerializer
from api.serializers import UserLevelsPermissionSerializer
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission

User = get_user_model()

class TokenView(views.APIView):
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get(self, request):
        user = request.user
        if user:
            token = request.user.token
            if not token:
                user.token = uuid.uuid4()
                user.save()
        else:
            logging.error(
                """
                    Impossible de générer le token car l'utilisateur
                    n'est pas connecté
                """
            )
            return Response(
                "Bad request : USER is missing",
                status=400
            )
        return Response(data=token, status=200)


@swagger_auto_schema(deprecated=True)
class UserViewSetDeprecated(viewsets.ModelViewSet):
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


@swagger_auto_schema(deprecated=True)
class UserLevelsPermissionDeprecated(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    
    queryset = UserLevelPermission.objects.all()
    serializer_class = UserLevelsPermissionSerializer
