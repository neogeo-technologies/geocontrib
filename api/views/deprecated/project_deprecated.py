from django.contrib.auth import get_user_model
from drf_yasg.utils import swagger_auto_schema
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import mixins

from api.serializers import ProjectDetailedSerializer
from geocontrib.models import Project

User = get_user_model()


@swagger_auto_schema(deprecated=True)
class ProjectTypesViewDeprecated(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):
    """
    Get all project-types
    """
    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    queryset = Project.objects.filter(is_project_type=True).order_by('-created_on')

    serializer_class = ProjectDetailedSerializer


