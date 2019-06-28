from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from . import views
from collab.views.attachment import Attachment
from collab.views.comment import Comment
import collab.views.feature as feature
from collab.views.feature import ProjectFeature
from collab.views.feature import ProjectFeatureDetail
import collab.views.import_export as import_export
from collab.views.subscription import Subscription
from collab.views.views import LoginView
from collab.views.views import LogoutView
from collab.views.views import ProjectAdminView
from collab.views.views import ProjectServiceView
from collab.views.views import ProjectView

services = [
    path('api/liste_utilisateur/<slug:project_slug>', views.user_list),
    path('api/liste_projet/', views.project_list),
    path('api/export/', import_export.export_data),
    path('api/import/', import_export.import_data),
    path('api/json_feature_model/', import_export.get_json_feature_model),
    path('api/projet/', ProjectServiceView.as_view()),

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
    path('projet/<slug:project_slug>/membres/', views.project_members, name='project_members'),
    path('projet/<slug:project_slug>/ajout/', ProjectFeature.as_view(), name='project_add_feature'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/commentaire', Comment.as_view(),
         name='project_comment'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/attachment', Attachment.as_view(),
         name='project_attachment'),
    path('projet/<slug:project_slug>/<slug:feature_type_slug>/<uuid:feature_id>/abonnement', Subscription.as_view(),
          name='project_subscription'),
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
