from django.utils.translation import ugettext as _
from rest_framework.exceptions import AuthenticationFailed
from rest_framework import HTTP_HEADER_ENCODING
from rest_framework.authentication import BaseAuthentication
from rest_framework.authentication import get_authorization_header

from api import messages
from geocontrib.models import User

import logging

logger = logging.getLogger(__name__)

class TokenAuthentication(BaseAuthentication):
    www_authenticate_realm = 'api'
    user_id_field = 'user_id'
    auth_header_types = ('Bearer', 'JWT')
    auth_header_type_bytes = set(h.encode(HTTP_HEADER_ENCODING) for h in auth_header_types)

    def get_raw_token(self, header):
        parts = header.split()

        if not parts or parts[0] not in self.auth_header_type_bytes:
            # Assume the header does not contain a JSON web token
            return None

        if len(parts) != 2:
            raise AuthenticationFailed(
                _('Authorization header must contain two space-delimited values'),
                code='bad_authorization_header',
            )

        return parts[1]

    def validate_token(self, token):
        try:
            user = User.objects.get(token=token.decode("utf-8"))
        except User.DoesNotExist:
            raise AuthenticationFailed(messages.AUTHENTICATION_FAILED)
        return user
    
    def authenticate(self, request):
        # Check for custom header first
        custom_header = request.META.get('HTTP_AUTHORIZATION_GEOCONTRIB')
        if custom_header:
            # Directly use the token from custom header
            logger.error('authenticate from TokenAuthentification with custom_header')
            raw_token = custom_header.encode('ascii')
        else:
            logger.error('authenticate from TokenAuthentification with Bearer')
            header = get_authorization_header(request)
            if header is None:
                return None

            raw_token = self.get_raw_token(header)
            if raw_token is None:
                return None

        try:
            user = self.validate_token(raw_token)
        except:
            raise AuthenticationFailed(messages.TOKEN_INVALID)
        if user is None:
            return None

        return user, None