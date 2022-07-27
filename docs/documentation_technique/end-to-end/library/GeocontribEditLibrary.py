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
    driver = get_driver()
    driver.find_element_by_class_name("button-hover-orange").click()
    # modify title
    title_input_elt = driver.find_element_by_id("title")
    title_input_elt.click()
    title_input_elt.clear()
    title_input_elt.send_keys("{}{}".format(project_name, project_edition))

    # modify description
    driver.find_element_by_name("description").click()
    driver.find_element_by_name("description").clear()
    driver.find_element_by_name("description").send_keys(project_edition)

    # click on dropdown "Visibilité des signalements publiés" to open it
    driver.find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div"
    ).click()
    # click on dropdown "Visibilité des signalements publiés" to select an option
    driver.find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div/div/div[2]/div[2]"
    ).click()

    # click on dropdown "Visibilité des signalements archivés" to open it
    driver.find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div"
    ).click()
    # click on dropdown "Visibilité des signalements archivés" to select an option
    driver.find_element_by_xpath(
        "//form[@id='form-project-edit']/div[5]/div[2]/div/div[2]/div[2]"
    ).click()

    # toggle moderation
    driver.find_element_by_css_selector("label[for=moderation]").click()
    # toggle is_project_type
    driver.find_element_by_css_selector("label[for=is_project_type]").click()
    # toggle generate_share_link
    driver.find_element_by_css_selector("label[for=generate_share_link]").click()
    # toggle fast_edition
    driver.find_element_by_css_selector("label[for=fast_edition_mode]").click()

    # submit the form
    driver.find_element_by_id("send-project").click()


def geocontrib_edit_featuretype(featuretypename, added_text):
    driver = get_driver()
    # got to first feature type edition page    
    driver.find_element_by_css_selector("a[data-tooltip*='Éditer le type de signalement']").click()
    # modify feature type title
    title_input_elt = driver.find_element_by_id("title")
    title_input_elt.click()
    title_input_elt.clear()
    title_input_elt.send_keys("{}{}".format(featuretypename, added_text))
    # todo: add an option to change geometry when we can test more than points
    optionnal_title_input_elt = driver.find_element_by_id("title_optional")
    optionnal_title_input_elt.click
    # submit the form
    driver.execute_script("document.getElementById('send-feature_type').scrollIntoView('alignToTop');")
    driver.find_element_by_id("send-feature_type").click()


def geocontrib_edit_feature(feature_name, added_text):
    driver = get_driver()
    # go to edition page
    driver.find_element_by_css_selector("a[href*=editer]").click()
    # modify the name
    name_input_elt = driver.find_element_by_id("name")
    name_input_elt.click()
    name_input_elt.clear()
    name_input_elt.send_keys("{}{}".format(feature_name, added_text))
    # modify description
    description_input_elt = driver.find_element_by_name("description")
    description_input_elt.click()
    description_input_elt.clear()
    description_input_elt.send_keys(added_text)
    # modify status
    ## open the status dropdown
    driver.find_element_by_css_selector("#form-feature-edit div.required:nth-child(2)>div[id*='dropdown']").click()
    ## select second status option
    driver.find_element_by_css_selector("#form-feature-edit div.required:nth-child(2)>div[id*='dropdown'] div.menu > div.item:nth-child(2)").click()

def geocontrib_access_featuretype_symbology(featureTypeName):
    driver = get_driver()
    # got to first feature type edition page
    driver.find_element_by_css_selector(
        "#" + featureTypeName + " " + "a[data-tooltip*='Éditer la symbologie du type de signalement']"
    ).click()

def geocontrib_edit_featuretype_symbology(colorcode, opacity, form_selector):
    driver = get_driver()
    color_input_elt = driver.find_element_by_css_selector(form_selector + " #couleur")
    #*because color selector is an os tool, we can't interact with, thus we send the value directly to the input
    color_input_elt.send_keys(colorcode)
    #*for Vue to detect the change and update the value, we need to dispatch an event
    driver.execute_script('document.querySelector("{} #couleur").dispatchEvent(new Event("change"));'.format(form_selector))
    #*edit default symbology color
    #opacity_input_elt = driver.find_element_by_id("opacity")
    #opacity_input_elt.send_keys(opacity) # doesn't work
    driver.execute_script('document.querySelector("{} #opacity").value = {};'.format(form_selector, opacity))
    #*same as above, dispatching an event to be recorded by Vue
    driver.execute_script('document.querySelector("{} #opacity").dispatchEvent(new Event("input"));'.format(form_selector))
    driver.implicitly_wait(1) # seconds

def geocontrib_edit_custom_field_symbology(colors, opacities, custom_field_name, list_options):
    driver = get_driver()
    #*open the dropdown for custom fields
    driver.find_element_by_css_selector("#custom_types-dropdown > .dropdown").click()
    #*select the field
    driver.find_element_by_id(custom_field_name).click()

    form_selector_1 = ''
    form_selector_2 = ''
    if list_options:
        form_selector_1 = "div[id='{}']".format(list_options[0])
        form_selector_2 = "div[id='{}']".format(list_options[1])
    elif custom_field_name == "char":
        form_selector_1 = "div[id='Vide']"
        form_selector_2 = "div[id^='Non']" 
    elif custom_field_name == "boolean":
        form_selector_1 = "div[id='Décoché']"
        form_selector_2 = "div[id='Coché']"
    #*edit first field
    geocontrib_edit_featuretype_symbology(colors[0], opacities[0], form_selector_1)
    #*edit second field
    geocontrib_edit_featuretype_symbology(colors[1], opacities[1], form_selector_2)

def geocontrib_activate_fast_edition_for_project():
    driver = get_driver()
    driver.find_element_by_class_name("button-hover-orange").click()
    # check the input if not already selected
    if driver.find_element_by_id("fast_edition_mode").is_selected() == False:
        driver.find_element_by_css_selector("label[for=fast_edition_mode]").click() #click on label to toggle checkbox
    # submit the form
    driver.find_element_by_id("send-project").click()

def geocontrib_fast_edit_feature_detail(name, description, added_text):
    driver = get_driver()
    driver.find_element_by_id("feature_detail_title_input").clear()
    driver.find_element_by_id("feature_detail_title_input").send_keys("{}{}".format(name, added_text))
    driver.find_element_by_name("description").clear()
    driver.find_element_by_name("description").send_keys(description)
    #*open the dropdown for status
    driver.find_element_by_css_selector("#status > .dropdown").click()
    #*select the field
    driver.find_element_by_id("Archivé").click()

def geocontrib_fast_edit_custom_fields(list_name, char_name, list_option):
    driver = get_driver()
    # scroll the page to reveal the button
    driver.execute_script("document.getElementById('{}').scrollIntoView('alignToTop');".format(list_name))
    # fill list field
    driver.find_element_by_css_selector("#{} .dropdown".format(list_name)).click()
    driver.find_element_by_css_selector("#{} .dropdown [id='{}']".format(list_name, list_option)).click()
    # fill char field
    char_input_elt = driver.find_element_by_name("char")
    char_input_elt.click()
    char_input_elt.clear()
    char_input_elt.send_keys(char_name)
    # fill boolean field
    driver.find_element_by_name("boolean").click()