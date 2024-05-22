from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.http import HttpResponseRedirect
from django.urls import reverse
from django.urls import NoReverseMatch
from django.views.static import serve

from geocontrib.models import Attachment
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.views import HomePageView
from geocontrib.views import MyAccount
from geocontrib.views import FeatureTypeDetail
from geocontrib.views import view404

import logging

app_name = 'geocontrib'

# Configuration du logging
logging.basicConfig(level=logging.DEBUG, format='[%(asctime)s] %(levelname)s: %(message)s')
logger = logging.getLogger(__name__)
"""
This function distinguishes between a URL name and an absolute URL.
For a URL name, it constructs the absolute URL by appending the base URL.
"""
def build_full_url(url_name):
    logger.debug(f"Building full URL for {url_name}.")
    if url_name.startswith(('http://', 'https://')):
        # It's already an absolute URL, return it as is
        return url_name
    else:
        try:
            # Try to resolve the URL name using reverse
            resolved_url = reverse(url_name)
            # Build the full URL if settings.BASE_URL is defined
            logger.debug(f"Value for resolved URL: {resolved_url}.")
            logger.debug(f"Value for environment variable BASE_URL: {settings.BASE_URL}.")
            full_url = f"{settings.BASE_URL}{resolved_url}" if hasattr(settings, 'BASE_URL') else resolved_url
            return full_url
        except NoReverseMatch:
            # Handle the error if the URL name is not valid
            logger.error(f"No reverse match for {url_name}. Check your URL configuration.")
            return None

"""Redirects the user to a login page if they are not authenticated."""
def redirect_to_login(request):
    # Get custom login URL if the environment variable LOG_URL is defined
    login_url = getattr(settings, 'LOG_URL', None)
    if login_url is None:
        # Or get LOGIN_URL (either specified custom login URL or Django's default)
        login_url = settings.LOGIN_URL
    # Resolve the login URL using our utility function to handle both types of URLs
    login_url = build_full_url(login_url)
    # Use build_absolute_uri to obtain the complete URL of the current request
    full_url = request.build_absolute_uri()
    # Create the redirect URL including the original URL as a query parameter for later redirection
    redirect_url = f'{login_url}?url_redirect={full_url}'
    logger.debug(f"User not allowed to access this resource, redirecting to login URL: {redirect_url}.")
    return HttpResponseRedirect(redirect_url)

"""
This function aims at protecting files served in media folder from being viewed
without having the right access to the feature to which the attachment is associated
It uses the method to retrieve available features for a given user which does all the checks
with custom permissions designed within geocontrib application
"""
def protected_serve(request, path='', document_root=None, show_indexes=False):
    logger.debug(f"Entering function to protect static files for {path}.")
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
            if attachment_feature:
                # if the feature associated with the attachment is found among the available features
                # for this user, then continue with serving the ressource
                return serve(request, path, document_root, show_indexes)
    # If permission denied or attachment not found, redirect user to login page
    return redirect_to_login(request)

urlpatterns = [
    # Get the media files path to register routes towards it and control if the requested files can be viewed by current user
    path('media/<path:path>', protected_serve, {'document_root': settings.MEDIA_ROOT}),
    # Vues générales de navigation
    path('', HomePageView.as_view(), name='index'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='geocontrib/registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='geocontrib/registration/login.html'), name='logout'),
    path('mon-compte/', MyAccount.as_view(), name='my_account'),


    path('projet/<slug:slug>/', view404, name='project'),

    # Vues de gestion et d'édition des données métiers
    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/',
         FeatureTypeDetail.as_view(), name='feature_type_detail'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/',
        view404,
        name='feature_detail'),
    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/editer/',
        view404,
        name='feature_update'),


]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
