from concurrent.futures import ProcessPoolExecutor
from sample_parser import SampleParser
from rule import Rule
from splunk_appinspect import App
import os
import re

class EventgenParser:
    """
    This class represents the entire eventgen.conf file.
    """
    def __init__(self, addon_path):
        self._app = App(addon_path, python_analyzer_enable=False)
        self.samples_from_conf = None
        self.eventgen = self._app.get_config("eventgen1.conf")
        self.path_to_samples = 'path_to_samples'
    def merge_eventgen_stanzas(self, eventgen_dict):

        sample_files = os.listdir(self.path_to_samples)

        for sample_file in sample_files:
            match_stanzas = [stanza for stanza in eventgen_dict if re.match(stanza, sample_file)]

            for stanza in match_stanzas:
                for index in range(len(match_stanzas)):    
                    eventgen_dict[stanza]['tokens'] = {**eventgen_dict[stanza]['tokens'], **eventgen_dict[match_stanzas[index]]['tokens']}

            # print(sample_file, match_stanzas)
        return eventgen_dict


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

        eventgen_dict = self.merge_eventgen_stanzas(eventgen_dict)
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

