import re
from os.path import basename
from os import path
from decimal import Decimal
from random import uniform, randint, choice
from time import strftime, time,mktime
import uuid 
import string
# from faker import Faker
from datetime import datetime, timedelta
import math
import csv

from . import SampleEvent

class Rule:
    def __init__(self, token):
        self.token = token["token"]
        self.replacement = token["replacement"]
        self.replacement_type = token["replacementType"]
        self.field = token.get("field", self.token.strip("#"))
        # self.fake = Faker()

    @classmethod
    def parse_rule(cls, token):
        rule_book = {
            'integer': IntRule,
            'list': ListRule,
            'ipv4': Ipv4Rule,
            'float': FloatRule,
            'ipv6': Ipv6Rule,
            'mac': MacRule,
            'file': FileRule,
            'url': UrlRule,
            'user': UserRule,
            'email': EmailRule
        }

        replacement_type = token['replacementType']
        replacement = token['replacement']
        if replacement_type == "static":
            return StaticRule(token)
        elif replacement_type == "timestamp":
            return TimeRule(token)
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
            token_values = self.replace(each_event, self.replacement_type == 'random')
            for each_token_value in token_values:
                new_event = SampleEvent.copy(each_event)
                new_event.replace_token(self.token, each_token_value)
                new_event.register_field_value(self.field, each_token_value)
                new_events.append(new_event)
        return new_events

    def get_lookup_value(self, sample, filename, key, index):
        f = open(filename)
        reader = csv.reader(f)
        csv_row = choice(list(reader))
        sample.__setattr__("replacement_map", { key:csv_row })
        return csv_row[index]

class IntRule(Rule):
    def replace(self, sample, random=True):
        lower_limit, upper_limit = re.match(r"[Ii]nteger\[(\d+):(\d+)\]", self.replacement).groups()
        if random:
            yield randint(int(lower_limit), int(upper_limit))
        else:
            for each_int in range(int(lower_limit), int(upper_limit)):
                yield each_int

class FloatRule(Rule):

    def replace(self, sample, random=True):
        lower_limit, upper_limit = re.match(r"[Ff]loat\[([\d\.]+):([\d\.]+)\]", self.replacement).groups()
        precision =  re.search('\[\d+\.?(\d*):', self.replacement).group(1)
        if not precision:
            precision = str(1)
        float_value = round(uniform(float(lower_limit), float(upper_limit)), len(precision))
        yield float_value

class ListRule(Rule):

    def replace(self, sample, random=True):
        value_list_str = re.match(r'[lL]ist(\[.*?\])', self.replacement).group(1)
        value_list = eval(value_list_str)

        if random:
            yield str(choice(value_list))
        else:
            for each_value in value_list:
                yield str(each_value)


class StaticRule(Rule):
    
    def apply(self, sample_raw):
        return self.replace_token(self.replacement, sample_raw)


class FileRule(Rule):
    
    def replace(self, sample, random=True):
        if random:
            try:
                f = open(self.replacement)
                txt = f.read()
                f.close()
                lines = [each for each in txt.split('\n') if each]
                yield choice(lines)
            except IOError as e:
                print("File not found : {}".format(self.replacement))
        else:
            sample_file_path = re.match(r'[fF]ile\[(.*?)\]', self.replacement).group(1)
            try:
                f = open(sample_file_path)
                txt = f.read()
                f.close()
                
                for each_value in txt.split('\n'):
                    yield each_value
            except IOError as e:
                print("File not found : {}".format(self.replacement))


class TimeRule(Rule):  

    def replace(self, sample, random=True):
        if r"%s" in self.replacement:
            yield self.replacement.replace(r'%s', str(int(time())))

        if r"%e" in self.replacement:
            print(r"timestamp -> %e has compatibility issues (works in linux only). Please replace it with %d.")
        yield strftime(self.replacement.replace(r'%e', r'%d'))


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
        if hasattr(sample, 'replacement_map') and 'email' in sample.replacement_map:
            yield sample.replacement_map["email"][0];
        else:
            yield self.get_lookup_value(sample, "user_email.csv", 'user', 0)

class EmailRule(Rule):
    
    def replace(self, sample, random=True): 
        if hasattr(sample, 'replacement_map') and 'user' in sample.replacement_map:
            yield sample.replacement_map["user"][1];
        else:
            yield self.get_lookup_value(sample, "user_email.csv", 'email', 1)

class UrlRule(Rule):
    
    def replace(self, sample, random=True):
        url = self.fake.uri()
        if randint(0, 1):
            url = url + "?"
            for _ in range(randint(1, 4)):
                field = ''.join(choice(string.ascii_lowercase) for _ in range(randint(2, 5)))
                value = ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(randint(2, 5)))
                url = url + field + "=" + value + "&"
            url = url[:-1]
        yield url

class DestRule(Rule):
    
    def replace(self, sample, random=True):
        yield "10.100." + str(randint(0, 255)) + "." + str(randint(1,255))

class SrcPortRule(Rule):

    def replace(self, sample, random=True):
        yield randint(4000, 5000)

class DvcRule(Rule):

    def replace(self, sample, random=True):
        yield "172.16." + str(randint(0, 255)) + "." + str(randint(1,255))

class SrcRule(Rule):

    def replace(self, sample, random=True):
        yield "10.1." + str(randint(0, 255)) + "." + str(randint(1,255))

class DestPortRule(Rule):

    def replace(self, sample, random=True):
        DEST_PORT = [80, 443, 25, 22, 21]
        yield self.replace_token(choice(DEST_PORT), sample)

class HostRule(Rule):

    def replace(self, sample, random=True):
        if hasattr(sample, 'replacement_map') and 'fqdn' in sample.replacement_map:
                yield sample.replacement_map["fqdn"][0];
        else:
            yield self.get_lookup_value(sample, "host_domain.sample", 'host', 0)
            
class FqdnRule(Rule):
    
    def replace(self, sample, random=True):
        if hasattr(sample, 'replacement_map') and 'host' in sample.replacement_map:
                yield sample.replacement_map["host"][1];
        else:
            yield self.get_lookup_value(sample, "host_domain.sample", 'fqdn', 1)