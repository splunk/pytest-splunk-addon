import abc
import csv
import math
import re
import string
import uuid

from datetime import datetime, timedelta
from decimal import Decimal
from faker import Faker
from os import path
from os.path import basename
from random import uniform, randint, choice
from time import strftime, time, mktime
from .time_parser import time_parse


from . import SampleEvent


class Rule:
    def __init__(self, token, eventgen_params=None):
        self.token = token["token"]
        self.replacement = token["replacement"]
        self.replacement_type = token["replacementType"]
        self.field = token.get("field", self.token.strip("#"))
        self.eventgen_params = eventgen_params
        self.fake = Faker()

    @classmethod
    def parse_rule(cls, token, eventgen_params):
        rule_book = {
            "integer": IntRule,
            "list": ListRule,
            "ipv4": Ipv4Rule,
            "float": FloatRule,
            "ipv6": Ipv6Rule,
            "mac": MacRule,
            "file": FileRule,
            "dvc": DvcRule,
            "destport": DestPortRule,
            "srcport": SrcPortRule,
            "dest": DestRule,
            "url": UrlRule,
            "user": UserRule,
            "email": EmailRule,
        }

        replacement_type = token["replacementType"]
        replacement = token["replacement"]
        if replacement_type == "static":
            return StaticRule(token)
        elif replacement_type == "timestamp":
            return TimeRule(token, eventgen_params)
        elif replacement_type == "random" or replacement_type == "all":
            for each_rule in rule_book:
                if replacement.startswith(each_rule):
                    return rule_book[each_rule](token)
        elif replacement_type == "file":
            return FileRule(token)

        print("No Rule Found.!")
        # TODO: Test the behavior if no rule found
        raise Exception("No Rule Found.!")

    def apply(self, events):
        new_events = []
        for each_event in events:
            token_count = each_event.get_token_count(self.token)
            if self.replacement_type == "all" and token_count > 1:
                raise NotImplementedError(
                    "replacement_type=all with multiple token not supported"
                )
            token_values = self.replace(token_count)
            if self.replacement_type == "all":
                for each_token_value in token_values:
                    new_event = SampleEvent.copy(each_event)
                    new_event.replace_token(self.token, each_token_value)
                    new_event.register_field_value(
                        self.field, each_token_value
                    )
                    new_events.append(new_event)
            else:
                each_event.replace_token(self.token, token_values)
                new_events.append(each_event)
        return new_events

    def get_lookup_value(self, sample, filename, key, index):
        f = open(filename)
        reader = csv.reader(f)
        csv_row = choice(list(reader))
        sample.__setattr__("replacement_map", {key: csv_row})
        return csv_row[index]


class IntRule(Rule):
    def replace(self, token_count, random=True):
        lower_limit, upper_limit = re.match(
            r"[Ii]nteger\[(\d+):(\d+)\]", self.replacement
        ).groups()
        if random:
            for _ in range(token_count):
                yield randint(int(lower_limit), int(upper_limit))
        else:
            for each_int in range(int(lower_limit), int(upper_limit)):
                yield each_int


class FloatRule(Rule):
    def replace(self, token_count):
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
    def replace(self, sample, random=True):
        value_list_str = re.match(
            r"[lL]ist(\[.*?\])", self.replacement
        ).group(1)
        value_list = eval(value_list_str)

        if random:
            yield str(choice(value_list))
        else:
            for each_value in value_list:
                yield str(each_value)


class StaticRule(Rule):
    def replace(self):
        yield self.replacement


class FileRule(Rule):
    def replace(self, sample, random=True):
        if random:
            try:
                f = open(self.replacement)
                txt = f.read()
                f.close()
                lines = [each for each in txt.split("\n") if each]
                yield choice(lines)
            except IOError as e:
                print("File not found : {}".format(self.replacement))
        else:
            sample_file_path = re.match(
                r"[fF]ile\[(.*?)\]", self.replacement
            ).group(1)
            try:
                f = open(sample_file_path)
                txt = f.read()
                f.close()

                for each_value in txt.split("\n"):
                    yield each_value
            except IOError as e:
                print("File not found : {}".format(self.replacement))


class TimeRule(Rule):
    def replace(self, random=True):
        """
        input -> sample_raw - sample event to be updated as per replacement for token
              -> earliest - splunktime formated time 
              -> latest - splunktime formated time
              -> timezone - time zone according to which time is to be generated

        output -> returns random time according to the parameters specified in the input         
        """
        earliest = self.eventgen_params.get("earlest")
        latest = self.eventgen_params.get("latest")
        timezone = self.eventgen_params.get("timezone")
        random_time = datetime.now()
        time_parser = time_parse()
        if earliest is not None and latest is not None:

            if earliest != "now":
                sign, num, unit = re.match(
                    r"([+-])(\d{1,})(.*)", earliest
                ).groups()
                earliest = time_parser.convert_to_time(sign, num, unit)
            else:
                earliest = datetime.now()

            if latest != "now":
                sign, num, unit = re.match(
                    r"([+-])(\d{1,})(.*)", latest
                ).groups()
                latest = time_parser.convert_to_time(sign, num, unit)
            else:
                latest = datetime.now()

            earliest_in_epoch = mktime(earliest.timetuple())
            latest_in_epoch = mktime(latest.timetuple())

            if earliest_in_epoch > latest_in_epoch:
                print("Latest time is earlier than earliest time.")
                return False

            random_time = datetime.fromtimestamp(
                randint(earliest_in_epoch, latest_in_epoch)
            )
        if timezone != "'local'" and timezone is not None:
            sign, hrs, mins = re.match(
                r"([+-])(\d\d)(\d\d)", timezone
            ).groups()
            random_time = self.get_timezone_time(random_time, sign, hrs, mins)

        if r"%s" in self.replacement:
            yield str(
                self.replacement.replace(
                    r"%s", str(int(random_time.strftime("%Y%m%d%H%M%S")))
                )
            )

        elif r"%e" in self.replacement:
            yield strftime(self.replacement.replace(r"%e", r"%d"))
        else:
            yield random_time.strftime(self.replacement)

    def get_timezone_time(self, random_time, sign, hrs, mins):
        """
        converts timezone formated time into datetime object for earliest and latest 
        input -> sign to increase or decrease time
              -> hrs : hours in timezone
              -> mins : minutes in timezone

        output -> returns datetime formated time
        """

        if (hrs <= "00" or hrs >= "23") or (mins <= "00" or mins >= "59"):
            print(
                "hours should be in range 0-23 and mins should be in range 0-59"
            )
            return random_time
        if sign == "-":
            random_time = random_time - timedelta(
                hours=int(hrs), minutes=int(mins)
            )
        else:
            random_time = random_time + timedelta(
                hours=int(hrs), minutes=int(mins)
            )
        return random_time


class Ipv4Rule(Rule):
    def replace(self, sample, sample_raw):
        ipv4 = self.fake.ipv4()
        yield ipv4


class Ipv6Rule(Rule):
    def replace(self, sample, sample_raw):
        ipv6 = self.fake.ipv6()
        yield ipv6


class MacRule(Rule):
    def replace(self, sample, sample_raw):
        mac = self.fake.mac_address()
        yield mac


class GuidRule(Rule):
    def replace(self, sample, sample_raw_data):
        yield str(uuid.uuid4())


class UserRule(Rule):
    def replace(self, sample, random=True):
        if (
            hasattr(sample, "replacement_map")
            and "email" in sample.replacement_map
        ):
            yield sample.replacement_map["email"][0]
        else:
            yield self.get_lookup_value(sample, "user_email.csv", "user", 0)


class EmailRule(Rule):
    def replace(self, sample, random=True):
        if (
            hasattr(sample, "replacement_map")
            and "user" in sample.replacement_map
        ):
            yield sample.replacement_map["user"][1]
        else:
            yield self.get_lookup_value(sample, "user_email.csv", "email", 1)


class UrlRule(Rule):
    def replace(self, sample, random=True):
        url = self.fake.uri()
        if randint(0, 1):
            url = url + "?"
            for _ in range(randint(1, 4)):
                field = "".join(
                    choice(string.ascii_lowercase)
                    for _ in range(randint(2, 5))
                )
                value = "".join(
                    choice(string.ascii_lowercase + string.digits)
                    for _ in range(randint(2, 5))
                )
                url = url + field + "=" + value + "&"
            url = url[:-1]
        yield url


class DestRule(Rule):
    def replace(self, sample, random=True):
        yield "10.100." + str(randint(0, 255)) + "." + str(randint(1, 255))


class SrcPortRule(Rule):
    def replace(self, sample, random=True):
        yield randint(4000, 5000)


class DvcRule(Rule):
    def replace(self, sample, random=True):
        yield "172.16." + str(randint(0, 255)) + "." + str(randint(1, 255))


class SrcRule(Rule):
    def replace(self, sample, random=True):
        yield "10.1." + str(randint(0, 255)) + "." + str(randint(1, 255))


class DestPortRule(Rule):
    def replace(self, sample, random=True):
        DEST_PORT = [80, 443, 25, 22, 21]
        yield self.replace_token(choice(DEST_PORT), sample)


class HostRule(Rule):
    def replace(self, sample, random=True):
        if (
            hasattr(sample, "replacement_map")
            and "fqdn" in sample.replacement_map
        ):
            yield sample.replacement_map["fqdn"][0]
        else:
            yield self.get_lookup_value(
                sample, "host_domain.sample", "host", 0
            )


class FqdnRule(Rule):
    def replace(self, sample, random=True):
        if (
            hasattr(sample, "replacement_map")
            and "host" in sample.replacement_map
        ):
            yield sample.replacement_map["host"][1]
        else:
            yield self.get_lookup_value(
                sample, "host_domain.sample", "fqdn", 1
            )

