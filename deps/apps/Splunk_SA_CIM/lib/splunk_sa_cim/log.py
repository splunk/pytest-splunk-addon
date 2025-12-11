import logging
import logging.handlers
import time

from splunk.clilib.bundle_paths import make_splunkhome_path

DEFAULT_FORMAT = '%(asctime)s %(levelname)s pid=%(process)d tid=%(threadName)s file=%(filename)s:%(funcName)s:%(lineno)d | %(message)s'
SHORT_FORMAT = '%(asctime)s %(levelname)s %(message)s'


class GMTimeFormatter(logging.Formatter):
    ''' An extension to the logging.Formatter base class
    Hardcodes "+0000" into default datefmt
    Use in conjunction with ModularActionFormatter.converter = time.gmtime
    '''
    converter = time.gmtime

    def formatTime(self, record, datefmt=None):
        '''
        Return the creation time of the specified LogRecord as formatted text.

        This method should be called from format() by a formatter which
        wants to make use of a formatted time. This method can be overridden
        in formatters to provide for any specific requirement, but the
        basic behaviour is as follows: if datefmt (a string) is specified,
        it is used with time.strftime() to format the creation time of the
        record. Otherwise, the ISO8601 format is used. The resulting
        string is returned. This function assumes time.gmtime() as the
        'converter' attribute in the Formatter class.
        '''
        ct = self.converter(record.created)
        if datefmt:
            s = time.strftime(datefmt, ct)
        else:
            t = time.strftime('%Y-%m-%d %H:%M:%S', ct)
            s = '%s,%03d+0000' % (t, record.msecs)
        return s


def setup_logger(
        name,
        level=logging.INFO,
        maxBytes=25000000,
        backupCount=5,
        fmt=DEFAULT_FORMAT):
    '''
    Set up a default logger.

    :param name: The log file name.
    :param level: The logging level.
    :param maxBytes: The maximum log file size before rollover.
    :param backupCount: The number of log files to retain.
    '''
    logfile = make_splunkhome_path(['var', 'log', 'splunk', name + '.log'])
    loginst = logging.getLogger(name)
    loginst.setLevel(level)
    # Prevent the log messages from being duplicated in the python.log file
    loginst.propagate = False

    # Prevent re-adding handlers to the logger object,
    # which can cause duplicate log lines.
    handler_exists = any(
        [True for h in loginst.handlers if h.baseFilename == logfile])
    if not handler_exists:
        file_handler = logging.handlers.RotatingFileHandler(
            logfile, maxBytes=maxBytes, backupCount=backupCount)
        formatter = GMTimeFormatter(fmt)
        file_handler.setFormatter(formatter)
        loginst.addHandler(file_handler)

    return loginst
