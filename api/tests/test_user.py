from pathlib import Path
import json
import pytest
import unittest
from unittest.mock import patch
from unittest.mock import Mock
import uuid

from django.core.management import call_command
from django.urls import reverse
from rest_framework.test import APIClient

from geocontrib.models.user import User


def verify_or_create_json(filename, json_result):

    path = Path(filename)
    if path.exists():
        with path.open() as fp:
            json_expected = json.load(fp)
            assert json_result == json_expected
    else:
        with path.open("w") as fp:
            json.dump(json_result, fp)


@pytest.mark.django_db(reset_sequences=True)
@pytest.mark.freeze_time('2021-08-05')
def test_user(api_client):

    # Ensure not connected 
    url = reverse('api:user-info')

    result = api_client.get(url)
    assert result.status_code == 403
    verify_or_create_json("api/tests/data/test_user_info_anonymous.json", result.json())

    # Ensure usual user
    user = User.objects.create(username="usertest")
    api_client.force_authenticate(user=user)

    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_user.json", result.json())

    # Ensure admin
    user = User.objects.create(username="admin", is_administrator=True)
    api_client.force_authenticate(user=user)

    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_admin.json", result.json())

    # Ensure admin
    user = User.objects.create(username="superuser", is_superuser=True)
    api_client.force_authenticate(user=user)

    result = api_client.get(url)
    assert result.status_code == 200
    verify_or_create_json("api/tests/data/test_user_info_superuser.json", result.json())


class TestToken(unittest.TestCase):
    token_mock = Mock(return_value=uuid.UUID('77f1df52-4b43-11e9-910f-b8ca3a9b9f3e'))

    def setUp(self):
        self.admin_user = User.objects.create_superuser(
            username="admin_test",
            email="admin@email.com",
            first_name="Test",
            last_name="ADMINISTRATOR",
            is_active=True,
            is_staff=True,
            is_superuser=True,
        )
        self.client = APIClient(enforce_csrf_checks=True)


    @pytest.mark.django_db(transaction=True)
    @patch(target='uuid.uuid4',  new=token_mock)
    def test_get_unique_identifier(self):
        # Ensure not connected 
        url = reverse('api:get-token')
        result = self.client.get(url)
        assert result.status_code == 403
        verify_or_create_json("api/tests/data/test_user_token_anonymous.json", result.json())

        # Ensure usual user
        user = User.objects.create(
            username="usertest",
            token=self.token_mock.return_value
        )
        # SET LOGIN WITH USER
        self.client.force_authenticate(user=user)
        result = self.client.get(url)
        assert result.status_code == 200
        verify_or_create_json("api/tests/data/test_user_token_user.json", result.json())
        token = result.json()
        
        # RESET SELF CLIENT
        self.client.force_authenticate(user=None)

        # SET LOGIN USER WITH TOKEN
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + token)
        result = self.client.get(url)
        assert result.status_code == 200
        verify_or_create_json("api/tests/data/test_user_token_user.json", result.json())
