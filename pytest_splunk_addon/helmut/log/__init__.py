"""
Created on Jun 15, 2012

@author: parhamfh
"""

import datetime
import logging
import logging.config
import os
from builtins import object
from logging import Formatter

from future.utils import with_metaclass

_LOG_FORMAT = "[%(asctime)s] %(levelname)s - %(name)s: %(message)s"
_DATE_FORMAT = "%Y-%m-%d %H:%M:%S.%f"
_FILE_NAME = "..log"


def setup_logger():
    """
    Setups up the logging library
    """
    logging_conf = os.path.join(
        os.path.dirname(os.path.abspath(__file__)), "logging.conf"
    )
    logging.config.fileConfig(logging_conf)


class HelmutFormatter(Formatter):

    # Disabling error b/c function overrides old style Python function
    # pylint: disable=C0103
    def formatTime(self, record, datefmt=None):
        t = datetime.datetime.now()
        # The [:-3] is put there to trim the last three digits of the
        # microseconds, remove it if you intend to remove microseconds
        # from the _DATE_FORMAT
        return t.strftime(_DATE_FORMAT)[:-3]


from abc import ABCMeta


class Logging(with_metaclass(ABCMeta, object)):
    def __init__(self):
        self._logger = self._get_logger()
        super(Logging, self).__init__()

    def _get_logger(self):
        """
        Creates a new logger for this instance, should only be called once.

        @return: The newly created logger.
        """
        return logging.getLogger(self._logger_name)

    @property
    def _logger_name(self):
        """
        The name of the logger.

        @rtype: str
        """
        return self.__class__.__name__

    @property
    def logger(self):
        """
        The logger of this Splunk object.

        @return: The associated logger.
        """
        return self._logger
