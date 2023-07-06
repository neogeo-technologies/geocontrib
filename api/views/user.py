import logging
import uuid

from django.contrib.auth import get_user_model, login
from django.utils import timezone
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

class UserLevelsPermission(mixins.RetrieveModelMixin,
                            mixins.ListModelMixin,
                            viewsets.GenericViewSet):
    
    queryset = UserLevelPermission.objects.all()
    serializer_class = UserLevelsPermissionSerializer
