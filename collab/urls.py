from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
import collab.views.feature as feature
from collab.views.attachment import ProjectAttachment
from collab.views.comment import ProjectComment
from collab.views.views import LoginView
from collab.views.views import LogoutView
from collab.views.views import ProjectAdminView
from collab.views.feature import ProjectFeature
from collab.views.feature import ProjectFeatureDetail
from collab.views.views import ProjectView

services = [
    path('api/liste_projet/', views.project_list),
]

urlpatterns = services + [
    path('connexion/', LoginView.as_view(), name='login'),
    path('deconnexion/', LogoutView.as_view(), name='logout'),
    path('', views.index, name='index'),
    path('mon_compte/', views.my_account, name='my_account'),
    path('mentions/', views.legal, name='legal'),
    path('aide/', views.site_help, name='help'),
    path('creer_projet/', ProjectView.as_view(), name='create_project'),
    path('admin_projet/<slug:project_slug>/', ProjectAdminView.as_view(), name='admin_project'),
    path('projet/<slug:project_slug>/ajouter_type_signalement/', views.add_feature_model, name="add_feature_model"),
    path('projet/<slug:project_slug>/', views.project, name='project'),
    path('projet/<slug:project_slug>/utilisateurs/', views.project_users, name='project_users'),
    path('projet/<slug:project_slug>/ajout/', ProjectFeature.as_view(), name='project_add_feature'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/commentaire', ProjectComment.as_view(),
         name='project_add_comment'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/attachment', ProjectAttachment.as_view(),
         name='project_add_attachment'),
    path('projet/<slug:project_slug>/liste/', feature.project_feature_list, name='project_feature_list'),
    path('projet/<slug:project_slug>/carte/', feature.project_feature_map, name='project_feature_map'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>', ProjectFeatureDetail.as_view(),
         name='project_feature_detail'),
    path('projet/<slug:project_slug>/import/', views.project_import_issues, name='project_import_issues'),
    path('projet/<slug:project_slug>/import-geo-image/', views.project_import_geo_image,
         name='project_import_geo_image'),
    path('projet/<slug:project_slug>/export/', views.project_download_issues, name='project_download_issues'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
