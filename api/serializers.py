from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from django.shortcuts import reverse
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import BaseMap
from geocontrib.models import ContextLayer
from geocontrib.models import CustomField
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import Project
from geocontrib.models import Event
from geocontrib.models import StackedEvent
from geocontrib.models import Layer


import logging
logger = logging.getLogger(__name__)

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


class FeatureTypeColoredSerializer(serializers.ModelSerializer):

    class Meta:
        model = FeatureType
        fields = (
            'title',
            'slug',
            'geom_type',
            'color',
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


class FeatureGeoJSONSerializer(GeoFeatureModelSerializer):

    feature_type = serializers.SlugRelatedField(slug_field='slug', read_only=True)

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
            'feature_type',
        )

    def get_properties(self, instance, fields):
        # Ici on retourne les champs extra d'une feature au meme niveau
        # que les champs de bases
        properties = super().get_properties(instance, fields)
        if instance.feature_data:
            for key, value in instance.feature_data.items():
                properties[key] = value
        return properties


class FeatureSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    user = UserSerializer(read_only=True)

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'created_on',
            'user',
        )


class FeatureDetailedSerializer(GeoFeatureModelSerializer):

    feature_url = serializers.SerializerMethodField(read_only=True)

    feature_type_url = serializers.SerializerMethodField(read_only=True)

    feature_type = FeatureTypeColoredSerializer(read_only=True)

    status = serializers.SerializerMethodField(read_only=True)

    creator = serializers.SerializerMethodField(read_only=True)

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    updated_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    archived_on = serializers.DateField(format="%d/%m/%Y", read_only=True)

    class Meta:
        model = Feature
        geo_field = 'geom'
        fields = (
            'feature_id',
            'title',
            'description',
            'status',
            'creator',
            'created_on',
            'updated_on',
            'archived_on',
            'deletion_on',
            'feature_type',
            'feature_url',
            'feature_type_url',
        )

    def __init__(self, *args, **kwargs):
        self.is_authenticated = kwargs.pop('is_authenticated', False)
        super().__init__(*args, **kwargs)

    def get_properties(self, instance, fields):
        # Ici on retourne les champs extra d'une feature au meme niveau
        # que les champs de bases
        properties = super().get_properties(instance, fields)
        if instance.feature_data:
            for key, value in instance.feature_data.items():
                properties[key] = value
        return properties

    def get_status(self, obj):
        return {'value': obj.status, 'label': obj.get_status_display()}

    def get_creator(self, obj):
        res = {}
        if self.is_authenticated and obj.creator:
            res = {
                'full_name': obj.creator.get_full_name(),
                'first_name': obj.creator.first_name,
                'last_name': obj.creator.last_name,
                'username': obj.creator.username,
            }
        return res

    def get_feature_url(self, obj):
        return reverse(
            'geocontrib:feature_detail', kwargs={
                'slug': obj.project.slug,
                'feature_type_slug': obj.feature_type.slug,
                'feature_id': obj.feature_id})

    def get_feature_type_url(self, obj):
        return reverse(
            'geocontrib:feature_type_detail',
            kwargs={
                'slug': obj.project.slug,
                'feature_type_slug': obj.feature_type.slug
        })


class FeatureLinkSerializer(serializers.ModelSerializer):

    feature_to = serializers.SerializerMethodField()

    relation_type = serializers.ReadOnlyField(source='get_relation_type_display')

    def get_feature_to(self, obj):
        res = {}
        if obj.feature_to:
            try:
                feature = Feature.objects.get(feature_id=obj.feature_to)
                res = {
                    'feature_id': str(feature.feature_id),
                    'title': str(feature.title),
                    'feature_url': feature.get_view_url(),
                    'created_on': feature.created_on.strftime("%d/%m/%Y %H:%M"),
                    'creator': feature.display_creator,
                }
            except Exception:
                logger.exception('No related feature found')
        return res

    class Meta:
        model = FeatureLink
        fields = (
            'relation_type',
            'feature_to',
        )


class EventSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M", read_only=True)

    user = UserSerializer(read_only=True)

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
            'user',
            'related_comment',
            'related_feature',
            'project_url',
        )


class ContextLayerSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='layer.id', required=True)

    title = serializers.ReadOnlyField(source='layer.title')

    class Meta:
        model = ContextLayer
        fields = ('id', 'title', 'opacity', 'order')


class BaseMapSerializer(serializers.ModelSerializer):

    layers = ContextLayerSerializer(source='contextlayer_set', many=True)

    class Meta:
        model = BaseMap
        fields = ('id', 'title', 'layers')

    def context_layer_set(self, instance, context_layers):
        instance.layers.clear()
        for context_layer in context_layers:
            layer = context_layer.pop('layer')
            layer = get_object_or_404(Layer, id=layer['id'])
            ctx, created = ContextLayer.objects.update_or_create(
                base_map=instance,
                layer=layer,
                defaults=context_layer
            )
            logger.debug(ctx)

    def create(self, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        instance = BaseMap.objects.create(**validated_data)
        self.context_layer_set(instance, context_layers)
        return instance

    def update(self, instance, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        instance.email = validated_data.get('title', instance.title)
        self.context_layer_set(instance, context_layers)
        instance.save()
        return instance


class LayerSerializer(serializers.ModelSerializer):

    options = serializers.JSONField(read_only=True)

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

    nb_published_features = serializers.SerializerMethodField()

    nb_comments = serializers.SerializerMethodField()

    nb_published_features_comments = serializers.SerializerMethodField()

    nb_contributors = serializers.SerializerMethodField()

    access_level_pub_feature = serializers.ReadOnlyField(
        source='access_level_pub_feature.get_user_type_id_display')

    access_level_arch_feature = serializers.ReadOnlyField(
        source='access_level_arch_feature.get_user_type_id_display')

    def get_nb_features(self, obj):
        return Feature.objects.filter(project=obj).count()

    def get_published_features(self, obj):
        return Feature.objects.filter(project=obj, status="published")

    def get_nb_published_features(self, obj):
        return self.get_published_features(obj).count()

    def get_nb_comments(self, obj):
        return Comment.objects.filter(project=obj).count()

    def get_nb_published_features_comments(self, obj):
        return Comment.objects.filter(project=obj, feature_id__in=self.get_published_features(obj)).count()

    def get_nb_contributors(self, obj):
        return Authorization.objects.filter(project=obj).filter(
            level__rank__gt=1
        ).count()

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
            'nb_published_features',
            'nb_comments',
            'nb_published_features_comments',
            'nb_contributors'
        )


class StackedEventSerializer(serializers.ModelSerializer):

    events = EventSerializer(many=True, read_only=True)

    class Meta:
        model = StackedEvent
        fields = '__all__'
