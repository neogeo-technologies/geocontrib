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


import selenium
from selenium.webdriver.support.ui import Select

from utils import get_driver


# TODO: condition if : si ça existe, ne pas le recréer
def geo_create_layer(admin_url, layer_title, layer_url, layer_description):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Couches").click()
    # si le texte layer_title n'existe pas
        # get_driver().find_element_by_xpath("//html/body/div/div[3]/div/ul/li/a").click()
        # get_driver().find_element_by_id("id_title").click()
        # get_driver().find_element_by_id("id_title").clear()
        # get_driver().find_element_by_id("id_title").send_keys(layer_title)
        # get_driver().find_element_by_id("id_service").click()
        # get_driver().find_element_by_id("id_service").clear()
        # get_driver().find_element_by_id("id_service").send_keys(layer_url)
        # get_driver().find_element_by_id("id_options").click()
        # get_driver().find_element_by_id("id_options").clear()
        # get_driver().find_element_by_id("id_options").send_keys(layer_description)
        # get_driver().find_element_by_name("_save").click()

# TODO: au lieu de layer1, layer2, faire une liste avec une boucle for
# TODO: remplacer (wms) et (tms) par des variables
def geo_create_basemap(admin_url, basemapname, projectname, layer1_title, layer1_url, layer2_title, layer2_url):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Fonds cartographiques").click()
    get_driver().find_element_by_xpath("//html/body/div/div[3]/div/ul/li/a").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(basemapname)
    get_driver().find_element_by_id("id_project").click()
    Select(get_driver().find_element_by_id("id_project")).select_by_visible_text(projectname)
    get_driver().find_element_by_link_text(u"Ajouter un objet Liaison Fond-Couche supplémentaire").click()
    get_driver().find_element_by_id("id_contextlayer_set-0-layer").click()
    Select(get_driver().find_element_by_id("id_contextlayer_set-0-layer")).select_by_visible_text("{} - {} (wms)".format(layer1_title, layer1_url))
    get_driver().find_element_by_id("id_contextlayer_set-0-queryable").click()
    get_driver().find_element_by_link_text(u"Ajouter un objet Liaison Fond-Couche supplémentaire").click()
    get_driver().find_element_by_id("id_contextlayer_set-1-layer").click()
    Select(get_driver().find_element_by_id("id_contextlayer_set-1-layer")).select_by_visible_text("{} - {} (tms)".format(layer2_title, layer2_url))
    get_driver().find_element_by_id("id_contextlayer_set-1-queryable").click()
    get_driver().find_element_by_name("_save").click()    

def geo_query_basemap():
    pass
