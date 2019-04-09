from django.conf.urls import url
from django.urls import path
from . import views

urlpatterns = [
    url(r'^ajout_signalement/', views.ajout_signalement),
    path('', views.index, name='index'),
    path('mon_compte/', views.my_account, name='my_account'),
    path('mentions/', views.legal, name='legal'),
    path('aide/', views.site_help, name='help'),
    path('projet/<slug:project_slug>/', views.project, name='project'),
    path('projet/<slug:project_slug>/utilisateurs/', views.project_users, name='project_users'),
    path('projet/<slug:project_slug>/liste/', views.project_issues_list, name='project_issues_list'),
    path('projet/<slug:project_slug>/carte/', views.project_issues_map, name='project_issues_map'),
    path('projet/<slug:project_slug>/signalement/<int:issue_id>', views.project_issue_detail,
         name='project_issue_detail'),
    path('projet/<slug:project_slug>/import/', views.project_import_issues, name='project_import_issues'),
    path('projet/<slug:project_slug>/import-geo-image/', views.project_import_geo_image,
         name='project_import_geo_image'),
    path('projet/<slug:project_slug>/export/', views.project_download_issues, name='project_download_issues'),
]
