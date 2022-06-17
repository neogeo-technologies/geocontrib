from django.core.management import call_command
from django.urls import reverse
import pytest

from geocontrib.models.project import Project
from geocontrib.models.user import UserLevelPermission
from geocontrib.models.user import User
from conftest import verify_or_create_json
from conftest import verify_or_create
from conftest import sort_features_by_title

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

@pytest.mark.django_db
@pytest.mark.freeze_time('2021-08-05')
def test_projectfeature(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)
    # Test : get features of a project
    features_url = reverse('api:project-feature', args=["1-aze"])
    result = api_client.get(f'{ features_url }')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_projectfeature_anon.json",
                          result.json(),
                          sorter=sort_simple_features_by_title
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

    # Test : export a feature type in geojson
    features_url = reverse('api:project-export', args=["1-aze", "2-type-2"])
    result = api_client.get(f'{ features_url }?format_export=geojson')
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_project_export.geojson", result.json())

    # Test : export a feature type in CSV
    result = api_client.get(f'{ features_url }?format_export=csv')
    assert result.status_code == 200
    verify_or_create("api/tests/data/test_project_export.csv", result.content)

    # Test : export a feature type in MVT
    # TODO Test avec feature type Slug (fails)
    # TODO Test avec project__slug (fails)
    # Penser à utiliser l'image docker postgis/postgis (mdillon/postgis génère une autre tuile)
    features_url = reverse('api:features-mvt')
    result = api_client.get(f'{ features_url }?project_id=1&tile=4%2F7%2F5&limit=10&offset=0')
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
def test_feature_types_list(api_client):
    call_command("loaddata", "geocontrib/data/perm.json", verbosity=0)
    call_command("loaddata", "api/tests/data/test_features.json", verbosity=0)

    features_url = reverse('api:feature-types-list')
    # Ensure available even when not logged in
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_types_anon.json", result.json())


    user = User.objects.get(username="admin")
    api_client.force_authenticate(user=user)

    data = {
        'title': "New feature type",
        'title_optional': False,
        'geom_type': "point",
        'color': "#000000",
        'opacity': "0.5",
        'project': '1-aze',
        'customfield_set': None
    }

    # Test Can create feature type
    result = api_client.post(features_url, data, format="json")
    assert result.status_code == 201
    verify_or_create_json("api/tests/data/test_features_types_create.json", result.json())

    # To be able to edit the previous feature type
    #data["slug"] = "3-new-feature-type"
    data['title'] = "New feature type edited"

    # Test Can edit feature type
    features_url = reverse('api:feature-types-detail', args=['3-new-feature-type'])
    result = api_client.put(features_url, data, format="json")
    assert result.status_code == 200
    # TODO ne marche pas, PUT retourne le vielle objet, pas le nouveau... mais il est bien inscrit en base
    #verify_or_create_json("api/tests/data/test_features_types_edit.json", result.json())

    features_url = reverse('api:feature-types-detail', args=['3-new-feature-type'])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_types_edit.json", result.json())

    # TODO ajouter test sur les customfields (ou les ajouter dans ces test
