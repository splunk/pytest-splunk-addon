"""
@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""
from pytest_splunk_addon.helmut.exceptions.confs import StanzaNotFound
from pytest_splunk_addon.helmut.manager.confs.stanza import Stanza


class SDKStanzaWrapper(Stanza):
    """
    This class is the associated subclass of Stanza to the L{SDKConnector}.
    This represents and wraps a Stanza object in the Splunk Python SDK.
    """

    def __init__(self, sdk_conf, sdk_stanza):
        super(SDKStanzaWrapper, self).__init__(sdk_conf, sdk_stanza.name)
        self._raw_sdk_stanza = sdk_stanza

    @property
    def raw_sdk_stanza(self):
        return self._raw_sdk_stanza

    @property
    def raw_sdk_conf(self):
        return self.conf.raw_sdk_conf

    @property
    def _service(self):
        return self.connector.service

    def items(self):
        #        return self.raw_sdk_stanza.read()['content']
        return self.raw_sdk_stanza.content

    def __setitem__(self, key, value):
        try:
            self.logger.info(
                "Setting key '%s' to '%s' in stanza '%s' "
                "in %s.conf." % (key, value, self.name, self.conf_name)
            )
            # Update takes positional arguments and we send a dictionary so
            # if written update(key=value) field 'key' in stanza will get value
            self.raw_sdk_stanza.update(**{key: value})
            self.raw_sdk_stanza.refresh()

        except StanzaNotFound as s:
            self.logger.warn(s)
            raise

    def delete_value(self, key):
        try:
            self.logger.info(
                "Deleting key %s in stanza '%s' in %s.conf."
                % (key, self.name, self.conf_name)
            )
            # Update takes positional arguments and we send a dictionary
            # If written update(key=value) field 'key' in stanza will get value
            self.raw_sdk_stanza.update(**{key: ""})
            self.raw_sdk_stanza.refresh()

            # If key has value '' or None when fetched return True
            if self[key] is None or self[key] == "":
                return True

            # Something is wrong since the key still contains _some_ value
            raise RuntimeError(
                "delete_value(%s, %s, %s) did not properly"
                " delete value. unexpected value in self[%s]: "
                "%s" % (key, self.name, self.conf_name, key, self[key])
            )
        except StanzaNotFound as s:
            self.logger.warn(s)
            raise
