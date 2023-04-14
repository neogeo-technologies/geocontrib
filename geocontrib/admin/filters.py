from django.contrib.admin.filters import SimpleListFilter
from django.db.models import Q

from geocontrib.models import Project
from geocontrib.models import FeatureType


class ProjectFilter(SimpleListFilter):
    template = 'admin/geocontrib/dropdown_filter.html'

    # Filter title
    title = 'Projets'

    # url param
    parameter_name = 'project__id'

    def lookups(self, request, model_admin):
        return Project.objects.all().values_list('pk', 'title')

    def queryset(self, request, queryset):
        if self.value():
            return queryset.filter(
                Q(feature_from__project__pk=self.value()) | Q(feature_to__project__pk=self.value())
            )

        return queryset


class FeatureTypeFilter(SimpleListFilter):
    template = 'admin/geocontrib/dropdown_filter.html'

    # Filter title
    title = 'Type de signalement'

    # url param
    parameter_name = 'feature_type__id'

    def lookups(self, request, model_admin):
        return FeatureType.objects.all().values_list('pk', 'title')

    def queryset(self, request, queryset):
        # Si filtre il y'a
        if self.value():
            return queryset.filter(
                Q(feature_from__feature_type__pk=self.value()) | Q(feature_to__feature_type__pk=self.value())
            )

        return queryset
