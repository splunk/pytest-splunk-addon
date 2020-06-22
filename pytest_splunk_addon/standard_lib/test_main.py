from sample_generation import SampleGenerator

sample_generator = SampleGenerator(r'G:\My Drive\TA-Factory\automation\testing\package')
for each in (sample_generator.get_samples()):
    print(each.event)
    print(each.get_key_fields())