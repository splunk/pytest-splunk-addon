# ******* Input - requirement_log file, Transforms.conf of the addon Function:  parse and extract events from
# requirement files from path TA/requirement_files/abc.log Example
# TA_broken/requirement_files/sample_requirement_file.log
# Function:  Sourcetype the event before ingesting  to Splunk by using
# transforms.conf regex in config [Metadata: Sourcetype]


class RequirementEventIngestor(object):

    def __init__(self, app_path):
        """
        app_path to drill down to requirement file folder in package/tests/requirement_files/
        """
        pass

    def extract_raw_events(self):
        """
        This function returns raw events in <raw> section of the requirement files
        Iterate over all the requirement files and then send all the events to ingestor helper class
        """
        pass

    def extract_sourcetype(self):
        """
        Using app path extract sourcetype of the events
        From tranforms.conf [Metadata: Sourcetype] Regex
        This only works for syslog apps with this section
        """
        pass

    def get_events(self):
        """
        Send Sourcetyped events to event ingestor
        """
        pass
