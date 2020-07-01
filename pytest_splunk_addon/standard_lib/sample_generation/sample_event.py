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
    }


class SampleEvent(object):
    """
    This class represents an event which will be ingested in Splunk.
    """

    def __init__(self, event_string, metadata, sample_name):
        """
        init method for the class
        
        Args:
            event_string(str): Sample event string 
            metadata(dict): Dictionary of metadata
            sample_name(str): sample name
        """
        self.event = event_string
        self.key_fields = dict()
        self.metadata = metadata
        self.sample_name = sample_name
        self.host_count = 0
        self.fake = Faker()

    def update(self, new_event):
        """
        This method update the event string

        Args:
            new_event(str): Event string 
        """
        self.event = new_event

    def get_host(self):
        """
        Return the unique host value
        """
        self.host_count += 1
        return "{}_{}_{}".format("host", self.sample_name, str(self.host_count))

    def get_field_host(self, rule):
        """
        Returns unique host value for the key fields src, dest, host, dvc

        Args:
            rule(str): Type of rule either src, host, dest, dvc
        """
        global host_count
        host_count += 1
        return "{}_{}{}".format(rule, "sample_host", host_count)
    
    def get_field_fqdn(self, rule):
        """
        Returns unique fqdn value for the key fields src, dest, host, dvc

        Args:
            rule(str): Type of rule either src, host, dest, dvc
        """
        global fqdn_count
        fqdn_count += 1
        return "{}_{}.{}{}.com".format(rule, "sample_host", "sample_domain", fqdn_count)

    def get_ipv4(self, rule):
        """
        Returns Ipv4 Address as per the rule.

        Args:
            rule(str): Type of rule either src, host, dest, dvc
            If the value is not one of the key field it will return a randomly generated Ipv4 address.
        """
        if rule == "src":
            global src_ipv4
            src_ipv4 += 1
            addr = [int(src_ipv4 / 256) % 256, src_ipv4 % 256]
            return "".join([ip_rules.get(rule)["ipv4"], str(addr[0]), ".", str(addr[1])])
        elif rule == "host":
            global host_ipv4
            host_ipv4 += 1
            return "".join([ip_rules.get(rule)["ipv4"], str(host_ipv4 % 101), ".0"])
        elif rule == "dvc":
            global dvc_ipv4
            dvc_ipv4 += 1
            return "".join([ip_rules.get(rule)["ipv4"], str(dvc_ipv4 % 51), ".0"])
        elif rule == "dest":
            global dest_ipv4
            dest_ipv4 += 1
            addr = [int(dest_ipv4 / 256) % 256, dest_ipv4 % 256]
            return "".join([ip_rules.get(rule)["ipv4"], str(addr[0]), ".", str(addr[1])])
        else:
            return self.fake.ipv4()

    def get_ipv6(self, rule):
        """
        Returns Ipv6 Address as per the rule.

        Args:
            rule(str): Type of rule either src, host, dest, dvc
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
            return self.fake.ipv6()

        hex_count = hex(ipv6)
        non_zero_cnt = len(hex_count[2:])
        addr = "{}{}".format("0"*(16-non_zero_cnt), hex_count[2:])
        return "{}:{}".format(ip_rules.get(rule)["ipv6"],':'.join(addr[i:i+4] for i in range(0, len(addr), 4)))

    def get_token_count(self, token):
        """
        This method find the token count in event

        Args:
            token(str): Token name 
        """
        return len(re.findall(token, self.event))

    def replace_token(self, token, token_values):
        """
        This method replace the token value in event string

        Args:
            token(str): Token name 
            token_values(list/str): Value to be replace in token 
        """
        # TODO: How to handle dependent Values with list of token_values
        if isinstance(token_values, list):
            sample_tokens = re.finditer(token, self.event)
                
            for token_index, token_value in enumerate(token_values):
                self.event = re.sub(
                    next(sample_tokens).group(0), lambda x: str(token_value), self.event, 1, flags=re.MULTILINE
                )
        else:
            self.event = re.sub(
                token, lambda x: str(token_values), self.event, flags=re.MULTILINE
            )

    def register_field_value(self, field, token_values):
        """
        This method register the key value in event instance

        Args:
            field(str): Token field name 
            token_values(list/str): Value to be replace in token 
        """
        if field in key_fields.KEY_FIELDS:
            if isinstance(token_values, list):
                for token_value in token_values:
                    self.key_fields.setdefault(field, []).append(str(token_value))
            else:
                self.key_fields.setdefault(field, []).append(str(token_values))

    def get_key_fields(self):
        """
        Return the key field value from event
        """
        return self.key_fields

    @classmethod
    def copy(cls, event):
        """
        This method is copy the sample event

        Args:
            event(SampleEvent): event class instance
        """
        new_event = cls("", {}, "")
        new_event.__dict__ = event.__dict__.copy()
        new_event.key_fields = event.key_fields.copy()
        new_event.metadata = deepcopy(event.metadata)
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
            metadata_format::
                {
                    "host": "sample_host",
                    "source": "sample_source"
                }
        Args:
            event(str): event string
            metadata(dict): dictionary of metadata
        Returns:
            syslog event and the dictionary of updated metadata
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