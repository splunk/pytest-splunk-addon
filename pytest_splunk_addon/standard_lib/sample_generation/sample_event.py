class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """
    def __init__(self, event_string):
        self.event = event_string
        # self.key_fields = tuple
        # self.fields = list()
        # self.sourcetype = str
        # self.source = str
