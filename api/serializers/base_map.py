from django.contrib.auth import get_user_model
from rest_framework import serializers

from geocontrib.models import BaseMap
from geocontrib.models import ContextLayer
from geocontrib.models import Layer
from geocontrib.models import Project


User = get_user_model()


class ContextLayerSerializer(serializers.ModelSerializer):

    id = serializers.PrimaryKeyRelatedField(
        source='layer',
        queryset=Layer.objects.all(),
        # required=True
    )

    title = serializers.ReadOnlyField(source='layer.title')

    class Meta:
        model = ContextLayer
        fields = ('id', 'title', 'opacity', 'order', 'queryable')


class BaseMapSerializer(serializers.ModelSerializer):

    layers = ContextLayerSerializer(source='contextlayer_set', many=True)

    project = serializers.SlugRelatedField(
        slug_field='slug', queryset=Project.objects.all())

    class Meta:
        model = BaseMap
        fields = ('id', 'title', 'layers', 'project')

    def context_layer_set(self, instance, context_layers):
        # import pdb; pdb.set_trace()
        # # if isinstance(context_layers, list):
        # #     instance.contextlayer_set.all().delete()
        instance.layers.clear()
        for context_layer in context_layers:
            context_layer['base_map'] = instance
            ContextLayer.objects.create(**context_layer)

    def create(self, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        try:
            instance = BaseMap.objects.create(**validated_data)
            self.context_layer_set(instance, context_layers)
        except Exception:
            raise serializers.ValidationError('')
        return instance

    def update(self, instance, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        instance.title = validated_data['title']
        self.context_layer_set(instance, context_layers)
        instance.save()
        return instance


class LayerSerializer(serializers.ModelSerializer):

    options = serializers.JSONField(read_only=True)

    class Meta:
        model = Layer
        fields = (
            'id',
            'title',
            'service',
            'schema_type',
            'options',
        )
