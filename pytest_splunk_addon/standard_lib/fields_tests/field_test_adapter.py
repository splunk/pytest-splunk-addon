from ..addon_parser import Field

class FieldTestAdapater(Field):
    """
    Field adapter to include the testing related properties on top of Field

    Properties:
        valid_field (str): New field generated which can only have the valid values
        validity_query (str): The query which extracts the valid_field out of the field

    """
    VALID_FIELD = "{}_valid"
    INVALID_FIELD = "{}_invalid"
    FIELD_COUNT = "{}_count"
    VALID_FIELD_COUNT = "{}_valid_count"
    INVALID_FIELD_VALUES = "{}_invalid_values"

    def __init__(self, field):
        self.__dict__ = field.__dict__.copy()
        self.valid_field = self.VALID_FIELD.format(field)
        self.invalid_field = self.INVALID_FIELD.format(field)
        self.validity_query = None

    @staticmethod
    def get_query_from_values(values):
        """
        List of values into SPL list
            Example: ["a", "b"] to '\"a\", \"b\"'

        Args:
            values (list): List of str values 
        
        Returns:
            str: SPL query list
        """
        query = '\\", \\"'.join(values)
        return f'\\"{query}\\"'

    def gen_validity_query(self):
        if not self.validity_query is None:
            return self.validity_query
        else:
            self.validity_query = ""
            
            self.validity_query += ("\n"
                f"| eval {self.valid_field}={self.validity}")
            if self.expected_values:
                self.validity_query += ("\n"
                     "| eval {valid_field}=if(searchmatch(\"{valid_field} IN ({values})\"), {valid_field}, null())".format(
                         valid_field=self.valid_field,
                         values=self.get_query_from_values(self.expected_values)
                     )
                )
            if self.negative_values:
                self.validity_query += ("\n"
                     "| eval {valid_field}=if(searchmatch(\"{valid_field} IN ({values})\"), null(), {valid_field})".format(
                         valid_field=self.valid_field,
                         values=self.get_query_from_values(self.negative_values)
                     )
                )
            self.validity_query += ("\n"
                f"| eval {self.invalid_field}=if(isnull({self.valid_field}), {self.name}, null())")
            return self.validity_query

    def get_stats_query(self):
        query = f", count({self.name}) as {self.FIELD_COUNT.format(self.name)}"
        if self.gen_validity_query():
            query += f", count({self.valid_field}) as {self.VALID_FIELD_COUNT.format(self.name)}"
            query += f", values({self.invalid_field}) as {self.INVALID_FIELD_VALUES.format(self.name)}"
        return query

    @classmethod
    def get_test_fields(cls, fields):
        return [cls(each_field) for each_field in fields]
