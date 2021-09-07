from django.urls import path
from rest_framework import routers

from api.views.base_map import GetFeatureInfo
from api.views.base_map import BaseMapViewset
from api.views.feature import ExportFeatureList
from api.views.feature import FeatureSearch
from api.views.feature import FeatureTypeView
from api.views.feature import ProjectFeature
from api.views.feature import ProjectFeatureTypes
from api.views.flat_pages import FlatPagesView
from api.views.login import LoginView
from api.views.login import LogoutView
from api.views.login import UserInfoView
from api.views.misc import ImportTaskSearch
from api.views.misc import ProjectComments
from api.views.project import ProjectAuthorization
from api.views.project import ProjectThumbnailView
from api.views.project import ProjectView
from api.views.user import UserLevelProjectView
from api.views.user import UserPermissionsView
from api.views.user import UserViewSet


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, basename='projects')
router.register(r'feature-types', FeatureTypeView, basename='feature-types')
router.register(r'users', UserViewSet, basename='users')
router.register(r'import-tasks', ImportTaskSearch, basename='importtask')
router.register(r'base-maps', BaseMapViewset, basename='base-maps')

urlpatterns = [
    # Vues générales de navigation
    path("login/", LoginView.as_view(), name="signin-view"),
    path("user_info/", UserInfoView.as_view(), name="user-info"),
    path("logout/", LogoutView.as_view(), name="signout-view"),

    path('flat-pages/', FlatPagesView.as_view(), name='help'),

    # Vues de gestion et d'édition des données métiers
    path(
        'user_level_project/',
        UserLevelProjectView.as_view(),
        name='user_level_project'),
    path(
        'user_permissions/',
        UserPermissionsView.as_view(),
        name='user_permissions'),
    path(
        'projects/<slug:slug>/thumbnail/',
        ProjectThumbnailView.as_view(), name='project-thumbnail'),
    path(
        'projet/<slug:slug>/utilisateurs/',
        ProjectAuthorization.as_view(), name='project-authorization'),
    path(
        'projet/<slug:slug>/feature_types/',
        ProjectFeatureTypes.as_view(), name='project-feature-types'),
    path(
        'projet/<slug:slug>/feature/',
        ProjectFeature.as_view(), name='project-feature'),
    path(
        'projet/<slug:slug>/comments/',
        ProjectComments.as_view(), name='project-comments'),
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
