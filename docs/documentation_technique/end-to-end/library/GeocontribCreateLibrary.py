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

#def add_custom_field(custom_field_name, custom_field_type, list_options):
#    driver = get_driver()
#    add_field_btn = driver.find_element_by_id("add-field")
#    # scroll the page to reveal the button
#    driver.execute_script("document.getElementById('add-field').scrollIntoView('alignToTop');")
#    add_field_btn.click()
#    # scroll the page to reveal the button after the new element was added to the page
#    driver.execute_script("document.getElementById('send-feature_type').scrollIntoView('alignToTop');")
#    # add the label & name
#    driver.find_element_by_css_selector("#custom_form-1 #label").send_keys(custom_field_name)
#    driver.find_element_by_css_selector("#custom_form-1 #name").send_keys(custom_field_name)
#    # select the type
#    driver.find_element_by_css_selector("#custom_form-1 #field_type > .dropdown").click()
#    driver.find_element_by_css_selector("#custom_form-1 #field_type > .dropdown [id='" + custom_field_type + "']").click()
#    # for a list add options list
#    if list_options:
#        driver.find_element_by_css_selector("#custom_form-0 #options").send_keys(list_options)


def geocontrib_create_featuretype(feature_type_name, geometry_type):
    driver = get_driver()
    driver.find_element_by_link_text(
        u"Créer un nouveau type de signalement"
    ).click()
    # fill the feature type title
    title_el = driver.find_element_by_id("title")
    title_el.click()
    #title_el.clear()
    title_el.send_keys(feature_type_name)
    # select a geometry type
    driver.find_element_by_id("geometry-type").click()
    driver.find_element_by_id(geometry_type).click()

def geocontrib_add_custom_fields(list_name, char_name, bool_name, list_options):
    driver = get_driver()
    # fill custom field with a list
    #add_custom_field(list_name, "Liste de valeurs", list_options);
    #add_custom_field(char_name, "Chaîne de caractères", list_options);
    #add_custom_field(list_name, "Booléen", list_options);

    add_field_btn = driver.find_element_by_id("add-field")
    # add custom field for list
    add_field_btn.click()
    driver.find_element_by_css_selector("#custom_form-0 #label").send_keys(list_name)
    driver.find_element_by_css_selector("#custom_form-0 #name").send_keys(list_name)
    driver.find_element_by_css_selector("#custom_form-0 #field_type > .dropdown").click()
    driver.find_element_by_css_selector("#custom_form-0 #field_type > .dropdown [id='Liste de valeurs']").click()
    driver.find_element_by_css_selector("#custom_form-0 #options").send_keys(",".join(list_options))

    ## add custom field for characters
    ### scroll the page to reveal the button
    driver.execute_script("document.getElementById('add-field').scrollIntoView('alignToTop');")
    add_field_btn.click()
    ### scroll the page to reveal the button after the new element was added to the page
    driver.execute_script("document.getElementById('send-feature_type').scrollIntoView('alignToTop');")
    driver.find_element_by_css_selector("#custom_form-1 #label").send_keys(char_name)
    driver.find_element_by_css_selector("#custom_form-1 #name").send_keys(char_name)
    driver.find_element_by_css_selector("#custom_form-1 #field_type > .dropdown").click()
    driver.find_element_by_css_selector("#custom_form-1 #field_type > .dropdown [id='Chaîne de caractères']").click()

    ## add custom field with a boolean
    driver.execute_script("document.getElementById('add-field').scrollIntoView('alignToTop');")
    add_field_btn.click()
    ### scroll the page to reveal the button after the new element was added to the page
    driver.execute_script("document.getElementById('send-feature_type').scrollIntoView('alignToTop');")
    driver.find_element_by_css_selector("#custom_form-2 #label").send_keys(bool_name)
    driver.find_element_by_css_selector("#custom_form-2 #name").send_keys(bool_name)
    driver.find_element_by_css_selector("#custom_form-2 #field_type > .dropdown").click()
    driver.find_element_by_css_selector("#custom_form-2 #field_type > .dropdown [id='Booléen']").click()

    ## scroll the page to reveal the button
    driver.execute_script("document.getElementById('send-feature_type').scrollIntoView('alignToTop');")
    # submit the form
    #get_driver().find_element_by_id("send-feature_type").click()

def geocontrib_create_feature(feature_name, feature_type_name, added_text):
    driver = get_driver()

    selector = "div[id='{}{}'] a[data-tooltip~=Ajouter]".format(feature_type_name, added_text)
    driver.find_element_by_css_selector(selector).click()
    # fill the name
    driver.find_element_by_id("name").click()
    driver.find_element_by_id("name").clear()
    driver.find_element_by_id("name").send_keys(feature_name)
    # add description
    description_input_elt = driver.find_element_by_name("description")
    description_input_elt.click()
    description_input_elt.clear()
    description_input_elt.send_keys("Exemple de description")

def geocontrib_fill_custom_fields(list_name, char_name, list_option):
    driver = get_driver()
    # fill list field
    driver.find_element_by_css_selector("#{} > .dropdown".format(list_name)).click()
    driver.find_element_by_css_selector("#{} > .dropdown [id='{}']".format(list_name, list_option)).click()
    # fill char field
    char_input_elt = driver.find_element_by_name("char")
    char_input_elt.click()
    char_input_elt.send_keys(char_name)
    # fill boolean field
    driver.find_element_by_css_selector("label[for=boolean]").click()
