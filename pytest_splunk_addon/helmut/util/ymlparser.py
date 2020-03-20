import logging
import os
from builtins import object
from builtins import str

import yaml
from pytest_splunk_addon.helmut.util.hosts import Host, Hosts

LOGGER = logging.getLogger("..util.ymlparser")
YAML_HOLDER = {}


class YMLParser(object):
    """
    Returns the entire contents of the yml file as a dictionary
    """

    @classmethod
    def extract_key_values(self, yaml_file):
        if os.path.isabs(yaml_file) == False:
            path = os.getcwd()
            while (
                path.endswith("new_test") == False
                and path.endswith("new_test" + os.sep) == False
            ):
                path = os.path.abspath(os.path.join(path, os.pardir))
            # if the input yaml_file path is not absolute, then we expect that
            # the path is relative to new_test/config/. so new_test/config/
            # + yaml_file path
            yaml_file = path + os.sep + "config" + os.sep + yaml_file
        if os.path.isfile(yaml_file) == False:
            msg = "Invalid yaml_file path:" + yaml_file
            LOGGER.warn(msg)
            raise Exception(msg)

        if not yaml_file in YAML_HOLDER:
            LOGGER.info("Trying to Open yml file: " + yaml_file)
            file_object = open(yaml_file)
            LOGGER.info("Successfully opened yml file: " + yaml_file)
            yaml_dict = yaml.load(file_object)
            for item in yaml_dict:
                LOGGER.info(
                    "item in yaml file: {key}: {value}".format(
                        key=item, value=str(yaml_dict[item])
                    )
                )
            YAML_HOLDER[yaml_file] = yaml_dict
        return YAML_HOLDER[yaml_file]

    """
    Returns all the values of a given key in the yml file
    """

    @classmethod
    def get_values(self, key, yaml_file):
        dict = self.extract_key_values(yaml_file)
        if key in dict:
            return dict[key]
        else:
            return None

    """
    Returns the hosts that are in the yml file as a Hosts class.
    """

    @classmethod
    def get_hosts(self, yaml_file):
        if yaml_file is None:
            return None
        config = self.extract_key_values(yaml_file)
        if not "hosts" in config:  # if no hosts in the yml file
            return None
        host_list = config["hosts"]
        hosts = Hosts()
        for host in host_list:
            hosts.add_host(
                Host(
                    host_name=host,
                    ssh_user=config["ssh_user"],
                    ssh_password=config["ssh_password"],
                    splunk_home=config["splunk_home"],
                    ssh_domain=config["ssh_domain"],
                    ssh_port=config.get("ssh_port", 22),
                    ssh_identity=config.get("ssh_identity"),
                )
            )
        return hosts
