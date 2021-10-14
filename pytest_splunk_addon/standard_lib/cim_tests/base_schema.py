#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
# -*- coding: utf-8 -*-
"""
Includes base class for data model schema. 
"""
from abc import ABC, abstractclassmethod


class BaseSchema(ABC):
    """
    Abstract class to parse the Data model files.
    The possible format can be JSON, YML, CSV, Cim_json
    """

    @abstractclassmethod
    def parse_data_model(cls, file_path):
        """
        Parse the DataModel file
        Convert it to JSON

        Expected Output::

            {
                "name":"Default_Authentication",
                "tags": ["authentication","default"],
                "fields_cluster":[],
                "fields":[
                    {
                        "fieldname": "action",
                        "field_type": "required",
                        "condition": "action IN ('success','failure','error')",
                        "comment":"The action performed on the resource."
                    },
                    ],
                "child_dataset": [
                    {
                        "name":"SuccessFul_Default_Authentication",
                        "tags": ["authentication","default"],
                        "fields_cluster":[],
                        "fields":[]
                        "child_dataset":[],
                        "search_constraints": "action='success'"
                    }
                ],
                "search_constraints":"action='failure'"
            }
        """
        pass
