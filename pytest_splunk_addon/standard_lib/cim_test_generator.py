from .base_test_generator import BaseTestGenerator
from .data_model_handler import DataModelHandler
from .addon_parser import AddonParser

class CIMTestGenerator(BaseTestGenerator):

    def __init__(
        self, data_model_path, addon_path, 
        only_required_fields=False,
        only_recommended_fields=False,
        only_cim_fields=False
    ):

        self.data_model_handler = DataModelHandler(data_model_path)
        self.addon_parser = AddonParser(addon_path)

    def get_cim_models(self):
        yield from self.data_model_handler.get_mapped_data_models(self.addon_parser)

    def generate_cim_fields(self):
        for each_model in self.get_cim_models():
            # get each fields from the model 
            # Generate test case for each model 
            pass

    def generate_tests(self):

        pass
