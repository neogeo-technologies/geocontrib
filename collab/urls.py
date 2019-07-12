from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from collab.views.accounts import HomePageView
from collab.views.accounts import MyAccount
# from collab.views.accounts import LoginView
# from collab.views.accounts import LogoutView
from collab.views.accounts import legal
from collab.views.accounts import site_help
from collab.views.content_managment import ProjectDetail
from collab.views.content_managment import FeatureList
from collab.views.content_managment import FeatureDetail
# from collab.views.content_managment import FeatureUpdate
from collab.views.content_managment import FeatureDelete
from collab.views.content_managment import ProjectExtendedDetail
from collab.views.content_managment import ProjectMap
from collab.views.content_managment import CreateFeature
from collab.views.content_managment import CreateFeatureType
from collab.views.content_managment import CreateProject
from collab.views.content_managment import CreateComment
from collab.views.content_managment import CreateAttachment
from collab.views.content_managment import ProjectMembers

# from . import views
# import collab.views.feature as feature
# from collab.views.attachment import ProjectAttachment
# from collab.views.comment import ProjectComment
# from collab.views.views import ProjectAdminView
# from collab.views.feature import ProjectFeature
# from collab.views.feature import ProjectFeatureDetail
# from collab.views.views import ProjectView

app_name = 'collab'
urlpatterns = [

    # Vues générales de navigation
    path('', HomePageView.as_view(), name='index'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='collab/registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='collab/registration/login.html'), name='logout'),
    path('mon-compte/', MyAccount.as_view(), name='my_account'),
    path('aide', site_help, name='help'),
    path('mentions', legal, name='legal'),

    # Vues de gestion et d'édition des données métiers
    path('creer-projet/', CreateProject.as_view(), name='create_project'),

    path('projet/<slug:slug>/', ProjectDetail.as_view(), name='project'),

    path('projet/<slug:slug>/editer/', ProjectExtendedDetail.as_view(), name='admin_project'),

    path('projet/<slug:slug>/membres/', ProjectMembers.as_view(), name='project_members'),

    path('projet/<slug:slug>/type-signalement/ajouter',
         CreateFeatureType.as_view(), name="add_feature_type"),

    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/ajouter/',
         CreateFeature.as_view(), name='add_feature'),

    path('projet/<slug:slug>/signalement/lister/',
         FeatureList.as_view(), name='feature_list'),

    path('projet/<slug:slug>/carte/', ProjectMap, name='project_map'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>',
        FeatureDetail.as_view(),
        name='feature_detail'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/supprimer',
        FeatureDelete.as_view(),
        name='feature_delete'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/commentaire/ajouter',
        CreateComment.as_view(),
        name='add_comment'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/piece-jointe/ajouter',
        CreateAttachment.as_view(),
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
