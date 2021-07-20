from rest_framework import serializers
from django.contrib.flatpages.models import FlatPage

class FlatPagesSerializer(serializers.ModelSerializer):
    class Meta:
        model = FlatPage
        fields = (
            'url',
            'title',
            'content',
            'sites',
            'template_name'
        )