from django.urls import path
from rest_framework import routers

from api.views.feature import ExportFeatureList
from api.views.feature import FeatureSearch
from api.views.project import ProjectView
from api.views.project import ProjectAuthorization
from api.views.base_map import GetFeatureInfo
from api.views.misc import ImportTaskSearch


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, basename='projects')
router.register(r'import-tasks', ImportTaskSearch, basename='importtask')

urlpatterns = [
    path(
        'projet/<slug:slug>/utilisateurs',
        ProjectAuthorization.as_view(), name='project-authorization'),
    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/export',
        ExportFeatureList.as_view(), name='project-export'),
    path(
        'projet/<slug:slug>/signalement/recherche/',
        FeatureSearch.as_view(), name='feature-search'),
    path(
        'proxy/',
        GetFeatureInfo.as_view(), name='proxy'),
]


urlpatterns += router.urls
