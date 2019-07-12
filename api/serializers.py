from rest_framework import serializers
from rest_framework_gis.serializers import GeometrySerializerMethodField

from collab.models import Project
from collab.models import Feature


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
