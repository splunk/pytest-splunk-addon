import logging

LOGGER = logging.getLogger("pytest-splunk-addon")
class IndexTimeTestGenerator(object):
    def generate_tests(self, sample_events):
        for sample in sample_events:
            sourcetype = sample.metadata.get("sourcetype_after_transforms",sample.metadata.get("sourcetype",*))
            source = sample.metadata.get("source_after_transforms",sample.metadata.get("source",*))
            
            hosts = sample.key_fields.pop()
