from django.urls import path
from django.urls import re_path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.core.exceptions import PermissionDenied
from django.views.static import serve

from geocontrib.models import Attachment
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.views import HomePageView
from geocontrib.views import MyAccount
from geocontrib.views import FeatureTypeDetail
from geocontrib.views import view404

app_name = 'geocontrib'

"""
This function aims at protecting files served in media folder from being viewed
without having the right access to the feature to which the attachment is associated
It uses the method to retrieve available features for a given user which does all the checks
with custom permissions designed within geocontrib application
"""
def protected_serve(request, path, document_root=None, show_indexes=False):
    # check if an attachment exist with the file pathname
    attachment = Attachment.objects.get(attachment_file=path)
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
    # else return a permission denied exception
    raise PermissionDenied()

urlpatterns = [
    # Get the media files path to register routes towards it and control if the requested files can be viewed by current user
    re_path(r'^%s(?P<path>.*)$' % settings.MEDIA_URL[1:], protected_serve, {'document_root': settings.MEDIA_ROOT}),
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
