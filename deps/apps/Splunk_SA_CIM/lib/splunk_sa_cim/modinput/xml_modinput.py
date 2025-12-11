"""
Copyright (C) 2005 - 2017 Splunk Inc. All Rights Reserved.
"""
import sys
import xml.dom
from xml.dom.minidom import Document
import xml.sax.saxutils
from .base_modinput import BaseModularInput, ModularInputConfig


class XmlModularInput(BaseModularInput):

    def _create_formatter_textnode(self, xmldoc, nodename, value):
        """Shortcut for creating a formatter textnode.

        Arguments:
        xmldoc - A Document object.
        nodename - A string name for the node.
        """
        node = xmldoc.createElement(nodename)
        text = xmldoc.createTextNode(str(value))
        node.appendChild(text)

        return node

    def _create_document(self):
        """Create the document for sending XML streaming events."""

        doc = Document()

        # Create the <stream> base element
        stream = doc.createElement('stream')
        doc.appendChild(stream)

        return doc

    def _create_event(self, doc, params, stanza, unbroken=False, close=True):
        """Create an event for XML streaming output.

        Arguments:
        doc - a Document object.
        params - a dictionary of attributes for the event.
        stanza - the stanza
        """

        # Create the <event> base element
        event = doc.createElement('event')

        # Indicate if this event is to be unbroken (meaning a </done> tag will
        # need to be added by a future event.
        if unbroken:
            event.setAttribute('unbroken', '1')

        # Indicate if this script is single-instance mode or not.
        if self.use_single_instance == 'true':
            event.setAttribute('stanza', stanza['name'])

        # Define the possible elements
        valid_elements = ['host', 'index', 'source', 'sourcetype', 'time', 'data']

        # Append the valid child elements. Invalid elements will be dropped.
        for element in filter(lambda x: x in valid_elements, params.keys()):
            event.appendChild(self._create_formatter_textnode(
                doc, element, params[element]))

        if close:
            event.appendChild(doc.createElement('done'))

        return event

    def _print_event(self, doc, event):
        """Adds an event to XML streaming output."""

        # Get the stream from the document.
        stream = doc.firstChild

        # Append the event.
        stream.appendChild(event)

        # Return the content as a string WITHOUT the XML header; remove the
        # child object so the next event can be returned and reuse the same
        # Document object.
        output = doc.documentElement.toxml()

        stream.removeChild(event)

        return output

    def _add_events(self, doc, events):
        """Adds a set of events to XML streaming output."""

        # Get the stream from the document.
        stream = doc.firstChild

        # Add the <event> node.
        for event in events:
            stream.appendChild(event)

        # Return the content as a string WITHOUT the XML header.
        return doc.documentElement.toxml()

    def get_scheme(self):
        """
        Get the scheme of the inputs parameters and return as a string.
        """

        # Create the XML document
        doc = Document()

        # Create the <scheme> base element
        element_scheme = doc.createElement("scheme")
        doc.appendChild(element_scheme)

        # Create the title element
        element_title = doc.createElement("title")
        element_scheme.appendChild(element_title)

        element_title_text = doc.createTextNode(self.title)
        element_title.appendChild(element_title_text)

        # Create the description element
        element_desc = doc.createElement("description")
        element_scheme.appendChild(element_desc)

        element_desc_text = doc.createTextNode(self.description)
        element_desc.appendChild(element_desc_text)

        # Create the use_external_validation element
        element_external_validation = doc.createElement(
            "use_external_validation")
        element_scheme.appendChild(element_external_validation)

        element_external_validation_text = doc.createTextNode(
            self.use_external_validation)
        element_external_validation.appendChild(
            element_external_validation_text)

        # Create the streaming_mode element
        element_streaming_mode = doc.createElement("streaming_mode")
        element_scheme.appendChild(element_streaming_mode)

        element_streaming_mode_text = doc.createTextNode(self.streaming_mode)
        element_streaming_mode.appendChild(element_streaming_mode_text)

        # Create the use_single_instance element
        element_use_single_instance = doc.createElement("use_single_instance")
        element_scheme.appendChild(element_use_single_instance)

        element_use_single_instance_text = doc.createTextNode(
            self.use_single_instance)
        element_use_single_instance.appendChild(
            element_use_single_instance_text)

        # Create the elements to stored args element
        element_endpoint = doc.createElement("endpoint")
        element_scheme.appendChild(element_endpoint)

        element_args = doc.createElement("args")
        element_endpoint.appendChild(element_args)

        # Create the argument elements
        self.add_xml_args(doc, element_args)

        # Return the content as a string
        return doc.toxml()

    def add_xml_args(self, doc, element_args):
        """
        Add the arguments to the XML scheme.

        Arguments:
        doc -- The XML document
        element_args -- The element that should be the parent of the arg elements that will be added.
        """

        for arg in self.args:
            element_arg = doc.createElement("arg")
            element_arg.setAttribute("name", arg.name)

            element_args.appendChild(element_arg)

            # Create the title element
            element_title = doc.createElement("title")
            element_arg.appendChild(element_title)

            element_title_text = doc.createTextNode(arg.title)
            element_title.appendChild(element_title_text)

            # Create the description element
            element_desc = doc.createElement("description")
            element_arg.appendChild(element_desc)

            element_desc_text = doc.createTextNode(arg.description)
            element_desc.appendChild(element_desc_text)

            # Create the data_type element
            element_data_type = doc.createElement("data_type")
            element_arg.appendChild(element_data_type)

            element_data_type_text = doc.createTextNode(arg.get_data_type())
            element_data_type.appendChild(element_data_type_text)

            # Create the required_on_create element
            element_required_on_create = doc.createElement(
                "required_on_create")
            element_arg.appendChild(element_required_on_create)

            element_required_on_create_text = doc.createTextNode(
                "true" if arg.required_on_create else "false")
            element_required_on_create.appendChild(
                element_required_on_create_text)

            # Create the required_on_save element
            element_required_on_edit = doc.createElement("required_on_edit")
            element_arg.appendChild(element_required_on_edit)

            element_required_on_edit_text = doc.createTextNode(
                "true" if arg.required_on_edit else "false")
            element_required_on_edit.appendChild(element_required_on_edit_text)

    def print_error(self, error, out=sys.stdout):
        """
        Prints the given error message to standard output.

        Arguments:
        error -- The message to be printed
        out -- The stream to write the message to (defaults to standard output)
        """

        out.write("<error><message>%s</message></error>" % xml.sax.saxutils.escape(error))

    def read_config(self, in_stream=sys.stdin):
        """
        Read the config from standard input and return the configuration.

        in_stream -- The stream to get the input from (defaults to standard input)
        """

        config_str_xml = in_stream.read()

        return ModularInputConfig.get_config_from_xml(config_str_xml)

    def get_validation_data(self, in_stream=sys.stdin):
        """
        Get the validation data from standard input

        Arguments:
        in_stream -- The stream to get the input from (defaults to standard input)
        """

        val_data = {}

        # Read everything from stdin
        val_str = in_stream.read()

        # Parse the validation XML
        doc = xml.dom.minidom.parseString(val_str)
        root = doc.documentElement

        item_node = root.getElementsByTagName("item")[0]
        if item_node:

            name = item_node.getAttribute("name")
            val_data["name"] = name

            params_node = item_node.getElementsByTagName("param")

            for param in params_node:
                name = param.getAttribute("name")

                if name and param.firstChild and param.firstChild.nodeType == param.firstChild.TEXT_NODE:
                    val_data[name] = param.firstChild.data

        return val_data
