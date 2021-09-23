import logging

from django.db.models import Q
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth import get_user_model
from django.utils.translation import gettext_lazy as _
from rest_framework import permissions
from rest_framework import status
from rest_framework import views
from rest_framework.exceptions import AuthenticationFailed, NotAuthenticated
from rest_framework.response import Response

from geocontrib import choices

from api.serializers import EventSerializer
from api.serializers import ProjectDetailedSerializer
from api.serializers.signin import SigninSerializer
from api.serializers.user import UserSerializer
from api.serializers.user import UserLevelPermissionSerializer
from api.serializers.user import AuthorizationSerializer
from geocontrib.models import Authorization
from geocontrib.models import Event
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission


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

class UserInfoView(views.APIView):

    def get(self, request):
        user = request.user
        if not user or user.is_anonymous:
            raise NotAuthenticated()
        data = {
            "detail": _(f"{user.username} session is enabled"),
            "user":  UserSerializer(user).data
        }
        return Response(data=data, status=status.HTTP_200_OK)


class LogoutView(views.APIView):
#class SignoutView(views.APIView):

    permission_classes = [
        permissions.IsAuthenticated,
        #permissions.AllowAny,
    ]

    def get(self, request):
        username = request.user.username
        logout(request)
        data = {"detail": _(f"{username} signed out")}
        return Response(data=data, status=status.HTTP_200_OK)


class MyAccountView(views.APIView):

    def get(self, request):
        data = {}
        user = request.user
        # data['user'] = user

        # on liste les droits de l'utilisateur pour chaque projet
        data['permissions'] = {}
        data['rank'] = {}
        for project in Project.objects.all():
            data['permissions'][project.slug] = Authorization.has_permission(
                user, 'can_view_project', project)
            
            try:
                rank = Authorization.objects.get(project=project, user=user).level
                rank = AuthorizationSerializer(rank).data
            except Exception:
                if user.is_superuser:
                    usertype = choices.ADMIN
                else:
                    usertype = choices.LOGGED_USER
                serializer_rank = UserLevelPermission.objects.get(user_type_id=usertype)
                rank = UserLevelPermissionSerializer(serializer_rank).data

            data['rank'][project.slug] = rank

        project_authorized = Authorization.objects.filter(
            user=user
        ).filter(
            level__rank__lte=2
        ).values_list('project__pk', flat=True)
        serialized_projects = ProjectDetailedSerializer(
            Project.objects.filter(
                Q(pk__in=project_authorized) | Q(creator=user)
            ).order_by('-created_on'), many=True)

        all_events = Event.objects.filter(user=user).order_by('-created_on')
        serialized_events = EventSerializer(all_events[0:5], many=True)

        feature_events = Event.objects.filter(
            user=user, object_type='feature').order_by('-created_on')
        serialized_feature_events = EventSerializer(feature_events[0:5], many=True)

        comment_events = Event.objects.filter(
            user=user, object_type='comment').order_by('-created_on')
        serialized_comment_events = EventSerializer(comment_events[0:5], many=True)

        data['projects'] = serialized_projects.data
        data['events'] = serialized_events.data
        data['features'] = serialized_feature_events.data
        data['comments'] = serialized_comment_events.data
        data['title'] = "Mon compte"

        return Response(data=data, status=status.HTTP_200_OK)
