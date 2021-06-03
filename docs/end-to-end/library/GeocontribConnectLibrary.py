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


def geocontrib_connect_superuser(username, password):
    get_driver().find_element_by_link_text("Se Connecter").click()
    get_driver().find_element_by_name("username").clear()
    get_driver().find_element_by_name("username").send_keys(username)
    get_driver().find_element_by_name("password").clear()
    get_driver().find_element_by_name("password").send_keys(password)
    get_driver().find_element_by_xpath("//button[@type='submit']").click()


def geocontrib_disconnect():
    get_driver().find_element_by_xpath("//i").click()
