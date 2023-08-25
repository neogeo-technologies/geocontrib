from django.contrib import admin
from django.urls import path
from django.urls import include
from django.conf import settings
from django.conf.urls.static import static
cas_server = None
if hasattr(settings, "CAS_SERVER_URL"):
    import django_cas_ng.views
    cas_server = settings.CAS_SERVER_URL


url_prefix = settings.URL_PREFIX

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('', include('geocontrib.urls', namespace='geocontrib')),
]

if cas_server:
    urlpatterns = urlpatterns + [
        path('cas/login', django_cas_ng.views.LoginView.as_view(), name='cas_ng_login'),
        path('cas/logout', django_cas_ng.views.LogoutView.as_view(), name='cas_ng_logout'),
    ]

# add prefix to URL
urlpatterns = [path(url_prefix, include(urlpatterns))]

# static and media paths
if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# if user connection managed externally, hide button to disconnect user from django admin
if settings.LOGOUT_HIDDEN:
    admin.site.index_template = 'admin/geocontrib/base.html'
    admin.autodiscover()