from .base_test_generator import BaseTestGenerator
from .fields_test_generator import FieldTestGenerator
from .cim_test_generator import CIMTestGenerator


class AppTestGenerator(object):
    def __init__(self, pytest_config):
        self.pytest_config = pytest_config
        self.fieldtest_generator = FieldTestGenerator(
                self.pytest_config.getoption("splunk_app")
            )
        # self.test_generator = CIMTestGenerator(
        #         True or self.pytest_config.getoption("dm_path"),
        #         self.pytest_config.getoption("splunk_app"),
        #     )

    def generate_tests(self, fixture):
        if fixture.endswith("fields"):
            is_positive = "positive" in fixture or not "negative" in fixture
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_field_tests(is_positive=is_positive)
            )
        elif fixture.endswith("tags"):
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_tag_tests()
            )
        elif fixture.endswith("eventtypes") :
            yield from self.dedup_tests(
                self.fieldtest_generator.generate_eventtype_tests()
            )

        elif fixture.endswith("cim"):
            pass

    def dedup_tests(self, test_list):
        """
        Deduplicate the test case parameters based on param.id
        Args:
            test_list(Generator): Generator of pytest.param
        Yields:
            Generator: De-duplicated pytest.param
        """
        seen_tests = set()
        for each_param in test_list:
            if each_param.id not in seen_tests:
                yield each_param
                seen_tests.add(each_param.id)
