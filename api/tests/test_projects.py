from django.core.management import call_command
import pytest

from geocontrib.models.project import Project
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User


@pytest.mark.django_db
def test_projects_list(api_client):
    result = api_client.get('/api/projects/')
    assert result.status_code == 200
    assert result.json() == []

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    user = User.objects.create(username="usertest")

    anon_perm = UserLevelPermission.objects.get(pk="anonymous")

    p = Project.objects.create(
        title="Projet 1",
        access_level_pub_feature=anon_perm,
        access_level_arch_feature=anon_perm,
        creator=user,
    )
    p.save()

    result = api_client.get('/api/projects/')
    assert result.status_code == 200
    assert result.json() == [{
        'access_level_arch_feature': 'Utilisateur anonyme',
        'access_level_pub_feature': 'Utilisateur anonyme',
        'archive_feature': None,
        'created_on': '05/08/2021',
        'creator': 1,
        'delete_feature': None,
        'description': None,
        'is_project_type': False,
        'moderation': False,
        'nb_comments': 0,
        'nb_contributors': 1,
        'nb_features': 0,
        'nb_published_features': 0,
        'nb_published_features_comments': 0,
        'slug': '1-projet-1',
        'thumbnail': 'http://testserver/media/default.png',
        'title': 'Projet 1',
        'updated_on': '05/08/2021'}] 


@pytest.mark.django_db
def test_projects_post(api_client):

    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)

    User.objects.create(username="usertest")

    project_json = dict(
        title="Projet 2",
        access_level_pub_feature="anonymous",
        access_level_arch_feature="anonymous",
        #creator="usertest",
    )

    print(project_json)
    

    result = api_client.post('/api/projects2/', json=project_json)
    assert result.status_code == 200, result.content.decode()
    assert result.json() == [{
        'access_level_arch_feature': 'Utilisateur anonyme',
        'access_level_pub_feature': 'Utilisateur anonyme',
        'archive_feature': None,
        'created_on': '05/08/2021',
        'creator': 1,
        'delete_feature': None,
        'description': None,
        'is_project_type': False,
        'moderation': False,
        'nb_comments': 0,
        'nb_contributors': 1,
        'nb_features': 0,
        'nb_published_features': 0,
        'nb_published_features_comments': 0,
        'slug': '1-projet-1',
        'thumbnail': 'http://testserver/media/default.png',
        'title': 'Projet 1',
        'updated_on': '05/08/2021'}] 
