"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.roles import RoleNotFound
from pytest_splunk_addon.helmut.manager.roles import Roles
from pytest_splunk_addon.helmut.manager.roles.sdk.role import SDKRoleWrapper


class SDKRolesWrapper(Roles):
    """
    The Roles subclass that wraps the Splunk Python SDK's Roles object.
    It basically contains a collection of L{SDKRoleWrapper}s.

    As a part of 6.3, copy_role returns disabled parameter. This param is not supported when making a REST call to authorization/roles to update a role
    Hence, deleting this param from copied_role
    """

    @property
    def _service(self):
        return self.connector.service

    def create_role(self, role_name, parent_role_name=None):
        try:
            self.logger.info("Creating role %s" % role_name)
            self._service.roles.create(role_name)
            if not parent_role_name:
                return
            copied_role = self[parent_role_name].raw_sdk_role.content

            for key, value in list(copied_role.items()):
                if "imported_" in key or value is None:
                    copied_role.pop(key)
                    if "imported_capabilities" == key:
                        copied_role["capabilities"] += value

                if "disabled" in key:
                    del copied_role["content"]["disabled"]

            self._service.roles[role_name].update(**copied_role)
        except HTTPError as err:
            # Role already exists
            if not err.status == 409:
                raise
            self.logger.warn(
                "Role %s already existed. HTTPError: %s" % (role_name, err)
            )

    def delete_role(self, role_name):
        self.logger.info("Deleting role %s" % role_name)
        self._service.roles.delete(role_name)

    def update_role(self, role_name, **kwargs):
        self.logger.info("Updating role %s with: %s" % (role_name, kwargs))
        self._service.roles[role_name].update(**kwargs).refresh()

    def __getitem__(self, role_name):
        for role in self:
            if role.name == role_name:
                return role
        raise RoleNotFound(role_name)

    def __contains__(self, role_name):
        for role in self:
            if role.name == role_name:
                return True
        return False

    def items(self):
        roles = self._service.roles
        return [SDKRoleWrapper(self.connector, role) for role in roles]
