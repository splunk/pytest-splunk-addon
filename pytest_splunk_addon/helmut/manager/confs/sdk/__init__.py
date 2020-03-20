"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from pytest_splunk_addon.helmut.manager.confs import Confs
from pytest_splunk_addon.helmut.manager.confs.sdk.conf import SDKConfWrapper


class SDKConfsWrapper(Confs):
    """
    The Confs subclass that is associated with the SDKConnector.
    It wraps the Splunk Python SDK's Confs object and contains a collection of
    L{SDKConfWrapper}s.
    """

    @property
    def _service(self):
        return self.connector.service

    def __getitem__(self, conf_name):
        for conf in self:
            if conf.name == conf_name:
                return conf
        raise ConfNotFound(conf_name)

    def create(self, conf_name):
        if conf_name in self:
            self.logger.info("conf file '%s' already existed" % conf_name)
            return

        self.logger.info("Creating conf file %s" % conf_name)
        return SDKConfWrapper(self.connector, self._service.confs.create(conf_name))

    def items(self):
        conf_names = self._service.confs.list()
        #        for c in conf_names:
        #            print c.name
        return [SDKConfWrapper(self.connector, conf_name) for conf_name in conf_names]


class ConfNotFound(RuntimeError):
    """
    Raised when a conf file that does not exist is read from.

    @ivar conf: The name of the conf that did not exist.
    """

    def __init__(self, conf):
        """
        Creates a new exception.

        @param conf: The name of the conf file that was missing.
        """
        self.conf = conf
        super(ConfNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        """
        The error message for this exception.

        @rtype: str
        """
        msg = "The conf file {conf}.conf doesn't exist"
        return msg.format(conf=self.conf)
