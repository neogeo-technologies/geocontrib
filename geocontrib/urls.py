from django.urls import path
from django.conf.urls.static import static
from django.conf import settings

from geocontrib.views import FeatureTypeDetail
from geocontrib.views import view404
from geocontrib.views import protected_serve

app_name = 'geocontrib'

urlpatterns = [
    # Get the media files path to register routes towards it and control if the requested files can be viewed by current user
    path('media/<path:path>', protected_serve, {'document_root': settings.MEDIA_ROOT}),

    path('projet/<slug:slug>/', view404, name='project'),

    # Vues de gestion et d'édition des données métiers
    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/',
         FeatureTypeDetail.as_view(), name='feature_type_detail'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/',
        view404,
        name='feature_detail'),
    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/editer/',
        view404,
        name='feature_update'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
