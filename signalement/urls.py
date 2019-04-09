from django.conf.urls import url
from . import views

urlpatterns = [
    url(r'^ajout_signalement/', views.ajout_signalement)
]
