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


def geocontrib_draft_search_list(project_name):
    get_driver().find_element_by_link_text(u"GéoContrib").click()
    get_driver().find_element_by_link_text(project_name).click()
    get_driver().find_element_by_id("map").click()
    get_driver().find_element_by_xpath("//div[2]/div/a[2]").click()
    get_driver().find_element_by_xpath("//form[@id='form-filters']/div[2]/div/input[2]").click()
    get_driver().find_element_by_xpath("//form[@id='form-filters']/div[2]/div/div[2]/div").click()


def geocontrib_draft_search_map(project_name):
    get_driver().find_element_by_link_text(u"GéoContrib").click()
    get_driver().find_element_by_link_text(project_name).click()
    get_driver().find_element_by_id("map").click()
    get_driver().find_element_by_xpath("//form[@id='form-filters']/div[2]/div/input[2]").click()
    get_driver().find_element_by_xpath("//form[@id='form-filters']/div[2]/div/div[2]/div").click()
