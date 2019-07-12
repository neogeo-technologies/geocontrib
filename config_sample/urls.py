from django.contrib import admin
from django.urls import path
from django.urls import include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('api.urls')),
    path('', include('collab.urls')),
]

handler404 = 'collab.views.error.custom_404'

handler403 = 'collab.views.error.custom_403'
