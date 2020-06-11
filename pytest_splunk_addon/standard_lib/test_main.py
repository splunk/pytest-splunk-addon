from sample_generation import SampleGenerator

sample_generator = SampleGenerator(r'C:\Jay\Work\Automation\pytest-splunk-addon\new_dev_environment\eventgen_package')
for each in (sample_generator.get_samples()):
    print(each.event)
    print(each.get_key_fields())