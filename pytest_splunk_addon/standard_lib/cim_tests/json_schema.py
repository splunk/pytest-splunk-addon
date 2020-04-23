# -*- coding: utf-8 -*-
"""
Includes JSON schema for data models
"""
import json
from .base_schema import BaseSchema
from jsonschema import Draft7Validator
import logging

LOGGER = logging.getLogger("pytest-splunk-addon")


class JSONSchema(BaseSchema):
    """
    Json Parser of the Data model files 
    """

    def __init__(
        self,
        schema_path="pytest-splunk-addon\pytest_splunk_addon\standard_lib\cim_tests\DatamodelSchema.json",
    ):
        self.schema_path = schema_path

    @classmethod
    def parse_data_model(cls, file_path):
        """
        Parse the Json file
        """
        try:
            with open(file_path, "r") as json_f:
                with open(cls().schema_path, "r",) as schema:
                    json_data, json_schema = json.load(json_f), json.load(schema)
                    errors = Draft7Validator(json_schema).iter_errors(json_data)
                    error_location, exc = "", ""
                    LOGGER.info("Validating {}".format(file_path))
                    for error in errors:
                        for i in error.path:
                            error_location = error_location + "[{}]".format(i)
                        if type(error.instance) == dict:
                            exc = exc + "\n{} for {}".format(
                                error.message, error_location
                            )
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
