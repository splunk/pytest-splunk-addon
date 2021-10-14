#
# Copyright 2021 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
# http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#
"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

from abc import abstractmethod

from pytest_splunk_addon.helmut.manager.object import ItemFromManager
from pytest_splunk_addon.helmut.misc.collection import Collection


class Conf(ItemFromManager, Collection):
    """
    This class represents a .conf file in the Splunk system and is the subclass
    associated with the L{SDKConnector}. A Conf object holds Stanza objects
    that represent the .conf files content.

    See documentation for L{Confs} for more information.
    """

    def __init__(self, connector, conf_name):
        """
        The constructor for Conf.

        @param connector: The connector which is used to talk to Splunk.
        @type connector: L{Connector}
        @param conf_name: The name of the conf file to be created. The suffix
                            .conf does not need to be specified here.
        @type conf_name: String
        """
        ItemFromManager.__init__(self, connector)
        Collection.__init__(self)
        self._name = conf_name

    @property
    def name(self):
        return self._name

    @abstractmethod
    def __getitem__(self, stanza_name):
        """
        Fetch a stanza.

        @param stanza_name: Name of the stanza to fetch.
        type stanza_name: String
        """
        pass

    @abstractmethod
    def items(self):
        pass

    @abstractmethod
    def create_stanza(self, stanza_name, values=None):
        """
        Create stanza in conf-file. Do nothing if stanza exists.

        @param stanza_name: The name of the stanza to create.
        @type stanza_name: String.
        """
        pass

    @abstractmethod
    def delete_stanza(self, stanza_name):
        """
        Delete stanza in conf-file. If stanza doesn't exist, do nothing.

        @param stanza_name: The name of the stanza to remove.
        @type stanza_name: String.
        """
        pass

    def __contains__(self, stanza_name):
        for stanza in self:
            if stanza.name == stanza_name:
                return True
        return False
