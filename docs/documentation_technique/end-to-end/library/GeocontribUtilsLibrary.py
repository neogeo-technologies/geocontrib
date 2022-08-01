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


def geocontrib_click_save_changes():
    # scroll the page to reveal the button
    get_driver().execute_script("window.scrollTo(0, document.body.scrollHeight);")
    get_driver().implicitly_wait(1) # seconds
    # try twice to increase the chances that the button would be clickable
    try :
        get_driver().find_element_by_css_selector("form#form-feature-edit.ui.form button.ui.teal.icon.button").click()
    except :
        get_driver().find_element_by_css_selector("form#form-feature-edit.ui.form button.ui.teal.icon.button").click()