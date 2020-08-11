import re
import logging
from ..index_tests import key_fields
from faker import Faker
from copy import deepcopy

LOGGER = logging.getLogger("pytest-splunk-addon")

host_ipv4, dvc_ipv4 = 50, 0
src_ipv4, dest_ipv4 = 0, 0
host_ipv6, dvc_ipv6 = 0, 0
src_ipv6, dest_ipv6 = 0, 0
host_count, fqdn_count = 0,0
url_ip_count = 0
host_ipv4_octet_count, dvc_ipv4_octet_count = 0, 0

ip_rules = {
        "src":{
            "ipv4": "10.1.",
            "ipv6": "fdee:1fe4:2b8c:3261",
        },
        "dest":{
            "ipv4": "10.100.",
            "ipv6": "fdee:1fe4:2b8c:3262",
        },
        "dvc":{
            "ipv4": "172.16.",
            "ipv6": "fdee:1fe4:2b8c:3263",
        },
        "host":{
            "ipv4": "172.16.",
            "ipv6": "fdee:1fe4:2b8c:3264",
        },
        "url":{
            "ip_host": "192.168.",
        }
    }


class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.

    Args:
        event_string (str): Event content
        metadata (dict): Contains metadata for the event
        sample_name (str): Name of the file containing this event
    """

    def __init__(self, event_string, metadata, sample_name):
        self.event = event_string
        self.key_fields = dict()
        self.time_values = list()
        self.metadata = metadata
        self.sample_name = sample_name
        self.host_count = 0

    def update(self, new_event):
        """
        This method updates the event content

        Args:
            new_event (str): Event content 
        """
        self.event = new_event

    def get_host(self):
        """
        Returns a unique host value
        """
        global host_count
        host_count += 1
        return "{}_{}_{}".format("host", self.sample_name, str(host_count))

    def get_field_host(self, rule):
        """
        Returns unique host value for the key fields src, dest, host, dvc

        Args:
            rule (str): Type of rule either src, host, dest, dvc
        """
        global host_count
        host_count += 1
        return "{}_{}{}".format(rule, "sample_host", host_count)

    def get_field_fqdn(self, rule):
        """
        Returns unique fqdn value for the key fields src, dest, host, dvc

        Args:
            rule (str): Type of rule either src, host, dest, dvc
        """
        global fqdn_count
        fqdn_count += 1
        return "{}_{}.{}{}.com".format(rule, "sample_host", "sample_domain", fqdn_count)

    def get_ipv4(self, rule):
        """
        Returns Ipv4 Address as per the rule.

        Args:
            rule (str): Type of rule either src, host, dest, dvc.
            If the value is not one of the key field it will return a randomly generated Ipv4 address.
        """
        if rule == "src":
            global src_ipv4
            src_ipv4 += 1
            addr = [int(src_ipv4 / 256) % 256, src_ipv4 % 256]
            return "".join([ip_rules.get(rule)["ipv4"], str(addr[0]), ".", str(addr[1])])
        elif rule == "host":
            global host_ipv4, host_ipv4_octet_count
            host_ipv4 += 1
            if host_ipv4 == 101:
                host_ipv4 = 51
            host_ipv4_octet_count += 1
            return "".join([ip_rules.get(rule)["ipv4"], str(host_ipv4 % 101), ".", str(host_ipv4_octet_count % 256)])
        elif rule == "dvc":
            global dvc_ipv4, dvc_ipv4_octet_count
            dvc_ipv4 += 1
            dvc_ipv4_octet_count += 1
            return "".join([ip_rules.get(rule)["ipv4"], str(dvc_ipv4 % 51), ".", str(dvc_ipv4_octet_count % 256)])
        elif rule == "dest":
            global dest_ipv4
            dest_ipv4 += 1
            addr = [int(dest_ipv4 / 256) % 256, dest_ipv4 % 256]
            return "".join([ip_rules.get(rule)["ipv4"], str(addr[0]), ".", str(addr[1])])
        elif rule == "url":
            global url_ip_count
            url_ip_count += 1
            addr = [int(url_ip_count / 256) % 256, url_ip_count % 256]
            return "".join([ip_rules.get(rule)["ip_host"], str(addr[0]), ".", str(addr[1])])
        else:
            return Faker().ipv4()

    def get_ipv6(self, rule):
        """
        Returns Ipv6 Address as per the rule.

        Args:
            rule (str): Type of rule either src, host, dest, dvc.
            If the value is not one of the key field it will return a randomly generated Ipv6 address.
        """
        if rule == "src":
            global src_ipv6
            ipv6 = src_ipv6 % (int("ffffffffffffffff", 16))
            src_ipv6 += 1
        elif rule == "host":
            global host_ipv6
            ipv6 = host_ipv6 % (int("ffffffffffffffff", 16))
            host_ipv6 += 1
        elif rule == "dvc":
            global dvc_ipv6
            ipv6 = dvc_ipv6 % (int("ffffffffffffffff", 16))
            dvc_ipv6 += 1
        elif rule == "dest":
            global dest_ipv6
            ipv6 = dest_ipv6 % (int("ffffffffffffffff", 16))
            dest_ipv6 += 1
        else:
            return Faker().ipv6()

        hex_count = hex(ipv6)
        non_zero_cnt = len(hex_count[2:])
        addr = "{}{}".format("0"*(16-non_zero_cnt), hex_count[2:])
        return "{}:{}".format(ip_rules.get(rule)["ipv6"],':'.join(addr[i:i+4] for i in range(0, len(addr), 4)))

    def get_token_count(self, token):
        """
        Returns the token count in event

        Args:
            token (str): Token name
        """
        return len(re.findall(token, self.event, flags=re.MULTILINE))

    def replace_token(self, token, token_values):
        """
        Replaces the token value in event

        Args:
            token (str): Token name 
            token_values (list/str): Value(s) to be replaced in the token 
        """
        # TODO: How to handle dependent Values with list of token_values
        if isinstance(token_values, list):
            sample_tokens = re.finditer(token, self.event, flags=re.MULTILINE)

            for _, token_value in enumerate(token_values):
                token_value = token_value.value
                match_object = next(sample_tokens)
                match_str = match_object.group(0) if len(match_object.groups()) == 0 else match_object.group(1)
                match_str = re.escape(match_str)
                self.event = re.sub(
                    match_str, lambda x: str(token_value), self.event, 1, flags=re.MULTILINE
                )
        else:
            self.event = re.sub(
                token,
                lambda x: str(token_values),
                self.event,
                flags=re.MULTILINE
            )

    def register_field_value(self, field, token_values):
        """
        Registers the value for the key fields in its SampleEvent object

        Args:
            field (str): Token field name 
            token_values (list/str): Token value(s) which are replaced in the key fields
        """
        if field == "_time":
            time_list = token_values if isinstance(token_values, list) else [token_values]
            self.time_values.extend([i.key for i in time_list])
        elif field in key_fields.KEY_FIELDS:
            if isinstance(token_values, list):
                for token_value in token_values:
                    self.key_fields.setdefault(field, []).append(
                        str(token_value.key)
                        )
            else:
                self.key_fields.setdefault(field, []).append(str(token_values.key))

    def get_key_fields(self):
        """
        Returns the key field value from event
        """
        return self.key_fields

    @classmethod
    def copy(cls, event):
        """
        Copies the SampleEvent object into a new one.
        Args:
            event (SampleEvent): Event object which has to be copied

        Returns:
            Copy of the SampleEvent object
        """
        new_event = cls("", {}, "")
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        new_event.time_values = event.time_values[:]
        new_event.metadata = deepcopy(event.metadata)
        return new_event

    def update_metadata(self, event, metadata, key_fields):
        """
        Processes the syslog formated samples
        Format::

            '***SPLUNK*** source=<source> sourcetype=<sourcetype> \
            field_1       field2        field3 \
            ##value1##    ##value2##   ##value3##'

        Args:
            event (str): event string containing raw syslog data
            metadata (dict): Contains metadata for the event

        Returns:
            Syslog event and the updated metadata
        """
        try:
            if isinstance(event, str) and event.startswith("***SPLUNK***"):
                header,event = event.split("\n", 1)
 
                for meta_field in re.findall(r"[\w]+=[^\s]+", header):
                    field, value = meta_field.split("=")
                    if field == "host":
                        metadata[field] = f"host_{metadata[field]}"
                        key_fields["host"] = list([metadata["host"]])
                    else:
                        metadata[field] = value

            return event, metadata, key_fields

        except IndexError as error:
            LOGGER.error(f"Unexpected data found. Error: {error}")
            raise Exception(error)
