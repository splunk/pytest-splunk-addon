from concurrent.futures import ProcessPoolExecutor
from sample_parser import SampleParser
from rule import Rule
from splunk_appinspect import App

class EventgenParser:
    """
    This class represents the entire eventgen.conf file.
    """
    def __init__(self):
        self._app = App('Splunk_TA_cisco-wsa', python_analyzer_enable=False)
        self.samples_from_conf = None
        self.eventgen = self._app.get_config("eventgen.conf")

    def get_eventgen_stanzas(self):
        """
        Return: Eventgen stanzas dictionary
        """
        eventgen_dict = {}
        Rule.init_variables()
        for stanza in self.eventgen.sects:
            eventgen_sections = self.eventgen.sects[stanza]
            eventgen_dict[stanza] = {
                'tokens': {}
            }

            for stanza_param in eventgen_sections.options:
                eventgen_property = eventgen_sections.options[stanza_param]

                if eventgen_property.name.startswith('token'):
                    token_row = eventgen_property.name.split('.')
                    if not token_row[1] in eventgen_dict[stanza]['tokens'].keys():
                        eventgen_dict[stanza]['tokens'][token_row[1]] = {}
                    eventgen_dict[stanza]['tokens'][token_row[1]][token_row[2]] = eventgen_property.value

                else:
                    eventgen_dict[stanza].update({eventgen_property.name: eventgen_property.value})


        return eventgen_dict

    def parse_eventgen(self):
        """
        Yields: SampleParser Object
        """
        eventgen_dict = self.get_eventgen_stanzas()
        for stanza_name, stanza_params in eventgen_dict.items():
            rules = []
            for each_token, token_value in stanza_params['tokens'].items():

                rule_data = Rule.parse_rule(token_value['token'], token_value['replacementType'], token_value['replacement'])

                if 'field' in token_value:
                    rule_data.field = token_value['field']

                rules.append(rule_data)

            yield SampleParser(
                stanza_name,
                rules,
                stanza_params['ingest_type']
            )

    def parse_samples(self):
        """
        Input: List of all samples
        """
        executor = ProcessPoolExecutor(max_workers=3)
        result = list(executor.map(self.tokenize, self.samples_from_conf))

    def tokenize(self, sample):
        sample.tokenize()
