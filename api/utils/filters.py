from logging import log
from django.db.models import Q
from django.shortcuts import get_object_or_404
from rest_framework import filters

from api.serializers import FeatureDetailedSerializer
from api.serializers import FeatureListSerializer
from geocontrib.models import Authorization
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project

class AuthorizationLevelCodenameFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        level__codename__in = request.query_params.get('level__codename__in')
        if level__codename__in:
            values = [param.strip() for param in level__codename__in.split(',')]
            queryset = queryset.filter(level__user_type_id__in=values)
        level__codename__not = request.query_params.get('level__codename__not')
        if level__codename__not:
            values = [param.strip() for param in level__codename__not.split(',')]
            queryset = queryset.exclude(level__user_type_id__in=values)
        return queryset

class ProjectsModerationFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        moderation = request.query_params.get('moderation')
        if moderation:
            if moderation == 'true':
                queryset = queryset.filter(moderation=True)
            if moderation == 'false':
                queryset = queryset.filter(moderation=False)
        return queryset

class ProjectsAccessLevelFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        access_level = request.query_params.get('access_level')
        if access_level:
            queryset = queryset.filter(access_level_pub_feature_id=access_level)
        return queryset

class ProjectsUserAccessLevelFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        user_level_projects = Authorization.get_user_level_projects_ids(request.user)
        user_access_level = request.query_params.get('user_access_level')
        if user_access_level:
            requested_user_access_level_projects = dict((k, v) for k, v in user_level_projects.items() if v == int(user_access_level))
            queryset = queryset.filter(slug__in =requested_user_access_level_projects.keys())
        return queryset

class ProjectsUserAccessibleFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        user_level_projects = Authorization.get_user_level_projects_ids(request.user)
        if request.query_params.get('accessible'):
            for i, c in enumerate(queryset):
                if (c.access_level_pub_feature.rank > user_level_projects[c.slug]):
                    queryset = queryset.exclude(slug=c.slug)
        return queryset

class ProjectsUserAccountFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        myaccount = request.query_params.get('myaccount', None)
        user = request.user
        if myaccount and user and not user.is_anonymous :
            project_authorized = Authorization.objects.filter(user=user
            ).filter(
                level__rank__gte=2
            ).values_list('project__pk', flat=True)
            queryset = queryset.filter(Q(pk__in=project_authorized) | Q(creator=user))
        return queryset

class ProjectsTypeFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        is_project_type = request.query_params.get('is_project_type')
        if is_project_type:
            if is_project_type == 'true':
                queryset = queryset.filter(is_project_type=True)
            if is_project_type == 'false':
                queryset = queryset.filter(is_project_type=False)
        return queryset


class FeatureTypeFilter(filters.BaseFilterBackend):

    def filter_queryset(self, request, queryset, view):
        slug = request.query_params.get('project__slug', None)
        if slug:
            queryset = FeatureType.objects.filter(
                project__slug=slug
                ).order_by("title")
        return queryset