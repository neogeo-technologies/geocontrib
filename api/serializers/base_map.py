from django.contrib.auth import get_user_model
from django.shortcuts import get_object_or_404
from rest_framework import serializers

from api import logger
from geocontrib.models import BaseMap
from geocontrib.models import ContextLayer
from geocontrib.models import Layer


User = get_user_model()


class ContextLayerSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField(source='layer.id', required=True)

    title = serializers.ReadOnlyField(source='layer.title')

    class Meta:
        model = ContextLayer
        fields = ('id', 'title', 'opacity', 'order', 'queryable')


class BaseMapSerializer(serializers.ModelSerializer):

    layers = ContextLayerSerializer(source='contextlayer_set', many=True)

    class Meta:
        model = BaseMap
        fields = ('id', 'title', 'layers')

    def context_layer_set(self, instance, context_layers):
        instance.layers.clear()
        for context_layer in context_layers:
            layer = context_layer.pop('layer')
            layer = get_object_or_404(Layer, id=layer['id'])
            ctx, created = ContextLayer.objects.update_or_create(
                base_map=instance,
                layer=layer,
                defaults=context_layer
            )
            logger.debug(ctx)

    def create(self, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        instance = BaseMap.objects.create(**validated_data)
        self.context_layer_set(instance, context_layers)
        return instance

    def update(self, instance, validated_data):
        context_layers = validated_data.pop('contextlayer_set', [])
        instance.email = validated_data.get('title', instance.title)
        self.context_layer_set(instance, context_layers)
        instance.save()
        return instance


class LayerSerializer(serializers.ModelSerializer):

    options = serializers.JSONField(read_only=True)

    class Meta:
        model = Layer
        fields = '__all__'
