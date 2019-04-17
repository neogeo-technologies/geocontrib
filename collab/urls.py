from django.conf.urls import re_path
from django.urls import path
from . import views
from collab.views.views import ProjectFeature

services = [
    path('liste_projet/', views.project_list),
]

urlpatterns = services + [
    path('ajout_signalement/', views.add_feature_model),
    path('', views.index, name='index'),
    path('mon_compte/', views.my_account, name='my_account'),
    path('mentions/', views.legal, name='legal'),
    path('aide/', views.site_help, name='help'),
    path('projet/<slug:project_slug>/', views.project, name='project'),
    path('projet/<slug:project_slug>/utilisateurs/', views.project_users, name='project_users'),
    path('projet/<slug:project_slug>/add/', ProjectFeature.as_view(), name='project_add_feature'),
    path('projet/<slug:project_slug>/liste/', views.project_issues_list, name='project_issues_list'),
    path('projet/<slug:project_slug>/carte/', views.project_issues_map, name='project_issues_map'),
    path('projet/<slug:project_slug>/signalement/<int:issue_id>', views.project_issue_detail,
         name='project_issue_detail'),
    path('projet/<slug:project_slug>/import/', views.project_import_issues, name='project_import_issues'),
    path('projet/<slug:project_slug>/import-geo-image/', views.project_import_geo_image,
         name='project_import_geo_image'),
    path('projet/<slug:project_slug>/export/', views.project_download_issues, name='project_download_issues'),
]
