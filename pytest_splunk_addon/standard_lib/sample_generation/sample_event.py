import re
import logging
from ..index_tests import key_fields

LOGGER = logging.getLogger("pytest-splunk-addon")

host_ipv4 = 50
src_ipv4 = 0
host_ipv6 = 0
src_ipv6 = 0


class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """

    def __init__(self, event_string, metadata, sample_name):
        self.event = event_string
        self.key_fields = dict()
        self.metadata = metadata
        self.sample_name = sample_name
        self.host_count = 0

    def update(self, new_event):
        self.event = new_event

    def get_host(self):
        self.host_count += 1
        return self.sample_name + "_" + str(self.host_count)

    def get_host_ipv4(self):
        global host_ipv4
        host_ipv4 += 1
        return "".join(["172.16.", str(host_ipv4 % 101), ".0"])

    def get_src_ipv4(self):
        global src_ipv4
        src_ipv4 += 1
        addr = [int(src_ipv4 / 256) % 256, src_ipv4 % 256]
        return "".join(["10.1.", str(addr[0]), str(addr[1])])

    def get_host_ipv6(self):
        global host_ipv6
        host_ipv6 = host_ipv6 % (int("ffffffffffffffff", 16))
        host_ipv6 += 1
        hex_count = hex(host_ipv6)
        non_zero_cnt = len(hex_count[2:])
        addr = "{}{}".format("0"*(16-non_zero_cnt), hex_count[2:])
        return "{}:{}".format("fdee:1fe4:2b8c:3264",':'.join(addr[i:i+4] for i in range(0, len(addr), 4)))

    def get_src_ipv6(self):
        global src_ipv6
        src_ipv6 = src_ipv6 % (int('ffffffffffffffff', 16))
        src_ipv6 += 1
        hex_count = hex(src_ipv6)
        non_zero_cnt = len(hex_count[2:])
        addr = "{}{}".format("0"*(16-non_zero_cnt), hex_count[2:])
        return "{}:{}".format("fdee:1fe4:2b8c:3261",':'.join(addr[i:i+4] for i in range(0, len(addr), 4)))

    def get_token_count(self, token):
        return len(re.findall(token, self.event))

    def replace_token(self, token, token_values):
        # TODO: How to handle dependent Values with list of token_values
        if isinstance(token_values, list):
            for token_value in token_values:
                self.event = re.sub(
                    token, str(token_value), self.event, 1, flags=re.MULTILINE
                )
        else:
            self.event = re.sub(
                token, str(token_values), self.event, flags=re.MULTILINE
            )

    def register_field_value(self, field, token_values):
        if field in key_fields.KEY_FIELDS:
            if isinstance(token_values, list):
                for token_value in token_values:
                    self.key_fields.setdefault(field, []).append(str(token_value))
            else:
                self.key_fields.setdefault(field, []).append(str(token_values))

    def get_key_fields(self):
        return self.key_fields

    @classmethod
    def copy(cls, event):
        new_event = cls("", {}, "")
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        return new_event

    def update_metadata(self, event, metadata):
        """
        This method is to process the syslog formated samples data
        data: raw syslog data
            data_format::
                ***SPLUNK*** source=<source> sourcetype=<sourcetype>

                field_1       field2        field3
                ##value1##    ##value2##   ##value3##
            metadata: dictionary of metadata
            params_format::
                {
                    "host": "sample_host",
                    "source": "sample_source"
                }
        Returns:
            syslog data and params that contains syslog_headers
        """
        try:
            if isinstance(event, str) and event.startswith("***SPLUNK***"):
                header = event.split("\n", 1)[0]
                self.event = event.split("\n", 1)[1]

                meta_fields = re.findall(r"[\w]+=[^\s]+", header)
                for meta_field in meta_fields:
                    field = meta_field.split("=")[0]
                    value = meta_field.split("=")[1]
                    self.metadata[field] = value

                return self.event, self.metadata
            else:
                return event, metadata
        except IndexError as error:
            LOGGER.error(f"Unexpected data found. Error: {error}")
            raise Exception(error)
