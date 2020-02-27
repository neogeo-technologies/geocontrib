# Copyright (c) 2019 Neogeo-Technologies.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging

from django.contrib.auth import get_user_model
from django.db import transaction
from django.http import HttpResponse
from rest_framework.views import APIView
from rest_framework import mixins
from rest_framework import permissions
from rest_framework import viewsets
from rest_framework import status
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
import xmltodict

from plugin_ideo_bfc.xml_io import XMLtParser
from plugin_ideo_bfc.xml_io import XMLRenderer
from plugin_ideo_bfc.exceptions import SidGenericError


User = get_user_model()
logger = logging.getLogger(__name__)


class AbstractUsrViews(mixins.CreateModelMixin, mixins.UpdateModelMixin,
                       mixins.DestroyModelMixin, viewsets.GenericViewSet):
    queryset = User.objects.all()
    parser_classes = [
        # Si le contenu est envoyé en raw
        XMLtParser,
        # Si le fichier est envoyé dans le form-data dans la clé 'file'
        MultiPartParser,
    ]
    renderer_classes = [XMLRenderer, ]
    permission_classes = [
        # permissions.IsAuthenticated, # TODO limiter aux connectés
        permissions.AllowAny
    ]
    lookup_field = 'username'
    lookup_url_kwarg = 'username'
    http_method_names = ['post', 'put']  # ['post', 'put', 'delete']

    def get_object(self):
        try:
            instance = super().get_object()
        except Exception:
            raise SidGenericError(
                client_error_code='003',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': self.kwargs.get('username', 'N/A'),
                },
                status_code=status.HTTP_404_NOT_FOUND
            )
        return instance

    @transaction.atomic
    def parse_and_create(self, data):
        root = data.get(self.profile_element, {})
        sid_id = root.get('id', None)
        if User.objects.filter(username=sid_id).exists():
            raise SidGenericError(
                client_error_code='005',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': sid_id,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        try:
            data_user = root['user']
            user = User.objects.create(
                username=root['id'],
                email=root['email'],
                first_name=data_user['firstname'][:30],
                last_name=data_user['lastname'][:30],
                is_superuser=root['roles']['role']['name'] == "administrateur",
                is_staff=root['roles']['role']['name'] == "administrateur",
                is_active=data_user['enabled'] == 'true',
            )

        except Exception:
            logger.exception(self.__class__.__name__)
            raise SidGenericError(
                client_error_code='002',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': sid_id,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return user

    @transaction.atomic
    def parse_and_update(self, user, data):

        root = data.get(self.profile_element, {})
        sid_id = root.get('id', None)
        if sid_id != str(user.username):
            raise SidGenericError(
                client_error_code='002',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': user.username,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        if not User.objects.filter(username=sid_id).exists():
            raise SidGenericError(
                client_error_code='003',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': user.username,
                },
                status_code=status.HTTP_404_NOT_FOUND
            )

        try:
            data_user = root['user']
            user.first_name = data_user['firstname'][:30]
            user.last_name = data_user['lastname'][:30]
            # user.username = data_user['username']  # Modifiable
            user.email = root['email']
            user.is_superuser = root['roles']['role']['name'] == "administrateur"
            user.is_staff = root['roles']['role']['name'] == "administrateur"
            user.is_active = data_user['enabled'] == "true"
            user.save()

        except Exception:
            logger.exception(self.__class__.__name__)
            raise SidGenericError(
                client_error_code='002',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': user.username,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        return user

    def get_data(self, request):
        data = None
        if request.FILES.get('file'):
            _file = request.FILES.get('file')
            data = xmltodict.parse(_file)
        else:
            data = request.data
        return data

    def create(self, request, *args, **kwargs):
        data = self.get_data(request)
        if not data:
            raise SidGenericError(
                client_error_code='001',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )

        instance = self.parse_and_create(data)
        logger.info('User::create() OK: id->{}, username->{}'.format(
            instance.id,
            instance.username,
        ))
        response = HttpResponse(status=201)
        response['Content-Location'] = ''  # Pas de content-Location
        return response

    def update(self, request, *args, **kwargs):

        data = self.get_data(request)
        sid_id = self.kwargs.get(self.lookup_url_kwarg, '')
        if not data:
            raise SidGenericError(
                client_error_code='001',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': sid_id,
                },
                status_code=status.HTTP_400_BAD_REQUEST
            )
        else:
            # On permet la creation à partir du PUT
            try:
                # On appel get_object() pour le 404 custom
                instance = self.get_object()
            except SidGenericError:
                instance = self.parse_and_create(data)
                logger.info('create() from PUT OK: id->{}, username->{}'.format(
                    instance.id,
                    instance.username,
                ))
            else:
                instance = self.parse_and_update(instance, data)
                logger.info('update() OK: id->{}, username->{}'.format(
                    instance.id,
                    instance.username,
                ))

            return HttpResponse(status=200)

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        try:
            instance.delete()
            instance.profile.contributions.clear()
            instance.profile.delete()
        except Exception:
            logger.exception(self.__class__.__name__)
            raise SidGenericError(
                client_error_code='006',
                extra_context={
                    'classType': self.class_type,
                    'methodType': self.request.method,
                    'resourceId': instance.username,
                },
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

        return HttpResponse(status=200)


class AgentViews(AbstractUsrViews):

    class_type = 'AGENT_PROFILE'
    profile_element = 'agentProfile'


class EmployeeViews(AbstractUsrViews):

    class_type = 'EMPLOYEE_PROFILE'
    profile_element = 'employeeProfile'


class TestAuthentViews(APIView):
    queryset = User.objects.all()
    permission_classes = [
        permissions.IsAdminUser,
    ]

    http_method_names = ['get', ]

    def get(self, request, *args, **kargs):

        data = {
            'username': request.user.username,
            'first_name': request.user.first_name,
            'last_name': request.user.last_name,
            'is_staff': request.user.is_staff,
        }
        return Response(data=data, status=status.HTTP_200_OK)
