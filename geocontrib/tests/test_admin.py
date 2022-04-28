from django.core.management import call_command
from django.contrib.admin.sites import AdminSite
import pytest

from geocontrib.admin.feature import FeatureAdmin
from geocontrib.admin.project import ProjectAdmin
from geocontrib.models import Feature
from geocontrib.models import Project
from geocontrib.models import User

@pytest.mark.django_db
def test_admin_project_viewsite(api_client):
    """
    Test les boutons admin "view in site" sur les projets
    """
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    admin = User.objects.first()
    my_proj_admin = ProjectAdmin(Project, AdminSite())
    my_proj = Project.objects.first()

    url = my_proj_admin.get_view_on_site_url(my_proj)

    api_client.force_login(user=admin)
    res = api_client.get(url)
    assert res.url == 'http://example.com/projet/1-aze/'


@pytest.mark.django_db
def test_admin_feature_viewsite(api_client):
    """
    Test les boutons admin "view in site" sur les signalements
    """
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    admin = User.objects.first()
    my_feat_admin = FeatureAdmin(Feature, AdminSite())
    my_feat = Feature.objects.first()

    url = my_feat_admin.get_view_on_site_url(my_feat)

    api_client.force_login(user=admin)
    res = api_client.get(url)
    assert res.url == 'http://example.com/projet/1-aze/type-signalement/1-dfsdfs/signalement/71f9778a-fe84-4c2e-ab9b-4dba95d2aeee/editer/'
