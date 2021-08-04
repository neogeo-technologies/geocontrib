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


from utils import get_driver


def geocontrib_delete_project(project_name, admin_url):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Projets").click()
    get_driver().find_element_by_link_text(project_name).click()
    get_driver().find_element_by_link_text("Supprimer").click()
    get_driver().find_element_by_xpath(u"//input[@value='Oui, je suis sûr']").click()


def geocontrib_delete_featuretype(admin_url, feature_type_name):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Types de signalements").click()
    get_driver().find_element_by_link_text(feature_type_name).click()
    get_driver().find_element_by_link_text("Supprimer").click()
    get_driver().find_element_by_xpath(u"//input[@value='Oui, je suis sûr']").click()


def geocontrib_delete_feature(admin_url, feature_name):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Signalements").click()
    get_driver().find_element_by_link_text(feature_name).click()
    get_driver().find_element_by_link_text("Supprimer").click()
    get_driver().find_element_by_xpath(u"//input[@value='Oui, je suis sûr']").click()


def geocontrib_delete_layer(admin_url, layer_title, layer_url,  layer_type):
    get_driver().get(admin_url)
    get_driver().find_element_by_link_text("Couches").click()
    get_driver().find_element_by_link_text("{} - {} ({})".format(layer_title, layer_url,  layer_type.lower())).click()
    get_driver().find_element_by_link_text("Supprimer").click()
    get_driver().find_element_by_xpath(u"//input[@value='Oui, je suis sûr']").click()
