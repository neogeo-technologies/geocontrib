from django.contrib.auth import get_user_model
from rest_framework import serializers

from api import logger
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.models import Event
from geocontrib.models import StackedEvent
from geocontrib.models import ImportTask


User = get_user_model()


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name() or obj.username

    class Meta:
        model = User
        fields = (
            'full_name',
            'username'
        )


class CommentSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    display_author = serializers.ReadOnlyField()

    related_feature = serializers.SerializerMethodField()

    def get_related_feature(self, obj):
        res = {}
        if obj.feature_id:
            try:
                feature = Feature.objects.get(feature_id=obj.feature_id)
                res = {
                    'feature_id': str(feature.feature_id),
                    'title': str(feature.title),
                    'feature_url': feature.get_view_url()
                }
            except Exception:
                logger.exception('No related feature found')
        return res

    class Meta:
        model = Comment
        fields = (
            'created_on',
            'comment',
            'display_author',
            'related_feature',
        )
        read_only_fields = fields


class EventSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    display_user = serializers.ReadOnlyField()

    related_comment = serializers.SerializerMethodField()

    related_feature = serializers.SerializerMethodField()

    project_url = serializers.SerializerMethodField()

    def get_related_comment(self, obj):
        res = {}
        if obj.object_type == 'comment':
            try:
                comment = Comment.objects.get(id=obj.comment_id)
                res = {
                    'comment': comment.comment,
                    'attachments': [
                        {'url': att.attachment_file.url, 'title': att.title} for att in comment.attachment_set.all()
                    ]
                }
            except Exception:
                logger.exception('No related comment found')
        return res

    def get_related_feature(self, obj):
        res = {}
        if obj.feature_id:
            try:
                feature = Feature.objects.get(feature_id=obj.feature_id)
                res = {
                    'feature_id': str(feature.feature_id),
                    'title': str(feature.title),
                    'feature_url': feature.get_view_url()
                }
            except Exception:
                logger.exception('No related feature found')
        return res

    def get_project_url(self, obj):
        url = ''
        if obj.project_slug:
            try:
                project = Project.objects.get(slug=obj.project_slug)
                url = project.get_absolute_url()
            except Exception:
                logger.exception('No related project found')
        return url

    class Meta:
        model = Event
        fields = (
            'created_on',
            'object_type',
            'event_type',
            'data',
            'project_slug',
            'feature_type_slug',
            'feature_id',
            'comment_id',
            'attachment_id',
            'display_user',
            'related_comment',
            'related_feature',
            'project_url',
        )


class StackedEventSerializer(serializers.ModelSerializer):

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = StackedEvent
        fields = '__all__'


class ImportTaskSerializer(serializers.ModelSerializer):

    project_title = serializers.SerializerMethodField()
    feature_type_title = serializers.SerializerMethodField()
    geojson_file_name = serializers.SerializerMethodField()

    
    def get_project_title(self, obj):
        return str(obj.project.slug)

    def get_feature_type_title(self, obj):
        return str(obj.feature_type.slug)

    def get_geojson_file_name(self, obj):
        try:
            filename = str(obj.geojson_file.name.split('/')[-1])
        except:
            filename = 'example_error.file'
        return filename

    class Meta:
        model = ImportTask
        fields = (
            'created_on',
            'started_on',
            'finished_on',
            'status',
            # 'project',
            'project_title',
            # 'feature_type',
            'feature_type_title',
            'user',
            # 'geojson_file',
            'geojson_file_name',
            'infos',
        )