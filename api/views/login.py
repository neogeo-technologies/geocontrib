import logging

from django.contrib.auth import authenticate, login
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.exceptions import AuthenticationFailed
from rest_framework.response import Response

from api.serializers.signin import SigninSerializer
from api.serializers.user import UserSerializer


User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(views.APIView):

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    serializer_class = SigninSerializer

    def post(self, request):
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

