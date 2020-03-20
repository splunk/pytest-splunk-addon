"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.manager.users import UserNotFound
from pytest_splunk_addon.helmut.manager.users import Users
from pytest_splunk_addon.helmut.manager.users.sdk.user import SDKUserWrapper


class SDKUsersWrapper(Users):
    """
    The Users subclass that wraps the Splunk Python SDK's Users object.
    It basically contains a collection of L{SDKUserWrapper}s.
    """

    @property
    def _service(self):
        return self.connector.service

    def create_user(self, username, password, roles, **kwargs):
        self.logger.info(
            "Creating user. Username: %s. Password: %s. Role: %s"
            % (username, password, roles)
        )
        try:
            kwargs["password"] = password
            kwargs["roles"] = roles

            return SDKUserWrapper(
                username, self.connector.service.users.create(username, **kwargs)
            )
        except HTTPError as err:
            # User already exists
            if not err.status == 400:
                raise
            self.logger.warn("User already exists. HTTPError: %s" % err)

    def delete_user(self, user_or_username):
        """
        Delete an user.

        @param user_name: The name of the user to be deleted or a SDKUserWrapper
                          object.
        @type user_name: String or SDKUserWrapper
        """
        # If attribute name exists it is (probably) a SDKUserWrapper object
        try:
            username = user_or_username.name
        # If not it is (hopefully) the name of the User
        except AttributeError:
            self.logger.debug(
                "Value given to delete_user() had no attribute"
                " 'name'. Assuming it is of type 'str'."
            )
            username = user_or_username
        self.logger.info("Deleting user %s." % username)
        self.connector.service.users.delete(username)

    def __getitem__(self, username):
        for user in self:
            if user.name == username:
                return user
        raise UserNotFound(username)

    def __contains__(self, username):
        for user in self:
            if user.name == username:
                return True
        return False

    def items(self):
        users = self._service.users
        return [SDKUserWrapper(self.connector, user) for user in users]
