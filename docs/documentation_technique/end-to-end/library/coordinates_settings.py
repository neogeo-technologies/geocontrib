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

import random


def get_variables():
    variables = {
                "X0":   150, #this position keeps the map bbox coordinates fixed 
                "Y0":   50, #to be able to click on feature on the map, if changed previous tests might fail
                "X1":   random.randint(500, 700),
                "Y1":   random.randint(100, 200),
                "X2":   random.randint(500, 700),
                "Y2":   random.randint(100, 200),
                "X3":   random.randint(500, 700),
                "Y3":   random.randint(100, 200),
                "X4":   random.randint(500, 700),
                "Y4":   random.randint(100, 200),
                }
    return variables
