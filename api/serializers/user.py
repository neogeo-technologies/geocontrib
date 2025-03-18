
from django.contrib.auth import get_user_model
from rest_framework import serializers

from geocontrib.models import Authorization
from geocontrib.models import UsersGroup
from geocontrib.models import UserGroupMembership
from geocontrib.models import UserLevelPermission
from geocontrib.models import GeneratedToken

User = get_user_model()


class UserSerializer(serializers.ModelSerializer):
    can_create_project = serializers.SerializerMethodField()

    def get_can_create_project(self, obj):
        can_create_project = False
        if obj.is_superuser or obj.is_administrator:
            can_create_project = True
        return can_create_project


    class Meta:
        model = User
        fields = [
            'username',
            'is_active',
            'first_name',
            'last_name',
            'is_administrator',
            'is_superuser',
            'can_create_project',
            'email',
            'id',
        ]

class UserCreateSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True, style={'input_type': 'password'})
    usersgroups = serializers.ListField(
        child=serializers.CharField(), required=False, write_only=True
    )


    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email', 'password', 'usersgroups']

    def create(self, validated_data):
        usersgroups_data = validated_data.pop('usersgroups', [])  # Récupère et supprime `usersgroups`
        
        # Création de l'utilisateur
        user = User.objects.create_user(
            username=validated_data['username'],
            first_name=validated_data.get('first_name', ''),
            last_name=validated_data.get('last_name', ''),
            email=validated_data.get('email', ''),
            password=validated_data['password']
        )

        # Ajout de l'utilisateur aux groupes s'ils existent
        for group_codename in usersgroups_data:
            group = UsersGroup.objects.filter(codename=group_codename).first()
            if group:
                UserGroupMembership.objects.create(user=user, group=group)

        return user

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
        
class UserLevelsPermissionSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserLevelPermission
        fields = [
            'user_type_id',
            'rank',
        ]

class GeneratedTokenSerializer(serializers.ModelSerializer):

    class Meta:
        model = GeneratedToken
        fields = (
            'token_sha256',
            'expire_on',
            'username',
            'first_name',
            'last_name',
            'email'
        )

class UsersGroupsSerializer(serializers.ModelSerializer):

    class Meta:
        model = UsersGroup
        fields = [
            'codename',
            'display_name',
            'usergroup_type',
            'is_global'
        ]