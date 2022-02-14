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
import json
import logging
import pytest
import re
from .requirement_test_datamodel_tag_constants import dict_datamodel_tag

INTERVAL = 3
RETRIES = 3


class ReqsTestTemplates(object):
    """
    Test templates to test the log files in the event_analytics folder
    """

    logger = logging.getLogger()

    # Function to remove the data model subset concatenated to fields from the dictionary
    # eg : All_traffic.dest -> dest else do nothing
    def process_str(self, in_str):
        new_dict = {}
        for k, v in in_str.items():
            # self.logger.info(k, v)
            b = k.split(".", 1)
            if len(b) == 1:
                new_dict.update({b[0]: v})
            else:
                new_dict.update({b[1]: v})
        return new_dict

    # Function to compare the fields extracted from XML and the fields extracted from Splunk search
    def compare(self, keyValueSPL, keyValueXML, escapedKeyValue):
        dict_missing_key_value = {}
        # keyValueprocessedSPL = self.process_str(keyValueSPL)
        flag = True
        for key, value in keyValueXML.items():
            res = key in keyValueSPL and value == keyValueSPL[key]
            if (not res) and (key not in escapedKeyValue):
                valueinsplunk = None
                if key in keyValueSPL.keys():
                    valueinsplunk = keyValueSPL[key]
                dict_missing_key_value.update(
                    {
                        "Key value in requirement file: " + key: value,
                        "Key value extracted by Splunk: " + key: valueinsplunk,
                    }
                )
                flag = False
        return flag, dict_missing_key_value

    # Function to extract tags from Splunk search result returned.
    def extract_tag(self, keyValueSPL):
        for key, value in keyValueSPL.items():
            if key == "tag":
                # Converting string to list
                self.logger.info(value)
                list_of_extracted_tags = value.strip("][").split(", ")
                c = []
                for item in list_of_extracted_tags:
                    item = item.replace("'", "")
                    c.append(item)
                self.logger.info(list_of_extracted_tags)
                return c

    # Function to find matching data models based on the tags
    def fetch_datamodel_by_tags(self, tag):
        list_matching_datamodel = {}
        for datamodel, tags in dict_datamodel_tag.items():
            if set(tags) <= set(tag):
                list_matching_datamodel.update({datamodel: tags})
        return list_matching_datamodel

    # Function to remove subset datamodels from the list
    def remove_subset_datamodel(self, datamodel_dict):
        return dict(
            [
                i
                for i in datamodel_dict.items()
                if not any(
                    set(j).issuperset(set(i[1])) and j != i[1]
                    for j in datamodel_dict.values()
                )
            ]
        )

    # Function to compare datamodel from tags returned in splunk search and requirement file
    def compare_datamodel(self, requirementfile_datamodels, datamodel_based_on_tag):
        lis_extra_extracted_splunkside = []
        list_extra_datamodel_requirement_file = []
        for key in datamodel_based_on_tag:
            if key in requirementfile_datamodels:
                continue
            else:
                lis_extra_extracted_splunkside.append(key)
        for item in requirementfile_datamodels:
            if item in datamodel_based_on_tag.keys():
                continue
            else:
                list_extra_datamodel_requirement_file.append(item)
        return set(lis_extra_extracted_splunkside), set(
            list_extra_datamodel_requirement_file
        )

    # Function which runs data model check
    def datamodel_check_test(self, keyValue_dict_SPL, requrement_file_model_list):
        extracted_tags = self.extract_tag(keyValue_dict_SPL)
        if extracted_tags == None:
            datamodel_based_on_tag = {}
        else:
            datamodel_based_on_tag = self.fetch_datamodel_by_tags(extracted_tags)
            datamodel_based_on_tag = self.remove_subset_datamodel(
                datamodel_based_on_tag
            )
        (
            lis_extra_extracted_splunkside,
            list_extra_datamodel_requirement_file,
        ) = self.compare_datamodel(requrement_file_model_list, datamodel_based_on_tag)
        return (
            list_extra_datamodel_requirement_file,
            lis_extra_extracted_splunkside,
            datamodel_based_on_tag,
        )

    def remove_empty_keys(self, event):
        event = re.sub(
            r"(\s[a-zA-Z0-9_]*(\\=|\\:)(\\\"\\\"|\\'\\'|\\-))", "", str(event)
        )
        return event

    @pytest.mark.splunk_searchtime_requirements
    def test_requirement_params(
        self,
        splunk_searchtime_requirement_param,
        splunk_search_util,
        splunk_ingest_data,
    ):
        model_datalist = splunk_searchtime_requirement_param["model_list"]
        escaped_event = splunk_searchtime_requirement_param["escaped_event"]
        key_values_xml = splunk_searchtime_requirement_param["Key_value_dict"]
        exceptions_dict = splunk_searchtime_requirement_param["exceptions_dict"]
        modinput_params = splunk_searchtime_requirement_param["modinput_params"]
        transport_type = splunk_searchtime_requirement_param["transport_type"]
        logging.info(exceptions_dict)
        # search = f" search source= pytest_splunk_addon:hec:raw sourcetype={sourcetype} {escaped_event} |fields * "
        # removed source and sourcetype as sc4s assigns it based on event
        if transport_type in (
            "modinput",
            "Modinput",
            "Mod input",
            "Modular Input",
            "Modular input",
            "modular input",
            "modular_input",
            "Mod Input",
        ):
            host = modinput_params["host"]
            source = modinput_params["source"]
            sourcetype = modinput_params["sourcetype"]
            search = f'search index=* host="{host}" source="{source}" sourcetype="{sourcetype}" {escaped_event}|fields * '
        else:
            search = f"search index=* {escaped_event} |fields * "
        ingestion_check = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )

        if not ingestion_check and transport_type.lower() == "syslog":
            empty_field_removed = self.remove_empty_keys(escaped_event)
            search = f"search index=* {empty_field_removed} |fields * "
            ingestion_check = splunk_search_util.checkQueryCountIsGreaterThanZero(
                search, interval=INTERVAL, retries=RETRIES
            )

        assert ingestion_check, f"ingestion failure \nsearch={search}\n"
        self.logger.info(f"ingestion_check: {ingestion_check}")
        keyValue_dict_SPL = splunk_search_util.getFieldValuesDict(
            search, interval=INTERVAL, retries=RETRIES
        )
        (
            list_unmatched_datamodel_splunkside,
            list_unmatched_datamodel_requirement_file,
            datamodel_based_on_tag,
        ) = self.datamodel_check_test(keyValue_dict_SPL, model_datalist)
        datamodel_check = not bool(
            list_unmatched_datamodel_splunkside
            or list_unmatched_datamodel_requirement_file
        )
        self.logger.info(f"Data model check: {datamodel_check}")
        sourcetype = keyValue_dict_SPL["_sourcetype"]
        field_extraction_check, missing_key_value = self.compare(
            keyValue_dict_SPL, key_values_xml, exceptions_dict
        )
        self.logger.info(f"Field mapping check: {field_extraction_check}")

        assert datamodel_check and field_extraction_check, (
            f" Issue with either field extraction or data model.\nsearch={search}\n"
            f" data model check: {datamodel_check} \n"
            f" data model in requirement file  {model_datalist}\n "
            f" data model extracted by TA {list(datamodel_based_on_tag.keys())}\n"
            f" Field_extraction_check: {field_extraction_check} \n"
            f" Field extraction errors: {json.dumps(missing_key_value, indent=4)} \n"
            f" sourcetype of ingested event: {sourcetype} \n"
        )
