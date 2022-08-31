from django.core.management import call_command
from django.urls import reverse
import pytest

from conftest import verify_or_create_json

from geocontrib.models.user import User


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
    customfield =[
        {
            "field_type": "list",
            "label": "SA",
            "name": "ZA",
            "options": [
                "12",
                "125"
            ],
            "position": 0,
            'is_mandatory': True,
        },
        {
            "field_type": "list",
            "label": "SA1",
            "name": "ZA2",
            "options": [
                "13",
                "123"
            ],
            "position": 0,
            "is_mandatory": False
        }
    ]

    data = {
        'title': "New feature type",
        'title_optional': False,
        'geom_type': "point",
        'color': "#000000",
        'opacity': "0.5",
        'project': '1-aze',
        'customfield_set': customfield
    }

    # Test Can create feature type
    result = api_client.post(features_url, data, format="json")
    assert result.status_code == 201
    verify_or_create_json("api/tests/data/test_features_types_create.json", result.json())
    # To be able to edit the previous feature type
    #data["slug"] = "4-new-feature-type"
    data['title'] = "New feature type edited"

    # Test Can edit feature type
    features_url = reverse('api:feature-types-detail', args=['4-new-feature-type'])
    result = api_client.put(features_url, data, format="json")
    assert result.status_code == 200
    # TODO ne marche pas, PUT retourne le vielle objet, pas le nouveau... mais il est bien inscrit en base
    #verify_or_create_json("api/tests/data/test_features_types_edit.json", result.json())

    features_url = reverse('api:feature-types-detail', args=['4-new-feature-type'])
    result = api_client.get(features_url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_features_types_edit.json", result.json())

    # TODO ajouter test sur les customfields (ou les ajouter dans ces test