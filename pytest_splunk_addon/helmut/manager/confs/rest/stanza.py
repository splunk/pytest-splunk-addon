"""
@author: Lei Zhang
@contact: U{leiz@splunk.com<mailto:leiz@splunk.com>}
@since: 2018-05-01
"""
from pytest_splunk_addon.helmut.exceptions.confs import StanzaNotFound
from pytest_splunk_addon.helmut.manager.confs.stanza import Stanza
from pytest_splunk_addon.helmut.util.string_unicode_convert import normalize_to_unicode


class RESTStanzaWrapper(Stanza):
    """
        This class is the associated subclass of Stanza to the L{RESTConnector}.
        This represents and wraps a Stanza object using the Splunk REST API.
    """

    def __init__(self, rest_conf, rest_stanza):
        super(RESTStanzaWrapper, self).__init__(rest_conf, rest_stanza.name)
        self._raw_rest_stanza = rest_stanza

    @property
    def raw_rest_stanza(self):
        return self._raw_rest_stanza

    @property
    def raw_rest_conf(self):
        return self.conf.raw_rest_conf

    def items(self):
        return self.raw_rest_stanza.content

    def __setitem__(self, key, value):
        key = normalize_to_unicode(key)
        value = normalize_to_unicode(value)
        try:
            self.logger.info(
                "Setting key '%s' to '%s' in stanza '%s' "
                "in %s.conf." % (key, value, self.name, self.conf_name)
            )
            # Update takes positional arguments and we send a dictionary so
            # if written update(key=value) field 'key' in stanza will get value
            self.raw_rest_stanza.update(**{key: value})
            self.raw_rest_stanza.refresh()

        except StanzaNotFound as s:
            self.logger.warn(s)
            raise

    def delete_value(self, key):
        key = normalize_to_unicode(key)
        try:
            self.logger.info(
                "Deleting key %s in stanza '%s' in %s.conf."
                % (key, self.name, self.conf_name)
            )
            # Update takes positional arguments and we send a dictionary
            # If written update(key=value) field 'key' in stanza will get value
            self.raw_rest_stanza.update(**{key: ""})
            self.raw_rest_stanza.refresh()

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
