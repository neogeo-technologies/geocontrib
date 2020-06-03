from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from geocontrib.views.accounts import HomePageView
from geocontrib.views.accounts import MyAccount
# from geocontrib.views.accounts import LoginView
# from geocontrib.views.accounts import LogoutView
from geocontrib.views.accounts import legal
from geocontrib.views.accounts import site_help
from geocontrib.views.content_managment import ProjectDetail
from geocontrib.views.content_managment import FeatureList
from geocontrib.views.content_managment import FeatureDetail
from geocontrib.views.content_managment import FeatureUpdate
from geocontrib.views.content_managment import FeatureDelete
from geocontrib.views.content_managment import ProjectUpdate
from geocontrib.views.content_managment import ProjectMapping
from geocontrib.views.content_managment import FeatureCreate
from geocontrib.views.content_managment import FeatureTypeCreate
from geocontrib.views.content_managment import FeatureTypeDetail
from geocontrib.views.content_managment import FeatureTypeUpdate
from geocontrib.views.content_managment import ImportFromGeoJSON
from geocontrib.views.content_managment import ImportFromImage
from geocontrib.views.content_managment import ProjectCreate
from geocontrib.views.content_managment import CommentCreate
from geocontrib.views.content_managment import AttachmentCreate
from geocontrib.views.content_managment import ProjectMembers
from geocontrib.views.content_managment import SubscribingView

# from . import views
# import geocontrib.views.feature as feature
# from geocontrib.views.attachment import ProjectAttachment
# from geocontrib.views.comment import ProjectComment
# from geocontrib.views.views import ProjectAdminView
# from geocontrib.views.feature import ProjectFeature
# from geocontrib.views.feature import ProjectFeatureDetail
# from geocontrib.views.views import ProjectView

app_name = 'geocontrib'

urlpatterns = [

    # Vues générales de navigation
    path('', HomePageView.as_view(), name='index'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='geocontrib/registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='geocontrib/registration/login.html'), name='logout'),
    path('mon-compte/', MyAccount.as_view(), name='my_account'),
    path('aide', site_help, name='help'),
    path('mentions', legal, name='legal'),

    # Vues de gestion et d'édition des données métiers
    path('creer-projet/', ProjectCreate.as_view(), name='project_create'),  # create_project

    path('projet/<slug:slug>/', ProjectDetail.as_view(), name='project'),

    path('projet/<slug:slug>/editer/', ProjectUpdate.as_view(), name='project_update'),  # admin_project

    path('projet/<slug:slug>/membres/', ProjectMembers.as_view(), name='project_members'),

    path('projet/<slug:slug>/administration-carte/', ProjectMapping.as_view(), name='project_mapping'),

    path(
        'projet/<slug:slug>/abonnement/<str:action>/', SubscribingView.as_view(),
        name='subscription'),

    path('projet/<slug:slug>/type-signalement/ajouter/',
         FeatureTypeCreate.as_view(), name="feature_type_create"),  # add_feature_type

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/',
         FeatureTypeDetail.as_view(), name='feature_type_detail'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/editer',
         FeatureTypeUpdate.as_view(), name='feature_type_update'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/importer-geojson/',
         ImportFromGeoJSON.as_view(), name='import_from_geojson'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/importer-image/',
         ImportFromImage.as_view(), name='import_from_image'),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/ajouter/',
         FeatureCreate.as_view(), name='feature_create'),  # add_feature

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

    # path('mon_compte/activation', views.activation, name='activation'),
    # path('projet/<slug:project_slug>/utilisateurs/', views.project_users, name='project_users'),
    # path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/attachment', ProjectAttachment.as_view(),
    #      name='project_add_attachment'),
    # path('projet/<slug:project_slug>/import/', views.project_import_issues, name='project_import_issues'),
    # path('projet/<slug:project_slug>/import-geo-image/', views.project_import_geo_image,
    #      name='project_import_geo_image'),
    # path('projet/<slug:project_slug>/export/', views.project_download_issues, name='project_download_issues'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
