import pdb
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response

from api.serializers.misc import ImportTaskSerializer
from api.serializers.feature import FeatureTypeAttachmentsSerializer
from geocontrib.models.task import ImportTask
from geocontrib.models import Attachment
from geocontrib.models import Project

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
        queryset = queryset.order_by('-id')[:5]
        return queryset

    def get_queryset(self):
        queryset = super().get_queryset()
        queryset = queryset.select_related('user')
        queryset = queryset.select_related('feature_type')
        queryset = queryset.select_related('project')
        # NB filter_queryset() bien appelé par ListModelMixin
        return queryset

class ProjectComments(views.APIView):
    queryset = Project.objects.all()
    lookup_field = 'slug'
    http_method_names = ['get', ]

    def get(self, request, slug):
        attachments = Attachment.objects.filter(project__slug=slug)
        serializers = FeatureTypeAttachmentsSerializer(attachments, many=True)
        data = {
            'attachments': serializers.data,
        }
        return Response(data, status=200)