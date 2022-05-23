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


def geocontrib_edit_project(project_name, project_edition):
    get_driver().find_element_by_class_name("button-hover-orange").click()
    # modify title
    get_driver().find_element_by_id("title").click()
    get_driver().find_element_by_id("title").clear()
    get_driver().find_element_by_id("title").send_keys("{}{}".format(project_name, project_edition))

    # modify description
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys(project_edition)

    # click on dropdown "Visibilité des signalements publiés" to open it
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div"
    ).click()
    # click on dropdown "Visibilité des signalements publiés" to select an option
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div/div[2]/div[2]"
    ).click()

    # click on dropdown "Visibilité des signalements archivés" to open it
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div"
    ).click()
    # click on dropdown "Visibilité des signalements archivés" to select an option
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div/div[2]/div[2]"
    ).click()

    # toggle moderation
    get_driver().find_element_by_css_selector("label[for=moderation]").click()
    # toggle is_project_type
    get_driver().find_element_by_css_selector("label[for=is_project_type]").click()
    # toggle generate_share_link
    get_driver().find_element_by_css_selector("label[for=generate_share_link]").click()

    # submit the form
    get_driver().find_element_by_id("send-project").click()


def geocontrib_edit_featuretype(featuretypename, added_text):
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]").click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]/div/a[1]").click()
    get_driver().find_element_by_link_text(featuretypename).click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]").click()
    get_driver().find_element_by_xpath("//html/body/header/div/div/div[1]/div/a[1]").click()
    get_driver().find_element_by_xpath("//html/body/main/div/div[2]/div[1]/div/div/div/a[4]").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys("{}{}".format(featuretypename, added_text))
    get_driver().find_element_by_xpath("//html/body/main/div/div/form/button[2]").click()


def geocontrib_edit_feature(feature_name, added_text):
    get_driver().find_element_by_link_text(feature_name).click()
    get_driver().find_element_by_xpath("//h1/div/div/a[2]/i").click()
    get_driver().find_element_by_id("id_title").click()
    get_driver().find_element_by_id("id_title").clear()
    get_driver().find_element_by_id("id_title").send_keys("{}{}".format(feature_name, added_text))
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys(added_text)
    get_driver().find_element_by_xpath("//button[@type='submit']").click()
