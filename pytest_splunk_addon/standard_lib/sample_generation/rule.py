"""
Provides Rules for all possible replacements for tokens.
"""
import csv
import re
import string
import uuid

from collections import namedtuple
from datetime import datetime, timezone
from faker import Faker
from random import uniform, randint, choice
from time import mktime
from .time_parser import time_parse
import os
import random

from . import SampleEvent
import logging
import warnings

LOGGER = logging.getLogger("pytest-splunk-addon")

user_email_count = 0
# user_email_count to generate unique values for
# ["name", "email", "domain_user", "distinquised_name"] in each token

event_host_count = 0
# event_host_count is used to generate unique host for each event in
# case of replacementType = all


def raise_warning(warning_string):
    """
    To raise a pytest user warning along with a log.

    Args:
        warning_string(str): warning string
    """
    LOGGER.warning(warning_string)
    warnings.warn(UserWarning(warning_string))


class Rule:
    """
    Base class for all the rules.

    Args:
        token (dict): Dictionary containing token and its data
        eventgen_params (dict): Eventgen stanzas dictionary
        sample_path (str): Path to the samples directory
    """

    user_header = ["name", "email", "domain_user", "distinquised_name"]
    src_header = ["host", "ipv4", "ipv6", "fqdn"]
    token_value = namedtuple("token_value", ['key', 'value'])

    def __init__(self, token, eventgen_params=None, sample_path=None):
        self.token = token["token"]
        self.replacement = token["replacement"]
        self.replacement_type = token["replacementType"]
        self.field = token.get("field", self.token.strip("#"))
        self.eventgen_params = eventgen_params
        self.sample_path = sample_path
        self.fake = Faker()
        self.file_count = 0

    @classmethod
    def parse_rule(cls, token, eventgen_params, sample_path):
        """
        Returns appropriate Rule object as per replacement type of token.

        Args:
            token (dict): Dictionary containing token and its data
            eventgen_params (dict): Eventgen stanzas dictionary
            sample_path (str): Path to the samples directory
        """
        rule_book = {
            "integer": IntRule,
            "list": ListRule,
            "ipv4": Ipv4Rule,
            "float": FloatRule,
            "ipv6": Ipv6Rule,
            "mac": MacRule,
            "file": FileRule,
            "url": UrlRule,
            "user": UserRule,
            "email": EmailRule,
            "host": HostRule,
            "hex": HexRule,
            "src_port": SrcPortRule,
            "dest_port": DestPortRule,
            "src": SrcRule,
            "dest": DestRule,
            "dvc": DvcRule,
            "guid": GuidRule
        }
        rule_all_support = ["integer", "list", "file"]
        if token.get("replacementType") not in ["static", "all", "random", "timestamp", "mvfile", "file"]:
            raise_warning("Invalid replacementType: '{}' for token:'{}' using 'random' as replacementType".format(token.get("replacementType"), token.get("token")))
            token["replacement"] = "random"
        replacement_type = token["replacementType"]
        replacement = token["replacement"]
        if replacement_type == "static":
            return StaticRule(token)
        elif replacement_type == "timestamp":
            return TimeRule(token, eventgen_params)
        elif replacement_type == "random" or replacement_type == "all":
            for each_rule in rule_book:
                if replacement.lower().startswith(each_rule):
                    if replacement_type == "all" and each_rule not in rule_all_support:
                        token["replacementType"] = "random"
                        LOGGER.warning("replacement_type=all is not supported for {} rule applied to {} token.".format(each_rule, token.get("token")))
                        warnings.warn(UserWarning("replacement_type=all is not supported for {} rule applied to {} token.".format(each_rule, token.get("token"))))
                    return rule_book[each_rule](token, sample_path=sample_path)
        elif replacement_type == "file" or replacement_type == "mvfile":
            return FileRule(token, sample_path=sample_path)


    def apply(self, events):
        """
        Replaces the token with appropriate values as per rules mapped with the tokens in the event.
        For replacement_type = all it will generate an event for each replacement value.
        i.e. integer[1:50] => will generate 50 events

        Args:
            events (list): List of events(SampleEvent)
        """
        new_events = []
        for each_event in events:
            token_count = each_event.get_token_count(self.token)
            token_values = list(self.replace(each_event, token_count))
            if token_count > 0:
                if self.replacement_type == "all":
                    # NOTE: If replacement_type is all and same token is more than
                    #       one time in event then replace all tokens with same
                    #       value in that event
                    for each_token_value in token_values:
                        new_event = SampleEvent.copy(each_event)
                        global event_host_count
                        event_host_count += 1
                        new_event.metadata["host"] = "{}_{}".format(
                            each_event.sample_name, event_host_count
                            )
                        new_event.replace_token(self.token, each_token_value.value)
                        new_event.register_field_value(
                            self.field, each_token_value
                        )
                        new_events.append(new_event)
                else:
                    each_event.replace_token(
                        self.token,
                        token_values
                    )

                    if not (
                        each_event.metadata.get(
                                'timestamp_type') != 'event'
                            and self.field == "_time"):
                        each_event.register_field_value(self.field, token_values)
                    new_events.append(each_event)
            else:
                new_events.append(each_event)
        return new_events

    def get_lookup_value(self, sample, key, headers, value_list):
        """
        Common method to read csv and get a random row.

        Args:
            sample (SampleEvent): Instance containing event info
            key (str): fieldname i.e. host, src, user, dvc etc
            headers (list): Headers of csv file in list format
            value_list (list): list of replacement values mentioned in configuration file.

        Returns:
            index_list (list): list of mapped columns(int) as per value_list
            csv_row (list): list of replacement values for the rule.
        """
        csv_row = []
        global user_email_count
        user_email_count += 1
        name = "user{}".format(user_email_count)
        email = "user{}@email.com".format(user_email_count)
        domain_user = r"sample_domain.com\user{}".format(user_email_count)
        distinguished_name = "CN=user{}".format(user_email_count)
        csv_row.extend([name, email, domain_user, distinguished_name])
        index_list = [
            i
            for i, item in enumerate(headers)
            if item in value_list
        ]
        if (
            hasattr(sample, "replacement_map")
            and key in sample.replacement_map
        ):
            sample.replacement_map[key].append(csv_row)
        else:
            sample.__setattr__("replacement_map", {key: [csv_row]})
        return index_list, csv_row

    def get_rule_replacement_values(self, sample, value_list, rule):
        """
        Common method for replacement values of
        SrcRule, Destrule, DvcRule, HostRule.

        Args:
            sample (SampleEvent): Instance containing event info
            value_list (list): list of replacement values mentioned in configuration file.
            rule (str): fieldname i.e. host, src, user, dvc etc

        Returns:
            index_list (list): list of mapped columns(int) as per value_list
            csv_row (list): list of replacement values for the rule.
        """
        csv_row = []
        for each in value_list:
            if each == "host":
                csv_row.append(sample.get_field_host(rule))
            elif each == "ipv4":
                csv_row.append(sample.get_ipv4(rule))
            elif each == "ipv6":
                csv_row.append(sample.get_ipv6(rule))
            elif each == "fqdn":
                csv_row.append(sample.get_field_fqdn(rule))
        return csv_row

    @staticmethod
    def clean_rules():
        global event_host_count
        event_host_count = 0

class IntRule(Rule):
    """
    IntRule 
    """
    def replace(self, sample, token_count):
        """
        Yields a random int between the range mentioned in token.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        limits_match = re.match(
            r"[Ii]nteger\[(-?\d+):(-?\d+)\]", self.replacement
        )
        if limits_match:
            lower_limit, upper_limit = limits_match.groups() 
            if self.replacement_type == "random":
                for _ in range(token_count):
                    yield self.token_value(
                        *([randint(int(lower_limit), int(upper_limit))]*2)
                        )
            else:
                for each_int in range(int(lower_limit), int(upper_limit)):
                    yield self.token_value(
                        *([str(each_int)]*2)
                        )
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try integer[0:10]".format(self.replacement, sample.sample_name))


class FloatRule(Rule):
    """
    FloatRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random float no. between the range mentioned in token.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        float_match = re.match(
            r"[Ff]loat\[(-?[\d\.]+):(-?[\d\.]+)\]", self.replacement
        )
        if float_match:
            lower_limit, upper_limit = float_match.groups()
            precision = re.search("\[-?\d+\.?(\d*):", self.replacement).group(1)
            if not precision:
                precision = str(1)
            for _ in range(token_count):
                yield self.token_value(
                        *([round(
                            uniform(
                                float(lower_limit),
                                float(upper_limit)
                                ),
                            len(precision),
                            )
                        ]*2)
                        )
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n i.e float[0.00:70.00]".format(self.replacement, sample.sample_name))


class ListRule(Rule):
    """
    ListRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random value from the list mentioned in token.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(
            r"[lL]ist(\[.*?\])", self.replacement
        )
        if value_match:    
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)

            if self.replacement_type == "random":
                for _ in range(token_count):
                    yield self.token_value(*([str(choice(value_list))]*2))
            else:
                for each_value in value_list:
                    yield self.token_value(*([str(each_value)]*2))
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try  list['value1','value2']".format(self.replacement, sample.sample_name))


class StaticRule(Rule):
    """
    StaticRule
    """
    def replace(self, sample, token_count):
        """
        Yields the static value mentioned in token.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(*([self.replacement]*2))


class FileRule(Rule):
    """
    FileRule
    """
    every_replacement_types = []
    def replace(self, sample, token_count):
        """
        Yields the values of token by reading files.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        relative_file_path, index = self.get_file_path()

        if index:
            try:
                index = int(index)
                for i in self.indexed_sample_file(sample, relative_file_path, index, token_count):
                    yield self.token_value(*([i]*2))   

            except ValueError:
                for i in self.lookupfile(sample, relative_file_path, index, token_count):
                    yield self.token_value(*([i]*2))
                
        else:
            try:
                with open(relative_file_path) as f:
                    txt = f.read()
                    lines = [each.strip() for each in txt.split("\n") if each]
                    if self.replacement_type == 'random' or self.replacement_type == 'file':
                        for _ in range(token_count):
                            yield self.token_value(*([choice(lines)]*2))
                    elif self.replacement_type == 'all':
                        for each_value in lines:
                            yield self.token_value(*([each_value]*2))
            except IOError:
                LOGGER.warning("File not found : {}".format(relative_file_path))

    def get_file_path(self):
        """
        Returns the relative sample file path and index value
        """
        if self.replacement.startswith("file" or "File"):
            sample_file_path = re.match(
                    r"[fF]ile\[(.*?)\]", self.replacement
                ).group(1)
        else:
            sample_file_path = self.replacement

        sample_file_path = sample_file_path.replace("/", os.sep)
        relative_file_path = self.sample_path.split(f"{os.sep}samples")[0]
        try:
            # get the relative_file_path and index value from filepath
            # mentioned in the token if the filepath matches the pattern
            # pattern like: <directory_path>/apps/<addon_name>/<file_path> or
            # pattern like:
            # <directory_path>/apps/<addon_name>/<file_path>:<index>
            _, splitter, file_path = re.search(
                r"(.*)(\\?\/?apps\\?\/?[a-zA-Z-_0-9.*]+\\?\/?)(.*)",
                sample_file_path
                ).groups()
            relative_file_path = os.path.join(
                relative_file_path,
                file_path.split(":")[0]
                )
            file_index = file_path.split(":")
            index = (file_index[1] if len(file_index) > 1 else None)

            if not os.path.isfile(relative_file_path):
                raise AttributeError

        except AttributeError:
            # get the relative_file_path and index value from filepath
            # mentioned in the token if the filepath matches the pattern
            # pattern like: <directory_path>/<file_path> or
            # pattern like: <directory_path>/<file_path>:<index>
            file_path = sample_file_path
            index = None
            if file_path.count(":") > 0:
                file_index = file_path.rsplit(":", 1)
                index = (file_index[1] if len(file_index) > 1 else None)
                file_path = file_path.rsplit(":", 1)[0]
            relative_file_path = file_path
        
        return relative_file_path, index

    def indexed_sample_file(self, sample, file_path, index, token_count):
        """
        Yields the column value of token by reading files.

        Args:
            sample (SampleEvent): Instance containing event info
            file_path (str): path of the file mentioned in token.
            index (int): index value mentioned in file_path i.e. <file_path>:<index>
            token_count (int): No. of token in sample event where rule is applicable
        """
        all_data = []
        try:
            with open(file_path, 'r') as _file:
                selected_sample_lines = _file.readlines()
                for i in selected_sample_lines:
                    if i.strip() != '':
                        all_data.append(i.strip())
            
                if (
                    hasattr(sample, "replacement_map")
                    and file_path in sample.replacement_map
                ):
                    index = int(index)
                    file_values = sample.replacement_map[file_path]["data"][self.file_count].split(',')
                    if sample.replacement_map[file_path].get("find_all"):
                        # if condition to increase the line no. of sample data
                        # when the replacement_type = all provided in token for indexed file
                        if self.file_count == len(all_data)-1:
                            # reset the file count when count reaches to pick value corresponding to 
                            # length of the sample data
                            self.file_count = 0
                        else:
                            self.file_count += 1
                    for _ in range(token_count):
                        yield file_values[index-1]
                else:
                    if self.replacement_type == 'all':
                        sample.__setattr__("replacement_map", {file_path: {"data":all_data, "find_all":True}})
                        for i in all_data:
                            file_values = i.split(',')
                            yield file_values[index-1]
                    else:
                        random_line = random.randint(0, len(all_data)-1)
                        if hasattr(sample, "replacement_map"):
                            sample.replacement_map.update({file_path: {"data":[all_data[random_line]]}})
                        else:
                            sample.__setattr__("replacement_map", {file_path: {"data":[all_data[random_line]]}})
                        file_values = all_data[random_line].split(',')
                        for _ in range(token_count):
                            yield file_values[index-1]
        except IndexError:
            LOGGER.error(
                f"Index for column {index} in replacement"
                f"file {file_path} is out of bounds"
                )
        except IOError:
            LOGGER.warning("File not found : {}".format(file_path))

    def lookupfile(self, sample, file_path, index, token_count):
        """
        Yields the column value of token by reading files.

        Args:
            sample (SampleEvent): Instance containing event info
            file_path (str): path of the file mentioned in token.
            index (int): index value mentioned in file_path i.e. <file_path>:<index>
            token_count (int): No. of token in sample event where rule is applicable
        """
        all_data = []
        header = ''
        try:
            with open(file_path, 'r') as _file:
                header = next(_file)
                for line in _file:
                    if line.strip() != '':
                        all_data.append(line.strip())
            for _ in range(token_count):
                if (
                    hasattr(sample, "replacement_map")
                    and file_path in sample.replacement_map
                ):
                    index = sample.replacement_map[file_path][0].strip().split(',').index(index)
                    file_values = sample.replacement_map[file_path][1].split(',')
                    for _ in range(token_count):
                        yield file_values[index]
                else:
                    if (
                        hasattr(sample, "replacement_map")
                        and file_path in sample.replacement_map
                    ):
                        sample.replacement_map[file_path].append(all_data)
                    else:
                        if self.replacement_type == 'random' or self.replacement_type == 'file':
                            self.file_count = random.randint(0, len(all_data)-1)
                            sample.__setattr__("replacement_map", {file_path: [header, all_data[self.file_count]]})
                            index = header.strip().split(',').index(index)
                            file_values = all_data[self.file_count].split(',')
                            for _ in range(token_count):
                                yield file_values[index]
                        else:
                            LOGGER.warning(f"'replacement_type = {self.replacement_type}' is not supported for the lookup files. Please use 'random' or 'file'")
                            yield self.token
        except ValueError:
            LOGGER.error("Column '%s' is not present replacement file '%s'" % (index, file_path))
        except IOError:
            LOGGER.warning("File not found : {}".format(file_path))


class TimeRule(Rule):

    def replace(self, sample, token_count):
        """
        Returns time according to the parameters specified in the input.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        earliest = self.eventgen_params.get("earliest")
        latest = self.eventgen_params.get("latest")
        timezone_time = self.eventgen_params.get("timezone",'0000')
        random_time = datetime.utcnow()
        time_parser = time_parse()
        time_delta = datetime.now().timestamp() - datetime.utcnow().timestamp()

        if earliest != "now" and earliest is not None:

            earliest_match = re.match(
                r"([+-])(\d{1,})(.*)", earliest
            )
            if earliest_match:
                sign, num, unit = earliest_match.groups()
                earliest = time_parser.convert_to_time(sign, num, unit)
            else:
                raise_warning("Invalid value found in earliest: '{}' for stanza '{}'. using earliest = now".format(earliest, sample.sample_name))
                earliest = datetime.utcnow()
        else:
            earliest = datetime.utcnow()

        if latest != "now" and latest is not None:

            latest_match = re.match(r"([+-])(\d{1,})(.*)", latest)
            if latest_match:
                sign, num, unit = latest_match.groups()
                latest = time_parser.convert_to_time(sign, num, unit)
            else:
                raise_warning("Invalid value found in latest: '{}' for stanza '{}'. using latest = now".format(latest, sample.sample_name))
                latest = datetime.utcnow()
        else:
            latest = datetime.utcnow()

        earliest_in_epoch = mktime(earliest.timetuple())
        latest_in_epoch = mktime(latest.timetuple())

        if earliest_in_epoch > latest_in_epoch:
            LOGGER.info("Latest time is earlier than earliest time.")
            yield self.token
        for _ in range(token_count):
            random_time = datetime.fromtimestamp(
                randint(earliest_in_epoch, latest_in_epoch)
            )
            if timezone_time in ['local', '"local"', "'local'"]:
                random_time = random_time.replace(
                    tzinfo=timezone.utc).astimezone(tz=None)

            elif timezone_time and timezone_time.strip("'").strip('"') != r"0000":
                random_time = time_parser.get_timezone_time(
                    random_time, timezone_time
                )

            if r"%s" == self.replacement.strip("'").strip('"'):
                time_in_sec = self.replacement.replace(
                    r"%s",
                    str(int(mktime(random_time.timetuple())))
                    )
                yield self.token_value(float(time_in_sec), time_in_sec)

            else:
                if timezone_time not in (None, '0000'):
                    modified_random_time = time_parser.get_timezone_time(
                        random_time, self.invert_timezone(timezone_time)
                    )
                else:
                    modified_random_time = random_time
                yield self.token_value(
                    float(mktime(modified_random_time.timetuple()))
                    + time_delta,
                    random_time.strftime(
                        self.replacement.replace(r"%e", r"%d")
                    ),
                )

    def invert_timezone(self, timezone_time):
        if timezone_time == '0000':
            return '0000'
        elif timezone_time[0] == '-':
            return '+'+timezone_time[-4:]
        elif timezone_time[0] == '+':
            return '-'+timezone_time[-4:]
        else:
            raise Exception("Invalid timezone value found.")


class Ipv4Rule(Rule):
    """
    Ipv4Rule
    """
    def replace(self, sample, token_count):
        """
        Yields a random ipv4 address.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(*([self.fake.ipv4()]*2))


class Ipv6Rule(Rule):
    """
    Ipv6Rule
    """
    def replace(self, sample, token_count):
        """
        Yields a random ipv6 address

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(*([self.fake.ipv6()]*2))


class MacRule(Rule):
    """
    MacRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random mac address

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(*([self.fake.mac_address()]*2))


class GuidRule(Rule):
    """
    GuidRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random guid.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(*([str(uuid.uuid4())]*2))


class UserRule(Rule):
    """
    UserRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random user replacement value from the list of values mentioned in token.
        Possible values: ["name", "email", "domain_user", "distinquised_name"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(
            r"[uU]ser(\[.*?\])", self.replacement
        )
        if value_match:
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)

            for i in range(token_count):
                if (
                    hasattr(sample, "replacement_map")
                    and "email" in sample.replacement_map
                    and i < len(sample.replacement_map["email"])
                ):
                    index_list = [
                        i
                        for i, item in enumerate(self.user_header)
                        if item in value_list
                    ]
                    csv_rows = sample.replacement_map["email"]
                    yield self.token_value(
                        *([csv_rows[i][choice(index_list)]]*2)
                        )
                else:
                    index_list, csv_row = self.get_lookup_value(
                        sample,
                        "user",
                        self.user_header,
                        value_list,
                    )
                    if index_list:
                        yield self.token_value(*([csv_row[choice(index_list)]]*2))
                    else:
                        raise_warning("Invalid Value: '{}' in stanza '{}'.\n Accepted values: ['name','email','domain_name','distinquised_name']".format(self.replacement, sample.sample_name))
        else:
            raise_warning("Unidentified format: '{}' in stanza '{}'.\n Try  user['name','email','domain_name','distinquised_name']".format(self.replacement, sample.sample_name))


class EmailRule(Rule):
    """
    EmailRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random email from lookups\\user_email.csv file.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """

        for i in range(token_count):
            if (
                hasattr(sample, "replacement_map")
                and "user" in sample.replacement_map
                and i < len(sample.replacement_map["user"])
            ):
                csv_rows = sample.replacement_map["user"]
                yield self.token_value(
                    *([csv_rows[i][self.user_header.index("email")]]*2)
                    )
            else:
                index_list, csv_row = self.get_lookup_value(
                    sample,
                    "email",
                    self.user_header,
                    ["email"],
                )
                yield self.token_value(*([csv_row[self.user_header.index("email")]]*2))

class UrlRule(Rule):
    """
    UrlRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random url replacement value from the list
        of values mentioned in token.

        Possible values: ["ip_host", "fqdn_host", "path", "query", "protocol", "full"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        replace_token = True
        value_match = re.match(r"[uU]rl(\[.*?\])", self.replacement)
        if value_match:    
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)
            for each in value_list:
                if each not in ["ip_host", "fqdn_host", "path", "query", "protocol", "full"]:
                    raise_warning('Invalid Value for url: "{}" for replacement {} in stanza "{}".\n Accepted values: ["ip_host", "fqdn_host", "path", "query", "protocol"]'.format(each, self.replacement, sample.sample_name))
                    replace_token = False
            if replace_token:
                for _ in range(token_count):
                    if bool(
                        set(["ip_host", "fqdn_host", "full"]).intersection(value_list)
                    ):
                        url = ""
                        domain_name = []
                        if bool(set(["full", "protocol"]).intersection(value_list)):
                            url = url + choice(["http://", "https://"])
                        if bool(set(["full", "ip_host"]).intersection(value_list)):
                            domain_name.append(sample.get_ipv4("url"))
                        if bool(set(["full", "fqdn_host"]).intersection(value_list)):
                            domain_name.append(self.fake.hostname())
                        url = url + choice(domain_name)
                    else:
                        url = self.fake.url()

                    if bool(set(["full", "path"]).intersection(value_list)):
                        url = (
                            url
                            + "/"
                            + choice(
                                [
                                    self.fake.uri_path(),
                                    self.fake.uri_page() + self.fake.uri_extension(),
                                ]
                            )
                        )
                    
                    if bool(set(["full", "query"]).intersection(value_list)):
                        url = url + self.generate_url_query_params()
                    yield self.token_value(*([str(url)]*2))
        else:
            raise_warning('Unidentified format: "{}" in stanza "{}".\n Expected values: ["ip_host", "fqdn_host", "path", "query", "protocol", "full"]'.format(self.replacement, sample.sample_name))

    def generate_url_query_params(self):
        """
        Generates random query params for url
    
        Returns:
            Return the query param string
        """
        url_params = "?"
        for _ in range(randint(1, 4)):
            field = "".join(
                choice(string.ascii_lowercase) for _ in range(randint(2, 5))
            )
            value = "".join(
                choice(string.ascii_lowercase + string.digits)
                for _ in range(randint(2, 5))
            )
            url_params = url_params + field + "=" + value + "&"
        return url_params[:-1]


class DestRule(Rule):
    """
    DestRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random dest replacement value from the list
        of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(
            r"[dD]est(\[.*?\])", self.replacement
        )
        if value_match:
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)

            for _ in range(token_count):
                csv_row = self.get_rule_replacement_values(
                    sample,
                    value_list,
                    rule="dest"
                )
                if csv_row:
                    yield self.token_value(*([choice(csv_row)]*2))
                else:
                    raise_warning("Invalid Value: '{}' in stanza '{}'.\n Accepted values: ['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))
        else:    
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try  dest['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))


class SrcPortRule(Rule):
    """
    SrcPortRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random port value from the range 4000-5000

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        for _ in range(token_count):
            yield self.token_value(
                *([randint(4000, 5000)]*2)
                )


class DvcRule(Rule):
    """
    DvcRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random dvc replacement value from the list
        of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(r"[dD]vc(\[.*?\])", self.replacement)
        if value_match:
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)
            for _ in range(token_count):
                csv_row = self.get_rule_replacement_values(
                    sample,
                    value_list,
                    rule="dvc"
                    )
                if csv_row:
                    yield self.token_value(*([choice(csv_row)]*2))
                else:
                    raise_warning("Invalid Value: '{}' in stanza '{}'.\n Accepted values: ['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try  dvc['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))


class SrcRule(Rule):
    """
    SrcRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random src replacement value from the list
        of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(r"[sS]rc(\[.*?\])", self.replacement)
        if value_match:
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)
            for _ in range(token_count):
                csv_row = self.get_rule_replacement_values(
                    sample,
                    value_list,
                    rule="src"
                    )
                if csv_row:
                    yield self.token_value(*([choice(csv_row)]*2))
                else:
                    raise_warning("Invalid Value: '{}' in stanza '{}'.\n Accepted values: ['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try  src['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))


class DestPortRule(Rule):
    """
    DestPortRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random port value from [80, 443, 25, 22, 21]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        DEST_PORT = [80, 443, 25, 22, 21]
        for _ in range(token_count):
            yield self.token_value(*([choice(DEST_PORT)]*2))


class HostRule(Rule):
    """
    HostRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random host replacement value from the list
        of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        value_match = re.match(
            r"[hH]ost(\[.*?\])", self.replacement
        )
        if value_match:
            value_list_str = value_match.group(1)
            value_list = eval(value_list_str)
            for _ in range(token_count):
                csv_row = self.get_rule_replacement_values(
                    sample, value_list, rule="host"
                )
                if csv_row:
                    if "host" in value_list:
                        if sample.metadata.get("input_type") in [
                            "modinput",
                            "windows_input",
                            "syslog_tcp",
                            "syslog_udp",
                        ]:
                            csv_row[0] = sample.metadata.get("host")
                        elif sample.metadata.get("input_type") in [
                            "file_monitor",
                            "scripted_input",
                            "default",
                        ]:
                            csv_row[0] = sample.get_host()
                    yield self.token_value(*([choice(csv_row)]*2))
                else:
                    raise_warning("Invalid Value: '{}' in stanza '{}'.\n Accepted values: ['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))
        else:
            raise_warning("Non-supported format: '{}' in stanza '{}'.\n Try  host['host','ipv4','ipv6','fqdn']".format(self.replacement, sample.sample_name))


class HexRule(Rule):
    """
    HexRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random hex value.

        Args:
            sample (SampleEvent): Instance containing event info
            token_count (int): No. of token in sample event where rule is applicable
        """
        hex_match =  re.match(r"[Hh]ex\((.*?)\)", self.replacement)
        if hex_match:
            hex_range = hex_match.group(1)
            if hex_range.isnumeric():
                hex_digits = [
                    "0",
                    "1",
                    "2",
                    "3",
                    "4",
                    "5",
                    "6",
                    "7",
                    "8",
                    "9",
                    "a",
                    "b",
                    "c",
                    "d",
                    "e",
                    "f",
                ]
                hex_array = []
                for _ in range(token_count):
                    for i in range(int(hex_range)):
                        hex_array.append(hex_digits[randint(0, 15)])
                    hex_value = "".join(hex_array)
                    yield self.token_value(*([hex_value]*2))
            else:
                raise_warning("Invalid Value: '{}' in stanza '{}'.\n '{}' is not an integer value".format(self.replacement, sample.sample_name, hex_range))
        else:
            raise_warning("Invalid Hex value: '{}' in stanza '{}'. Try hex(<i>) where i is an integer".format(self.replacement, sample.sample_name))
