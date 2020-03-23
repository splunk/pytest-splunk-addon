"""
Summary
=======
A module which deals with a Splunk app
"""

import logging
import os
from builtins import object

from pytest_splunk_addon.helmut.manager.confs import Confs


class App(object):
    """
    A representation of a Splunk Application

    @ivar __logger: The logger we use
    @ivar _required_indexes: Sub classes can indexes to this list and they will
                             be added as part of the setup. The indexes must be
                             know by the filegetter.py, the format of each
                             entry is a dictionary with the same parameters as
                             the filegetter.get_file method.
    @ivar _required_configs: A list of paths to config files that should be
                             copied to the app's local config directory as part
                             of the setup
    @ivar _required_lookups: A list of paths to lookup files that should be
                             copied to the app's lookup directory as part of
                             the setup
    @ivar _name: The name of this app
    @ivar _splunk: The splunk instance this app belongs to
    @ivar _config_manager: The config manager for this app
    @ivar _shared_service: The shared service for this app.
    @ivar package: The package this app will be installed from or None if not
                   package exists.
    """

    DEFAULT_NAMESPACE = "nobody:{app_name}"

    def __init__(self, name, splunk, package=None):
        """
        Constructs this app

        @param name: The name of the app, should be all lower case.
        @type name: str

        @param splunk: The splunk instance this app belongs to.
        @type splunk: Splunk

        @param package: An optional path to any package this app can be
                        installed from
        @type package: str
        """
        super(App, self).__init__()

        self.__logger = logging.getLogger("App-{0}".format(name))

        self._name = name
        self._splunk = splunk
        self._confs = None

        self.package = package

    @property
    def confs(self):
        """
        The confs manager that is used for this app.

        The manager will have a namespace that has the app portion set to this
        app.

        @rtype: L{Confs}
        """
        if self._confs is None:
            self._confs = self._create_confs_manager()
        return self._confs

    def _create_confs_manager(self):
        """
        Creates a confs manager for this app.

        It uses the same connector factory as the Splunk instance.

        @return: The newly created confs manager.
        @rtype: L{Confs}
        """
        return Confs(self.splunk.default_connector)

    @property
    def namespace(self):
        """
        The namespace for this app.

        @rtype: str
        """
        return self.DEFAULT_NAMESPACE.format(app_name=self._name)

    @confs.setter
    def confs(self, value):
        """
        Updates the confs manager for this app.

        @param value: The new manager.
        @type value: L{Confs}
        """
        self._confs = value

    @property
    def installed(self):
        """
        Checks too see whether this app is already installed or not.

        It does this by checking if the directory exists which means that there
        is no guarantee that it was installed this session.

        @rtype: bool
        """
        return self.splunk.has_app(self.name)

    @property
    def name(self):
        """
        The name for this app

        @rtype: str
        """
        return self._name

    @property
    def splunk(self):
        """
        The Splunk instance this app belongs to

        @rtype: L{Splunk}
        """
        return self._splunk

    @property
    def apps_dir(self):
        """
        The path to the directory that splunk stores it's apps

        @rtype: str
        """
        return self.splunk.apps_dir

    @property
    def install_path(self):
        """
        The path to the directory where this app will be/is installed

        @rtype: str
        """
        return os.path.join(self.apps_dir, self.name)

    def can_install(self):
        """
        Checks if this app can be installed meaning if a package has been
        supplied.

        @rtype: bool
        @return: True if this app can be installed
        """
        return self.package is not None

    def install(self):
        """
        Installs this app.

        @rtype: bool
        @return: True if the app was installed and splunk needs to restart
        """
        self._verify_can_install()
        return self.splunk.install_app(self.name, self.package)

    def _verify_can_install(self):
        """
        Checks that this app can be installed and raising an exception if it
        can't.

        @raise AppHasNoPackage: If the app can't be installed.
        """
        if not self.package:
            raise AppHasNoPackage(self.name)

    def uninstall(self):
        """
        Uninstalls this app

        @rtype: bool
        @return: True if the app was installed and has now been removed
        """
        return self.splunk.uninstall_app(self.name)


class AppHasNoPackage(RuntimeError):
    def __init__(self, app_name):
        msg = "The app {0} has no package to install from".format(app_name)
        super(AppHasNoPackage, self).__init__(msg)
