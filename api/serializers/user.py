
from django.contrib.auth import get_user_model
from rest_framework import serializers


#from geocontrib.models import Authorization

User = get_user_model()
#UserLevelProject = Authorization.get_user_level_projects()

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = [
            'username',
            'is_active',
            'first_name',
            'last_name',
            'is_administrator'
        ]

# class UserLevelProjectSerializer(serializers.ModelSerializer):
#     class Meta:
#         model = UserLevelProject
#         fields = [
#             'level'
#         ]