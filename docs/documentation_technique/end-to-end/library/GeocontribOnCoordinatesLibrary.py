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

#from selenium.webdriver.common.action_chains import ActionChains
from utils import get_driver

#browser = driver.get("https://gojs.net/latest/samples/panelLayout.html");


def geocontrib_click_at_coordinates(pos_x, pos_y):
    # in chrome, web driver implementation calculates from top left
    # in firefox web driver implementation start at canvas center
    # thus not using random values until we can detect
    #actions = ActionChains(get_driver())
    # my_map = get_driver().find_element_by_css_selector("canvas")
    # actions.move_to_element_with_offset(my_map, 0, 0).click().perform()
    # actions.move_to_element_with_offset(my_map, pos_x, pos_y).click().perform()

    get_driver().find_element_by_css_selector("canvas").click()
    get_driver().find_element_by_css_selector("form#form-feature-edit.ui.form button.ui.teal.icon.button").click()
