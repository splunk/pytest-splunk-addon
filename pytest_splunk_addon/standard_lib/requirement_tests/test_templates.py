import logging
import pytest
import time

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
            b = k.split('.', 1)
            if len(b) == 1:
                new_dict.update({b[0]: v})
            else:
                new_dict.update({b[1]: v})
        return new_dict

    # Function to compare the fields extracted from XML and the fields extracted from Splunk search
    def compare(self, keyValueSPL, keyValueXML):
        keyValueprocessedSPL = self.process_str(keyValueSPL)
        flag = True
        for key, value in keyValueXML.items():
            res = key in keyValueprocessedSPL and value == keyValueprocessedSPL[key]
            if not res:
                self.logger.info(key + " not in SPL extracted fields")
                flag = False
        return flag

    @pytest.mark.splunk_searchtime_requirements
    def test_requirement_params(self, splunk_searchtime_requirement_param, splunk_search_util):
        model = splunk_searchtime_requirement_param["model"]
        escaped_event = splunk_searchtime_requirement_param["escaped_event"]
        filename = splunk_searchtime_requirement_param["filename"]
        sourcetype = splunk_searchtime_requirement_param["sourcetype"]
        key_values_xml = splunk_searchtime_requirement_param["Key_value_dict"]
        self.logger.info(key_values_xml)
        result = False
        if model is None and escaped_event is None:
            self.logger.info("Issue parsing log file {}".format(filename))
            pytest.skip('Issue parsing log file')
        if model is None and escaped_event is not None:
            self.logger.info("No model present in file")
            pytest.skip('No model present in file')
        if sourcetype is None:
            self.logger.info("Issue finding sourcetype")
            assert result

        # Search for getting both data model and field extractions
        search = f"| datamodel {model}  search | search source=	pytest_splunk_addon:hec:raw sourcetype={sourcetype} {escaped_event}"
        datamodel_check = splunk_search_util.checkQueryCountIsGreaterThanZero(
            search, interval=INTERVAL, retries=RETRIES
        )
        assert datamodel_check, (
            f"Data model mismatch \nsearch={search}\n"
        )
        self.logger.info(f"Data model mapping check: {datamodel_check}")

        keyValue_dict_SPL = splunk_search_util.getFieldValuesDict(
            search, interval=INTERVAL, retries=RETRIES
        )
        field_extraction_check = self.compare(keyValue_dict_SPL, key_values_xml)
        self.logger.info(f"Field mapping check: {field_extraction_check}")

        assert field_extraction_check, (
            f"Issue with the field extraction.\nsearch={search}\n"
            f" Field_extraction_check: {field_extraction_check} \n"
        )
