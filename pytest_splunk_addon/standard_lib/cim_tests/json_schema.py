# -*- coding: utf-8 -*-
"""
Includes JSON schema for data models
"""
import json
import os.path as op
from .base_schema import BaseSchema
from jsonschema import Draft7Validator
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")


class JSONSchema(BaseSchema):
    """
    JsonSchema + Parser of the Data model json files 

    Args:
        schema_path (str): Relative or absolute path of the schema file
    """

    SCHEMA_FILE = "DatamodelSchema.json"

    def __init__(
        self, schema_path=None,
    ):
        self.schema_path = schema_path or op.join(
            op.dirname(op.abspath(__file__)), self.SCHEMA_FILE
        )

    @classmethod
    def parse_data_model(cls, file_path):
        """
        Parse and validate the Json file

        Args:
            schema_path (str): Relative or absolute path of the data model json file
        """
        try:
            with open(cls().schema_path, "r",) as schema_f:
                json_schema = json.load(schema_f)
            with open(file_path, "r") as json_f:
                json_data = json.load(json_f)
                errors = Draft7Validator(json_schema).iter_errors(json_data)
                error_location, exc = "", ""
                LOGGER.info("Validating {}".format(file_path))
                for error in errors:
                    for error_index in error.path:
                        error_location = error_location + "[{}]".format(error_index)
                    if type(error.instance) == dict:
                        exc = exc + "\n{} for {}".format(error.message, error_location)
                    elif type(error.instance) in [str, list]:
                        exc = exc + "\nType mismatch: {} in property {}".format(
                            error.message, error_location
                        )
                    else:
                        exc = exc + "\n{}".format(error)
                if not error_location:
                    LOGGER.info("Valid Json")
                    return json_data
                else:
                    LOGGER.exception(exc)
                    raise Exception(exc)

        except json.decoder.JSONDecodeError as err:
            LOGGER.error("Json Decoding error in {} ".format(file_path))
            raise Exception("{} in file {}".format(err.args[0], file_path))
