from django.urls import path
from rest_framework import routers
# from django.conf.urls.static import static
# from django.conf import settings

from api.views import ExportFeatureList
from api.views import ProjectView
from api.views import ProjectAuthorization


app_name = 'api'

router = routers.DefaultRouter()
router.register(r'projects', ProjectView, base_name='projects')

urlpatterns = [
    path('projects/<slug:slug>/users', ProjectAuthorization.as_view(), name='project-authorization'),
    path('projects/<slug:slug>/export', ExportFeatureList.as_view(), name='project-export'),
]


urlpatterns += router.urls
