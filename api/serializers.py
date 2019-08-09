from django.contrib.auth import get_user_model

from rest_framework import serializers
from rest_framework.reverse import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from collab.models import Attachment
from collab.models import Authorization
from collab.models import CustomField
from collab.models import Comment
from collab.models import Feature
from collab.models import FeatureType
from collab.models import Project
from collab.models import Event
from collab.models import StackedEvent
from collab.models import Layer


import logging
logger = logging.getLogger('django')

User = get_user_model()


######################
# SHARED SERIALIZERS #
######################

class AttachmentSerializer(serializers.ModelSerializer):

    class Meta:
        model = Attachment
        fields = '__all__'


class CustomFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomField
        fields = (
            'position',
            'label',
            'name',
            'field_type',
        )


class FeatureTypeSerializer(serializers.ModelSerializer):

    customfield_set = CustomFieldSerializer(
        many=True, read_only=True)

    class Meta:
        model = FeatureType
        fields = (
            'title',
            'slug',
            'geom_type',
            'customfield_set',
        )


class UserSerializer(serializers.ModelSerializer):

    full_name = serializers.SerializerMethodField()

    def get_full_name(self, obj):
        return obj.get_full_name()

    class Meta:
        model = User
        fields = (
            'full_name',
            'username'
        )


######################
# HOOKED SERIALIZERS #
######################


class CommentSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    author = UserSerializer(read_only=True)

    related_feature = serializers.SerializerMethodField()

    def get_related_feature(self, obj):
        res = {}
        if obj.feature_id:
            try:
                feature = Feature.objects.get(feature_id=obj.feature_id)
                res = {
                    'feature_id': str(feature.feature_id),
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
            'author',
            'related_feature',
        )


class FeatureGeoJSONSerializer(GeoFeatureModelSerializer):

    # feature_type = FeatureTypeSerializer(read_only=True)

    class Meta:
        model = Feature
        geo_field = 'geom'
        fields = (
            'feature_id',
            'title',
            'description',
            'status',
            'created_on',
            'updated_on',
            'archived_on',
            'deletion_on',
            # 'feature_type',
        )

    def get_properties(self, instance, fields):
        # Ici on retourne les champs extra d'une feature au meme niveau
        # que les champs de bases
        properties = super().get_properties(instance, fields)
        for key, value in instance.feature_data.items():
            properties[key] = value
        return properties


class FeatureLinkSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    user = UserSerializer(read_only=True)

    def get_user_full_name(self, obj):
        return obj.creator.get_full_name()

    def get_username(self, obj):
        return obj.creator.username

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'created_on',
            'user',
        )


class EventSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    user = UserSerializer(read_only=True)

    related_comment = serializers.SerializerMethodField()

    related_feature = serializers.SerializerMethodField()

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
            'user',
            'related_comment',
            'related_feature',
        )


class LayerSerializer(serializers.ModelSerializer):

    options = serializers.SerializerMethodField(read_only=True)

    def get_options(self, obj):
        import json
        return json.dumps(obj.options)

    class Meta:
        model = Layer
        fields = '__all__'


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


class ProjectDetailedSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    updated_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    nb_features = serializers.SerializerMethodField()

    nb_comments = serializers.SerializerMethodField()

    nb_contributors = serializers.SerializerMethodField()

    access_level_pub_feature = serializers.ReadOnlyField(
        source='access_level_pub_feature.get_user_type_id_display')

    access_level_arch_feature = serializers.ReadOnlyField(
        source='access_level_arch_feature.get_user_type_id_display')

    def get_nb_features(self, obj):
        return Feature.objects.filter(project=obj).count()

    def get_nb_comments(self, obj):
        return Comment.objects.filter(project=obj).count()

    def get_nb_contributors(self, obj):
        return Authorization.objects.filter(project=obj).count()

    class Meta:
        model = Project
        fields = (
            'title',
            'slug',
            'created_on',
            'updated_on',
            'description',
            'moderation',
            'thumbnail',
            'creator',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
            'nb_features',
            'nb_comments',
            'nb_contributors'
        )


class StackedEventSerializer(serializers.ModelSerializer):

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = StackedEvent
        fields = '__all__'
