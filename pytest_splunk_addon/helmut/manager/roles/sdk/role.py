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

from pytest_splunk_addon.helmut.manager.roles.role import Role


class SDKRoleWrapper(Role):
    """
    The L{Role} subclass corresponding to an Role object in the
    Splunk Python SDK.
    """

    def __init__(self, sdk_connector, sdk_role):
        """
        SDKRoleWrapper's constructor.

        @param sdk_connector: The connector which talks to Splunk through the
                              Splunk Python SDK.
        @type sdk_connector: SDKConnector
        @param sdk_role: The name of the new role.
        @type sdk_role: String
        """
        super(SDKRoleWrapper, self).__init__(sdk_connector)
        self._raw_sdk_role = sdk_role

    @property
    def raw_sdk_role(self):
        return self._raw_sdk_role

    @property
    def _service(self):
        """
        Return the service associated with
        """
        return self.connector.service

    @property
    def name(self):
        """
        The name of the role.
        """
        return self.raw_sdk_role.name

    def edit(self, **kwargs):
        self.logger.info("Editing role %s with: %s" % (self.name, kwargs))
        self.raw_sdk_role.update(**kwargs).refresh()
