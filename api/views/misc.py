from rest_framework import mixins
from rest_framework import viewsets
from api.serializers.misc import ImportTaskSerializer
from geocontrib.models.task import ImportTask


class ImportTaskSearch(
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    queryset = ImportTask.objects.all()

    serializer_class = ImportTaskSerializer

    http_method_names = ['get', ]

    def filter_queryset(self, queryset):
        status = self.request.query_params.get('status')
        feature_type_id = self.request.query_params.get('feature_type_id')
        if status:
            queryset = queryset.filter(status__icontains=status)
        if feature_type_id:
            queryset = queryset.filter(feature_type__pk=feature_type_id)
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        # NB filter_queryset() bien appelé par ListModelMixin
        return queryset
