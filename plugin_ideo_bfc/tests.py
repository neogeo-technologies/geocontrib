# Copyright (c) 2019 Neogeo-Technologies.
# All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License"); you may
# not use this file except in compliance with the License. You may obtain
# a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS, WITHOUT
# WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied. See the
# License for the specific language governing permissions and limitations
# under the License.


import logging
from pprint import pformat
from django.contrib.auth import get_user_model
from django.test import tag
from django.urls import reverse
from rest_framework.test import APITransactionTestCase

User = get_user_model()

logger = logging.getLogger(__name__)


class RootTestCase(APITransactionTestCase):
    create_xml_path = ''
    put_create_xml_path = ''
    update_xml_path = ''
    create_url_path = ''
    update_url_path = ''
    username = ''
    sid_id_pust = ''
    queryset = None

    def test_create(self):
        with open(self.create_xml_path) as fp:
            resp = self.client.post(
                reverse(self.create_url_path),
                data=fp.read(),
                content_type='application/xml',
            )

            self.assertEqual(resp.status_code, 201)
            self.assertEqual(self.queryset.filter(username=self.username).count(), 1)

    def test_create_update(self):

        with open(self.create_xml_path) as fp:
            data = {'file': fp}

            resp = self.client.post(
                reverse(self.create_url_path),
                data=data,
            )

            self.assertEqual(resp.status_code, 201)
            self.assertEqual(self.queryset.all().count(), 1)

        logger.info(
            pformat(self.queryset.get(username=self.username).__dict__)
        )

        with open(self.update_xml_path) as fp2:
            data = {'file': fp2}

            resp = self.client.put(
                reverse(self.update_url_path, kwargs={'username': self.username}),
                data=fp2.read(),
                content_type='application/xml',
            )

            logger.info(
                pformat(self.queryset.get(username=self.username).__dict__)
            )

            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.queryset.all().count(), 1)

    def test_pust(self):
        """
        On test la création d'orga & company & employee & agent à travers un PUT
        """

        with open(self.put_create_xml_path) as fp2:

            resp = self.client.put(
                reverse(
                    self.update_url_path,
                    kwargs={'username': self.username_pust}
                ),
                data=fp2.read(),  # {'file': fp2}
                content_type='application/xml',
            )
            logger.info(
                pformat(self.queryset.get(username=self.username_pust).__dict__)
            )
            self.assertEqual(resp.status_code, 200)
            self.assertEqual(self.queryset.all().count(), 1)


@tag('selected')
class TestAgent(RootTestCase):

    create_xml_path = 'plugin_ideo_bfc/data/test/agent.xml'
    update_xml_path = 'plugin_ideo_bfc/data/test/agent_update1.xml'
    put_create_xml_path = 'plugin_ideo_bfc/data/test/agent_pust.xml'
    create_url_path = 'plugin_ideo_bfc:agent-list'
    update_url_path = 'plugin_ideo_bfc:agent-detail'
    username = '307164'
    username_pust = '123456789'
    queryset = User.objects.all()


@tag('selected')
class TestEmployee(RootTestCase):

    create_xml_path = 'plugin_ideo_bfc/data/test/employee.xml'
    put_create_xml_path = 'plugin_ideo_bfc/data/test/employee_pust.xml'
    update_xml_path = 'plugin_ideo_bfc/data/test/employee_update1.xml'
    create_url_path = 'plugin_ideo_bfc:employee-list'
    update_url_path = 'plugin_ideo_bfc:employee-detail'
    username = '307163'
    username_pust = '123456789'
    queryset = User.objects.all()
