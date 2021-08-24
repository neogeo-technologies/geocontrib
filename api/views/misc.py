import pdb
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import views
from rest_framework.response import Response

from django.shortcuts import get_object_or_404

from api.serializers.misc import ImportTaskSerializer
from api.serializers import CommentSerializer
from api.serializers.feature import FeatureTypeAttachmentsSerializer
from geocontrib.models.task import ImportTask
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Feature
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

    def get_object(self):
        slug = self.kwargs.get('slug') or None
        obj = get_object_or_404(Project, slug=self.kwargs.get('slug'))
        return obj

    def get(self, request, slug):
        user = self.request.user
        project = self.get_object()
        permissions = Authorization.all_permissions(user, project)

        # On filtre les signalements selon leur statut et l'utilisateur courant
        features = Feature.handy.availables(
            user=user,
            project=project
        ).order_by('-created_on')

        # On filtre les commentaire selon les signalements visibles
        last_comments = Comment.objects.filter(
            project=project,
            feature_id__in=[feat.feature_id for feat in features]
        ).order_by('-created_on')[0:5]

        serialized_comments = CommentSerializer(last_comments, many=True).data
        data = {
            'last_comments': serialized_comments,
        }
        return Response(data, status=200)