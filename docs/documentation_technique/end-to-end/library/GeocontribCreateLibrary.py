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


def geocontrib_create_project(project_name):
    get_driver().find_element_by_link_text(u"Créer un nouveau projet").click()
    # fill the project title
    title_input_elt = get_driver().find_element_by_id("title")
    title_input_elt.click()
    title_input_elt.clear()
    title_input_elt.send_keys(project_name)

    # add description
    get_driver().find_element_by_name("description").click()
    get_driver().find_element_by_name("description").clear()
    get_driver().find_element_by_name("description").send_keys("Exemple de description")
    
    # click on dropdown "Visibilité des signalements publiés" to open it
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div"
    ).click()
    # click on dropdown "Visibilité des signalements publiés" to select an option
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div/div[2]/div"
    ).click()
    # click on dropdown "Visibilité des signalements archivés" to open it
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div"
    ).click()
    # click on dropdown "Visibilité des signalements archivés" to select an option
    get_driver().find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div/div[2]/div"
    ).click()


    # toggle moderation
    get_driver().find_element_by_css_selector("label[for=moderation]").click()
    # toggle is_project_type
    get_driver().find_element_by_css_selector("label[for=is_project_type]").click()
    # toggle generate_share_link
    get_driver().find_element_by_css_selector("label[for=generate_share_link]").click()

    # submit the form
    get_driver().find_element_by_id("send-project").click()

def geocontrib_create_featuretype(feature_type_name):
    get_driver().find_element_by_link_text(
        u"Créer un nouveau type de signalement"
    ).click()
    # fill the feature type title
    get_driver().find_element_by_id("title").click()
    get_driver().find_element_by_id("title").clear()
    get_driver().find_element_by_id("title").send_keys(feature_type_name)
    # submit the form
    get_driver().find_element_by_id("send-feature_type").click()

def geocontrib_create_feature(feature_type_name, feature_name):
    # click on button to create new feature from the first feature type
    get_driver().find_element_by_css_selector("[data-tooltip~=Ajouter]").click()
    # fill the name
    get_driver().find_element_by_id("name").click()
    get_driver().find_element_by_id("name").clear()
    get_driver().find_element_by_id("name").send_keys(feature_name)
    # add description
    description_input_elt = get_driver().find_element_by_name("description")
    description_input_elt.click()
    description_input_elt.clear()
    description_input_elt.send_keys("Exemple de description")
