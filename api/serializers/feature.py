from django.contrib.auth import get_user_model
from django.shortcuts import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api import logger
from api.serializers.misc import UserSerializer
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType


User = get_user_model()


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


class FeatureTypeListSerializer(serializers.ModelSerializer):

    project = serializers.ReadOnlyField(source='project.slug')
    customfield_set = CustomFieldSerializer(
        many=True,
        read_only=True
        )

    class Meta:
        model = FeatureType
        fields = (
            'title',
            'slug',
            'geom_type',
            'color',
            'colors_style',
            'project',
            'customfield_set',
            'is_editable',
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


class FeatureSearchSerializer(serializers.ModelSerializer):
    project_slug = serializers.ReadOnlyField(source='project.slug')
    feature_type_slug = serializers.ReadOnlyField(source='feature_type.slug')
    creator = UserSerializer()

    class Meta:
        model = Feature
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
            'project_slug',
            'feature_type_slug',
            'geom',
        )
        read_only_fields = fields


class FeatureDetailedSerializer(GeoFeatureModelSerializer):

    feature_url = serializers.SerializerMethodField()

    feature_type_url = serializers.SerializerMethodField()

    feature_type = FeatureTypeColoredSerializer()

    status = serializers.SerializerMethodField()

    creator = serializers.SerializerMethodField()

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    updated_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    archived_on = serializers.DateField(format="%d/%m/%Y")

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
            'color',
        )
        read_only_fields = fields

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
                feature = obj.feature_to
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
