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


from selenium.webdriver.support.ui import Select

from utils import get_driver


# TODO: condition if : si ça existe, ne pas le recréer
def geo_create_layer(admin_url, layer_title, layer_url, layer_description):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Couches").click()


# TODO: au lieu de layer1, layer2, faire une liste avec une boucle for
# TODO: remplacer (wms) et (tms) par des variables
def geo_create_basemap(admin_url, basemapname, projectname, layers):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Fonds cartographiques").click()
    get_driver().find_element_by_xpath("//html/body/div/div[3]/div/ul/li/a").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(basemapname)
    get_driver().find_element_by_id("id_project").click()
    Select(get_driver().find_element_by_id("id_project")).select_by_visible_text(projectname)

    for i, layer in enumerate(layers):
        get_driver().find_element_by_link_text(u"Ajouter un objet Liaison Fond-Couche supplémentaire").click()
        get_driver().find_element_by_id("id_contextlayer_set-{}-layer".format(i)).click()
        Select(get_driver().find_element_by_id("id_contextlayer_set-{}-layer".format(i)).select_by_visible_text("{} - {} ({})".format(layer.title, layer.url, layer.type))
        get_driver().find_element_by_id("id_contextlayer_set-{}-queryable".format(i)).click()

    get_driver().find_element_by_link_text(u"Ajouter un objet Liaison Fond-Couche supplémentaire").click()
    get_driver().find_element_by_id("id_contextlayer_set-1-layer").click()
    Select(get_driver().find_element_by_id("id_contextlayer_set-1-layer")).select_by_visible_text("{} - {} (tms)".format(layer2_title, layer2_url))
    get_driver().find_element_by_id("id_contextlayer_set-1-queryable").click()

    get_driver().find_element_by_name("_save").click()


def geo_query_basemap(url, projectname):
    get_driver().get(url)
    get_driver().find_element_by_link_text(projectname).click()
    get_driver().find_element_by_css_selector("#map").click()
    get_driver().find_element_by_id("Capa_1").click()

