import argparse
import re
import os

from splunk_appinspect import App
from .mapping import FIELD_MAPPING, FILE_MAPPING


class UpdateEventgen():
    """ Update eventgen file """

    def __init__(self, addon_path):
        self._app = App(addon_path, python_analyzer_enable=False)
        self._eventgen = None
        self.path_to_samples = os.path.join(addon_path, "samples")

    @property
    def eventgen(self):
        try:
            if not self._eventgen:
                self._eventgen = self._app.get_config("eventgen.conf")
            return self._eventgen
        except OSError:
            raise Exception("Eventgen.conf not found")
            return None

    def get_eventgen_stanzas(self):
        """
        To get eventgen stanza and create a dictionary. 
        If stanza contains regex for multiple sample files, then it creates stanza for each sample file.

        Return: 
            eventgen_dict (dict):
                {
                    "stanza_name": 
                    {    
                        "other metadata": "source, sourcetype, etc."
                        "sample_count" : int
                        "tokens": 
                        {
                            0: {
                                token: #One#
                                replacementType: random
                                replacement: static 
                               }
                        }
                    }
                }
        """
        eventgen_dict = {}
        for stanza in self.eventgen.sects:
            eventgen_sections = self.eventgen.sects[stanza]
            eventgen_dict.setdefault((stanza), {
                'tokens': {},
            })

            try:
                events_in_file = len(open(os.path.join(self.path_to_samples, stanza)).readlines())
                eventgen_dict[stanza]["sample_count"] = events_in_file

            except:
                pass

            for stanza_param in eventgen_sections.options:
                eventgen_property = eventgen_sections.options[stanza_param]
                if eventgen_property.name.startswith('token'):
                    _, token_id, token_param = eventgen_property.name.split(
                        '.')
                    if not token_id in eventgen_dict[stanza]['tokens'].keys():
                        eventgen_dict[stanza]['tokens'][token_id] = {
                        }
                    eventgen_dict[stanza]['tokens'][token_id][token_param] = eventgen_property.value

                else:
                    eventgen_dict[stanza][eventgen_property.name] = eventgen_property.value

            for sample_file in os.listdir(self.path_to_samples):

                if re.search(stanza, sample_file):

                    events_in_file = len(open(os.path.join(self.path_to_samples, sample_file)).readlines())
                    if sample_file not in eventgen_dict.keys():
                        eventgen_dict.setdefault((sample_file), {})
                        eventgen_dict[sample_file]["sample_count"] = events_in_file
                        eventgen_dict[sample_file]["add_comment"] = True
                        eventgen_dict[sample_file]["tokens"] = {}

        return eventgen_dict

    # update the stanzas in dict
    def update_eventgen_stanzas(self, eventgen_dict):
        """
        Updates the eventgen_dict by adding new metadata 
        New Metadata: ["input_type", "host_type", "sourcetype_to_search", "timestamp_type"]
        And update the tokens if possible based on the new Data-Generator rules.
        Input:
            eventgen_dict (dict) : eventgen dictionary in following format.

        Return: 
            eventgen_dict (dict): Updated Eventgen stanzas dictionary
        """

        metadata = ["input_type", "host_type", "sourcetype_to_search", "timestamp_type"]
        review_comments = {
            'metadata': "#REVIEW : Update metadata as per addon's requirement",
            'replacement': "# REVIEW : Possible value in list : ",
            'field': "# REVIEW : Check if the field is extracted from the events, else remove this field parameter",
            'mapping': "# REVIEW : Please check if it can be replace with %s rule",
            'sample_count': "# REVIEW : Please check for the events per stanza and update sample_count accordingly"
        }

        for stanza_name, stanza_data in eventgen_dict.items():
            # adding metadata
            for data in metadata:
                eventgen_dict[stanza_name][data] = (f"<<{data}>> "
                                                    f"{review_comments['metadata']}")

            eventgen_dict[stanza_name]['source'] = eventgen_dict[stanza_name].get(
                'source', f"pytest-splunk-addon:{eventgen_dict[stanza_name]['input_type']}")

            for _, token_data in stanza_data.get("tokens", {}).items():
                token_name = token_data.get("token").strip("#()").lower()
                for _, new_token_values in FIELD_MAPPING.items():

                    if token_name in new_token_values.get("token"):
                        new_replacement_type = new_token_values.get("replacementType")
                        new_replacement = new_token_values.get('replacement')

                        token_data["replacementType"] = new_replacement_type
                        token_data["replacement"] = new_replacement
                        if new_token_values.get("possible_replacement"):
                            token_data["replacement"] = (f"{new_replacement} "
                                                         f"{review_comments['replacement']} "
                                                         f"{new_token_values.get('possible_replacement')}")

                        if new_token_values.get("field"):
                            token_data["field"] = (f"{new_token_values.get('field')} "
                                                   f"{review_comments['field']}")

                if token_data.get('replacementType').lower() == "timestamp":
                    token_data["field"] = f"_time {review_comments['field']}"

                elif token_data.get('replacementType').lower() in ["file", "mvfile"]:
                    file_name = token_data.get('replacement').split('/')[-1].split(":")[0]
                    token_data["replacement"] = f"file[{token_data.get('replacement')}]"
                    token_data["replacementType"] = "random"

                    for key_fields, mapped_files in FILE_MAPPING.items():
                        replacement_type = FIELD_MAPPING.get(key_fields).get('replacementType')
                        replacement = FIELD_MAPPING.get(key_fields).get('replacement')
                        replacement_type_values = FIELD_MAPPING.get(key_fields).get('possible_replacement')
                        field_value = FIELD_MAPPING.get(key_fields).get('field')

                        if file_name in mapped_files:
                            if 'SA-Eventgen' in token_data["replacement"]:
                                token_data["replacementType"] = (f"{replacement_type} "
                                                                 f"{review_comments['mapping']%key_fields}")

                                token_data["replacement"] = (f"{replacement} "
                                                             f"{review_comments['mapping']%key_fields}")

                            if replacement_type_values:
                                token_data["replacement"] = (f"{token_data['replacement']} "
                                                             f"{review_comments['replacement']} "
                                                             f"{replacement_type_values}")

                            if field_value:
                                token_data["field"] = (f"{field_value} "
                                                       f"{review_comments['mapping']%key_fields}")

            # for assigning sample_count at the end of metadata
            if eventgen_dict.get(stanza_name).get("sample_count"):
                event_count = eventgen_dict[stanza_name].pop(
                    "sample_count")
                eventgen_dict[stanza_name]["sample_count"] =(f"{event_count}"
                                                             f"  {review_comments['sample_count']}")

            # for assigning tokens at the end of metadata
            if eventgen_dict.get(stanza_name).get("tokens"):
                token_dict = eventgen_dict[stanza_name].pop("tokens")
                eventgen_dict[stanza_name]["tokens"] = token_dict

        return eventgen_dict

    def create_new_eventgen(self, updated_eventgen_dict, new_conf_path):
        """
        Writes the new values in a new conf file
        params:
            updated_eventgen_dict (dict) : Containing all the new values for eventgen.conf
            new_conf_path : file path for creating new conf file
        """
        with open(new_conf_path, 'w') as new_eventgen:

            # writing file metadata in new eventgen file
            comment = "## Stanza gets metadata from main stanza"
            for file_metadata in self.eventgen.headers:
                new_eventgen.write(file_metadata + '\n')

            for stanza_name, stanza_data in updated_eventgen_dict.items():
                new_eventgen.write(f'\n[{stanza_name}]\n')
                for metadata_name, metadata_value in stanza_data.items():

                    if metadata_name == "add_comment":
                        new_eventgen.write(f"{comment}\n")

                    elif metadata_name != "tokens":
                        new_eventgen.write(
                            f"{metadata_name} = {metadata_value}\n")
                    else:
                        new_eventgen.write('\n')
                        for tokens_id, tokens_value in stanza_data.get("tokens").items():
                            new_eventgen.write(
                                f"token.{tokens_id}.token = {tokens_value['token']}\n")
                            new_eventgen.write(
                                f"token.{tokens_id}.replacementType = {tokens_value['replacementType']}\n")
                            new_eventgen.write(
                                f"token.{tokens_id}.replacement = {tokens_value['replacement']}\n")
                            if tokens_value.get("field"):
                                new_eventgen.write(
                                    f'token.{tokens_id}.field = {tokens_value.get("field")}\n')
                            new_eventgen.write('\n')


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument(
        "addon_path", help="Path to the addon for which eventgen.conf has to be converted. Must contains samples folder", metavar="addon-path"
    )
    ap.add_argument(
        "new_conf_path",
        help="Path to Save the new conf file",
        metavar="new-conf-path",
        nargs="?",
        default="pytest-splunk-addon-data.conf",
    )
    args = ap.parse_args()

    addon_path = args.addon_path
    new_conf_path = args.new_conf_path

    update_eventgen = UpdateEventgen(addon_path)
    eventgen_dict = update_eventgen.get_eventgen_stanzas()
    updated_eventgen_dict = update_eventgen.update_eventgen_stanzas(eventgen_dict)
    update_eventgen.create_new_eventgen(updated_eventgen_dict, new_conf_path)


if __name__ == "__main__":
    main()
