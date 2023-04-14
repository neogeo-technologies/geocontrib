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
    verify_or_create_json("api/tests/data/test_features_creation_admin.json",
                          result.json(),
                          hook=ignore_feature_id
                         )

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_feature_list(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    features_url = reverse('api:features-list')
    # Ensure no parameters Fails
    result = api_client.get(features_url)
    assert result.status_code == 400
    assert result.json() == ["Must provide parameter project__slug or feature_type__slug"]

    # Ensure anonymous project => only get published features of the 2 feature types
    result = api_client.get(f'{ features_url }?project__slug=1-aze&ordering=created_on')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_project_anon.json",
                          result.json(),
                          sorter=sort_features_by_title,
                         )

    # Ensure anonymous feature type => only get published features of the feature type
    result = api_client.get(f'{ features_url }?feature_type__slug=1-dfsdfs')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_featuretype_anon.json",
                          result.json(),
                          sorter=sort_features_by_title,
                         )


    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    # Ensure admin project => get all features
    result = api_client.get(f'{ features_url }?project__slug=1-aze&ordering=created_on')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_project_admin.json",
                          result.json(),
                          sorter=sort_features_by_title,
                         )

    # Ensure admin feature type => get all published features of the feature type
    result = api_client.get(f'{ features_url }?feature_type__slug=1-dfsdfs&ordering=created_on')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_featuretype_admin.json",
                          result.json(),
                          sorter=sort_features_by_title,
                         )

    # Ensure wrong project fails
    result = api_client.get(f'{ features_url }?project__slug=1-wrong')
    assert result.status_code == 404

    # Ensure wrong feature_type__slug fails
    result = api_client.get(f'{ features_url }?feature_type__slug=1-wrong')
    assert result.status_code == 404


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

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projectfeature(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # ************************* #
    format = 'list'
    project_slug = "1-aze"
    features_url = reverse('api:features-list')
    url = features_url + '?project__slug=' + project_slug + "&output=" + format
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json(
        "api/tests/data/test_projectfeature_anon.json",
        result.json(),
        sorter=sort_simple_features_by_title
    )

    # ************************* #
    format = 'geojson'
    features_url = reverse('api:features-list')
    url = features_url + '?project__slug=' + project_slug + "&output=" + format
    
    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json(
        "api/tests/data/test_projectfeature_anon_geojson.json",
        result.json(),
        sorter=sort_simple_features_geojson_by_title
    )

    # VIEW AFFECTED BY TICKET 14474
    features_url = reverse('api:features-list')
    url = features_url + '?project__slug=' + project_slug

    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json(
        "api/tests/data/test_projectfeature_anon_FeatureGeoJSONSerializer.json",
        result.json(),
        sorter=sort_simple_features_geojson_by_title
    )

def sort_paginated_features_by_title(data):
    """
    sort geojson by title
    """
    data["results"] = sorted(data.get("results", {}),  key=lambda d: d.get('title'))


@pytest.mark.skip(reason="is deprecated ?")
@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projectfeaturepaginated(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    # Test : get features of a project
    features_url = reverse('api:project-feature-paginated', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_projectfeaturepaginated_anon.json",
                          result.json(),
                          sorter=sort_paginated_features_by_title,
                         )

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    # Test : get features of a project authenticated
    features_url = reverse('api:project-feature-paginated', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_projectfeaturepaginated_authenticated.json",
                          result.json(),
                          sorter=sort_paginated_features_by_title,
                         )


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_project_feature_bbox(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    # Test : get bbox of a project
    features_url = reverse('api:project-feature-bbox', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_project_feature_bbox_anon.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_project_export(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    project_slug = "1-aze"

    # Test : export a feature type in geojson
    feature_type_export_url = reverse('api:project-export', args=["1-aze", "2-type-2"])
    result = api_client.get(f'{ feature_type_export_url }?format_export=geojson')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_project_export.geojson", result.json())

    # Test : export a feature type in CSV
    result = api_client.get(f'{ feature_type_export_url }?format_export=csv')
    assert result.status_code == 200
    verify_or_create("api/tests/data/test_project_export.csv", result.content)

    features_list_url = reverse('api:features-list')
    url = features_list_url + '?project__slug=' + project_slug
    result = api_client.get(url)
    feature = result.json()['features'][0]
    fts = feature['properties']['feature_type']
    feature_id = feature['id']
    features_detail_url = reverse('api:features-detail', args=[feature_id])

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    url = f'{ features_detail_url }?project__slug={project_slug}&feature_type__slug={fts}'
    result = api_client.delete(
        url,
        format="json"
    )
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_detail_delete.json", result.json())

    # Test : export a feature type in MVT
    # TODO Test avec feature type Slug (fails)
    # TODO Test avec project__slug (fails)
    # Penser à utiliser l'image docker postgis/postgis (mdillon/postgis génère une autre tuile)
    features_mvt_url = reverse('api:features-mvt')
    result = api_client.get(f'{ features_mvt_url }?project_id=1&tile=4%2F7%2F5&limit=10&offset=0')
    assert result.status_code == 200
    verify_or_create("api/tests/data/test_project_export.mvt", result.content)


def sort_search_features_by_title(data):
    """
    sort json by title
    """
    data["results"] = sorted(data.get("results", {}),  key=lambda d: d.get('title'))

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_feature_search(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    feature_id = "75540f8e-0f4d-4317-9818-cc1219a5df8c"
    features_url = reverse('api:feature-search', args=["1-aze"])

    # Test : search a feature by status
    result = api_client.get(f'{ features_url }?status=published')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_status.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)

    # Test : search a feature by id
    result = api_client.get(f'{ features_url }?feature_id={ feature_id }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_id.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)

    # Test : search a feature by excluding id
    result = api_client.get(f'{ features_url }?exclude_feature_id={ feature_id }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_exclude_id.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)

    # Test : search a feature by title
    result = api_client.get(f'{ features_url }?title=type+2')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_exclude_id.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)

    # Test : search a feature by feature type
    result = api_client.get(f'{ features_url }?feature_type_slug=type-2')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_feature_type.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)

    # Test : search a feature by bbox
    bbox = "1.0,46.14,3.3,47.8"
    result = api_client.get(f'{ features_url }?geom={ bbox }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_search_bbox.geojson",
                          result.json(),
                          sorter=sort_search_features_by_title)


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_feature_link(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    feature_id = "75540f8e-0f4d-4317-9818-cc1219a5df8c"
    features_url = reverse('api:feature-link', args=[feature_id])

    # Test : get a feature without linked feature
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_link_empty.json", result.json())

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    # Test : put a feature link
    feature_to = "71f9778a-fe84-4c2e-ab9b-4dba95d2aeee"
    data = {
        'relation_type': 'doublon',
        'feature_to' : {
            "feature_id": '71f9778a-fe84-4c2e-ab9b-4dba95d2aeee',
        }
    }
    result = api_client.put(features_url, [data], format="json")
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_link_put.json", result.json())

    # verifie que la laison dans l'autre sens aussi crée (doublon)
    features_url = reverse('api:feature-link', args=[feature_to])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_link_doublon.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_feature_event(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    feature_id = "75540f8e-0f4d-4317-9818-cc1219a5df8c"
    features_url = reverse('api:feature-events', args=[feature_id])

    # Test : get a feature without events
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_feature_events_empty.json", result.json())


@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_featurepositioninlist(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)
    # Test : get feature position of a project authenticated
    feature_position_url = reverse('api:project-feature-position-in-list', args=["1-aze", "75540f8e-0f4d-4317-9818-cc1219a5df8c"])
    # with default sort (first created)
    data = { 'ordering': 'created_on'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 1
    # with sort last created
    data = { 'ordering': '-created_on'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 3
    # with sort last modified
    data = { 'ordering': '-updated_on'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 4
    # with sort last created and first feature type
    data = { 'ordering': '-created_on', 'feature_type_slug': '1-dfsdfs'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 0
    # with sort last modified and first feature type
    data = { 'ordering': '-updated_on', 'feature_type_slug': '1-dfsdfs'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 1
    # with sort last created and third feature type that doesn't have feature
    data = { 'ordering': '-created_on', 'feature_type_slug': '3-type-multilinestring'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 404
    # with sort last modified, first feature type and status published
    data = { 'ordering': '-updated_on', 'feature_type_slug': '1-dfsdfs', 'status': 'published'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 0
    # with sort last created, second feature type and status published and another feature_id
    feature_position_url = reverse('api:project-feature-position-in-list', args=["1-aze", "7e29a761-6683-4baf-ae8b-9ce14557f053"])
    data = { 'ordering': '-created_on', 'status': 'published', 'title': 'type 2 publi\u00e9'}
    result = api_client.get(feature_position_url, data)
    assert result.status_code == 200
    assert result.data == 0
