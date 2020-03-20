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
