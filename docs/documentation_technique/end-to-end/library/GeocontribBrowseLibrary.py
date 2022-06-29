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


def geocontrib_browse_feature_list(feature_name, feature_type_name, added_text):
    driver = get_driver()
    #* access feature list page and display table view
    driver.find_element_by_id("features-list").click()
    driver.find_element_by_id("show-list").click()
    #* open the dropdown for custom fields
    driver.find_element_by_css_selector("#type > .dropdown").click()
    #*select the field
    driver.find_element_by_id("{}{}".format(feature_type_name, added_text)).click()
    #* click on the first feature containing feature name
    driver.find_element_by_partial_link_text(feature_name).click()

