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
    get_driver().find_element_by_id("id_title").send_keys(projectname, projectedition)
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

    # while there is a feature in the featuretype
    # delete it so the featuretype becomes editable
    # for feature_to_delete in get_driver().find_elements_by_xpath("//html/body/main/div/div/div[2]/div/a"):
    i = 0
    for feature_to_delete in get_driver().find_elements_by_css_selector(".small > a:nth-child(2)"):
        # feature_to_delete.click()
        # get_driver().find_element_by_xpath("//html/body/main/div/div[1]/div/h1/div/div[1]/a[3]/i").click()
        # get_driver().find_element_by_xpath("//html/body/div/div/div[2]/form/button").click()
        # get_driver().find_element_by_link_text(featuretypename).click()
        i += 1
        get_driver().refresh()

    # get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]").click()
    # get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]/div/a[1]").click()
    # get_driver().find_element_by_xpath("//html/body/main/div/div[2]/div[1]/div/div/div/a[4]").click()
    # get_driver().find_element_by_id("id_title").click()
    # get_driver().find_element_by_id("id_title").clear()
    # get_driver().find_element_by_id("id_title").send_keys("{}{}".format(featuretypename, featuretypeedition))

    # TODO: colors feature won't react the same way on MacOS/Linux/Win
    # get_driver().find_element_by_id("id_color").click()
    # time.sleep(2)
    # get_driver().find_element_by_id("id_color").send_keys("Blue")
    # get_driver().find_element_by_id("id_color").send_keys(Keys.RETURN)  
 
    # get_driver().find_element_by_xpath("//html/body/main/div/div/form/button[2]").click()


def geo_edit_feature(featurename, featureedition):
    get_driver().find_element_by_link_text(featurename).click()
    get_driver().find_element_by_xpath("//h1/div/div/a[2]/i").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys(featurename, featureedition)
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys(featureedition)
    get_driver().find_element_by_xpath("//button[@type='submit']").click()
