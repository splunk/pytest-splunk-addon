class Field(object):

    def __init__(self, field_json=None):
        self.name = field_json.get("name")
        self.field_type = field_json.get("field_type")
        self.expected_values = field_json.get("expected_values", ["*"])
        self.negative_values = field_json.get("negative_values", ["-", ""])
        self.condition = 

    def __str__(self):
        return self.name

    @classmethod
    def parse_fields(cls, field_list):
        for each_fields in field_list:
            yield Field(each_fields)

def convert_to_fields(func):
    """
    Decorator to initialize the list of fields 
    """
    def inner_func(*args, **kwargs):
        for each_field in func(*args, **kwargs):
            if each_field:
                yield Field(each_field)
    return inner_func


"""
If positive values = None and negative value != ["-", ""]
 -> Search  1+) field=* 
            2-) field = "-" OR field = "" 

if positive value = splunkd and negative value = any 
 -> Search 1+) field in ( splunkd )
           2-) NOT field in (splunkd) 
    Events should be present with mentioned value 
    There should not be any other value than positive_values 

"""