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


class User(ItemFromManager):
    """
    A User is the means by which you login to Splunk via.
    This class represents a User object and the different
    functions you have to manipulate that User object.
    """

    def __init__(self, username, connector):
        """
        The constructor of the User class.

        @param username: The username of the Splunk User
        @type username: String
        @param connector: The connector which talks to Splunk.
        @type connector: _Connector
        """
        self._name = username
        super(User, self).__init__(connector)

    @abstractmethod
    def full_name(self):
        pass

    @property
    def name(self):
        """
        The name of the user.
        """
        return self._name
