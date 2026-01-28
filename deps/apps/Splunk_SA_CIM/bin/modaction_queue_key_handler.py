# Copyright 2026 Splunk Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

import binascii

try:
    import http.client as http_client
except ImportError:
    import httplib as http_client
import json
import os
import operator
import sys

from splunk import RESTException
from splunk.clilib.bundle_paths import make_splunkhome_path
from splunk.persistconn.application import PersistentServerConnectionApplication

sys.path.append(make_splunkhome_path(["etc", "apps", "Splunk_SA_CIM", "lib"]))
from splunk_sa_cim.log import setup_logger
from splunk_sa_cim.modaction_queue import ModularActionQutils

logger = setup_logger("modaction_queue_handler")


class ModularActionQueueKeyHandler(PersistentServerConnectionApplication):
    """REST handler for generating modular action queue api keys."""

    def __init__(self, command_line, command_arg):
        super(ModularActionQueueKeyHandler, self).__init__()

        try:
            params = json.loads(command_arg)
        except Exception as e:
            logger.warn(e)
            params = {}

        ModularActionQutils.set_log_level(logger, params)

        self.modaction_qutils = ModularActionQutils(logger, None)

    def handle(self, args):
        """Main function for REST call.

        :param args:
            A JSON string representing a dictionary of arguments
            to the REST call.
        :type args: str

        :return A valid REST response.
        :rtype dict

        - Routing of GET, POST, etc. happens here.
        - All exceptions should be caught here.
        """

        logger.debug("ARGS: %s", args)
        args = json.loads(args)

        try:
            logger.info("Handling %s request.", args["method"])
            method = "handle_" + args["method"].lower()
            if callable(getattr(self, method, None)):
                return operator.methodcaller(method, args)(self)
            else:
                return self.modaction_qutils.error(
                    "Invalid method for this endpoint", http_client.METHOD_NOT_ALLOWED
                )
        except RESTException as e:
            return self.modaction_qutils.error(
                "RESTexception: %s" % e, http_client.INTERNAL_SERVER_ERROR
            )
        except Exception as e:
            msg = "Unknown exception: %s" % e
            logger.exception(msg)
            return self.modaction_qutils.error(msg, http_client.INTERNAL_SERVER_ERROR)

    def handle_get(self, args):
        """Main function for REST call.

        :param args:
            A JSON string representing a dictionary of arguments
            to the REST call.
        :type args: str

        :return A valid REST response.
        :rtype dict

        - Routing of GET, POST, etc. happens here.
        - All exceptions should be caught here.
        """
        return {
            "status": http_client.OK,
            "payload": binascii.hexlify(os.urandom(64)).decode("utf-8"),
        }
