#
# Inputs:   requirement file in TA's test folder
# Function: Send event to test template for testing
#           Parse XML   Extract Model to be verified from XML
#                       Extract key value pair for (Field name and value from XML)
#            Send one set of all above for each event in XML file and all the XML files in requirement folder


class ReqsTestGenerator(object):
    """
    Generates test cases to test the events in the log files
    * Provides the pytest parameters to the test_templates.py.
    """
    def __init__(self, app):
        """
        Args:
        app_path (str): Path of the app package to get access to requirement files
        """
        pass

    def xml_processing(self):
        # iterate through xml_files
        #   calls get model
        #   calls get extractKeyValue
        pass

    def get_model(self):
        # returns Model name for each event
        pass

    def get_field_key_value(self):
        # returns field name and value pair as stored in the
        pass

    def generate_tests(self, fixture):
        """
        Generate the test cases based on the fixture provided
        Args:
        fixture(str): fixture name which will initiate this
        """
        # yield from generate params

    def generate_params(self):
        # yield event, model, Dict(field_name,value)
        pass
