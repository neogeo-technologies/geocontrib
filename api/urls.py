from django.urls import path
from rest_framework import routers

from api.views.feature import ExportFeatureList
from api.views.feature import FeatureSearch
from api.views.project import ProjectView
from api.views.project import ProjectAuthorization


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, base_name='projects')

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
]


urlpatterns += router.urls
