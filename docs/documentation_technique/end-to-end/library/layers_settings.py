# Copyright (c) 2017-2021 Neogeo-Technologies.
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

import datetime


def get_variables():
    variables = {
                "LAYER1_TITLE":      "PIGMA Occupation du sol",
                "LAYER1_URL":        "https://www.pigma.org/geoserver/asp/wms?",
                "LAYER1_TYPE":       "WMS",
                "LAYER1_OPTIONS":    "{\n\"format\": \"image/png\",\n\"layers\": \"asp_rpg_2012_047\",\n\"maxZoom\": 18,\n\"minZoom\": 7,\n\"opacity\": 0.8,\n\"attribution\": \"PIGMA\",\n\"transparent\": true\n}",

                "LAYER2_TITLE":      "OpenStreetMap France",
                "LAYER2_URL":        "https://{s}.tile.openstreetmap.fr/osmfr/{z}/{x}/{y}.png",
                "LAYER2_TYPE":       "TMS",
                "LAYER2_OPTIONS":    "{\n\"maxZoom\": 20,\n\"attribution\": \"\u00a9 les contributeurs d\u2019OpenStreetMap\"\n}",

                "BASEMAPNAME":       "fond carto - {}".format(datetime.datetime.now()),
                }
    return variables
