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
import datetime
import logging
import logging.config
from logging import FileHandler, Formatter

_LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
_FILE_NAME = "helmut.log"


def setup_logger(debug=False):
    """
    Setups up the logging library

    @param debug: If debug log messages are to be outputted
    @type debug: bool
    """
    logger = logging.getLogger("helmut")
    handler = FileHandler(filename=_FILE_NAME)
    handler.setFormatter(HelmutFormatter(_LOG_FORMAT))
    level = logging.DEBUG if debug else logging.INFO
    logger.addHandler(handler)
    logger.setLevel(level)
    logger.debug("Logger: DEBUG logging is enabled")


class HelmutFormatter(Formatter):

    # Disabling error b/c function overrides old style Python function
    # pylint: disable=C0103
    def formatTime(self, record, datefmt=None):
        t = datetime.datetime.now()
        # The [:-3] is put there to trim the last three digits of the
        # microseconds, remove it if you intend to remove microseconds
        # from the _DATE_FORMAT
        return t.strftime(_DATE_FORMAT)[:-3]
