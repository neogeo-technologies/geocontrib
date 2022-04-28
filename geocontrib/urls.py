from django.urls import path
from django.conf.urls.static import static
from django.conf import settings
from django.contrib.auth import views as auth_views

from geocontrib.views import HomePageView
from geocontrib.views import MyAccount
from geocontrib.views import FeatureDetail
from geocontrib.views import FeatureTypeDetail
from geocontrib.views import view404

from geocontrib.views import NotFoundView
from geocontrib.views import ProjectDetail

# from django.conf.urls import handler404

# from django.conf.urls.defaults import handler404
from geocontrib.views import view404
from geocontrib.views import custom_page_not_found_view
from geocontrib.views import custom_error_view
from geocontrib.views import custom_permission_denied_view
from geocontrib.views import custom_bad_request_view

app_name = 'geocontrib'
# handler404 = NotFoundView.get_rendered_view()
# handler404 = view404.error_handler
handler302 = custom_page_not_found_view
handler404 = custom_page_not_found_view
handler500 = custom_error_view
handler403 = custom_permission_denied_view
handler400 = custom_bad_request_view


urlpatterns = [

    # Vues générales de navigation
    path('', HomePageView.as_view(), name='index'),
    path('connexion/', auth_views.LoginView.as_view(
        template_name='geocontrib/registration/login.html'), name='login'),
    path('deconnexion/', auth_views.LogoutView.as_view(
        template_name='geocontrib/registration/login.html'), name='logout'),
    path('mon-compte/', MyAccount.as_view(), name='my_account'),


    # path('project/<slug:slug>', NotFoundView.as_view(), name='project'),
    path('projet/<slug:slug>/', ProjectDetail.as_view(), name='project'),

    # Vues de gestion et d'édition des données métiers
    path('projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/',
         FeatureTypeDetail.as_view(), name='feature_type_detail'),

    path(
        'projet/<slug:slug>/type-signalement/<slug:feature_type_slug>/signalement/<uuid:feature_id>/',
        FeatureDetail.as_view(),
        name='feature_detail'),
]

if settings.DEBUG:
    urlpatterns = urlpatterns + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
    urlpatterns = urlpatterns + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
