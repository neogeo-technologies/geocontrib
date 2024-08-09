import logging
import uuid

from django.contrib.auth import get_user_model, login
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import mixins
from rest_framework import views
from rest_framework import viewsets
from rest_framework import permissions
from rest_framework.response import Response

from api.serializers import UserSerializer
from api.serializers import UserLevelsPermissionSerializer
from api.serializers import GeneratedTokenSerializer
from api.serializers.user import UserSerializer as DetailedUserSerializer
from geocontrib.models import Authorization
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission
from geocontrib.models import GeneratedToken

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

class GenerateTokenView(views.APIView):
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission
    def get(self, request):
        # get login, mail and name/surname if provided
        login = request.GET.get('login', '')
        mail = request.GET.get('mail', '')
        nom = request.GET.get('nom', '')
        prenom = request.GET.get('prenom', '')
        # generate & save token, login, mail,... in DB
        token = GeneratedToken.objects.create(
            username = login,
            email = mail,
            first_name = prenom,
            last_name = nom
        )
        # return the token
        token_data = GeneratedTokenSerializer(token).data
        return Response(data=token_data, status=200)
    
class LoginByTokenView(views.APIView):
    authentication_classes = [] # disables authentication
    permission_classes = [] # disables permission
    def get(self, request):
        # retrieve token
        token = request.GET.get('token', '')
        # check if token exist in bdd)
        queryset = GeneratedToken.objects.all().filter(token_sha256=token).first()
        if queryset:
            # check if token expire_on is previous to now
            if queryset.expire_on < timezone.now():
                # if token is not valid delete it and return error response
                queryset.delete()
                return Response(data="Le token fourni n'est plus valide", status=401)
            # check if a user exists already
            elif queryset.username:
                user = User.objects.all().filter(username=queryset.username).first()
                status = 200
                # if doesn't exist => create user
                if not user:
                    user = User.objects.create(
                        username=queryset.username,
                        first_name=queryset.first_name,
                        last_name=queryset.last_name,
                        email=queryset.email,
                    )
                    user.save()
                    status = 201
                # log the user
                login(request, user)
                user_data = DetailedUserSerializer(user).data
                return Response(data=user_data, status=status)

        return Response(data="Le token fourni n'a pas pu être authentifié", status=404)

class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all().order_by('-date_joined')
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Retrieve a list of users"
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Retrieve a specific user"
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Create a new user"
    )
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Update a specific user"
    )
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Partially update a specific user"
    )
    def partial_update(self, request, *args, **kwargs):
        return super().partial_update(request, *args, **kwargs)

    @swagger_auto_schema(
        tags=["users"],
        operation_summary="Delete a specific user"
    )
    def destroy(self, request, *args, **kwargs):
        return super().destroy(request, *args, **kwargs)


class UserLevelProjectView(views.APIView):
    """
    Retrieve the user level for each project.
    """

    permission_classes = [
        permissions.AllowAny,
    ]

    @swagger_auto_schema(
        operation_summary="Retrieve user levels for all projects",
        tags=["users"],
        responses={
            200: openapi.Response(
                description="A dictionary mapping project slugs to user levels.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_STRING,
                        example="Utilisateur anonyme"
                    ),
                    example={
                        "1-projet1": "Utilisateur anonyme",
                        "2-mon-projet": "Administrateur projet",
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Returns a dictionary where each key is a project slug and the value is the user's level within that project.
        """
        try:
            user_level_projects = Authorization.get_user_level_projects(request.user)
        except Exception:
            user_level_projects = {}

        return Response(data=user_level_projects, status=200)


class UserPermissionsView(views.APIView):
    """
    Retrieve permissions for the current user across all projects.
    """

    permission_classes = [
        permissions.AllowAny,
    ]

    @swagger_auto_schema(
        operation_summary="Retrieve user permissions for all projects",
        tags=["users"],
        responses={
            200: openapi.Response(
                description="A dictionary of permissions for each project.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    additional_properties=openapi.Schema(
                        type=openapi.TYPE_OBJECT,
                        properties={
                            "can_view_project": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_create_project": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_update_project": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_view_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_view_archived_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_create_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_update_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_delete_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_publish_feature": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_create_feature_type": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "can_view_feature_type": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "is_project_super_contributor": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "is_project_moderator": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                            "is_project_administrator": openapi.Schema(type=openapi.TYPE_BOOLEAN),
                        }
                    ),
                    example={
                        "1-projet1": {
                            "can_view_project": True,
                            "can_create_project": False,
                            "can_update_project": False,
                            "can_view_feature": True,
                            "can_view_archived_feature": False,
                            "can_create_feature": False,
                            "can_update_feature": False,
                            "can_delete_feature": False,
                            "can_publish_feature": False,
                            "can_create_feature_type": False,
                            "can_view_feature_type": True,
                            "is_project_super_contributor": False,
                            "is_project_moderator": False,
                            "is_project_administrator": False
                        }
                    }
                )
            )
        }
    )
    def get(self, request):
        """
        Returns a dictionary containing the permissions of the current user for each project.

        The key is the project slug, and the value is a list of permissions for that project.
        """
        data = {}
        user = request.user
        for project in Project.objects.all():
            data[project.slug] = Authorization.all_permissions(user, project)
        return Response(data=data, status=200)

class UserLevelsPermission(
        mixins.RetrieveModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    queryset = UserLevelPermission.objects.all()
    serializer_class = UserLevelsPermissionSerializer

    @swagger_auto_schema(
        operation_summary="Retrieve a specific user level permission",
        tags=["users"]
    )
    def retrieve(self, request, *args, **kwargs):
        return super().retrieve(request, *args, **kwargs)

    @swagger_auto_schema(
        operation_summary="List all user level permissions",
        tags=["users"]
    )
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)