
from django.contrib.auth import get_user_model
from rest_framework import serializers

from geocontrib.models import Authorization
from geocontrib.models import UserLevelPermission

User = get_user_model()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'is_active',
            'first_name',
            'last_name',
            'is_administrator',
            'is_superuser'
        ]

class UserLevelPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLevelPermission
        fields = [
            'user_type_id',
            'rank',
        ]


class AuthorizationSerializer(serializers.ModelSerializer):
    
    project = serializers.ReadOnlyField(source='project.slug')
    level = UserLevelPermissionSerializer()

    class Meta:
        model = Authorization
        fields = [
            'user',
            'project',
            'level',
            'created_on',
            'updated_on',
        ]
