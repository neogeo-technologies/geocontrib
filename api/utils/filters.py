from django.db.models import Q
import json
from rest_framework import filters

from geocontrib.models import Authorization
from geocontrib.models import FeatureType
from geocontrib.models import ProjectAttributeAssociation

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

class ProjectsAttributeFilter(filters.BaseFilterBackend):
    """
    A filter backend that adjusts the queryset based on project attributes.
    It handles boolean attribute filters by including projects without an association 
    for the attribute when the filter value is 'false', and excludes projects 
    with the attribute set to 'true' when filtering for 'false'.
    """

    def filter_queryset(self, request, queryset, view):
        attributes = self._parse_attributes(request)
        if not attributes:
            return queryset.distinct()

        for attribute_id, value in attributes.items():
            if self._is_boolean(value):
                queryset = self._filter_boolean_attribute(queryset, attribute_id, value)
            else:
                queryset = self._filter_non_boolean_attribute(queryset, attribute_id, value)

        return queryset.distinct()

    def _parse_attributes(self, request):
        """Parse the JSON 'attributes' parameter from request."""
        attributes_param = request.query_params.get('attributes')
        if not attributes_param:
            return None
        try:
            return json.loads(attributes_param)
        except json.JSONDecodeError:
            return None

    def _is_boolean(self, value):
        """Check if the value is a string representing a boolean."""
        return value.lower() in ['true', 'false']

    def _filter_boolean_attribute(self, queryset, attribute_id, value):
        """Apply filtering for boolean attribute values."""
        is_true = value.lower() == 'true'
        if is_true:
            # Directly filter the projects that have an association with the value 'true'.
            return queryset.filter(
                projectattributeassociation__attribute_id=attribute_id,
                projectattributeassociation__value='true'
            )
        else:
            # Find projects that have a 'true' association for this attribute.
            projects_with_attr_true = ProjectAttributeAssociation.objects.filter(
                attribute_id=attribute_id,
                value='true'
            ).values_list('project_id', flat=True)
            # Exclude those projects from the queryset, effectively including projects without an association or with a 'false' value.
            return queryset.exclude(id__in=projects_with_attr_true)

    def _filter_non_boolean_attribute(self, queryset, attribute_id, value):
        """Apply filtering for non-boolean attribute values using OR logic."""
        # Split comma-separated string into a list of values
        list_values = value.split(',')
        # Initialize an empty Q object to start with no conditions
        query = Q()
        # Loop over each value and build OR conditions
        for list_value in list_values:
            query |= Q(
                projectattributeassociation__attribute_id=attribute_id,
                projectattributeassociation__value__icontains=list_value
            )
        # Apply the constructed OR conditions to the queryset.
        return queryset.filter(query)


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