from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField
from rest_framework_gis.serializers import GeoFeatureModelSerializer
from collab.models import Project
from collab.models import Feature

import logging
logger = logging.getLogger('django')


class FeatureGeoJSONSerializer(GeoFeatureModelSerializer):

    class Meta:
        model = Feature
        geo_field = "geom"
        fields = '__all__'
        # you can also explicitly declare which fields you want to include
        # as with a ModelSerializer.
        # fields = ('id', 'address', 'city', 'state')

    def get_properties(self, instance, fields):
        # This is a PostgreSQL JSON field, which django maps to a dict
        return instance.feature_data


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

    # def to_representation(self, obj):
    #     url = reverse(
    #         'collab:feature-detail',
    #         kwargs={
    #             'slug': obj.project.slug,
    #             'feature_type_slug': obj.feature_type.slug,
    #             'feature_id': obj.feature_id
    #         })
    #
    #     return OrderedDict([
    #         ('geom', obj.geom),
    #         ('status', obj.status),
    #         ('user', obj.user.username),
    #         ('url', url),
    #     ])


class ProjectSerializer(serializers.HyperlinkedModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'
