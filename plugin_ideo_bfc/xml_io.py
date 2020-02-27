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

from django.template.loader import render_to_string
from rest_framework.parsers import BaseParser
from rest_framework.renderers import BaseRenderer
import xmltodict


logger = logging.getLogger(__name__)


class XMLRenderer(BaseRenderer):
    """
    Les retours xml se font pour contextualiser les erreurs de l'api SID
    Cf. fichiers exemple et schema: `error.xml` et `error.xsd`

    <?xml version="1.0" encoding="UTF-8" standalone="yes"?>
    <error xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:noNamespaceSchemaLocation="error.xsd">
      <classType>ORGANISM</classType>
      <errorCode>004</errorCode>
      <errorLabel>Not Found</errorLabel>
      <errorMessage>Organism u6i not found</errorMessage>
      <methodType>PUT</methodType>
      <resourceId>5</resourceId>
    </error>

    """
    def __init__(self):
        self.media_type = 'application/xml'
        self.format = 'xml'
        self.charset = 'UTF-8'

    def render(self, data, accepted_media_type=None, renderer_context=None):
        return render_to_string('ideo_bfc_sid/default_renderer.xml', {'data': data})


class XMLtParser(BaseParser):

    def __init__(self):
        self.media_type = 'application/xml'
        self.charset = 'UTF-8'

    def parse(self, stream, media_type=None, parser_context=None):

        assert xmltodict, 'XMLParser need xmltodict to be installed'

        # parser_context = parser_context or {}
        # encoding = parser_context.get('encoding', self.charset)
        # parser = etree.DefusedXMLParser(encoding=encoding)
        try:
            tree = xmltodict.parse(stream)
        except Exception:
            logger.exception('xmlparser')
        return tree
