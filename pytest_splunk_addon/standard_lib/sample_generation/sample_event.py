import re

class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """
    def __init__(self, event_string):
        self.event = event_string
        self.host = str
        self.sourcetype = str
        self.source = str
        self.ingest_type = str
        self.key_fields = dict()

    def update(self, new_event):
        self.event = new_event

    def replace_token(self, token, token_value):
        # TODO: Replace values one by one
        # TODO: How to handle dependent Values with list of token_values 
        self.event = re.sub(token, str(token_value), self.event, flags=re.MULTILINE)

    def register_field_value(self, field, token_value):
        self.key_fields.setdefault(field, []).append(token_value)

    def get_key_fields(self):
        return self.key_fields

    @classmethod
    def copy(cls, event):
        new_event = cls("")
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        return new_event
