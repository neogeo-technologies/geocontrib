from django.urls import path
from rest_framework import routers
# from django.conf.urls.static import static
# from django.conf import settings

from api.views import ExportFeatureList
from api.views import AvailablesFeatureLinkList
from api.views import ProjectView
from api.views import ProjectAuthorization


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, base_name='projects')

urlpatterns = [
    path('projet/<slug:slug>/utilisateurs', ProjectAuthorization.as_view(), name='project-authorization'),
    path('projet/<slug:slug>/export', ExportFeatureList.as_view(), name='project-export'),
    path(
        'projet/<slug:slug>/type-signalements/<slug:feature_type_slug>/recherche',
        AvailablesFeatureLinkList.as_view(), name='feature-search'
    ),
]


urlpatterns += router.urls
