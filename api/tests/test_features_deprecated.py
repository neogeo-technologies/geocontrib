from django.core.management import call_command
from django.conf import settings
from django.urls import reverse
import pytest

from geocontrib.models.user import User
from conftest import verify_or_create_json
from conftest import verify_or_create
from conftest import sort_features_by_title

from geocontrib.models import StackedEvent

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
@pytest.mark.parametrize('with_multiple_stackedevents', [False, True])
def test_feature_creation(api_client, with_multiple_stackedevents):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Bug 14455 Several stacked events exists when creating feature
    if with_multiple_stackedevents:
        StackedEvent.objects.create(
            sending_frequency=settings.DEFAULT_SENDING_FREQUENCY,
            state='pending',
            project_slug="1-aze")
        StackedEvent.objects.create(
            sending_frequency=settings.DEFAULT_SENDING_FREQUENCY,
            state='pending',
            project_slug="1-aze")

    features_url = reverse('api:features-list')
    # Ensure anonymous no parameters Fails
    result = api_client.post(features_url)
    assert result.status_code == 403
    assert result.json() == {'detail': "Informations d'authentification non fournies."}

    # Ensure anonymous with project => fails
    result = api_client.post(f'{ features_url }?project__slug=1-aze&ordering=created_on')
    assert result.status_code == 403
    assert result.json() == {'detail': "Informations d'authentification non fournies."}

    # Ensure anonymous feature type => fails
    result = api_client.post(f'{ features_url }?feature_type__slug=1-dfsdfs')
    assert result.status_code == 403
    assert result.json() == {'detail': "Informations d'authentification non fournies."}


    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Ensure admin with data => Fails
    result = api_client.post(features_url)
    assert result.status_code == 400
    assert result.json() == {
        'feature_type': ['Ce champ est obligatoire.'],
        'geom': ['Ce champ est obligatoire.'],
        'project': ['Ce champ est obligatoire.'],
    }

    data = {
        'type': "Feature",
        'geometry': "{\"type\":\"LineString\",\"coordinates\":[[1.173194580078125,43.654672565596],[1.1031567382812502,43.54726848158805],[1.11963623046875,43.444658199457194],[1.0083996582031252,43.439672680464525]]}",
        "properties": {
            'project': "1-aze",
            'feature_type': '1-dfsdfs',
            "description": "description de mon signalement",
            'status': "draft",
            'title': 'titre de mon signalement',
        }
    }

    def ignore_feature_id (expected, result):
        result.pop('id')
        expected.pop('id')

    # Ensure admin project data => OK
    result = api_client.post(features_url, data, format='json')
    assert result.status_code == 201
    verify_or_create_json("api/tests/data/deprecated/test_features_creation_admin.json",
                          result.json(),
                          hook=ignore_feature_id
                         )

def sort_simple_features_by_title(data):
    """
    sort geojson by title
    """
    data["features"] = sorted(data.get("features", {}),  key=lambda d: d.get('title'))

def sort_simple_features_geojson_by_title(data):
    """
    sort geojson by title
    """
    features = data.get("features", {})
    data["features"] = sorted(features,  key=lambda d: d.get('properties')['title'])

# DEPRECATED ENDPOINT API

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projectfeature(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # ************************* #
    format = 'list'
    # Test : get features of a project
    project_slug = "1-aze"
    features_url = reverse('api:project-feature', args=[project_slug])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200

    verify_or_create_json("api/tests/data/deprecated/test_projectfeature_anon.json",
                          result.json(),
                          sorter=sort_simple_features_by_title
                         )

    # ************************* #
    format = 'geojson'
    features_url = reverse('api:project-feature', args=[project_slug])
    url = features_url  + '?output=' + format
    result = api_client.get(url)
    assert result.status_code == 200

    verify_or_create_json(
        "api/tests/data/deprecated/test_projectfeature_anon_geojson.json",
        result.json(),
        sorter=sort_simple_features_geojson_by_title
    )

def sort_paginated_features_by_title(data):
    """
    sort geojson by title
    """
    data["results"] = sorted(data.get("results", {}),  key=lambda d: d.get('title'))



@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projectfeaturepaginated(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    # Test : get features of a project
    features_url = reverse('api:project-feature-paginated', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/deprecated/test_projectfeaturepaginated_anon.json",
                          result.json(),
                          sorter=sort_paginated_features_by_title,
                         )

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    # Test : get features of a project authenticated
    features_url = reverse('api:project-feature-paginated', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/deprecated/test_projectfeaturepaginated_authenticated.json",
                          result.json(),
                          sorter=sort_paginated_features_by_title,
                         )
