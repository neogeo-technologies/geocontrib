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
from geocontrib.models import Project

# from deepdiff import DeepDiff

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

    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())
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
            'colors_style',
            'project',
            'customfield_set',
            'is_editable',
        )
        read_only_fields = [
            'slug',
        ]

    def handle_related(self, instance, custom_fields):
        if isinstance(custom_fields, list):
            instance.customfield_set.all().delete()
            for field in custom_fields:
                CustomField.objects.create(feature_type=instance, **field)

    def validate_project(self, obj):
        user = self.context['request'].user
        if not Authorization.has_permission(user, 'can_create_feature_type', obj):
            raise serializers.ValidationError({
                'error': "Vous ne pouvez pas éditer de type de signalement pour ce projet. "})
        return obj

    def create(self, validated_data):
        customfield_set = validated_data.pop('customfield_set', None)
        try:
            feature_type = FeatureType.objects.create(**validated_data)
            self.handle_related(feature_type, customfield_set)
        except Exception as err:
            raise serializers.ValidationError({'error': str(err)})
        return feature_type

    def update(self, instance, validated_data):

        # Look for symbology differences
        comp_keys = ['color', 'icon', 'colors_style']
        # is_symbology_edited = not all(DeepDiff(self.data.get(key), validated_data.get(key), ignore_order=True) for key in comp_keys)
        is_symbology_edited = not all(self.data.get(key) == validated_data.get(key) for key in comp_keys)

        if not instance.is_editable:

            if is_symbology_edited:
                # Handle symbology edition
                setattr(instance, 'color', validated_data.get('color'))
                setattr(instance, 'icon', validated_data.get('icon'))
                setattr(instance, 'colors_style', validated_data.get('colors_style'))

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
            'archived_on',
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


class FeatureGeoJSONSerializer(GeoFeatureModelSerializer):
    
    feature_type = serializers.SlugRelatedField(
        slug_field='slug', queryset=FeatureType.objects.all())

    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())

    display_creator = serializers.SerializerMethodField()

    display_last_editor = serializers.SerializerMethodField()

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
            'project',
            'display_creator',
            'display_last_editor',
            'creator',
        )
        read_only_fields = (
            'created_on',
            'updated_on',
            'archived_on',
            'deletion_on',
            'display_last_editor',
        )

    def get_properties(self, instance, fields):
        # Ici on retourne les champs extra d'une feature au meme niveau
        # que les champs de bases
        properties = super().get_properties(instance, fields)
        if instance.feature_data:
            for key, value in instance.feature_data.items():
                properties[key] = value
        return properties

    def handle_custom_fields(self, validated_data):
        # Hack: les champs extra n'etant pas serializé ou défini dans le modele
        # FIXME: les champs ne sont donc pas validé mais récupérer direct
        # depuis les données initial
        custom_fields = validated_data.get(
            'feature_type'
        ).customfield_set.values_list('name', flat=True)
        properties = self.initial_data.get('properties', {})
        validated_data['feature_data'] = {
            k: v for k, v in properties.items() if k in custom_fields
        }
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
    
    display_last_editor = serializers.SerializerMethodField()

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
            'display_last_editor',
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