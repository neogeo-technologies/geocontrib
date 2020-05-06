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

from decouple import config, Csv
from django.contrib.auth import get_user_model
from django.contrib.auth import login
from django.contrib.auth import logout
from django.core.exceptions import PermissionDenied
from django.urls import reverse
from django.urls import resolve

User = get_user_model()
logger = logging.getLogger(__name__)

IGNORED_PATHS = config('IGNORED_PATHS', default='geocontrib:logout,', cast=Csv())
HEADER_UID = config('HEADER_UID', default='HTTP_SEC_USERNAME')


class RemoteUserMiddleware(object):

    def __init__(self, get_response):
        self.get_response = get_response

    def path_is_ignored(self, request, admin_ignored=False):
        """Détermine si la requête courante concerne une url qui n'a pas besoin
        d'être traitée par ce middleware. Et si on traite les requêtes en direction
        du site d'admin Django
        """
        if admin_ignored and request.path.startswith(reverse('admin:index')):
            return True
        resolved = resolve(request.path)
        if len(resolved.app_names) > 0:
            namespace = "{}:{}".format(resolved.app_names[0], resolved.url_name)
            return IGNORED_PATHS.count(namespace) > 0
        return True

    def sso_setted(self, request):
        return request.META.get('HTTP_SEC_PROXY', 'false') == 'true'

    def process_request(self, request):
        sid_user_id = request.META.get(HEADER_UID)
        if self.sso_setted(request) and sid_user_id:
            logger.debug('HEADER_UID: {header_uid}, VALUE: {value}'.format(
                header_uid=HEADER_UID,
                value=sid_user_id,
            ))

            try:
                proxy_user = User.objects.get(username=sid_user_id)
            except User.DoesNotExist as e:
                logger.debug(e)
                raise PermissionDenied()

            # Sanity Check: Si l'utilisateur connecté n'est pas celui envoyé par le proxy
            if request.user.is_authenticated and proxy_user != request.user:
                logout(request)
                logger.debug('USER LOGGED OUT')
                logger.debug(request.headers)

            # On evite de reconnecter un utilsateur deja connecté sinon
            # les tokens csrf sont altérés entre la création du form et son post
            # login() n'est appelé qu'une seule fois
            if not request.user.is_authenticated:
                backend = 'django.contrib.auth.backends.ModelBackend'
                login(request, proxy_user, backend=backend)
                logger.debug('USER LOGGED IN')
                logger.debug(request.headers)

    def __call__(self, request):

        if not self.path_is_ignored(request):
            self.process_request(request)

        response = self.get_response(request)
        return response
