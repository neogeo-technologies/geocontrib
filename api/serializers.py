from django.conf import settings
from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from collab.models import Authorization
from collab.models import CustomField
from collab.models import Comment
from collab.models import Feature
from collab.models import FeatureType
from collab.models import Project

import logging
logger = logging.getLogger('django')


class ExportFeatureSerializer(serializers.ModelSerializer):

    geometrie = GeometrySerializerMethodField(
        read_only=True,
        source="geom",
    )

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'geometrie',
            'description',
            'status',
            'created_on',
            'updated_on',
            'archived_on',
            'deletion_on',
            'feature_type',
            'feature_data',
        )


class FeatureGeoJSONSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Feature
        geo_field = "geom"
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
            'feature_data',
        )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        ret['geometry'].update({
            'crs': {
                "type": "name",
                "properties": {"name": "EPSG:{}".format(settings.DB_SRID)}}}
        )
        return ret

    # def get_properties(self, instance, fields):
    #     # This is a PostgreSQL JSON field, which django maps to a dict
    #     return instance.feature_data


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
