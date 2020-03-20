"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from splunklib.client import HTTPError

from pytest_splunk_addon.helmut.exceptions.confs import StanzaNotFound
from pytest_splunk_addon.helmut.manager.confs.conf import Conf
from pytest_splunk_addon.helmut.manager.confs.sdk.stanza import SDKStanzaWrapper


class SDKConfWrapper(Conf):
    """
    The L{Conf} object corresponding to a Conf object in the Splunk Python SDK.
    It holds a set of L{SDKStanzaWrapper}s.
    """

    def __init__(self, sdk_connector, sdk_conf):
        super(SDKConfWrapper, self).__init__(sdk_connector, sdk_conf.name)
        self._raw_sdk_conf = sdk_conf

    @property
    def _service(self):
        return self.connector.service

    @property
    def raw_sdk_conf(self):
        return self._raw_sdk_conf

    @property
    def _path(self):
        return self._raw_sdk_conf.path

    def __getitem__(self, stanza_name):
        for stanza in self:
            if stanza.name == stanza_name:
                return stanza
        raise StanzaNotFound(self.name, stanza_name)

    def items(self):
        stanzas = self._service.confs[self.name].list()
        return [SDKStanzaWrapper(self, stanza) for stanza in stanzas]

    def create_stanza(self, stanza_name, values=None):
        values = values or {}
        try:
            self.logger.info(
                "Creating stanza '%s' in %s.conf with values:"
                " %s." % (stanza_name, self.name, values)
            )
            return SDKStanzaWrapper(
                self, self.raw_sdk_conf.create(stanza_name, **values)
            )
        except HTTPError as h:
            self.logger.warn(
                "Stanza '%s' already existed in %s.conf. "
                "HTTPError message: %s" % (stanza_name, self.name, h)
            )
            return self[stanza_name]
        except Exception:
            raise

    def delete_stanza(self, stanza_name):
        try:
            self.logger.info(
                "Deleting stanza '%s' in %s.conf" % (stanza_name, self.name)
            )
            self.raw_sdk_conf.delete(stanza_name)
        except HTTPError as h:
            self.logger.warn("Error during deletion: %s" % h)
        except Exception:
            raise
