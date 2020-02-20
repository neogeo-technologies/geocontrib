from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic.base import RedirectView

url_prefix = settings.URL_PREFIX

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('geocontrib.urls', namespace='geocontrib')),
]

# On ajoute les urls des différentes applis
for app in settings.OUR_APPS:
    urlpatterns.insert(
        1,
        path('{}/'.format(app), include('{}.urls'.format(app), namespace=app)),
    )

# add prefix to URL
urlpatterns = [path(url_prefix, include(urlpatterns))]

# static and media paths
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# error handlers
handler404 = 'geocontrib.views.error.custom_404'
handler403 = 'geocontrib.views.error.custom_403'
