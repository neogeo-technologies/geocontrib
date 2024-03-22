from uuid import uuid4

from django.contrib.auth import get_user_model
from django.db import transaction
from django.shortcuts import reverse
from rest_framework import serializers
from rest_framework_gis.serializers import GeoFeatureModelSerializer

from api import logger
from api.serializers.misc import UserSerializer
from geocontrib.models import Attachment
from geocontrib.models import Authorization
from geocontrib.models import Comment
from geocontrib.models import CustomField
from geocontrib.models import Feature
from geocontrib.models import FeatureLink
from geocontrib.models import FeatureType
from geocontrib.models import PreRecordedValues
from geocontrib.models import Project

User = get_user_model()


class CustomFieldSerializer(serializers.ModelSerializer):

    class Meta:
        model = CustomField
        fields = (
            'position',
            'label',
            'name',
            'field_type',
            'options',
            'is_mandatory',
            'conditional_field_config',
            'forced_value_config'
        )


class FeatureTypeSerializer(serializers.ModelSerializer):

    project = serializers.ReadOnlyField(source='project.slug')
    customfield_set = CustomFieldSerializer(many=True)

    class Meta:
        model = FeatureType
        fields = (
            'title',
            'slug',
            'geom_type',
            'customfield_set',
            'project',
        )


class FeatureTypeListSerializer(serializers.ModelSerializer):
    """
    A serializer for listing and handling feature types within a project.
    This serializer also manages custom fields associated with each feature type,
    allowing for dynamic modification of these fields based on user input.
    """
    
    # Relates each feature type to a project by its slug.
    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())
    
    # Nested serializer to handle custom fields, allowing null and not required by default.
    customfield_set = CustomFieldSerializer(
        many=True, allow_null=True, required=False
    )

    class Meta:
        model = FeatureType
        fields = (
            'title',
            'title_optional',
            'slug',
            'geom_type',
            'color',
            'icon',
            'opacity',
            'colors_style',
            'project',
            'customfield_set',
            'is_editable',
            'displayed_fields',
            'enable_key_doc_notif',
            'disable_notification',
        )
        # Prevents the slug from being modified after creation.
        read_only_fields = [
            'slug',
        ]

    def handle_related(self, instance, custom_fields):
        """
        Handles the creation or update of custom fields related to a feature type instance.
        Deletes existing custom fields and recreates them from provided list.
        """
        if isinstance(custom_fields, list):
            instance.customfield_set.all().delete()
            for field in custom_fields:
                CustomField.objects.create(feature_type=instance, **field)

    def validate_project(self, obj):
        """
        Ensures the user has permission to create or edit feature types within the project.
        Raises a validation error if not authorized.
        """
        user = self.context['request'].user
        if not Authorization.has_permission(user, 'can_create_feature_type', obj):
            raise serializers.ValidationError({
                'error': "Vous ne pouvez pas éditer de type de signalement pour ce projet. "})
        return obj

    def create(self, validated_data):
        """
        Creates a new feature type, handling the related custom fields as a transactional operation.
        """
        customfield_set = validated_data.pop('customfield_set', None)
        try:
            feature_type = FeatureType.objects.create(**validated_data)
            self.handle_related(feature_type, customfield_set)
        except Exception as err:
            raise serializers.ValidationError({'error': str(err)})
        return feature_type

    def update(self, instance, validated_data):
        """
        Updates an existing feature type and its related custom fields.
        Checks for changes in the display properties specifically to handle them conditionally.
        """
        # Check for changes in display-related properties.
        comp_keys = ['color', 'icon', 'opacity', 'colors_style', 'displayed_fields', 'enable_key_doc_notif', 'disable_notification']
        is_display_edited = not all(self.data.get(key) == validated_data.get(key) for key in comp_keys)

        if not instance.is_editable:
            if is_display_edited:
                # Update display-related properties if they have been changed.
                for key in comp_keys:
                    if key in validated_data:  # Ensure the key exists in the validated data before setting it.
                        setattr(instance, key, validated_data.get(key))

            else:
                raise serializers.ValidationError({
                    'error': "Vous ne pouvez pas éditer ce type de signalement. "})

        customfield_set = validated_data.pop('customfield_set', None)
        try:
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()
            self.handle_related(instance, customfield_set)
        except Exception as err:
            raise serializers.ValidationError([str(err), ])
        else:
            return instance


class FeatureListSerializer(serializers.ModelSerializer):

    project = serializers.ReadOnlyField(source='project.slug')
    feature_type = FeatureTypeSerializer(read_only=True)
    feature_data = serializers.SerializerMethodField()
    display_last_editor = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'description',
            'status',
            'created_on',
            'updated_on',
            'creator',
            'display_creator',
            'display_last_editor',
            'project',
            'feature_type',
            'geom',
            'feature_data',
        )

    def get_feature_data(self, obj):
        try:
            res = obj.custom_fields_as_list
        except Exception:
            res = []
        return res

    def get_display_last_editor(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_last_editor
        return res


class FeatureTypeColoredSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = FeatureType
        fields = (
            'title',
            'slug',
            'geom_type',
            'color',
        )


class FeatureJSONSerializer(serializers.ModelSerializer):
    
    feature_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=FeatureType.objects.all())

    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())

    display_creator = serializers.SerializerMethodField()

    display_last_editor = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'description',
            'status',
            'created_on',
            'updated_on',
            'deletion_on',
            'feature_type',
            'project',
            'display_creator',
            'display_last_editor',
            'creator',
            'assigned_member',
        )
        read_only_fields = (
            'created_on',
            'updated_on',
            'deletion_on',
            'display_last_editor',
        )

    def get_custom_properties(self, instance):
        """
        Retrieves custom properties for a feature instance.

        This method is responsible for extracting custom field data from the feature instance.
        It checks if the instance has any data in its 'feature_data' attribute. If so, it iterates
        over all custom fields defined for the feature's type. For each custom field, it attempts to
        fetch the corresponding value from 'feature_data'. If a value is present, it's included in the
        result; otherwise, None is used as a default.

        Parameters:
        - instance: The Feature model instance whose custom properties are being retrieved.

        Returns:
        - dict: A dictionary of custom properties with their values.
        """
        # Initialize an empty dictionary to hold custom properties
        properties = {}

        # Check if the instance has feature_data (which stores custom field values)
        if instance.feature_data:
            # Retrieve the feature type associated with this instance
            feature_type = FeatureType.objects.get(id=instance.feature_type_id)

            # Iterate over each custom field defined for this feature type
            for custom_field in CustomField.objects.filter(feature_type=feature_type):
                # Fetch the value for each custom field from feature_data
                # If the value is not present, default to None
                properties[custom_field.name] = instance.feature_data.get(custom_field.name, None)

        # Return the dictionary of custom properties
        return properties

    def handle_custom_fields(self, validated_data):
        # Hack: les champs extra n'etant pas serializé ou défini dans le modele
        # FIXME: les champs ne sont donc pas validé mais récupérer direct
        # depuis les données initial
        custom_fields = {}
        [custom_fields.update({i.name: i.field_type}) for i in validated_data.get('feature_type').customfield_set.all()]
        properties = self.initial_data.get('properties', {})
        res = {}
        # Tous les champs que pouvant etre nuls
        fields=[
            "char",
            "boolean",
            "char",
            "date",
            "list",
            "integer",
            "decimal",
            "text"
            ]
        for k, v in properties.items():
            if k in custom_fields.keys():
                if custom_fields[k] in fields and v == '':
                    v= None
                res.update({k: v})
        if res:
            validated_data['feature_data'] = res

        return validated_data

    def get_display_creator(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_creator
        return res

    def get_display_last_editor(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_last_editor
        return res

    def handle_title(self, validated_data):
        title = validated_data.get('title')
        if not title or title == '':
            uid = uuid4()
            validated_data['title'] = str(uid)
            validated_data['feature_id'] = uid
        return validated_data

    def create(self, validated_data):
        validated_data['creator'] = self.context.get('request').user
        validated_data = self.handle_custom_fields(validated_data)
        validated_data = self.handle_title(validated_data)
        try:
            instance = Feature.objects.create(**validated_data)
        except Exception as err:
            raise serializers.ValidationError({'detail': str(err)})
        return instance

    def update(self, instance, validated_data):
        validated_data = self.handle_custom_fields(validated_data)
        validated_data['last_editor'] = self.context.get('request').user
        try:
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()
        except Exception as err:
            raise serializers.ValidationError([str(err), ])
        return instance
    
    def to_representation(self, instance):
        """
        Customize the representation of the instance for serialization.

        This method overrides the default `to_representation` method to include custom properties.
        It first calls the base implementation to get the initial representation, and then it
        enhances this with additional custom properties specific to the instance. This approach
        ensures that all relevant data, including custom fields, are included in the serialized output.

        Parameters:
        - instance: The model instance that is being serialized.

        Returns:
        - dict: A dictionary representation of the instance, including custom properties.
        """
        # Call the base implementation first to get a dictionary
        ret = super().to_representation(instance)
        # Retrieve custom properties for the instance
        custom_properties = self.get_custom_properties(instance)
        # Update the dictionary with custom properties
        ret.update(custom_properties)
        return ret


class FeatureGeoJSONSerializer(FeatureJSONSerializer, GeoFeatureModelSerializer):

    class Meta(FeatureJSONSerializer.Meta):
        geo_field = 'geom'

    def get_properties(self, instance, fields):
        properties = super().get_properties(instance, fields)
        custom_properties = self.get_custom_properties(instance)
        properties.update(custom_properties)
        return properties

    def to_representation(self, instance):
        """
        Generate the dictionary representation of the instance.

        Overrides the parent class's `to_representation` method to exclude any custom properties
        handling specific to the FeatureJSONSerializer. This ensures that the representation 
        for the GeoJSON format is based solely on the functionality provided by the parent
        FeatureJSONSerializer, maintaining the integrity of the GeoJSON format.

        Parameters:
        - instance: The model instance that is being serialized.

        Returns:
        - dict: A dictionary representation of the instance, formatted as per the parent class.
        """
        return super(FeatureJSONSerializer, self).to_representation(instance)



class FeatureCSVSerializer(serializers.ModelSerializer):

    id = serializers.CharField(source="feature_id")
    
    feature_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=FeatureType.objects.all())

    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())

    display_creator = serializers.SerializerMethodField()

    display_last_editor = serializers.SerializerMethodField()

    class Meta:
        model = Feature
        fields = (
            'id',
            'title',
            'description',
            'status',
            'created_on',
            'updated_on',
            'deletion_on',
            'feature_type',
            'project',
            'display_creator',
            'display_last_editor',
            'creator',
            'geom',
            'feature_data'
        )
        read_only_fields = (
            'created_on',
            'updated_on',
            'deletion_on',
            'display_last_editor',
        )

    def get_display_creator(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_creator
        return res

    def get_display_last_editor(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_last_editor
        return res

    def handle_title(self, validated_data):
        title = validated_data.get('title')
        if not title or title == '':
            uid = uuid4()
            validated_data['title'] = str(uid)
            validated_data['feature_id'] = uid
        return validated_data

    def create(self, validated_data):
        try:
            instance = Feature.objects.create(**validated_data)
            validated_data['creator'] = self.context.get('request').user
            validated_data = self.handle_title(validated_data)
        except Exception as err:
            raise serializers.ValidationError({'detail': str(err)})
        return instance

    def update(self, instance, validated_data):
        validated_data['last_editor'] = self.context.get('request').user
        try:
            for k, v in validated_data.items():
                setattr(instance, k, v)
            instance.save()
        except Exception as err:
            raise serializers.ValidationError([str(err), ])
        return instance


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
    
    display_last_editor = serializers.SerializerMethodField()

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    updated_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M")

    class Meta:
        model = Feature
        geo_field = 'geom'
        fields = (
            'feature_id',
            'title',
            'description',
            'status',
            'creator',
            'display_creator',
            'display_last_editor',
            'created_on',
            'updated_on',
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

    def get_display_last_editor(self, obj):
        res = 'N/A'
        if self.context['request'].user.is_authenticated:
            res = obj.display_last_editor
        return res


class FeatureLinkListSerializer(serializers.ListSerializer):

    @transaction.atomic
    def bulk_create(self, feature_from):
        validated_data = self.validated_data
        feat_links = [FeatureLink(**item) for item in validated_data]
        feature_from.feature_from.all().delete()
        feature_from.feature_from.set(feat_links, bulk=False)


class FeatureCompactSerializer(serializers.ModelSerializer):

    created_on = serializers.DateTimeField(format="%d/%m/%Y %H:%M")
    url = serializers.ReadOnlyField(source='get_view_url')
    feature_type_slug = serializers.ReadOnlyField(source='feature_type.slug')

    class Meta:
        model = Feature
        fields = (
            'feature_id',
            'title',
            'display_creator',
            'created_on',
            'url',
            'feature_type_slug'
        )

    def to_internal_value(self, data):
        try:
            instance = Feature.objects.get(feature_id=data.get('feature_id'))
        except Exception:
            raise serializers.ValidationError({"error": "Aucun signalement ne correspond. "})
        return instance


class FeatureLinkSerializer(serializers.ModelSerializer):

    feature_to = FeatureCompactSerializer()

    relation_type_display = serializers.ReadOnlyField(source='get_relation_type_display')

    class Meta:
        list_serializer_class = FeatureLinkListSerializer
        model = FeatureLink
        fields = (
            'relation_type',
            'relation_type_display',
            'feature_to',
        )


class CommentsSerializer(serializers.ModelSerializer):

    class Meta:
        model = Comment
        fields = (
            'comment',
        )


class FeatureTypeAttachmentsSerializer(serializers.ModelSerializer):

    comment = CommentsSerializer()

    class Meta:
        model = Attachment
        fields = (
            'id',
            'created_on',
            'feature_id',
            'author',
            'project',
            'title',
            'info',
            'object_type',
            'attachment_file',
            'comment'
        )


class FeatureDetailedAuthenticatedSerializer(FeatureDetailedSerializer):

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.is_authenticated = True


class PreRecordedValuesSerializer(serializers.ModelSerializer):

    class Meta:
        model = PreRecordedValues
        fields = (
            'name',
            'values',
        )