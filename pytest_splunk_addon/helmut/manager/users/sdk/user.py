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

from pytest_splunk_addon.helmut.manager.users.user import User


class SDKUserWrapper(User):
    """
    The L{User} subclass corresponding to an User object in the
    Splunk Python SDK.
    """

    def __init__(self, sdk_connector, sdk_user, username=None):
        """
        SDKUserWrapper's constructor.

        @param username: The name of the User which this object represents.
        @type username: String
        @param sdk_connector: The connector which talks to Splunk through the
                              Splunk Python SDK.
        @type sdk_connector: SDKConnector
        @param sdk_user: The splunklib.Entity which represent an User in the
                         Python SDK.
        """
        if username is None:
            username = sdk_user.name
        super(SDKUserWrapper, self).__init__(username, sdk_connector)
        self._raw_sdk_user = sdk_user

    @property
    def raw_sdk_user(self):
        return self._raw_sdk_user

    @property
    def _service(self):
        """
        Return the service associated with
        """
        return self.connector.service

    def full_name(self):
        return self.raw_sdk_user.content.realname
