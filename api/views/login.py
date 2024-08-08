import logging
import requests

from django.conf import settings
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response

from api.serializers.signin import SigninSerializer
from api.serializers.user import UserSerializer


User = get_user_model()
logger = logging.getLogger(__name__)

# Data to fill responses in swagger doc
user_login_responses ={
    200: openapi.Response(
        description="OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'detail': openapi.Schema(type=openapi.TYPE_STRING, description='Detail message'),
                'user': openapi.Schema(type=openapi.TYPE_OBJECT, description='User data', example={
                    "username": "user1",
                    "is_active": True,
                    "first_name": "",
                    "last_name": "",
                    "is_administrator": False,
                    "is_superuser": False,
                    "can_create_project": True,
                    "email": "user1@example.com",
                    "id": 1
                })
            }
        )
    ),
    400: openapi.Response(
        description="Bad Request",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "username": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Username validation errors"
                ),
                "password": openapi.Schema(
                    type=openapi.TYPE_ARRAY,
                    items=openapi.Items(type=openapi.TYPE_STRING),
                    description="Password validation errors"
                ),
            },
            example={
                "username": ["Ce champ est obligatoire."],
                "password": ["Ce champ est obligatoire."]
            }
        )
    ),
    403: openapi.Response(
        description="Forbidden",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
            },
            example={"detail": "Informations d'authentification incorrectes."}
        )
    ),
}

user_logout_responses = {
    200: openapi.Response(
        description="OK",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Detail message")
            },
            example={"detail": "user1 signed out"}
        )
    ),
    403: openapi.Response(
        description="Forbidden",
        schema=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                "detail": openapi.Schema(type=openapi.TYPE_STRING, description="Error message")
            },
            example={"detail": "Informations d'authentification incorrectes."}
        )
    ),
}

class LoginView(views.APIView):
    """
    Login view to authenticate a user and start a session.
    """
    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    serializer_class = SigninSerializer

    @swagger_auto_schema(
        operation_description="",
        operation_summary="Authenticate a user and start a session.",
        tags=["auth"],
        request_body=SigninSerializer,
        responses=user_login_responses
    )
    def post(self, request):
        """
        Authenticates a user with username and password.
        """
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        username = serializer.data['username']
        password = serializer.data['password']
        user = authenticate(username=username, password=password)
        if not user or not user.is_active:
            raise AuthenticationFailed()

        login(request, user)
        data = {
            "detail": _(f"{user.username} session is enabled"),
            "user":  UserSerializer(user).data
        }
        return Response(data=data, status=status.HTTP_200_OK)

class UserInfoView(views.APIView):
    """
    API view to retrieve user information.

    This view handles two scenarios:
    1. If the user is already authenticated in the Django application, it returns the user information.
    2. If the user is not authenticated and SSO with OGS is configured, it checks the OGS session.
       - If the OGS session is active, it authenticates or creates the user in Django and returns the user information.
    Else it raises a not authenticated error
    """
    @swagger_auto_schema(
        operation_summary="Authenticate a user and start a session.",
        tags=["auth"],
        responses=user_login_responses
    )
    def get(self, request):
        user = request.user

        # Check if the user is already authenticated in Django
        if user and not user.is_anonymous:
            data = {
                "detail": f"{user.username} session is enabled",
                "user": UserSerializer(user).data
            }
            return Response(data=data, status=status.HTTP_200_OK)

        # If the user is not authenticated, check the OGS session if configured
        elif settings.SSO_OGS_SESSION_URL:
            session_id = request.COOKIES.get('sessionid')

            # If a session cookie for OGS is found
            if session_id:
                # Call the OGS session endpoint with the session cookie
                response = requests.get(settings.SSO_OGS_SESSION_URL, cookies={'sessionid': session_id})

                # If the response from OGS is successful
                if response.status_code == 200:
                    data = response.json()
                    username = data.get('user').get('username')

                    # If the username is found in the response, authenticate or create the user in Django
                    if username:
                        user, created = User.objects.get_or_create(username=username)
                        if created:
                            user.save()
                        login(request, user)
                        data = {
                            "detail": f"{user.username} session is enabled",
                            "user": UserSerializer(user).data
                        }
                        return Response(data=data, status=status.HTTP_200_OK)
        
        # If no authentication method is available, raise an error
        raise NotAuthenticated()

class LogoutView(views.APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]
    def logout_user(self):
        username = self.request.user.username
        logout(self.request)
        return {"detail": _(f"{username} signed out")}

    @swagger_auto_schema(
        operation_description="",
        operation_summary="Logs out current logged in user session",
        tags=["auth"],
        responses=user_logout_responses
    )
    def get(self, request):
        return Response(data=self.logout_user(), status=status.HTTP_200_OK)

    @swagger_auto_schema(
        operation_description="",
        operation_summary="Logs out current logged in user session",
        tags=["auth"],
        responses=user_logout_responses
    )
    def post(self, request):
        return Response(data=self.logout_user(), status=status.HTTP_200_OK)