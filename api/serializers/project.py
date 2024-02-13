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
from geocontrib.models import ProjectAttribute
from geocontrib.models import ProjectAttributeAssociation


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


class ProjectAttributeSerializer(serializers.ModelSerializer):
    """
    Serializer for ProjectAttribute model. Converts ProjectAttribute instances into JSON format
    and defines how the ProjectAttribute fields are represented in the API.
    """
    class Meta:
        model = ProjectAttribute
        fields = ['id', 'label', 'name', 'field_type', 'options', 'default_value']


class ProjectAttributeAssociationSerializer(serializers.ModelSerializer):
    """
    Serializer for the ProjectAttributeAssociation model. This serializer converts instances of ProjectAttributeAssociation
    into JSON format and defines how the fields of the association are represented in the API.

    The 'attribute' field of the model is represented in the serialized output as 'attribute_id' to explicitly indicate
    that it contains the ID of the associated ProjectAttribute.
    """

    attribute_id = serializers.PrimaryKeyRelatedField(
        source='attribute',  # Maps 'attribute_id' in the serializer back to the 'attribute' field in the model
        queryset=ProjectAttribute.objects.all(),
        write_only=False  # Set to True if 'attribute_id' should not be included in the serialized output
    )

    class Meta:
        model = ProjectAttributeAssociation
        fields = ['attribute_id', 'value']  # Include 'attribute_id' instead of 'attribute'


class ProjectDetailedSerializer(serializers.ModelSerializer):
    """
    Detailed serializer for the Project model, providing a comprehensive representation of a project
    and its related data, such as attributes, features, comments, and contributors.
    """

    # Formats 'created_on' and 'updated_on' fields to a specific date format.
    created_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)
    updated_on = serializers.DateTimeField(format="%d/%m/%Y", read_only=True)

    # SerializerMethodField is used to define fields that are computed through methods below.
    nb_features = serializers.SerializerMethodField()
    nb_published_features = serializers.SerializerMethodField()
    nb_comments = serializers.SerializerMethodField()
    nb_published_features_comments = serializers.SerializerMethodField()
    nb_contributors = serializers.SerializerMethodField()
    thumbnail = serializers.SerializerMethodField()
    bbox = serializers.SerializerMethodField()

    # Represents values of certain fields using Django's get_FOO_display method.
    access_level_pub_feature = serializers.ReadOnlyField(source='access_level_pub_feature.get_user_type_id_display')
    access_level_arch_feature = serializers.ReadOnlyField(source='access_level_arch_feature.get_user_type_id_display')

    # Includes a nested serializer to represent the project's attributes associations.
    project_attributes = ProjectAttributeAssociationSerializer(source='projectattributeassociation_set', many=True, read_only=True)

    # Methods to compute values for SerializerMethodFields.
    def get_bbox(self, obj):
        """Computes the bounding box of the project's features."""
        return obj.calculate_bbox()

    def get_nb_features(self, obj):
        """Returns the total number of features associated with the project."""
        return Feature.objects.filter(project=obj).count()

    def get_published_features(self, obj):
        """Helper method to fetch published features of the project."""
        return Feature.objects.filter(project=obj, status="published")

    def get_nb_published_features(self, obj):
        """Returns the count of published features."""
        return self.get_published_features(obj).count()

    def get_nb_comments(self, obj):
        """Returns the total number of comments associated with the project."""
        return Comment.objects.filter(project=obj).count()

    def get_nb_published_features_comments(self, obj):
        """Returns the count of comments on published features."""
        count = Comment.objects.filter(
            project=obj, feature_id__in=self.get_published_features(obj)
        ).count()
        return count

    def get_nb_contributors(self, obj):
        """Returns the number of contributors with access to the project."""
        return Authorization.objects.filter(project=obj).filter(
            level__rank__gt=1
        ).count()

    def get_thumbnail(self, obj):
        """Provides the URL for the project's thumbnail image, or a default image if not set."""
        if hasattr(obj, 'thumbnail') and obj.thumbnail.name:
            return reverse('api:project-thumbnail', kwargs={"slug": obj.slug})
        else:
            return static('geocontrib/img/default.png')

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
            'bbox',
            'project_attributes'
        )



class ProjectCreationSerializer(serializers.ModelSerializer):
    access_level_pub_feature = serializers.PrimaryKeyRelatedField(queryset=UserLevelPermission.objects.all())
    access_level_arch_feature = serializers.PrimaryKeyRelatedField(queryset=UserLevelPermission.objects.all())
    project_attributes = ProjectAttributeAssociationSerializer(source='projectattributeassociation_set', many=True, required=False)

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
            'creator',
            'access_level_pub_feature',
            'access_level_arch_feature',
            'archive_feature',
            'delete_feature',
            'map_max_zoom_level',
            'feature_browsing_default_filter',
            'feature_browsing_default_sort',
            'project_attributes',  # Include project attributes in the serialized representation
        )

    def create(self, validated_data):
        """
        Custom create method to handle the creation of project attributes associations
        alongside the project.
        """
        project_attributes_data = validated_data.pop('projectattributeassociation_set', [])
        with transaction.atomic():
            project = Project.objects.create(**validated_data)
            for attribute_data in project_attributes_data:
                ProjectAttributeAssociation.objects.create(project=project, **attribute_data)
        return project

    def update(self, instance, validated_data):
        """
        Custom update method to handle updating of project attributes associations
        alongside the project.
        """
        project_attributes_data = validated_data.pop('projectattributeassociation_set', [])
        with transaction.atomic():
            for attr, value in validated_data.items():
                setattr(instance, attr, value)
            instance.save()
            for attribute_data in project_attributes_data:
                ProjectAttributeAssociation.objects.update_or_create(
                    project=instance, 
                    attribute=attribute_data.get('attribute'), 
                    defaults={'value': attribute_data.get('value')}
                )
        return instance


class ProjectThumbnailSerializer(serializers.Serializer):
    thumbnail = serializers.FileField()
