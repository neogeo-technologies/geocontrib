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

from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.urls import resolve

User = get_user_model()
logger = logging.getLogger(__name__)

IGNORE_PATH = getattr(settings, 'IGNORE_PATH', ['geocontrib:login', ])


class RemoteUserMiddleware(object):

    header = getattr(settings, 'HEADER_UID', 'REMOTE_USER')
    oidc_setted = getattr(settings, 'OIDC_SETTED', False)

    def __init__(self, get_response):
        self.get_response = get_response

    def path_is_ignored(self, request, admin_ingnored=True):
        """Détermine si la requete courante concerne une url qui n'a pas besoin
        d'etre traiter par ce middleware. Et si on traite les requete en direction
        du site d'admin Django
        """
        if admin_ingnored and request.path.startswith(reverse('admin:index')):
            return True
        resolved = resolve(request.path)
        if len(resolved.app_names) > 0:
            namespace = "{}:{}".format(resolved.app_names[0], resolved.url_name)
            return IGNORE_PATH.count(namespace) > 0
        return True

    def process_request(self, request):
        sid_user_id = request.META.get(self.header)
        if self.oidc_setted and sid_user_id:
            logger.info('HEADER_UID: {header_uid}, VALUE: {value}'.format(
                header_uid=self.header,
                value=sid_user_id,
            ))
            logout(request)
            try:
                user = User.objects.get(username=sid_user_id)
            except User.DoesNotExist as e:
                logger.debug(e)
                raise PermissionDenied()
            else:
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, user, backend=backend)

    def __call__(self, request):
        logger.debug(request.META)
        if not self.path_is_ignored(request):
            self.process_request(request)

        response = self.get_response(request)
        return response
