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
def geocontrib_create_layer(admin_url, layer_title, layer_url, layer_type, layer_options):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Couches").click()
    get_driver().find_element_by_xpath("//html/body/div/div[3]/div/ul/li/a").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(layer_title)
    get_driver().find_element_by_id("id_service").clear()
    get_driver().find_element_by_id("id_service").send_keys(layer_url)
    get_driver().find_element_by_id("id_schema_type").click()
    get_driver().find_element_by_id("id_schema_type").click()
    Select(get_driver().find_element_by_id("id_schema_type")).select_by_visible_text(layer_type)
    get_driver().find_element_by_xpath("//form[@id='layer_form']/div/fieldset/div[4]/div").click()
    get_driver().find_element_by_id("id_options").clear()
    get_driver().find_element_by_id("id_options").send_keys(layer_options)
    get_driver().find_element_by_name("_save").click()


# TODO: au lieu de layer1, layer2, faire une liste avec une boucle for
def geocontrib_create_basemap(url, basemap_name, project_name, layer1_title, layer1_url, layer1_type, layer2_title, layer2_url, layer2_type):
    get_driver().get(url)
    get_driver().find_element_by_link_text(project_name).click()
    get_driver().find_element_by_xpath("//div/div/div").click()
    get_driver().find_element_by_link_text("Fonds cartographiques").click()
    get_driver().find_element_by_xpath("//form[@id='form-layers']/div/a/span").click()
    get_driver().find_element_by_id("id_basemap_set-0-title").click()
    get_driver().find_element_by_id("id_basemap_set-0-title").clear()
    get_driver().find_element_by_id("id_basemap_set-0-title").send_keys(basemap_name)
    get_driver().find_element_by_xpath("//form[@id='form-layers']/div[2]/div/div[2]/div[3]/a").click()
    get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-0-layer").click()
    get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-0-layer").click()
    Select(get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-0-layer")).select_by_visible_text("{} - {} ({})".format(layer1_title, layer1_url, layer1_type.lower()))
    get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-0-queryable").click()
    get_driver().find_element_by_xpath("//form[@id='form-layers']/div[2]/div/div[2]/div[3]/a/span").click()
    get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-1-layer").click()
    Select(get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-1-layer")).select_by_visible_text("{} - {} ({})".format(layer2_title, layer2_url, layer2_type.lower()))
    get_driver().find_element_by_id("id_contextlayer-basemap_set-0-contextlayer_set-1-queryable").click()
    get_driver().find_element_by_xpath("//button[@type='submit']").click()


def geocontrib_query_basemap(url, project_name):
    get_driver().get(url)
    get_driver().find_element_by_link_text(project_name).click()
    get_driver().find_element_by_css_selector("#map").click()
    get_driver().find_element_by_id("Capa_1").click()

