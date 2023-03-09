from django.urls import path, re_path
from rest_framework import routers


from api.views.base_map import BaseMapViewset
from api.views.base_map import GetFeatureInfo
from api.views.base_map import LayerViewset
from api.views.feature import ExportFeatureList
from api.views.feature import FeatureEventView
from api.views.feature import FeatureLinkView
from api.views.feature import FeatureSearch
from api.views.feature import FeatureTypeView
from api.views.feature import FeatureView
from api.views.feature import FeatureMVTView
from api.views.feature import GetExternalGeojsonView
from api.views.feature import GetIdgoCatalogView
from api.views.feature import PreRecordedValuesView
from api.views.feature import ProjectFeature
from api.views.feature import ProjectFeatureBbox
from api.views.feature import ProjectFeaturePaginated
from api.views.feature import ProjectFeaturePositionInList
from api.views.feature import ProjectFeatureTypes
from api.views.flat_pages import FlatPagesView
from api.views.login import LoginView
from api.views.login import LogoutView
from api.views.login import UserInfoView
from api.views.misc import FeatureAttachmentView
from api.views.misc import FeatureAttachmentUploadView
from api.views.misc import CommentView
from api.views.misc import CommentAttachmentUploadView
from api.views.misc import EventView
from api.views.misc import ExifGeomReaderView
from api.views.misc import ImportTaskSearch
from api.views.misc import ProjectComments
from api.views.project import ProjectAuthorizationView
from api.views.project import ProjectSubscription
from api.views.project import ProjectThumbnailView
from api.views.project import ProjectView
from api.views.project import ProjectTypesView
from api.views.project import ProjectDuplicate
from api.views.user import TokenView
from api.views.user import UserLevelProjectView
from api.views.user import UserPermissionsView
from api.views.user import UserViewSet
from api.views.user import UserLevelsPermission
from api.views import version

app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, basename='projects')
router.register(r'features', FeatureView, basename='features')
router.register(r'users', UserViewSet, basename='users')
router.register(r'import-tasks', ImportTaskSearch, basename='importtask')
router.register(r'base-maps', BaseMapViewset, basename='base-maps')
router.register(r'layers', LayerViewset, basename='layers')
router.register(r'levels-permissions', UserLevelsPermission, basename='levels-permissions')
router.register(r'project-types', ProjectTypesView, basename='projects-types')
# deprecated
router.register(r'feature-types', FeatureTypeView, basename='feature-types')

urlpatterns = [
    # Vues générales de navigation
    path('version', version, name='version'),
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
        'projects/<slug:slug>/duplicate/',
        ProjectDuplicate.as_view(), name='project-duplicate'),
    path(
        'projects/<slug:slug>/thumbnail/',
        ProjectThumbnailView.as_view(), name='project-thumbnail'),
    path(
        'projects/<slug:project__slug>/utilisateurs/',
        ProjectAuthorizationView.as_view(), name='project-authorization'),
    path(
        'projects/<slug:slug>/feature-types/',
        ProjectFeatureTypes.as_view(), name='project-feature-types'),
    path(
        'projects/<slug:slug>/feature/',
        ProjectFeature.as_view(), name='project-feature'),
    path(
        'projects/<slug:slug>/feature-paginated/',
        ProjectFeaturePaginated.as_view(), name='project-feature-paginated'),
    path(
        'projects/<slug:slug>/feature-bbox/',
        ProjectFeatureBbox.as_view(), name='project-feature-bbox'),
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
        'projects/<slug:slug>/subscription/',
        ProjectSubscription.as_view(), name='project-subscription'),
    path(
        'projects/<slug:slug>/feature/<uuid:feature_id>/position-in-list/',
        ProjectFeaturePositionInList.as_view(), name='project-feature-position-in-list'),
    path(
        'events/',
        EventView.as_view(), name='events-list'),
    path(
        'exif-geom-reader/',
        ExifGeomReaderView.as_view(), name='exif'),
    path(
        'features/<uuid:feature_id>/feature-links/',
        FeatureLinkView.as_view(), name='feature-link'),
    path(
        'features/<uuid:feature_id>/events/',
        FeatureEventView.as_view(), name='feature-events'),


    path(
        'features/<uuid:feature_id>/attachments/',
        FeatureAttachmentView.as_view(actions={'get': 'list', 'post': 'create'}),
        name='feature-attachments-list'),
    path(
        'features/<uuid:feature_id>/attachments/<uuid:attachment_id>/',
        FeatureAttachmentView.as_view(actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='feature-attachments-retrieve'),
    path(
        'features/<uuid:feature_id>/attachments/<uuid:attachment_id>/upload-file/',
        FeatureAttachmentUploadView.as_view(),
        name='feature-attachments-upload-file'),

    path(
        'features/<uuid:feature_id>/comments/',
        CommentView.as_view(actions={'get': 'list', 'post': 'create'}),
        name='comments-list'),
    path(
        'features/<uuid:feature_id>/comments/<uuid:comment_id>/',
        CommentView.as_view(actions={'get': 'retrieve', 'put': 'update', 'delete': 'destroy'}),
        name='comments-detail'),
    path(
        'features/<uuid:feature_id>/comments/<uuid:comment_id>/upload-file/',
        CommentAttachmentUploadView.as_view(),
        name='comments-upload-file'),

    path("features.mvt/", FeatureMVTView.as_view(), name="features-mvt"),
    path("external-geojson/", GetExternalGeojsonView.as_view()),
    path("idgo-catalog/", GetIdgoCatalogView.as_view()),

    path(
        'proxy/',
        GetFeatureInfo.as_view(), name='proxy'),

    path(
        'prerecorded-list-values/',
        PreRecordedValuesView.as_view(), name='prerecorded-list-values'),
    path(
        'prerecorded-list-values/<str:name>/',
        PreRecordedValuesView.as_view(), name='prerecorded-list-values'),

    path(
        'get-token/',
        TokenView.as_view(), name='get-token'
    )
]


urlpatterns += router.urls
