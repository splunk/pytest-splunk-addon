from concurrent.futures import ProcessPoolExecutor
from sample_parser import SampleParser
from rule import Rule
from re import compile, sub, search, match, MULTILINE

class EventgenParser:

    def __init__(self):
        self._app = App('Splunk_TA_cisco-wsa', python_analyzer_enable=False)
        self.samples_from_conf = None
        self.eventgen = self._app.get_config("eventgen.conf")

    def parse_eventgen(self):
        # self.sample_parser = [ <parse and add to this list> ]
        """
        Input: eventgen.conf
        Output: [SampleObj1, SampleObj2] SampleObj1 == Object of SampleParser Class
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
        
        samples = []
        for sample_name in eventgen_dict: 
            rules = []
            for each_token in eventgen_dict[sample_name]:
                rules.append(Rule.parse_rule(each_token, eventgen_dict[sample_name][each_token]['token'], eventgen_dict[sample_name][each_token]['replacementType'], eventgen_dict[sample_name][each_token]['replacement']))
            sample = SampleParser(sample_name, rules)
            samples.append(sample)

        return samples
        
    def parse_samples(self):
        """
        Input: List of all samples
        Output: Tokenised samples
        """
        executor = ProcessPoolExecutor(max_workers=3)
        result = list(executor.map(self.tokenize, self.samples_from_conf))

    def tokenize(self, sample):
        print(sample.sample_name)

        for each_token in sample.sample_rules:
            # sample.sample_raw_data = each_token.apply(sample.sample_raw_data)
            sample.sample_raw_data = each_token.apply(sample)

        print(sample.sample_raw_data)
        print("======================================================")
