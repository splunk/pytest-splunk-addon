from .addon_parser import AddonParser
from .base_test_generator import BaseTestGenerator
import pytest

class FieldTestGenerator(BaseTestGenerator):
    """
    A class who knows what kind of test case should be generated for testing the field extraction of the add-on
    """
    def __init__(self, addon_path):
        self.addon_parser = AddonParser(addon_path)

    def generate_field_tests(self, is_positive=True):
        for fields_group in self.addon_parser.get_props_fields():
            # Generate test case for the stanza 
            # Do not generate if it is a negative test case
            if is_positive:
                stanza_test_group = fields_group.copy()
                stanza_test_group["fields"] = []
                yield pytest.param(
                    stanza_test_group,
                    id="{stanza}".format(**fields_group)
                )

            # Generate a test case for all the fields in the classname 
            if self._contains_classname(fields_group, ["EXTRACT", "REPORT"]):
                yield pytest.param( 
                    fields_group,
                    id="{stanza}::{classname}".format(**fields_group)
                )

            # Generate test-cases for each field in classname one by one 
            for each_field in fields_group["fields"]:

                # Create a dictionary for a single field with classname and stanza
                one_field_group = fields_group.copy()
                one_field_group["fields"] = [each_field]

                stanza = fields_group["stanza"]
                yield pytest.param(
                    one_field_group,
                    id=f"{stanza}::field::{each_field}"
                )

    def generate_tag_tests(self):
        for each_tag_group in self.addon_parser.get_tags():
            yield pytest.param( 
                    each_tag_group,
                    id="{stanza}::tag::{tag}".format(**each_tag_group)
                )

    def generate_eventtype_tests(self):
        for each_eventtype in self.addon_parser.get_eventtypes():
            yield pytest.param( 
                    each_eventtype,
                    id="eventtype::{stanza}".format(**each_eventtype)
                )

    def _contains_classname(self, fields_group, criteria):
        return any([fields_group["classname"].startswith(each) for each in criteria ])