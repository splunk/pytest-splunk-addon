
from . import SampleGenerator
import os
import pickle
from filelock import FileLock

class SampleXdistGenerator():

    def __init__(self, addon_path, config_path=None, process_count=4):
        self.addon_path = addon_path
        self.process_count = process_count
        self.config_path = config_path

    def get_samples(self):
        if "PYTEST_XDIST_WORKER" in os.environ:
            file_path = os.environ.get("PYTEST_XDIST_TESTRUNUID") + "_events"
            with FileLock(str(file_path) + ".lock"):
                if os.path.exists(file_path):
                    with open(file_path, "rb") as file_obj:
                        store_sample = pickle.load(file_obj)
                else:
                    sample_generator = SampleGenerator(
                        self.addon_path, self.config_path)
                    tokenized_events = list(sample_generator.get_samples())
                    store_sample = {"conf_name" : SampleGenerator.conf_name, "tokenized_events" : tokenized_events}
                    with open(file_path, "wb") as file_obj:
                        pickle.dump(store_sample, file_obj)
        else:  
            sample_generator = SampleGenerator(
                self.addon_path, self.config_path)
            tokenized_events = list(sample_generator.get_samples())
            store_sample = {"conf_name" : SampleGenerator.conf_name, "tokenized_events" : tokenized_events}
        return store_sample
