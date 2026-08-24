#
# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
import json

from ..addon_parser import Field


class FieldTestAdapter(Field):
    """
    Field adapter to include the testing related properties on top of Field

    Properties:

    * valid_field (str): Result alias for the valid-value count
    * invalid_field (str): Result alias for invalid values
    * validity_query (str): Pre-aggregation query required by the field

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

        Example::
            ["a", "b"] to '\"a\", \"b\"'

        Args:
            values (list): List of str values

        Returns:
            str: SPL query list
        """
        query = '\\", \\"'.join(values)
        return f'\\"{query}\\"'

    def gen_validity_query(self):
        """
        Generate preprocessing required before aggregating validity results.

        Validity is evaluated directly by ``get_stats_query`` so multiple fields do
        not depend on sequential calculated fields in a distributed search.

        """
        if self.validity_query is None:
            self.validity_query = "\n" f"| nomv {self.name}" if self.multi_value else ""
        return self.validity_query

    @staticmethod
    def get_eval_query_from_values(values):
        return ", ".join(json.dumps(value) for value in values)

    def get_validity_expression(self):
        predicates = []
        if self.expected_values and "*" not in self.expected_values:
            predicates.append(
                "({validity}) IN ({values})".format(
                    validity=self.validity,
                    values=self.get_eval_query_from_values(self.expected_values),
                )
            )
        if self.negative_values:
            predicates.append(
                "NOT ({validity}) IN ({values})".format(
                    validity=self.validity,
                    values=self.get_eval_query_from_values(self.negative_values),
                )
            )
        if not predicates:
            return self.validity
        return "if({predicates}, {validity}, null())".format(
            predicates=" AND ".join(predicates),
            validity=self.validity,
        )

    def get_stats_query(self):
        """
        Generate stats search query::

            count(field) as field_count,
                count(eval(validity_expression)) as valid_field_count,
                values(eval(if(isnull(validity_expression), field, null()))) as invalid_values
        """
        validity_expression = self.get_validity_expression()
        query = f", count({self.name}) as {self.FIELD_COUNT.format(self.name)}"
        query += (
            f", count(eval({validity_expression})) as "
            f"{self.VALID_FIELD_COUNT.format(self.name)}"
        )
        query += (
            f", values(eval(if(isnull({validity_expression}), {self.name}, null()))) as "
            f"{self.INVALID_FIELD_VALUES.format(self.name)}"
        )
        return query

    @classmethod
    def get_test_fields(cls, fields):
        return [cls(each_field) for each_field in fields]
