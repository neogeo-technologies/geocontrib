from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.flatpages import views as flatpages_views

from geocontrib.views import HomePageView
from geocontrib.views import MyAccount
from geocontrib.views import ProjectDetail
from geocontrib.views import FeatureList
from geocontrib.views import FeatureDetail
from geocontrib.views import FeatureUpdate
from geocontrib.views import FeatureDelete
from geocontrib.views import ProjectUpdate
from geocontrib.views import ProjectMapping
from geocontrib.views import FeatureCreate
from geocontrib.views import FeatureTypeCreate
from geocontrib.views import FeatureTypeDetail
from geocontrib.views import FeatureTypeUpdate
from geocontrib.views import ImportFromGeoJSON
from geocontrib.views import ImportFromImage
from geocontrib.views import ProjectCreate
from geocontrib.views import CommentCreate
from geocontrib.views import AttachmentCreate
from geocontrib.views import ProjectMembers
from geocontrib.views import ProjectTypeListView
from geocontrib.views import SubscribingView


app_name = 'geocontrib'

urlpatterns = [

    # Vues générales de navigation
    path('', HomePageView.as_view(), name='index'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='geocontrib/registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='geocontrib/registration/login.html'), name='logout'),
    path('mon-compte/', MyAccount.as_view(), name='my_account'),

    path('aide/', flatpages_views.flatpage, {'url': '/aide/'}, name='help'),
    path('mentions/', flatpages_views.flatpage, {'url': '/mentions/'}, name='legal'),


    # Vues de gestion et d'édition des données métiers
    path('creer-projet/', ProjectCreate.as_view(), name='project_create'),

    path('projet-type/', ProjectTypeListView.as_view(), name='project_type_list'),

    path('projet/<slug:slug>/', ProjectDetail.as_view(), name='project'),

    path('projet/<slug:slug>/editer/', ProjectUpdate.as_view(), name='project_update'),

    path('projet/<slug:slug>/membres/', ProjectMembers.as_view(), name='project_members'),

    path('projet/<slug:slug>/administration-carte/', ProjectMapping.as_view(), name='project_mapping'),

    path(
        'projet/<slug:slug>/abonnement/<str:action>/', SubscribingView.as_view(),
        name='subscription'),

    path('projet/<slug:slug>/type-signalement/ajouter/',
         FeatureTypeCreate.as_view(), name="feature_type_create"),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/',
         FeatureTypeDetail.as_view(), name='feature_type_detail'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/editer',
         FeatureTypeUpdate.as_view(), name='feature_type_update'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/importer-geojson/',
         ImportFromGeoJSON.as_view(), name='import_from_geojson'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/importer-image/',
         ImportFromImage.as_view(), name='import_from_image'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/ajouter/',
         FeatureCreate.as_view(), name='feature_create'),

    path('projet/<slug:slug>/signalement/lister/',
         FeatureList.as_view(), name='feature_list'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/',
        FeatureDetail.as_view(),
        name='feature_detail'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/editer/',
        FeatureUpdate.as_view(),
        name='feature_update'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/supprimer/',
        FeatureDelete.as_view(),
        name='feature_delete'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/commentaire/ajouter/',
        CommentCreate.as_view(),
        name='add_comment'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/piece-jointe/ajouter/',
        AttachmentCreate.as_view(),
        name='add_attachment'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
