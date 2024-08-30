from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseNotFound
from django.http import HttpResponseRedirect
from django.views.decorators.csrf import csrf_exempt
from django.views.generic.detail import SingleObjectMixin
from django.views.static import serve

from api.serializers import BaseMapSerializer
from api.serializers import FeatureDetailedSerializer
from api.serializers import LayerSerializer
from geocontrib import logger
from geocontrib.models import Attachment
from geocontrib.models import BaseMap
from geocontrib.models import Feature
from geocontrib.models import FeatureType
from geocontrib.models import Layer
from geocontrib.models import Project


DECORATORS = [csrf_exempt, login_required(login_url=settings.LOGIN_URL)]


class BaseMapContextMixin(SingleObjectMixin):

    def get_context_data(self, feature_id=None, **kwargs):
        self.object = self.get_object()
        context = super().get_context_data(**kwargs)
        try:
            request = self.request
            project = None
            title = None
            if any([isinstance(self.object, model) for model in [Project, FeatureType, Feature]]):
                title = self.object.title
            if isinstance(self.object, Project):
                project = self.object
            elif isinstance(self.object, FeatureType) or isinstance(self.object, Feature):
                project = self.object.project

            serialized_base_maps = BaseMapSerializer(
                BaseMap.objects.filter(project=project),
                many=True
            )
            serialized_layers = LayerSerializer(
                Layer.objects.all(),
                many=True
            )
            features = Feature.handy.availables(user=self.request.user, project=project)

            if feature_id:
                features = features.filter(feature_id=feature_id)

            serialized_features = FeatureDetailedSerializer(
                features,
                is_authenticated=request.user.is_authenticated,
                context={'request': request},
                many=True
            )
            context['serialized_features'] = serialized_features.data
            context['serialized_base_maps'] = serialized_base_maps.data
            context['serialized_layers'] = serialized_layers.data
            context['title'] = title
        except Exception:
            logger.exception('BaseMapContext error')
        return context


def view404(request, *args, **kwargs):
    return HttpResponseNotFound('<h1>Page not implemented in Geocontrib backend</h1>')


"""
This function distinguishes between a URL name and an absolute URL.
For a URL name, it constructs the absolute URL by appending the base URL.
"""
def build_full_url(url_name):
    logger.error(f"Building full URL for {url_name}.")
    if url_name.startswith(('http://', 'https://')):
        # It's already an absolute URL, return it as is
        return url_name
    else:
        # Assume it's a path and append BASE_URL if available
        full_url = f"{settings.BASE_URL}{url_name}" if hasattr(settings, 'BASE_URL') else url_name
        logger.error(f"Full URL built: {full_url}.")
        return full_url

"""Redirects the user to a login page if they are not authenticated."""
def redirect_to_login(request):
    # Define a default login URL that matches the expected path in the frontend application.
    default = '/geocontrib/connexion'


    # Attempt to retrieve a custom login URL from settings, with priority for url accepting a redirect.
    # If 'SSO_LOGIN_URL_WITH_REDIRECT' is not defined in settings, getattr will return None, fallback to 'LOG_URL'.
    # If 'LOG_URL' is also not defined in settings, getattr will return the default value specified.
    # The 'or default' ensures that we fallback to the default URL if LOG_URL is an empty string (which should be the case here).
    login_url = getattr(settings, 'SSO_LOGIN_URL_WITH_REDIRECT', None) or getattr(settings, 'LOG_URL', default) or default

    # Resolve the login URL using our utility function to handle both types of URLs
    login_url = build_full_url(login_url)
    # Use build_absolute_uri to obtain the complete URL of the current request
    full_url = request.build_absolute_uri()
    # Create the redirect URL including the original URL as a query parameter for later redirection
    redirect_url = f'{login_url}?url_redirect={full_url}'

    logger.error(f"User not allowed to access this resource, redirecting to login URL: {redirect_url}.")
    return HttpResponseRedirect(redirect_url)

"""
This function aims at protecting files served in media folder from being viewed
without having the right access to the feature to which the attachment is associated
It uses the method to retrieve available features for a given user which does all the checks
with custom permissions designed within geocontrib application
"""
def protected_serve(request, path='', document_root=None, show_indexes=False):
    logger.error(f"Entering function to protect static files for {path}.")
    # check if an attachment exist with the file pathname
    attachment = Attachment.objects.filter(attachment_file=path).first()
    if attachment:
        # retrieve project instance to get available feature for current user
        attachment_project = Project.objects.get(id=attachment.project_id)
        if attachment_project:
            # get only features that the current user is allowed to view
            accessible_features = Feature.handy.availables(user=request.user, project=attachment_project)
            # retrieve the feature to which the file is associated inside available features
            attachment_feature = accessible_features.filter(feature_id=attachment.feature_id)
            # if the feature associated with the attachment is found among the available
            # features for this user, then continue with serving the ressource
            if attachment_feature:
                # Adapt header X-Frame-Options to view file in element like <embed> to view pdf in frontend
                response = serve(request, path, document_root, show_indexes)
                response['X-Frame-Options'] = 'ALLOW-FROM {}'.format(settings.BASE_URL)
                return response
    # If permission denied or attachment not found, redirect user to login page
    return redirect_to_login(request)