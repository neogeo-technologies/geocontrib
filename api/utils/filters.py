from rest_framework import filters


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
