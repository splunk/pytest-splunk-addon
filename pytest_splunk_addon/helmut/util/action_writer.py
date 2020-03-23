"""
Module for writing actions to the user.
Mostly used for coreapps

Summary
=======
It's used to print actions that look like this::

    Action1... done
    Action2...
        Action3... done
        Action4... done
    done
    Action5... failed

@author: Nicklas Ansman-Giertz
@contact: U{ngiertz@splunk.com<mailto:ngiertz@splunk.com>}
@since: 2011-11-23
"""

import sys
from builtins import range

_LAST_OPENED = 0
_LAST_CLOSED = 0
_LEVEL = 0

LOG_ONLY = True


def write_action(action, logger=None, logger_msg=None):
    """
    Writes the specified action to stdout.

    Writes the action appended by '... '

    @type action: str
    @param action: The action to write

    @type logger_msg: str
    @param logger_msg: If specified this message will be written to the
                       logger instead of action
    """
    if not LOG_ONLY:
        global _LEVEL, _LAST_OPENED
        # If there is one currently open print newline
        if _LEVEL > _LAST_OPENED:
            sys.stdout.write("\n")

        # Print tabs
        for _index in range(_LEVEL):
            sys.stdout.write("\t")

        sys.stdout.write(action + "... ")
        sys.stdout.flush()
    if logger:
        logger.info(logger_msg or action)

    _LAST_OPENED = _LEVEL
    _LEVEL += 1


def write_done():
    """
    Tells the user that we're done with the previous action.
    Does not print to the logger
    """
    if not LOG_ONLY:
        global _LEVEL, _LAST_CLOSED
        _LEVEL -= 1

        # If there has been actions in between, write tabs
        if _LAST_CLOSED > _LEVEL:
            for _index in range(_LEVEL):
                sys.stdout.write("\t")

        sys.stdout.write("done!\n")

        _LAST_CLOSED = _LEVEL
        sys.stdout.flush()


def write_failed(logger=None, msg=None):
    """
    Tells the user that the last action failed and raises an exception.

    If msg is an exception it will be raised, if it's a string an Exception
    will be raised.
    If unspecified a generic fail message is thrown

    @type msg: str
    @param msg: An optional fail message
    """
    if not LOG_ONLY:
        global _LEVEL
        msg = msg or "Testing failed, check your logs for more info"

        _LEVEL -= 1

        if _LAST_CLOSED > _LEVEL:
            for _index in range(_LEVEL):
                sys.stdout.write("\t")

        sys.stdout.write("failed!\n")
        sys.stdout.flush()

    if logger:
        logger.exception(msg)

    if isinstance(msg, Exception):
        raise
    raise Exception(msg)
