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
Created on Jul 18, 2012

@author: parhamfh
"""


class StanzaNotFound(RuntimeError):
    """
    Raised when a conf file does not contain the specified stanza.

    @ivar conf: The name of the conf file.
    @ivar stanza: The name of the stanza.
    """

    def __init__(self, conf, stanza):
        """
        Creates a new exception.

        @param conf: The name of conf file.
        @type conf: str
        @param stanza: The name of stanza.
        @type stanza: str
        """
        self.conf = conf
        self.stanza = stanza
        super(StanzaNotFound, self).__init__(self._error_message)

    @property
    def _error_message(self):
        """
        The error message for this exception.

        @rtype: str
        """
        msg = "Stanza '{stanza}' doesn't exist in conf-file '{conf}.conf'"
        return msg.format(stanza=self.stanza, conf=self.conf)
