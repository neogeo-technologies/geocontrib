from django.templatetags.static import static
from django.contrib.auth import get_user_model
from django.db import transaction
from django.urls import reverse
from rest_framework import serializers

from geocontrib.choices import ALL_LEVELS
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


class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = (
            'id',
            'first_name',
            'last_name',
            'username'
        )

    def to_internal_value(self, data):
        return User.objects.get(id=data.get('id'))


class LevelSerializer(serializers.ModelSerializer):

    codename = serializers.ChoiceField(ALL_LEVELS, source='user_type_id')
    display = serializers.CharField(source='get_user_type_id_display', read_only=True)

    class Meta:
        model = UserLevelPermission
        fields = (
            'display',
            'codename',
        )

    def to_internal_value(self, data):
        return UserLevelPermission.objects.get(user_type_id=data.get('codename'))


class BaseProjectAuthorizationListSerializer(serializers.ListSerializer):

    @transaction.atomic
    def bulk_edit(self, project):
        validated_data = self.validated_data
        authorizations = [Authorization(project=project, **item) for item in validated_data]
        if not any([row.level.user_type_id == 'admin' for row in authorizations]):
            raise serializers.ValidationError({
                'error': "Au moins un administrateur est requis par projet. "
            })
        project.authorization_set.all().delete()
        try:
            instances = Authorization.objects.bulk_create(authorizations)
        except Exception as err:
            raise serializers.ValidationError({
                'error': f"Échec de l'édition des permissions: {err}"
            })
        return instances


class ProjectAuthorizationSerializer(serializers.ModelSerializer):

    user = UserSerializer()
    level = LevelSerializer()

    class Meta:
        list_serializer_class = BaseProjectAuthorizationListSerializer
        model = Authorization
        fields = (
            'user',
            'level',
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

    bbox = serializers.SerializerMethodField()

    def get_bbox(self, obj):
        return obj.calculate_bbox()

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
            'generate_share_link',
            'fast_edition_mode',
            'feature_assignement',
            'thumbnail',
            'creator',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
            'map_max_zoom_level',
            'nb_features',
            'nb_published_features',
            'nb_comments',
            'nb_published_features_comments',
            'nb_contributors',
            'feature_browsing_default_filter',
            'feature_browsing_default_sort',
            'bbox'
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
            'generate_share_link',
            'fast_edition_mode',
            'feature_assignement',
            'creator',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
            'map_max_zoom_level',
            'feature_browsing_default_filter',
            'feature_browsing_default_sort',
        )


class ProjectThumbnailSerializer(serializers.Serializer):
    thumbnail = serializers.FileField()
