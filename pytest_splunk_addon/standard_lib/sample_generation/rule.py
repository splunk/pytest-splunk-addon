import csv
import re
import string
import uuid
from datetime import datetime
from faker import Faker
from random import uniform, randint, choice
from time import strftime, mktime
from .time_parser import time_parse
import os

from . import SampleEvent
import logging
import warnings

LOGGER = logging.getLogger("pytest-splunk-addon")

user_email_count = 0
# user_email_count to generate unique values for ["name", "email", "domain_user", "distinquised_name"] in each token 

event_host_count = 0
# event_host_count is used to generate unique host for each event in 
# case of replacementType = all 

class Rule:
    """
    Base class for all the rules.
    """
    user_header = ["name", "email", "domain_user", "distinquised_name"]
    src_header = ["host", "ipv4", "ipv6", "fqdn"]

    def __init__(self, token, eventgen_params=None, sample_path=None):
        self.token = token["token"]
        self.replacement = token["replacement"]
        self.replacement_type = token["replacementType"]
        self.field = token.get("field", self.token.strip("#"))
        self.eventgen_params = eventgen_params
        self.sample_path = sample_path
        self.fake = Faker()

    @classmethod
    def parse_rule(cls, token, eventgen_params, sample_path):
        """
        Returns appropriate Rule class object as per replacement type of token.

        Args:
            token(dict): represents a single token object.
            eventgen_params(dict): Dict object of the common params for each stanza.
            sample_path(str): Path to the samples directory.
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

        replacement_type = token["replacementType"]
        replacement = token["replacement"]
        if replacement_type == "static":
            return StaticRule(token)
        elif replacement_type == "timestamp":
            return TimeRule(token, eventgen_params)
        elif replacement_type == "random" or replacement_type == "all":
            for each_rule in rule_book:
                if replacement.lower().startswith(each_rule):
                    return rule_book[each_rule](token, sample_path=sample_path)
        elif replacement_type == "file" or replacement_type == "mvfile":
            return FileRule(token, sample_path=sample_path)

        LOGGER.error("No Rule Found for token = {}, with replacement = {} and replacement_type = {}!".format(token["token"], replacement, replacement_type))
        warnings.warn(UserWarning("No Rule Found for token = {}, with replacement = {} and replacement_type = {}!".format(token["token"], replacement, replacement_type)))

    def apply(self, events):
        """
        Replaces the token with appropriate values as per rules mapped with the token for the event.
        For replacement_type = all it will generate an event for each replacement value.
        i.e. integer[1:50] => will generate 50 events

        Args:
            events(list): List of event(SampleEvent)
        """
        new_events = []
        for each_event in events:
            token_count = each_event.get_token_count(self.token)
            token_values = list(self.replace(each_event, token_count))
            if self.replacement_type == "all" and token_count > 0:
                # NOTE: If replacement_type is all and same token is more than
                #       one time in event then replace all tokens with same
                #       value in that event
                for each_token_value in token_values:
                    new_event = SampleEvent.copy(each_event)
                    global event_host_count
                    event_host_count += 1
                    new_event.metadata["host"]  = "{}_{}".format(each_event.sample_name, event_host_count)
                    new_event.replace_token(self.token, each_token_value)
                    new_event.register_field_value(
                        self.field, each_token_value
                    )
                    new_events.append(new_event)
            else:
                each_event.replace_token(self.token, token_values)
                each_event.register_field_value(self.field, token_values)
                new_events.append(each_event)
        return new_events

    def get_lookup_value(self, sample, key, headers, value_list):
        """
        Common method to read csv and get a random row.

        Args:
            sample(object): Instance of SampleEvent class.
            key(str): fieldname i.e. host, src, user, dvc etc
            headers(list): Headers of csv file in list format.
            value_list(list): list of replacement values mentioned in configuration file.

        Returns:
            index_list(list): list of mapped columns(int) as per value_list
            csv_row(list): list of replacement values for the rule.
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
        Common method for replacement values of SrcRule, Destrule, DvcRule, HostRule.

        Args:
            sample(object): Instance of SampleEvent class.
            value_list(list): list of replacement values mentioned in configuration file.
            rule(str): fieldname i.e. host, src, user, dvc etc

        Returns:
            index_list(list): list of mapped columns(int) as per value_list
            csv_row(list): list of replacement values for the rule.
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


class IntRule(Rule):
    """
    IntRule 
    """
    def replace(self, sample, token_count):
        """
        Yields a random int between the range mentioned in token.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        lower_limit, upper_limit = re.match(
            r"[Ii]nteger\[(\d+):(\d+)\]", self.replacement
        ).groups()
        if self.replacement_type == "random":
            for _ in range(token_count):
                yield randint(int(lower_limit), int(upper_limit))
        else:
            for each_int in range(int(lower_limit), int(upper_limit)):
                yield str(each_int)


class FloatRule(Rule):
    """
    FloatRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random float no. between the range mentioned in token.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        lower_limit, upper_limit = re.match(
            r"[Ff]loat\[([\d\.]+):([\d\.]+)\]", self.replacement
        ).groups()
        precision = re.search("\[\d+\.?(\d*):", self.replacement).group(1)
        if not precision:
            precision = str(1)
        for _ in range(token_count):
            yield round(
                uniform(float(lower_limit), float(upper_limit)),
                len(precision),
            )


class ListRule(Rule):
    """
    ListRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random value from the list mentioned in token.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(
            r"[lL]ist(\[.*?\])", self.replacement
        ).group(1)
        value_list = eval(value_list_str)

        if self.replacement_type == "random":
            for _ in range(token_count):
                yield str(choice(value_list))
        else:
            for each_value in value_list:
                yield str(each_value)


class StaticRule(Rule):
    """
    StaticRule
    """
    def replace(self, sample, token_count):
        """
        Yields the static value mentioned in token.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield self.replacement


class FileRule(Rule):
    """
    FileRule
    """
    def replace(self, sample, token_count):
        """
        Yields the values of token by reading files.
        
        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
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
            # get the relative_file_path and index value from filepath mentioned in the token if the filepath matches the pattern
            # pattern like: <directory_path>/apps/<addon_name>/<file_path>  or
            # pattern like: <directory_path>/apps/<addon_name>/<file_path>:<index>
            _, splitter, file_path = re.search(r"(.*)(\\?\/?apps\\?\/?[a-zA-Z-_0-9.*]+\\?\/?)(.*)", sample_file_path).groups()
            relative_file_path = os.path.join(relative_file_path, file_path.split(":")[0])
            file_index = file_path.split(":")
            index = (file_index[1] if len(file_index)>1 else None)
            if not os.path.isfile(relative_file_path):
                raise AttributeError
        except AttributeError:
            # get the relative_file_path and index value from filepath mentioned in the token if the filepath matches the pattern 
            # pattern like: <directory_path>/<file_path>  or
            # pattern like: <directory_path>/<file_path>:<index>
            file_path = sample_file_path
            index = None
            if file_path.count(":") > 0:
                file_index = file_path.rsplit(":", 1)
                index = (file_index[1] if len(file_index)>1 else None)
                file_path = file_path.rsplit(":", 1)[0]
            relative_file_path = file_path

        if self.replacement_type == 'random':
            # yield random value for the token by reading sample file
            try:
                if index:
                    try:
                        index = int(index)
                        yield from self.indexed_sample_file(relative_file_path, index, token_count)
                    except ValueError:
                        yield from self.lookupfile(relative_file_path, index, token_count)
                else:
                    with open(relative_file_path) as f:
                        txt = f.read()
                        lines = [each for each in txt.split("\n") if each]
                        for _ in range(token_count):
                            yield choice(lines)
            except IOError as e:
                LOGGER.warning("File not found : {}".format(relative_file_path))
        elif self.replacement_type == 'all':
            # yield all values present in sample file for the token by reading sample file
            # it will not generate the value for indexed files
            if index:
                LOGGER.error(f"replacement_type 'all' is not supported for indexd file '{os.path.basename(file_path)}'")
                yield self.token
            else:
                with open(relative_file_path) as f: 
                    txt = f.read()
                    for each_value in txt.split("\n"):
                        yield each_value
        elif self.replacement_type == 'file':
            # yield random value for the token with indexed sample file by reading sample file
            # yield all values present in sample file for the token by reading sample file
            try:
                if index:
                    try:
                        index = int(index)
                        yield from self.indexed_sample_file(relative_file_path, index, token_count)
                    except ValueError:
                        yield from self.lookupfile(relative_file_path, index, token_count)
                else:
                    with open(relative_file_path) as f:
                        txt = f.read()
                        for each_value in txt.split("\n"):
                            yield each_value
            except IOError:
                LOGGER.warn("File not found : {}".format(relative_file_path))

    def indexed_sample_file(self, file_path, index, token_count):
        """
        Yields the column value of token by reading files.
        
        Args:
            file_path: path of the file mentioned in token.
            index: index value mentioned in file_path i.e. <file_path>:<index>
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        try:
            with open(file_path, 'r') as f:
                output = []
                for line in f:
                    cells = line.split(",")
                    output.append((cells[index-1].strip("\n")))
                for _ in range(token_count):
                    yield choice(output)
        except IndexError:
            LOGGER.error("Index for column '%s' in replacement file '%s' is out of bounds" % (index, file_path))
        except IOError:
            raise IOError

    def lookupfile(self, file_path, index, token_count):
        """
        Yields the column value of token by reading files.
        
        Args:
            file_path: path of the file mentioned in token.
            index: index value mentioned in file_path i.e. <file_path>:<index>
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        try:
            with open(file_path, 'r') as f:
                output = []
                data = csv.DictReader(f)
                try:
                    for row in data:
                        for col in [index]:
                            output.append(row[col])
                    for _ in range(token_count):
                        yield choice(output)
                except KeyError as e:
                    LOGGER.error("Column '%s' is not present replacement file '%s'" % (index, file_path))
        except IOError:
            raise IOError


class TimeRule(Rule):
    def replace(self, sample, token_count):
        """
        Args :
            sample_raw - sample event to be updated as per replacement for token.
            earliest - splunktime formated time.
            latest - splunktime formated time.
            timezone - time zone according to which time is to be generated

        returns :
            random time according to the parameters specified in the input.
        """
        earliest = self.eventgen_params.get("earliest")
        latest = self.eventgen_params.get("latest")
        timezone = self.eventgen_params.get("timezone")
        random_time = datetime.now()
        time_parser = time_parse()

        if earliest != "now" and earliest is not None:
            sign, num, unit = re.match(
                r"([+-])(\d{1,})(.*)", earliest
            ).groups()
            earliest = time_parser.convert_to_time(sign, num, unit)
        else:
            earliest = datetime.now()

        if latest != "now" and latest is not None:
            sign, num, unit = re.match(r"([+-])(\d{1,})(.*)", latest).groups()
            latest = time_parser.convert_to_time(sign, num, unit)
        else:
            latest = datetime.now()

        earliest_in_epoch = mktime(earliest.timetuple())
        latest_in_epoch = mktime(latest.timetuple())

        if earliest_in_epoch > latest_in_epoch:
            LOGGER.info("Latest time is earlier than earliest time.")
            yield self.token
        for _ in range(token_count):
            random_time = datetime.fromtimestamp(
                randint(earliest_in_epoch, latest_in_epoch)
            )
            if timezone != "'local'" and timezone is not None:
                sign, hrs, mins = re.match(
                    r"([+-])(\d\d)(\d\d)", timezone
                ).groups()
                random_time = time_parser.get_timezone_time(
                    random_time, sign, hrs, mins
                )

            if r"%s" in self.replacement:
                yield str(
                    self.replacement.replace(
                        r"%s", str(int(random_time.strftime("%Y%m%d%H%M%S")))
                    )
                )

            elif r"%e" in self.replacement:
                yield random_time.strftime(self.replacement.replace(r'%e', r'%d'))
            else:
                yield random_time.strftime(self.replacement)


class Ipv4Rule(Rule):
    """
    Ipv4Rule
    """
    def replace(self, sample, token_count):
        """
        Yields a random ipv4 address.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield self.fake.ipv4()


class Ipv6Rule(Rule):
    """
    Ipv6Rule
    """
    def replace(self, sample, token_count):
        """
        Yields a random ipv6 address

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield self.fake.ipv6()


class MacRule(Rule):
    """
    MacRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random mac address

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield self.fake.mac_address()


class GuidRule(Rule):
    """
    GuidRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random guid.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield str(uuid.uuid4())


class UserRule(Rule):
    """
    UserRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random user replacement value from the list of values mentioned in token.
        Possible values: ["name","email","domain_user","distinquised_name"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(
            r"[uU]ser(\[.*?\])", self.replacement
        ).group(1)
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
                yield csv_rows[i][choice(index_list)]
            else:
                index_list, csv_row = self.get_lookup_value(
                    sample,
                    "user",
                    self.user_header,
                    value_list,
                )
                yield csv_row[choice(index_list)]


class EmailRule(Rule):
    """
    EmailRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random email from the lookups\\user_email.csv.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """

        for i in range(token_count):
            if (
                hasattr(sample, "replacement_map")
                and "user" in sample.replacement_map
                and i < len(sample.replacement_map["user"])
            ):
                csv_rows = sample.replacement_map["user"]
                yield csv_rows[i][self.user_header.index("email")]
            else:
                index_list, csv_row = self.get_lookup_value(
                    sample,
                    "email",
                    self.user_header,
                    ["email"],
                )
                yield csv_row[choice(index_list)]


class UrlRule(Rule):
    """
    UrlRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random url replacement value from the list of values mentioned in token.
        Possible values: ["ip_host", "fqdn_host", "path", "query", "protocol"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(r"[uU]rl(\[.*?\])", self.replacement).group(
            1
        )
        value_list = eval(value_list_str)

        for _ in range(token_count):
            if bool(
                set(["ip_host", "fqdn_host", "full"]).intersection(value_list)
            ):
                url = ""
                domain_name = []
                if bool(set(["full", "protocol"]).intersection(value_list)):
                    url = url + choice(["http://", "https://"])
                if bool(set(["full", "ip_host"]).intersection(value_list)):
                    domain_name.append(self.fake.ipv4())
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
            yield str(url)

    

    def generate_url_query_params(self):
        """
        This method is generate the random query params for url
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
        Yields a random dest replacement value from the list of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(
            r"[dD]est(\[.*?\])", self.replacement
        ).group(1)
        value_list = eval(value_list_str)
        for _ in range(token_count):
            csv_row = self.get_rule_replacement_values(sample, value_list, rule="dest")
            yield choice(csv_row)


class SrcPortRule(Rule):
    """
    SrcPortRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random port value from the range 4000-5000

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        for _ in range(token_count):
            yield randint(4000, 5000)


class DvcRule(Rule):
    """
    DvcRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random dvc replacement value from the list of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(r"[dD]vc(\[.*?\])", self.replacement).group(
            1
        )
        value_list = eval(value_list_str)
        for _ in range(token_count):
            csv_row = self.get_rule_replacement_values(sample, value_list, rule="dvc")
            yield choice(csv_row)


class SrcRule(Rule):
    """
    SrcRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random src replacement value from the list of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(r"[sS]rc(\[.*?\])", self.replacement).group(
            1
        )
        value_list = eval(value_list_str)
        for _ in range(token_count):
            csv_row = self.get_rule_replacement_values(sample, value_list, rule="src")
            yield choice(csv_row)


class DestPortRule(Rule):
    """
    DestPortRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random port value from [80, 443, 25, 22, 21]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        DEST_PORT = [80, 443, 25, 22, 21]
        for _ in range(token_count):
            yield choice(DEST_PORT)


class HostRule(Rule):
    """
    HostRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random host replacement value from the list of values mentioned in token.
        Possible values: ["host", "ipv4", "ipv6", "fqdn"]

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        value_list_str = re.match(
            r"[hH]ost(\[.*?\])", self.replacement
        ).group(1)
        value_list = eval(value_list_str)
        for _ in range(token_count):
            csv_row = self.get_rule_replacement_values(
                sample, value_list, rule="host"
            )
            if "host" in value_list:
                if sample.metadata.get("input_type") in [
                    "modinput",
                    "windows_input",
                ]:
                    host_value = sample.metadata.get("host")
                elif sample.metadata.get("input_type") in [
                    "file_monitor",
                    "scripted_input",
                    "syslog_tcp",
                    "syslog_udp",
                    "other",
                ]:
                    host_value = sample.get_host()
                csv_row[0] = host_value
            yield choice(csv_row)


class HexRule(Rule):
    """
    HexRule
    """
    def replace(self, sample, token_count):
        """
        Yields a random hex value.

        Args:
            sample(object): Instance of SampleEvent class.
            token_count(int): No. of token in sample event where rule is to be applicable.
        """
        hex_range = re.match(r"[Hh]ex\((.*?)\)", self.replacement).group(1)
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
            yield hex_value
