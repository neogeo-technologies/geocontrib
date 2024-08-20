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
    """
    Retrieve or generate the mobile app authentication token for the authenticated user.
    
    This token is used specifically for generating a QR code that allows the user to authenticate in the mobile app.
    If the user does not already have a token, a new one will be generated and returned.
    """

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    @swagger_auto_schema(
        operation_summary="Retrieve or generate a mobile app authentication token",
        tags=["auth"],
        responses={
            200: openapi.Response(
                description="The user's token, either retrieved or newly generated.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="19535786-698b-44ce-9d61-2077f7642a1d"
                ),
                examples={
                    "application/json": "19535786-698b-44ce-9d61-2077f7642a1d"
                }
            ),
            400: openapi.Response(
                description="Bad request: User is missing or not authenticated.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Bad request : USER is missing"
                )
            ),
        }
    )
    def get(self, request):
        """
        Retrieve the token for the authenticated user.
        If the token does not exist, generate a new one and save it to the user profile.
        """
        user = request.user
        if user:
            token = user.token
            if not token:
                token = uuid.uuid4()
                user.token = token
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
        return Response(data=str(token), status=200)


class GenerateTokenView(views.APIView):
    """
    Generate an access token for authenticating the user on an external platform.
    
    This token is generated based on the user's credentials from another platform and is used to authenticate the user within the GeoContrib application.
    After generating this token, the external platform can redirect the user to GeoContrib with the token in the URL to seamlessly log the user into the application.
    """
    authentication_classes = [] #disables authentication
    permission_classes = [] #disables permission

    @swagger_auto_schema(
        operation_summary="Generate a token for external platform authentication",
        tags=["auth"],
        manual_parameters=[
            openapi.Parameter(
                'login',
                openapi.IN_QUERY,
                description="The user's login",
                type=openapi.TYPE_STRING,
                required=True,
            ),
            openapi.Parameter(
                'mail',
                openapi.IN_QUERY,
                description="The user's email",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'nom',
                openapi.IN_QUERY,
                description="The user's last name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
            openapi.Parameter(
                'prenom',
                openapi.IN_QUERY,
                description="The user's first name",
                type=openapi.TYPE_STRING,
                required=False,
            ),
        ],
        responses={
            200: openapi.Response(
                description="Token successfully generated.",
                schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "token_sha256": openapi.Schema(type=openapi.TYPE_STRING, example="7ad01429e095a442dc9296abc12d675694f8569f3024e39f6112286ec215dfb9"),
                        "username": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                        "email": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe@example.com"),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
                        "expire_on": openapi.Schema(type=openapi.TYPE_STRING, format="date-time", example="2024-08-31T12:34:56Z"),
                    }
                ),
                examples={
                    "application/json": {
                        "token_sha256": "7ad01429e095a442dc9296abc12d675694f8569f3024e39f6112286ec215dfb9",
                        "expire_on": "2024-08-31T12:34:56Z",
                        "username": "johndoe",
                        "first_name": "John",
                        "last_name": "Doe",
                        "email": "johndoe@example.com"
                    }
                }
            )
        }
    )
    def get(self, request):
        # get login, mail and name/surname if provided
        login = request.GET.get('login', '')
        mail = request.GET.get('mail', '')
        nom = request.GET.get('nom', '')
        prenom = request.GET.get('prenom', '')

        # generate & save token, login, mail, etc., in DB
        token = GeneratedToken.objects.create(
            username=login,
            email=mail,
            first_name=prenom,
            last_name=nom
        )

        # return the token
        token_data = GeneratedTokenSerializer(token).data
        return Response(data=token_data, status=200)

# Response datas for swagger documentation
swagger_login_token_schema=openapi.Schema(
                    type=openapi.TYPE_OBJECT,
                    properties={
                        "username": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe"),
                        "is_active": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=True),
                        "first_name": openapi.Schema(type=openapi.TYPE_STRING, example="John"),
                        "last_name": openapi.Schema(type=openapi.TYPE_STRING, example="Doe"),
                        "is_administrator": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "is_superuser": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "can_create_project": openapi.Schema(type=openapi.TYPE_BOOLEAN, example=False),
                        "email": openapi.Schema(type=openapi.TYPE_STRING, example="johndoe@example.com"),
                        "id": openapi.Schema(type=openapi.TYPE_INTEGER, example=6),
                    }
                )
swagger_login_token_example={
                    "application/json": {
                        "username": "johndoe",
                        "is_active": True,
                        "first_name": "John",
                        "last_name": "Doe",
                        "is_administrator": False,
                        "is_superuser": False,
                        "can_create_project": False,
                        "email": "johndoe@example.com",
                        "id": 6
                    }
                }
class LoginByTokenView(views.APIView):
    """
    Authenticates a user via a token generated by GeoContrib (api/generatetoken/) based on user information provided by an external platform.
    
    This token is passed in the URL by the external platform, enabling the user to log in to GeoContrib without re-entering credentials.
    """
    authentication_classes = [] # disables authentication
    permission_classes = [] # disables permission

    @swagger_auto_schema(
    operation_summary="Authenticate user using a token generated by GeoContrib at the request of an external platform.",
        tags=["auth"],
        manual_parameters=[
            openapi.Parameter(
                'token',
                openapi.IN_QUERY,
                description="The token used for authentication",
                type=openapi.TYPE_STRING,
                required=True,
            )
        ],
        responses={
            200: openapi.Response(
                description="User successfully authenticated and logged in.",
                schema=swagger_login_token_schema,
                examples=swagger_login_token_example
            ),
            201: openapi.Response(
                description="New user created and logged in.",
                schema=swagger_login_token_schema,
                examples=swagger_login_token_example
            ),
            401: openapi.Response(
                description="Token is expired and no longer valid.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Le token fourni n'est plus valide"
                )
            ),
            404: openapi.Response(
                description="Token not found or cannot be authenticated.",
                schema=openapi.Schema(
                    type=openapi.TYPE_STRING,
                    example="Le token fourni n'a pas pu être authentifié"
                )
            )
        }
    )
    def get(self, request):
        # retrieve token
        token = request.GET.get('token', '')
        # check if token exists in the database
        queryset = GeneratedToken.objects.all().filter(token_sha256=token).first()
        if queryset:
            # check if token's expire_on is earlier than now
            if queryset.expire_on < timezone.now():
                # if token is not valid, delete it and return error response
                queryset.delete()
                return Response(data="Le token fourni n'est plus valide", status=401)
            # check if a user already exists
            elif queryset.username:
                user = User.objects.all().filter(username=queryset.username).first()
                status = 200
                # if user doesn't exist, create a new user
                if not user:
                    user = User.objects.create(
                        username=queryset.username,
                        first_name=queryset.first_name,
                        last_name=queryset.last_name,
                        email=queryset.email,
                    )
                    user.save()
                    status = 201
                # log the user in
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