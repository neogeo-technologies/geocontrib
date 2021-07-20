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
# from auth.tokens import simple_token


User = get_user_model()
logger = logging.getLogger(__name__)


class LoginView(views.APIView):

    authentication_classes = []

    permission_classes = [
        permissions.AllowAny,
    ]

    serializer_class = SigninSerializer

    def post(self, request):
        print
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
            # "token": simple_token.make_token(
            #     {"id": user.pk, "username": user.username},
            #     access_token_lifetime=1
            # )
        }
        return Response(data=data, status=status.HTTP_200_OK)


class CheckSigninView(views.APIView):

    permission_classes = [
        permissions.AllowAny,
    ]

    def get(self, request):
        user = request.user
        if user.is_authenticated:
            serializer = UserSerializer(user)
            data = {
                "detail": _(f"{user.username} session is active"),
                "user": serializer.data,
                "authenticated": True,
            }
        else:
            data = {
                "detail": _("no session active"),
                "authenticated": False,
            }
        return Response(data=data, status=status.HTTP_200_OK)


# import json
# 
# from django.contrib.auth import login
# from django.views.decorators.http import require_POST
# from django.http import JsonResponse
# 
# @require_POST
# def login_view(request):
#     """
#     This function logs in the user and returns
#     and HttpOnly cookie, the `sessionid` cookie
#     """
#     print("MYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMYMY ≠≠≠> REQUEST:BODY ===", request.body)
#     data = json.loads(request.body)
#     email = data.get("email")
#     password = data.get("password")
#     if email is None or password is None:
#         return JsonResponse(
#             {"errors": {"__all__": "Please enter both username and password"}},
#             status=400,
#         )
#     user = authenticate(email=email, password=password)
#     if user is not None:
#         login(request, user)
#         request.session['foo'] = "bar"
#         return JsonResponse({"detail": "Success"})
#     return JsonResponse({"detail": "Invalid credentials"}, status=400)
# 
