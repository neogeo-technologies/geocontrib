import logging
from types import MethodType
from typing import Any
from django.db import transaction
from django.contrib import auth
from django.contrib import messages
from django.contrib.auth import get_user_model
from django.core.exceptions import PermissionDenied
from django.core.exceptions import SuspiciousOperation
from django.http import HttpRequest, HttpResponse
from django_pyoidc.client import OIDCClient
from django_pyoidc.exceptions import InvalidSIDException
from django.shortcuts import redirect
from django_pyoidc.views import OIDCLoginView
from oic.oauth2.consumer import TokenError
from oic.utils.http_util import BadRequest
from django_pyoidc.models import OIDCSession
from django_pyoidc.views import OIDCCallbackView
from geocontrib.emails import notif_user_account_created
from geocontrib.emails import notif_admin_user_created
from decouple import config, Csv

SSO_ADMIN_USERS = config('SSO_ADMIN_USERS', default="", cast=Csv())

logger = logging.getLogger(__name__)

User = get_user_model()

def hook_get_user(client, tokens):
    """
    Hook to retrieve or create a user from token claims.
    The user's groups are also updated.
    """
    claims = tokens.get("info_token_claims", {})
    email = claims.get("email")

    if not email:
        raise ValueError("An email is required to create or retrieve a user.")

    # Retrieve or create user
    user, created = User.objects.get_or_create(email=email)

    if created:
        user = create_user(user, claims)
    else:
        user = update_user(user, claims)

    user.backend = "django.contrib.auth.backends.ModelBackend"

    return user


def apply_user_claims(user, claims):
    """Remplit les champs de l'utilisateur Django depuis les claims OIDC."""
    user.username = claims.get('preferred_username') or claims.get('email', '')
    user.first_name = claims.get('preferred_givenname') or claims.get('given_name', '')
    user.last_name = claims.get('family_name', '')
    user.email = claims.get('email', '')
    user.is_active = True
    return user

def set_admin_flags_if_authorized(user):
    """Attribue les droits admin si l'utilisateur est dans SSO_ADMIN_USERS."""
    if user.username in SSO_ADMIN_USERS:
        user.is_staff = True
        user.is_superuser = True
        user.save(update_fields=['is_staff', 'is_superuser'])

def create_user(user, claims):
    user = apply_user_claims(user, claims)
    user.save(update_fields=['username', 'first_name', 'last_name', 'email', 'is_active'])

    set_admin_flags_if_authorized(user)

    if user.email:
        notif_user_account_created(user)
    notif_admin_user_created(user)

    return user

def update_user(user, claims):
    user = apply_user_claims(user, claims)
    user.save(update_fields=['username', 'first_name', 'last_name', 'email', 'is_active'])

    set_admin_flags_if_authorized(user)

    return user


class CustomOIDCLoginView(OIDCLoginView):
    def get(self, request, *args, **kwargs):
        sid = request.session.get("oidc_sid")
        if sid:
            try:
                client = OIDCClient(self.op_name, session_id=sid)
            except InvalidSIDException:
                # maybe a failed attempt trace in the session.
                # we ignore the session sid and get back on the first steps.
                client = OIDCClient(self.op_name)
        else:
            client = OIDCClient(self.op_name)

        callback_path = str(self.get_setting("oidc_callback_path"))
        if not callback_path.startswith("/"):
            # issue in pyoidc when base_url ends with "/" and path does not start with "/" there's an extra "/" added (doubling)
            # to prevent that we finally enforce the "/" prefix on the path
            callback_path = f"/{callback_path}"
        client.consumer.consumer_config["authz_page"] = callback_path
        next_redirect_uri = self.get_next_url(request, "next")

        if not next_redirect_uri:
            next_redirect_uri = str(
                self.get_setting(
                    "post_login_uri_success", request.build_absolute_uri("/")
                )
            )

        request.session["oidc_login_next"] = next_redirect_uri

        sid, location = client.consumer.begin(  # type: ignore[no-untyped-call] # oic package is untyped
            scope=self.opsettings.get("scope"), # NEOGEO EDIT : to use `scope` defined in `DJANGO_PYOIDC` in Django settings instead of just `openid`
            response_type="code",
            use_nonce=True,
            path=self.request.build_absolute_uri("/"),
        )
        request.session["oidc_sid"] = sid
        return redirect(location)


def custom_get_user_info(self, state):
    # NEOGEO EDIT : to avoid fork of `oic` lib (`oic/oic/__init__.py` line 878 `method == "GET"` into `method in ["GET", "POST"]`)
    uinfo = self.do_user_info_request(state=state, method="GET")

    if uinfo.type() == "ErrorResponse":
        raise TokenError(uinfo._dict.get("error"), uinfo) # NEOGEO EDIT : to avoid `AttributeError: 'ErrorResponse' object has no attribute 'error'`

    self.user_info = uinfo
    self._backup(state)

    return uinfo

class CustomOIDCClient(OIDCClient):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.consumer.get_user_info = MethodType(custom_get_user_info, self.consumer) # NEOGEO EDIT : to overwrite get_user_info method

class CustomOIDCCallbackView(OIDCCallbackView):
    def get(self, request, *args, **kwargs):
        try:
            # Vérifie la présence de l'identifiant OIDC dans la session utilisateur
            if "oidc_sid" in request.session:
                self.client = CustomOIDCClient( # NEOGEO EDIT : to use overwritten get_user_info method
                    self.op_name, session_id=request.session["oidc_sid"]
                )

                # Analyse la réponse d'autorisation OIDC reçue dans la requête (callback)
                parsing_result = self.client.consumer.parse_authz(
                    query=request.GET.urlencode()
                )
                if isinstance(parsing_result, BadRequest):
                    logger.error(
                        "OIDC login process failure; cannot parse OIDC response"
                    )
                    return self.login_failure(request)

                aresp, atr, idt = parsing_result

                if aresp is None:
                    logger.error("OIDC login process failure; empty OIDC response")
                    return self.login_failure(request)

                # Vérifie que l'état OIDC retourné correspond à celui stocké en session (protection CSRF)
                if aresp["state"] == request.session["oidc_sid"]:
                    state = aresp["state"]
                    session_state = aresp.get("session_state")  # type: ignore[no-untyped-call] # oic is untyped yet

                    # pyoidc will make the next steps in OIDC login protocol
                    # pyoidc effectue les prochaines étapes du protocole OIDC (échange le code d'autorisation contre des tokens)
                    try:
                        tokens = self.client.consumer.complete(
                            state=state, session_state=session_state
                        )
                    except Exception as e:
                        logger.exception(e)
                        logger.error(
                            "OIDC login process failure; cannot end login protocol."
                        )
                        return self.login_failure(request)

                    # Collect data from userinfo endpoint
                    # Récupère les informations utilisateur depuis l'endpoint userinfo
                    try:
                        userinfo = self.client.consumer.get_user_info(state=state)  # type: ignore[no-untyped-call] # oic is untyped yet
                    except Exception as e:
                        logger.exception(e)
                        logger.error(
                            "OIDC login process failure; Cannot retrieve userinfo."
                        )
                        return self.login_failure(request)

                    # TODO: add a setting to allow/disallow session storage of the tokens
                    access_token_jwt = (
                        tokens["access_token"] if "access_token" in tokens else None
                    )

                    # this will call token instrospection or user defined validator
                    # or return None
                    # Effectue une introspection/validation du token d'accès (ou appel un validateur custom)
                    # Peut retourner None si le token n'est pas valide ou si le validateur ne l'accepte pas
                    access_token_claims = self.engine.introspect_access_token(
                        access_token_jwt, self.client
                    )

                    id_token_claims = (
                        tokens["id_token"].to_dict() if "id_token" in tokens else None
                    )
                    # id_token_jwt = (
                    #     tokens["id_token_jwt"] if "id_token_jwt" in tokens else None
                    # )
                    userinfo_claims = userinfo.to_dict()
                    tokens = {
                        "info_token_claims": userinfo_claims,
                        "access_token_jwt": access_token_jwt,
                        "access_token_claims": access_token_claims,
                        "id_token_claims": id_token_claims,
                    }
                    # simplify check code, if any dict is None remove the entry
                    # Nettoie le dict des tokens: retire toutes les clés ayant pour valeur None
                    filtered_tokens = {k: v for k, v in tokens.items() if v is not None}

                    # Call user hook
                    # Appelle le hook de récupération de l'utilisateur à partir des claims OIDC
                    user = self.engine.call_get_user_function(
                        tokens=filtered_tokens,
                        client=self.client,
                    )

                    if not user or not user.is_authenticated:
                        logger.error(
                            "OIDC login process failure. Cannot set active authenticated user."
                        )
                        return self.login_failure(request)
                    else:
                        # Authentifie l'utilisateur Django et crée la session
                        auth.login(request, user)

                        if not request.session.session_key:
                            request.session.save()
                        # Enregistre l'association session utilisateur <-> session OIDC
                        OIDCSession.objects.create(
                            state=state,
                            sub=userinfo["sub"],
                            cache_session_key=request.session.session_key,  # type: ignore[misc] # we call auth.login right before, so session_key is set to a value
                            session_state=session_state,
                        )
                        # Appelle le callback post-login custom si défini
                        self.call_user_login_callback_function(request, user)
                        # Calcule l'URL finale de redirection après authentification
                        redir = self.success_url(request)
                        return redirect(redir)
                else:
                    logger.warning(
                        "OIDC login process failure. OIDC state does not match session sid."
                    )
                    raise SuspiciousOperation(
                        "Login process: OIDC state does not match session sid."
                    )
            else:
                logger.warning(
                    "OIDC login process failure. No OIDC sid state in user session for a request on the OIDC callback."
                )
                return self.login_failure(request)
        except PermissionDenied as exc:
            logger.exception(exc)
            messages.error(request, "Permission Denied.")
            return self.login_failure(request)






























# from django.contrib.auth.backends import BaseBackend
# from django_pyoidc.client import OIDCClient
# from django.contrib.auth import get_user_model

# User = get_user_model()

# class CustomOIDCAuthenticationBackend(BaseBackend):
#     def authenticate(self, request, **kwargs):
#         """Authentifier l'utilisateur via OIDC."""
#         token = kwargs.get('token')
#         if not token:
#             return None

#         # Utilisez le client OIDC pour valider le token
#         oidc_client = OIDCClient(op_name='sso_keycloak')
#         userinfo = oidc_client.userinfo(token)

#         if not userinfo:
#             return None

#         username = userinfo.get('preferred_username')
#         email = userinfo.get('email')

#         # Rapprocher ou créer l'utilisateur
#         user, created = User.objects.get_or_create(
#             username=username,
#             defaults={'email': email}
#         )
#         return user

#     def get_user(self, user_id):
#         """Récupérer un utilisateur par son ID."""
#         try:
#             return User.objects.get(pk=user_id)
#         except User.DoesNotExist:
#             return None