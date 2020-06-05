import re
from decimal import Decimal
from random import uniform, randint, choice
from time import strftime, time
import uuid


class Rule:

    def __init__(self, number, name, replacement, replacement_type):
        self.number = number
        self.name = name
        self.replacement = replacement
        self.replacement_type = replacement_type

    @classmethod
    def init_variables(cls):

        cls.rule_book = {
            ('random', 'integer'): IntRule,
            ('random', 'list'): ListRule,
            ('random', 'ipv4'): ipv4Rule,
            ('random', 'float'): FloatRule,
            ('random', 'ipv6'): ipv6Rule,
            ('random', 'mac'): macRule,
            ('file', 'file_name'): FileRule,
            ('mvfile', 'file_name'): FileRule,
            ('static', 'value'): StaticRule,
            ('timestamp', 'format'): TimeRule
        }

        cls.rules = {
            "random": {
                r"integer": "integer",
                r"^[Ll]ist.*": "list",
                r"ipv4": "ipv4",
                r"ipv6": "ipv6",
                r"float": 'float',
                r"mac": 'mac'
            },
            "file": {
                r".*": "file_name"
            },
            "mvfile": {
                r".*": "file_name"
            },
            "static": {
                r".*": "value"
            },
            "timestamp": {
                r".*": "format"
            }
        }

    @classmethod
    def parse_rule(cls, number, name, replacement_type, replacement):

        if replacement_type in cls.rules:
            for each_rule in cls.rules[replacement_type]:
                if re.search(each_rule, replacement):
                    # print("here", replacement)
                    return cls.rule_book[(replacement_type, cls.rules[replacement_type][each_rule])](number, name, replacement, replacement_type)


class IntRule(Rule):

    def apply(self, sample_raw_data):

        replace_range = re.match(r"[Ii]nteger\[(\d+):(\d+)\]", self.replacement).groups()
        tokenised_sample = re.sub(self.name, str(randint(int(replace_range[0]), int(replace_range[1]))), sample_raw_data)
        return tokenised_sample


class FloatRule(Rule):

    def apply(self, sample_raw_data):
        replace_range = re.match(r'float\[([\d\.]+):([\d\.]+)\]', self.replacement).groups()
        precision = re.search(r'\[\d+\.?(\d*):', self.replacement).group(1)
        right_precision = re.search(r':\d+\.?(\d*)\]', self.replacement).group(1)
        assert len(right_precision) == len(precision), "Float: Precision should be same in left and right end of the range. ex:float[0.001:10.000]"
        replace_float = Decimal(uniform(float(replace_range[0]), float(replace_range[1])))
        replace_float = round(replace_float, len(precision))
        tokenised_sample = re.sub(self.name, str(replace_float), sample_raw_data)
        return tokenised_sample


class ListRule(Rule):

    def apply(self, sample_raw_data):
        value_list_str = re.match(r'[lL]ist(\[.*?\])', self.replacement).group(1)
        value_list = eval(value_list_str)
        for each_value in value_list:
            for each_char in each_value:
                if not 32 <= ord(each_char) <= 126:
                    raise Exception("Invalid character in List")
        tokenised_sample = re.sub(self.name, str(choice(value_list)), sample_raw_data)
        return tokenised_sample


class StaticRule(Rule):

    def apply(self, sample_raw_data):
        tokenised_sample = re.sub(self.name, self.replacement, sample_raw_data)
        return tokenised_sample


class FileRule(Rule):

    def apply(self, sample_raw_data):
        is_csv = False
        sample_file_path = "{}\\{}".format(sample.path_to_samples, *self.replacement.split('samples')[-1].strip('/').split('/'))
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
            tokenised_sample = re.sub(self.name, choice(lines), sample_raw_data)
            return tokenised_sample

        except IOError as e:
            raise Exception("File not found : {}".format(sample_file_path))


class TimeRule(Rule):  

    def apply(self, sample_raw_data):
        if r"%s" in self.replacement:
            tokenised_sample = re.sub(self.name, self.replacement.replace(r'%s', str(int(time()))), sample_raw_data, flags=re.MULTILINE)
            return tokenised_sample

        if r"%e" in self.replacement:
            print(r"timestamp -> %e has compatibility issues (works in linux only). Please replace it with %d.")
        tokenised_sample = re.sub(self.name, strftime(self.replacement.replace(r'%e', r'%d')), sample_raw_data, flags=re.MULTILINE)
        return tokenised_sample


class ipv4Rule(Rule):

    def apply(self, sample_raw_data):
        tokenised_sample = re.sub(self.name, ".".join(map(str, (randint(0, 255) for _ in range(4)))), sample_raw_data)
        return tokenised_sample


class ipv6Rule(Rule):

    def apply(self, sample_raw_data):
        M = 16**4
        tokenised_sample = re.sub(self.name, ":".join(("%x" % randint(0, M) for i in range(6))), sample_raw_data)
        return tokenised_sample


class macRule(Rule):

    def apply(self, sample_raw_data):
        tokenised_sample = re.sub(self.name, "%02x:%02x:%02x:%02x:%02x:%02x" % (
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
                randint(0, 255),
                randint(0, 255)
            ), sample_raw_data)

        return tokenised_sample


class GuidRule(Rule):

    def apply(self, sample_raw_data):
        tokenised_sample = re.sub(self.name, str(uuid.uuid4()), sample_raw_data)
        return tokenised_sample
