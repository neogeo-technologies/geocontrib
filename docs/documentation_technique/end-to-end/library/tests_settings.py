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

from decouple import config

def get_variables():
    variables = {
                "BROWSER_NAME": config('BROWSER_NAME', default="Chrome"),
                "GEOCONTRIB_URL": config('GEOCONTRIB_URL', default="http://localhost:8080/geocontrib"),
                "ADMIN_URL": config('ADMIN_URL', default="http://localhost:8000/admin"),
                "SUPERUSERNAME": config('SUPERUSERNAME', default="admin_robot"),
                "SUPERUSERPASSWORD": config('SUPERUSERPASSWORD', default="roboto2022?"),
                "SUPERUSERDISPLAYNAME": config('SUPERUSERDISPLAYNAME', default="Admin Robot")
                }
    return variables
