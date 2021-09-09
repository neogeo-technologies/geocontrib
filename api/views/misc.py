import json

from django.shortcuts import get_object_or_404
from django.utils import timezone
from rest_framework import mixins
from rest_framework import viewsets
from rest_framework import views
from rest_framework import permissions
from rest_framework.exceptions import ValidationError
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.parsers import FormParser, MultiPartParser

from api.serializers import ImportTaskSerializer
from api.serializers import CommentSerializer
from api.serializers import AttachmentSerializer
from geocontrib.models.task import ImportTask
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.tasks import task_geojson_processing


class ImportTaskSearch(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    queryset = ImportTask.objects.all()

    serializer_class = ImportTaskSerializer

    http_method_names = ['get', 'post']

    def create(self, request, *args, **kwargs):
        try:
            up_file = request.FILES['json_file']
            feature_type = FeatureType.objects.get(slug=request.data.get('feature_type_slug'))
            import_task = ImportTask.objects.create(
                created_on=timezone.now(),
                project=feature_type.project,
                feature_type=feature_type,
                user=request.user,
                geojson_file=up_file
            )
        except Exception:
            return Response(
                {'error': 'error'},
                status=400,
            )
        else:
            task_geojson_processing.apply_async(kwargs={'import_task_id': import_task.pk})

        return Response({'detail': "L'import du fichier réussi. Le traitement des données est en cours. "}, status=200)

    def filter_queryset(self, queryset):
        status = self.request.query_params.get('status')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        if status:
            queryset = queryset.filter(status__icontains=status)
        if feature_type_slug:
            queryset = queryset.filter(feature_type__slug=feature_type_slug)
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


class AttachmentView(viewsets.ViewSet):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    def get_object(self, feature_id, attachment_id):
        return get_object_or_404(Attachment, id=attachment_id, feature_id=feature_id)

    def list(self, request, feature_id):
        feature = get_object_or_404(Feature, feature_id=feature_id)
        attachments = Attachment.objects.filter(
            feature_id=feature.feature_id, object_type='feature')
        data = AttachmentSerializer(attachments, many=True).data
        return Response(data, status=200)

    def retrieve(self, request, feature_id, attachment_id):
        instance = self.get_object(feature_id, attachment_id)
        data = AttachmentSerializer(instance).data
        return Response(data, status=200)

    @action(detail=False, methods=['post'], parser_classes=(FormParser, MultiPartParser))
    def create(self, request, feature_id):
        feature = get_object_or_404(Feature, feature_id=feature_id)
        try:
            attachement_file = request.data['file']
        except KeyError:
            raise ValidationError({'file': 'file entry is missing in post data'})
        try:
            data = json.loads(request.data['data'])
        except (KeyError, json.JSONDecodeError):
            raise ValidationError({'data': 'data entry is missing or incorrect in post data'})
        try:
            comment = Comment.objects.filter(id=data.get('comment', None)).first()
            instance = Attachment.objects.create(
                attachment_file=attachement_file,
                title=data.get('title'),
                info=data.get('info'),
                feature_id=feature_id,
                project=feature.project,
                object_type='feature',
                comment=comment,
                author=request.user
            )
        except Exception as err:
            raise ValidationError({'error': f'attachment not created {err}'})
        data = AttachmentSerializer(instance).data
        return Response(data, status=200)

    def destroy(self, request, feature_id, attachment_id):
        instance = self.get_object(feature_id, attachment_id)
        instance.delete()
        return Response({}, status=204)
