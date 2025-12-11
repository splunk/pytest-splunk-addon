"""
Copyright (C) 2005 - 2019 Splunk Inc. All Rights Reserved.
"""
import sys
import json
from .base_modinput import BaseModularInput, ModularInputConfig


class JsonModularInput(BaseModularInput):

    def _create_event(self, params, stanza):
        """Create an event for JSON streaming output.

        Arguments:
        params - a dictionary of attributes for the event
        stanza - the stanza
        """
        # Create the event base element
        event = {}
        # Indicate if this script is single-instance mode or not.
        if self.use_single_instance:
            event['stanza'] = stanza['name']

        # Fill s/st/h/i in first from stanza configs
        for element in filter(lambda x: x in ['host', 'index', 'source', 'sourcetype'], stanza.keys()):
            event[element] = stanza[element]

        # Define the possible elements
        valid_elements = ['host', 'index', 'source', 'sourcetype', 'time', 'event']

        # Append the valid child elements. Invalid elements will be dropped.
        # Override s/st/h/i if specified in params
        for element in filter(lambda x: x in valid_elements, params.keys()):
            event[element] = params[element]

        return event

    def _print_event(self, event):
        """
        Adds a single event or a list of evnets to JSON streaming output.
        """

        if isinstance(event, list):
            return ''.join([json.dumps(evt) for evt in event])
        else:
            return json.dumps(event)

    def get_scheme(self):
        """
        Get the scheme of the inputs parameters and return as a string.
        """

        doc = {
            "title": self.title,
            "description": self.description,
            "use_external_validation": str(getattr(self, "use_external_validation", '')).strip().lower() in ["true", "t", "1"],
            "streaming_mode": self.streaming_mode,
            "use_single_instance": str(getattr(self, "use_single_instance", '')).strip().lower() in ["true", "t", "1"],
            "endpoint": {"args": []}
        }

        # Create the argument elements
        self.add_json_args(doc["endpoint"]["args"])

        # Return the content as a string
        return json.dumps(doc)

    def add_json_args(self, endpoint_args):
        """
        Add the arguments to the JSON scheme.

        Arguments:
        endpoint_args -- The list that should be the parent of the arg elements that will be added.
        """
        for arg in self.args:
            endpoint_args.append({
                "name": arg.name,
                "title": arg.title,
                "description": arg.description,
                "data_type": arg.get_data_type(),
                "required_on_create": arg.required_on_create,
                "required_on_edit": arg.required_on_edit
            })

    def print_error(self, error, out=sys.stdout):
        """
        Prints the given error message to standard output.

        Arguments:
        error -- The message to be printed
        out -- The stream to write the message to (defaults to standard output)
        """

        json.dump({'message': error}, out)

    def read_config(self, in_stream=sys.stdin):
        """
        Read the config from standard input and return the configuration.

        in_stream -- The stream to get the input from (defaults to standard input)
        """

        config_str_json = in_stream.read()
        return ModularInputConfig.get_config_from_json(config_str_json)

    def get_validation_data(self, in_stream=sys.stdin):
        """
        Get the validation data from standard input

        Arguments:
        in_stream -- The stream to get the input from (defaults to standard input)
        """

        # Read everything from stdin
        val_str = in_stream.read()

        # Parse the validation JSON
        doc = json.loads(val_str)
        items = doc.get("items")
        stanza = list(items)[0]
        params = items[stanza]
        params['name'] = stanza

        return params if items else {}
