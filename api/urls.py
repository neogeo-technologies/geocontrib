from django.urls import include, path
from rest_framework import routers

from api.views.feature import ExportFeatureList
from api.views.feature import FeatureSearch
from api.views.project import ProjectView
from api.views.project import Projects
from api.views.project import ProjectAuthorization
from api.views.project import ProjectDatas
from api.views.base_map import GetFeatureInfo

from api.views.user import userViewSet
from api.views.user import GroupViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, basename='projects')
router.register(r'users', userViewSet)
router.register(r'groups', GroupViewSet)

urlpatterns = [
    path(
        'projects2/',
        Projects.as_view(), name='all_projects'),
    # path(
    #     'projet/<slug:slug>/project',
    #     ProjectDatas.as_view(), name='project-data'),
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
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))

]


urlpatterns += router.urls
