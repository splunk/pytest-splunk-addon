import re

class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """
    def __init__(self, event_string, metadata):
        self.event = event_string
        # self.host = str
        # self.sourcetype = str
        # self.source = str
        # self.ingest_type = str
        self.key_fields = dict()
        self.metadata = metadata

    def update(self, new_event):
        self.event = new_event

    def get_token_count(self, token):
        return len(re.findall(token, self.event))

    def replace_token(self, token, token_values):
        # TODO: How to handle dependent Values with list of token_values 
        if isinstance(token_values, list):
            for token_value in token_values:
                self.event = re.sub(token, str(token_value), self.event, 1, flags=re.MULTILINE)
        else:
            self.event = re.sub(token, str(token_values), self.event, flags=re.MULTILINE)
            
    def register_field_value(self, field, token_value):
        self.key_fields.setdefault(field, []).append(token_value)

    def get_key_fields(self):
        return self.key_fields

    @classmethod
    def copy(cls, event):
        new_event = cls("",{})
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        return new_event
