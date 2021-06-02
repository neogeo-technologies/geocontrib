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

import time

from utils import get_driver


def geo_edit_project(projectname, projectedition):
    get_driver().get("https://geocontrib.dev.neogeo.fr/")
    get_driver().find_element_by_link_text(projectname).click()
    get_driver().find_element_by_xpath("//h1/div/div/a[2]/i").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys("{}{}".format(projectname, projectedition))
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys(projectedition)
    get_driver().find_element_by_xpath("//form[@id='form-project-edit']/div[5]/div[3]/div").click()
    get_driver().find_element_by_xpath("//form[@id='form-project-edit']/div[5]/div[4]/div").click()
    get_driver().find_element_by_xpath("//form[@id='form-project-edit']/div[5]/div[4]/div/div[2]/div[5]").click()
    get_driver().find_element_by_id("id_moderation").click()
    get_driver().find_element_by_xpath("//button[@type='submit']").click()


def geo_edit_featuretype(featuretypename, featuretypeedition):
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]").click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]/div/a[1]").click()
    get_driver().find_element_by_link_text(featuretypename).click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]").click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]/div/a[1]").click()
    get_driver().find_element_by_xpath("//html/body/main/div/div[2]/div[1]/div/div/div/a[4]").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys("{}{}".format(featuretypename, featuretypeedition))
    get_driver().find_element_by_xpath("//html/body/main/div/div/form/button[2]").click()


def geo_edit_feature(featurename, featureedition):
    get_driver().find_element_by_link_text(featurename).click()
    get_driver().find_element_by_xpath("//h1/div/div/a[2]/i").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys("{}{}".format(featurename, featureedition))
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys(featureedition)
    get_driver().find_element_by_xpath("//button[@type='submit']").click()
