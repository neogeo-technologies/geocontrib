import json

from django.contrib.gis.geos import GEOSGeometry
from django.shortcuts import get_object_or_404
from django.utils import timezone
from drf_yasg.utils import swagger_auto_schema
from rest_framework import exceptions
from rest_framework import generics
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import views
from rest_framework import viewsets
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import FormParser, MultiPartParser
from rest_framework.response import Response

from api.serializers import FeatureAttachmentSerializer
from api.serializers import CommentSerializer
from api.serializers import CommentDetailedSerializer
from api.serializers import EventSerializer
from api.serializers import ImportTaskSerializer
from geocontrib.exif import exif
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Event
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.models.task import ImportTask
from geocontrib.tasks import task_geojson_processing, task_csv_processing


@swagger_auto_schema(deprecated=True)
class ImportTaskSearchDeprecated(
        mixins.CreateModelMixin,
        mixins.ListModelMixin,
        viewsets.GenericViewSet):

    queryset = ImportTask.objects.all()

    serializer_class = ImportTaskSerializer

    http_method_names = ['get', 'post']

    def create(self, request, *args, **kwargs):
        try:
            if request.FILES.get('json_file'):
                up_file = request.FILES['json_file']
                process = task_geojson_processing
            if request.FILES.get('csv_file'):
                up_file = request.FILES['csv_file']
                process = task_csv_processing
            feature_type = FeatureType.objects.get(slug=request.data.get('feature_type_slug'))
            import_task = ImportTask.objects.create(
                created_on=timezone.now(),
                project=feature_type.project,
                feature_type=feature_type,
                user=request.user,
                file=up_file
            )
        except Exception as e:
            return Response(
                {'error': 'error'},
                status=400,
            )
        else:
            process.apply_async(kwargs={'import_task_id': import_task.pk})

        return Response({'detail': "L'import du fichier réussi. Le traitement des données est en cours. "}, status=200)

    def filter_queryset(self, queryset):
        status = self.request.query_params.get('status')
        feature_type_slug = self.request.query_params.get('feature_type_slug')
        project_slug = self.request.query_params.get('project_slug')
        if project_slug:
            queryset = queryset.filter(project__slug=project_slug)
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


class FeatureAttachmentView(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    queryset = Attachment.objects.filter(object_type='feature')

    serializer_class = FeatureAttachmentSerializer

    def get_object(self):
        attachment_id = self.kwargs['attachment_id']
        feature_id = self.kwargs['feature_id']
        return get_object_or_404(
            Attachment, id=attachment_id, feature_id=feature_id)

    def get_queryset(self):
        feature_id = self.kwargs['feature_id']
        qs = super().get_queryset().filter(feature_id=feature_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        feature_id = self.kwargs['feature_id']
        feature = get_object_or_404(Feature, feature_id=feature_id)
        context.update({'feature': feature})
        return context


class FeatureAttachmentUploadView(views.APIView):

    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, feature_id, attachment_id):
        return get_object_or_404(
            Attachment, id=attachment_id, feature_id=feature_id)

    def read_file(self, request):
        _file = request.data.get('file')
        if not _file:
            raise exceptions.ValidationError({
                'error': "File entry is missing",
            })
        return _file

    def put(self, request, feature_id, attachment_id):
        instance = self.get_object(feature_id, attachment_id)
        attachment_file = self.read_file(request)
        instance.attachment_file.save(
            attachment_file.name, attachment_file, save=True)
        data = FeatureAttachmentSerializer(
            instance=instance,
            context={'request': request}
        ).data
        return Response(data=data, status=200)


class CommentView(
        mixins.ListModelMixin,
        mixins.CreateModelMixin,
        mixins.RetrieveModelMixin,
        mixins.UpdateModelMixin,
        mixins.DestroyModelMixin,
        viewsets.GenericViewSet
        ):

    permission_classes = [
        permissions.IsAuthenticatedOrReadOnly
    ]

    queryset = Comment.objects.all()

    serializer_class = CommentDetailedSerializer

    def get_object(self):
        comment_id = self.kwargs['comment_id']
        feature_id = self.kwargs['feature_id']
        return get_object_or_404(
            Comment, id=comment_id, feature_id=feature_id)

    def get_queryset(self):
        feature_id = self.kwargs['feature_id']
        qs = super().get_queryset().filter(feature_id=feature_id)
        return qs

    def get_serializer_context(self):
        context = super().get_serializer_context()
        feature_id = self.kwargs['feature_id']
        feature = get_object_or_404(Feature, feature_id=feature_id)
        context.update({'feature': feature})
        return context


class CommentAttachmentUploadView(views.APIView):
    """
        comment = Comment.objects.create(
            feature_id=feature.feature_id,
            feature_type_slug=feature.feature_type.slug,
            author=user,
            project=project,
            comment=form.cleaned_data.get('comment')
        )
        up_file = form.cleaned_data.get('attachment_file')
        title = form.cleaned_data.get('title')
        info = form.cleaned_data.get('info')
        if comment and up_file and title:
            Attachment.objects.create(
                feature_id=feature.feature_id,
                author=user,
                project=project,
                comment=comment,
                attachment_file=up_file,
                title=title,
                info=info,
                object_type='comment'
            )
    """
    permission_classes = [
        permissions.IsAuthenticated,
    ]

    def get_object(self, feature_id, comment_id):
        return get_object_or_404(
            Comment, id=comment_id, feature_id=feature_id)

    def read_file(self, request):
        _file = request.data.get('file')
        if not _file:
            raise exceptions.ValidationError({
                'error': "File entry is missing",
            })
        return _file

    def read_title(self, request):
        title = request.data.get('title')
        if not title:
            raise exceptions.ValidationError({
                'error': "Field 'title' is missing",
            })
        return title

    def put(self, request, feature_id, comment_id):
        feature = get_object_or_404(Feature, feature_id=feature_id)
        comment = self.get_object(feature_id, comment_id)
        attachment_file = self.read_file(request)
        attachment, create = Attachment.objects.update_or_create(
            comment=comment,
            defaults={
                'project': feature.project,
                'title': self.read_title(request),
                'info': request.data.get('info', ''),
                'feature_id': feature.feature_id,
                'author': request.user,
                'object_type': 'comment'
            }
        )
        attachment.attachment_file.save(
            attachment_file.name, attachment_file, save=True)
        data = CommentDetailedSerializer(
            instance=comment,
            context={'request': request}
        ).data
        return Response(data=data, status=200)


class EventView(views.APIView):

    permission_classes = [
        permissions.IsAuthenticated
    ]

    def get(self, request):
        user = request.user
        project_slug = request.GET.get('project_slug', '')
        # notifications
        all_events = Event.objects.filter(user=user).order_by('-created_on')
        if project_slug:
            all_events = all_events.filter(project_slug=project_slug)
        serialized_events = EventSerializer(all_events[0:5], many=True)
        # signalements
        feature_events = Event.objects.filter(
            user=user, object_type='feature').order_by('-created_on')
        if project_slug:
            feature_events = feature_events.filter(project_slug=project_slug)
        serialized_feature_events = EventSerializer(feature_events[0:5], many=True)
        # commentaires
        comment_events = Event.objects.filter(
            user=user, object_type='comment').order_by('-created_on')
        if project_slug:
            comment_events = comment_events.filter(project_slug=project_slug)
        serialized_comment_events = EventSerializer(comment_events[0:5], many=True)

        data = {
            'events': serialized_events.data,
            'features': serialized_feature_events.data,
            'comments': serialized_comment_events.data
        }
        return Response(data=data, status=200)


class ExifGeomReaderView(views.APIView):

    def get_geom(self, geom):
        # Si geoJSON
        if isinstance(geom, dict):
            geom = str(geom)
        geom = GEOSGeometry(geom, srid=4326)
        return geom

    def post(self, request):
        image_file = request.data.get('image_file')
        if not image_file:
            raise exceptions.ValidationError({
                'error': "Aucun fichier à ajouter",
            })
        try:
            data_geom_wkt = exif.get_image_geoloc_as_wkt(
                image_file, with_alt=False, ewkt=False)
            geom = self.get_geom(data_geom_wkt)
        except Exception:
            raise exceptions.ValidationError({
                'error': "Erreur lors de la lecture des données GPS.",
            })

        return Response({'geom': geom.wkt}, status=200)
