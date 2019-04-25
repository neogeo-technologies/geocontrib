from django.conf.urls import re_path
from django.urls import path
from . import views
from collab.views.views import ProjectFeature
from collab.views.views import ProjectView

services = [
    path('liste_projet/', views.project_list),
]

urlpatterns = services + [
    path('ajout_signalement/', views.add_feature_model),
    path('', views.index, name='index'),
    path('mon_compte/', views.my_account, name='my_account'),
    path('mentions/', views.legal, name='legal'),
    path('aide/', views.site_help, name='help'),
    path('creer_projet/', ProjectView.as_view(), name='create_project'),
    path('projet/<slug:project_slug>/', views.project, name='project'),
    path('projet/<slug:project_slug>/utilisateurs/', views.project_users, name='project_users'),
    path('projet/<slug:project_slug>/add/', ProjectFeature.as_view(), name='project_add_feature'),
    path('projet/<slug:project_slug>/liste/', views.project_feature_list, name='project_feature_list'),
    path('projet/<slug:project_slug>/<slug:feature_type>/<int:feature_pk>', views.project_feature_detail,
         name='project_feature_detail'),
    path('projet/<slug:project_slug>/import/', views.project_import_issues, name='project_import_issues'),
    path('projet/<slug:project_slug>/import-geo-image/', views.project_import_geo_image,
         name='project_import_geo_image'),
    path('projet/<slug:project_slug>/export/', views.project_download_issues, name='project_download_issues'),
]
