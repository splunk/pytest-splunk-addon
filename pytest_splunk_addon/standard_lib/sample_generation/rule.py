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
            'ipv4': Ipv4Rule,
            'float': FloatRule,
            'ipv6': Ipv6Rule,
            'mac': MacRule,
            'file': FileRule,
            'random': {
                'integer': IntRule,
                'list': ListRule,
                'emails': EmailRule,
                'users': UserRule,
                'url': UrlRule,
            },
            'all': {
                'list': ListRule,
                'integer': IntRule,
                'file': FileRule,
            }
        }

        replacement_type = token['replacementType']
        replacement = token['replacement']
        if replacement_type == "static":
            return StaticRule(token)
        elif replacement_type == "timestamp":
            return TimeRule(token)
        elif replacement_type == "random" or replacement_type == "all":
            for each_rule in rule_book[replacement_type]:
                if replacement.startswith(each_rule):
                    return rule_book[replacement_type][each_rule](token)
        elif replacement_type == "file":
            return FileRule(token)

        print("No Rule Found.!")
        # TODO: Test the behavior if no rule found
        raise Exception("No Rule Found.!")

    def apply(self, events):
        new_events = []
        for each_event in events:
            token_values = self.replace(self.replacement_type == 'random')
            for each_token_value in token_values:
                new_event = SampleEvent.copy(each_event)
                new_event.replace_token(self.token, each_token_value)
                new_event.register_field_value(self.field, each_token_value)
                new_events.append(new_event)
        return new_events

class IntRule(Rule):
    def replace(self, random=True):
        lower_limit, upper_limit = re.match(r"[Ii]nteger\[(\d+):(\d+)\]", self.replacement).groups()
        if random:
            yield randint(int(lower_limit), int(upper_limit))
        else:
            for each_int in range(int(lower_limit), int(upper_limit)):
                yield each_int

class FloatRule(Rule):

    def apply(self, sample_raw):
        lower_limit, upper_limit = re.match(r"[Ff]loat\[([\d\.]+):([\d\.]+)\]", self.replacement).groups()
        precision =  re.search('\[\d+\.?(\d*):', self.replacement).group(1)
        if not precision:
            precision = str(1)
        float_value = round(uniform(float(lower_limit), float(upper_limit)), len(precision))
        return self.replace_token(float_value, sample_raw)

class ListRule(Rule):

    def apply(self, sample_raw_data):
        value_list_str = re.match(r'[lL]ist(\[.*?\])', self.replacement).group(1)
        value_list = eval(value_list_str)
        if self.replacement_type == 'all':
            tokenised_sample = []
            for each_raw in sample_raw_data:
                for each_value in value_list:
                    for each_char in each_value:
                        if not 32 <= ord(each_char) <= 126:
                            raise Exception("Invalid character in List")
                    tokenised_sample.append(self.replace_token(each_value, each_raw))
            return tokenised_sample
        else:
            for each_value in value_list:
                for each_char in each_value:
                    if not 32 <= ord(each_char) <= 126:
                        raise Exception("Invalid character in List")

            return self.replace_token(str(choice(value_list)), sample_raw_data)


class StaticRule(Rule):
    
    def apply(self, sample_raw):
        return self.replace_token(self.replacement, sample_raw)


class FileRule(Rule):

    def apply(self, sample_raw_data):

        is_csv = False
        if re.search(':\d+', self.replacement):
            sample_file_path = re.sub(':\d+','', sample_file_path)
            is_csv = True

        try:
            f = open(sample_file_path)
            txt = f.read()
            f.close()
            if is_csv:
                col_id = re.search(':(\d+)', self.replacement).group(1)
                lines = [each.split(',')[int(col_id)-1] for each in txt.split('\n') if each]
            else:
                lines = [each for each in txt.split('\n') if each]
            return self.replace_token(choice(lines), sample_raw_data)
        except IOError as e:
            print("File not found : {}".format(self.replacement))
            return sample_raw_data


class TimeRule(Rule):  

    def apply(self, sample_raw_data):
        if r"%s" in self.replacement:
            tokenised_sample = re.sub(self.token, self.replacement.replace(r'%s', str(int(time()))), sample_raw_data, flags=re.MULTILINE)
            return tokenised_sample

        if r"%e" in self.replacement:
            print(r"timestamp -> %e has compatibility issues (works in linux only). Please replace it with %d.")
        tokenised_sample = re.sub(self.token, strftime(self.replacement.replace(r'%e', r'%d')), sample_raw_data, flags=re.MULTILINE)
        return tokenised_sample



class Ipv4Rule(Rule):

    def apply(self, sample_raw):
        ipv4 = self.fake.ipv4()
        return self.replace_token(ipv4, sample_raw)

class Ipv6Rule(Rule):

    def apply(self, sample_raw):
        ipv6 = self.fake.ipv6()
        return self.replace_token(ipv6, sample_raw)

class MacRule(Rule):
    
    def apply(self, sample_raw):
        mac = self.fake.mac_address()
        return self.replace_token(mac, sample_raw)


class GuidRule(Rule):
    
    def apply(self, sample_raw_data):
        tokenised_sample = re.sub(self.token, str(uuid.uuid4()), sample_raw_data)
        return tokenised_sample

class UserRule(Rule):
     
    def apply(self, sample):
        if "email" in self.replacement_map and sample.__hash__ in self.replacement_map["email"]:
            return self.replace_token(self.replacement_map["email"][sample.__hash__][0], sample.event)
        else:
            f = open("C:\\TA\\eventgenparsing\\Splunk_TA_cisco-wsa-old\\samples\\user_email.csv")
            reader = csv.reader(f)
            csv_row = choice(list(reader))
            self.replacement_map["user"] = {sample.__hash__:csv_row}
            return self.replace_token(csv_row[0], sample.event)

class EmailRule(Rule):
    
    def apply(self, sample):    
        if "user" in self.replacement_map and sample.__hash__ in self.replacement_map["user"]:
            return self.replace_token(self.replacement_map["user"][sample.__hash__][1], sample.event)
        else:
            f = open("C:\\TA\\eventgenparsing\\Splunk_TA_cisco-wsa-old\\samples\\user_email.csv")
            reader = csv.reader(f)
            csv_row = choice(list(reader))
            self.replacement_map["email"] = {sample.__hash__:csv_row}
            return self.replace_token(csv_row[1], sample.event)

class UrlRule(Rule):
    
    def apply(self, sample):
        self.fake = Faker()
        url = self.fake.uri()
        if randint(0, 1):
            url = url + "?"
            for _ in range(randint(1, 4)):
                field = ''.join(choice(string.ascii_lowercase) for _ in range(randint(2, 5)))
                value = ''.join(choice(string.ascii_lowercase + string.digits) for _ in range(randint(2, 5)))
                url = url + field + "=" + value + "&"
            url = url[:-1]
        return self.replace_token(url,  sample.event)

class DestRule(Rule):

    def apply(self, sample):
        return self.replace_token("10.100." + str(randint(0, 255)) + "." + str(randint(1,255)), sample)

class SrcPortRule(Rule):

    def apply(self, sample):
        return self.replace_token(randint(4000, 5000), sample)

class DvcRule(Rule):

    def apply(self, sample):
        return self.replace_token("172.16." + str(randint(0, 255)) + "." + str(randint(1,255)), sample)

class SrcRule(Rule):

    def apply(self, sample):
        return self.replace_token("10.1." + str(randint(0, 255)) + "." + str(randint(1,255)), sample)

class DestPortRule(Rule):

    def apply(self, sample):
        DEST_PORT = [80, 443, 25, 22, 21]
        return self.replace_token(choice(DEST_PORT), sample)

class HostRule(Rule):

    def apply(self, sample):    
        if "fqdn" in self.replacement_map and sample.__hash__ in self.replacement_map["fqdn"]:
            return self.replace_token(self.replacement_map["fqdn"][sample.__hash__][0], sample)
        else:
            f = open("host_domain.sample")
            reader = csv.reader(f)
            csv_row = choice(list(reader))
            self.replacement_map["host"] = {sample.__hash__:csv_row}
            return self.replace_token(csv_row[0], sample)
            
class FqdnRule(Rule):
    
    def apply(self, sample):

        if "host" in self.replacement_map and sample.__hash__ in self.replacement_map["host"]:
                return self.replace_token(self.replacement_map["host"][sample.__hash__][1], sample)
        else:
            f = open("host_domain.sample")
            reader = csv.reader(f)
            csv_row = choice(list(reader))
            self.replacement_map["fqdn"] = {sample.__hash__:csv_row}
            return self.replace_token(csv_row[1], sample)