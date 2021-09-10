from django.urls import path, re_path
from rest_framework import routers

from api.views.base_map import GetFeatureInfo
from api.views.base_map import BaseMapViewset
from api.views.base_map import LayerViewset
from api.views.feature import ExportFeatureList
from api.views.feature import FeatureSearch
from api.views.feature import FeatureTypeView
from api.views.feature import ProjectFeature
from api.views.feature import ProjectFeatureTypes
from api.views.feature import FeatureLinkView
from api.views.flat_pages import FlatPagesView
from api.views.login import LoginView
from api.views.login import LogoutView
from api.views.login import UserInfoView
from api.views.misc import AttachmentView
from api.views.misc import EventView
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
router.register(r'layers', LayerViewset, basename='base-maps')

urlpatterns = [
    # Vues générales de navigation
    path('login/', LoginView.as_view(), name='signin-view'),
    path('user_info/', UserInfoView.as_view(), name='user-info'),
    path('logout/', LogoutView.as_view(), name='signout-view'),
    path('flat-pages/', FlatPagesView.as_view(), name='help'),
    # Vues de gestion et d'édition des données métiers
    path(
        'user-level-projects/',
        UserLevelProjectView.as_view(), name='user-level-project'),
    path(
        'user-permissions/',
        UserPermissionsView.as_view(), name='user-permissions'),
    path(
        'projects/<slug:slug>/thumbnail/',
        ProjectThumbnailView.as_view(), name='project-thumbnail'),
    path(
        'projects/<slug:slug>/utilisateurs/',
        ProjectAuthorization.as_view(), name='project-authorization'),
    path(
        'projects/<slug:slug>/feature-types/',
        ProjectFeatureTypes.as_view(), name='project-feature-types'),
    path(
        'projects/<slug:slug>/feature/',
        ProjectFeature.as_view(), name='project-feature'),
    path(
        'projects/<slug:slug>/comments/',
        ProjectComments.as_view(), name='project-comments'),
    path(
        'projects/<slug:slug>/feature-type/<slug:feature_type_slug>/export/',
        ExportFeatureList.as_view(), name='project-export'),
    path(
        'projects/<slug:slug>/feature-search/',
        FeatureSearch.as_view(), name='feature-search'),
    path(
        'events/',
        EventView.as_view(), name='events-list'),
    path(
        'features/<uuid:feature_id>/feature-links/',
        FeatureLinkView.as_view(), name='feature-link'),
    path(
        'features/<uuid:feature_id>/attachments/',
        AttachmentView.as_view(actions={'post': 'create', 'get': 'list'}), name='attachments-list'),
    path(
        'features/<uuid:feature_id>/attachments/<uuid:attachment_id>/',
        AttachmentView.as_view(actions={'get': 'retrieve'}), name='attachments-retrieve'),
    path(
        'features/<uuid:feature_id>/attachments/<uuid:attachment_id>/',
        AttachmentView.as_view(actions={'delete': 'destroy'}), name='attachments-destroy'),
    path(
        'proxy/',
        GetFeatureInfo.as_view(), name='proxy'),
]


urlpatterns += router.urls
