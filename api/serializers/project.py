from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import serializers

from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.models import UserLevelPermission


User = get_user_model()


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = (
            'title',
            'slug',
            'created_on',
            'updated_on'
        )


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

    thumbnail = serializers.SerializerMethodField()

    def get_nb_features(self, obj):
        return Feature.objects.filter(project=obj).count()

    def get_published_features(self, obj):
        return Feature.objects.filter(project=obj, status="published")

    def get_nb_published_features(self, obj):
        return self.get_published_features(obj).count()

    def get_nb_comments(self, obj):
        return Comment.objects.filter(project=obj).count()

    def get_nb_published_features_comments(self, obj):
        count = Comment.objects.filter(
            project=obj, feature_id__in=self.get_published_features(obj)
        ).count()
        return count

    def get_nb_contributors(self, obj):
        return Authorization.objects.filter(project=obj).filter(
            level__rank__gt=1
        ).count()

    def get_thumbnail(self, obj):
        res = None
        if hasattr(obj, 'thumbnail') and obj.thumbnail.name:
            res = reverse('api:project-thumbnail', kwargs={"slug": obj.slug})
        else:
            res = static('geocontrib/img/default.png')
        return res

    class Meta:
        model = Project
        fields = (
            'title',
            'slug',
            'created_on',
            'updated_on',
            'description',
            'moderation',
            'is_project_type',
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


class ProjectCreationSerializer(serializers.ModelSerializer):
    access_level_pub_feature = serializers.PrimaryKeyRelatedField(queryset=UserLevelPermission.objects.all())
    access_level_arch_feature = serializers.PrimaryKeyRelatedField(queryset=UserLevelPermission.objects.all())

    class Meta:
        model = Project
        fields = (
            'title',
            'slug',
            'description',
            'moderation',
            'is_project_type',
            'creator',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
        )


class ProjectThumbnailSerializer(serializers.Serializer):
    thumbnail = serializers.FileField()
