from concurrent.futures import ProcessPoolExecutor
from sample_parser import SampleParser
from rule import Rule
from splunk_appinspect import App

class EventgenParser:

    def __init__(self):
        self._app = App('Splunk_TA_cisco-wsa', python_analyzer_enable=False)
        self.samples_from_conf = None
        self.eventgen = self._app.get_config("eventgen.conf")

    def parse_eventgen(self):
        """
        Return: samples dictionary
                [
                    {
                        'sample_name': ${sample_name}, // Sample name
                        'rules': ${rules}, // List of token
                    }
                ]
        """
        samples = []
        eventgen_dict = self.get_eventgen_stanzas()
        for sample_name in eventgen_dict: 
            rules = []
            for each_token in eventgen_dict[sample_name]:
                rule_data = Rule.parse_rule(each_token, eventgen_dict[sample_name][each_token]['token'], eventgen_dict[sample_name][each_token]['replacementType'], eventgen_dict[sample_name][each_token]['replacement'])
                
                if 'field' in eventgen_dict[sample_name][each_token]:
                    rule_data.field = eventgen_dict[sample_name][each_token]['field']
                rules.append(rule_data)
            # sample = SampleParser(sample_name, rules)
            # Yield sample from here
            samples.append({
                "sample_name": sample_name,
                "rules": rules
            })

        return samples
        
    def get_eventgen_stanzas(self):
        """
        Return: Eventgen stanzas dictionary
        """
        eventgen_dict = {}
        Rule.init_variables()
        for stanza in self.eventgen.sects:
            rules = []
            eventgen_sections = self.eventgen.sects[stanza]
            eventgen_dict[stanza] = {}
            for key in eventgen_sections.options:
                eventgen_property = eventgen_sections.options[key]
                if eventgen_property.name.startswith('token'):
                    token_row = eventgen_property.name.split('.')
                    if not token_row[1] in eventgen_dict[stanza].keys():
                        eventgen_dict[stanza][token_row[1]] = {}
                    eventgen_dict[stanza][token_row[1]][token_row[2]] = eventgen_property.value
        return eventgen_dict
        
    def parse_samples(self):
        """
        Input: List of all samples
        """
        executor = ProcessPoolExecutor(max_workers=3)
        result = list(executor.map(self.tokenize, self.samples_from_conf))

    def tokenize(self, sample):
        sample = SampleParser(sample['sample_name'], sample['rules'])
        sample.tokenize()
