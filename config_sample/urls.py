from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls', namespace='api')),
    path('', include('geocontrib.urls', namespace='geocontrib')),
]

handler404 = 'geocontrib.views.error.custom_404'

handler403 = 'geocontrib.views.error.custom_403'
