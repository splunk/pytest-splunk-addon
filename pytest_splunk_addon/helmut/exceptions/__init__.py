from httplib2 import HttpLib2Error


class UnsupportedConnectorError(BaseException):
    """
    Raised in manager_utils during creation of a Manager when the class type
    of the new Manager object is being determined. When mapping the class type
    of the connector currently in use to the appropriate and corresponding
    subclass of Manager associated with that connector type, this
    exception will be raised if the Manager has no subclasses associated with
    that connector type.

    Also raised during creation of a connector for a splunk instance if
    attempting to create a connector type which isn't supported or doesnt exist
    """

    def __init__(self, message=None):
        message = message or "The specified connector is not supported"
        super(UnsupportedConnectorError, self).__init__(message)


class InvalidFileModeError(BaseException):
    """
    When opening a steam to a file, if the file mode is invalid this exception
    will be raised.
    """

    def __init__(self, message="The specified file mode is invalid"):
        super(InvalidFileModeError, self).__init__(message)


class RetrieveError(RuntimeError):
    """
    Error raised when retrieving data over SSH.

    <i>NOTE</i>: If this exception is to be related to solely SSH
    communication, its name should be changed to reflect this.
    """

    pass


class SendError(RuntimeError):
    """
    Error raised when sending data over SSH.

    <i>NOTE</i>: If this exception is to be related to solely SSH
    communication, its name should be changed to reflect this.
    """

    pass


class AuthenticationError(HttpLib2Error):
    """
    Raised when a login request to Splunk fails.
    """

    pass


class ExpectedExceptionNotRaisedError(BaseException):
    """
    Raised when a expected exception is not raised
    """

    def __init__(self, err=None):
        """

        :param err: Expected Exception.
        :type err: Exception
        :return:
        """
        message = "Expected exception not raised: %s" % err
        super(ExpectedExceptionNotRaisedError, self).__init__(message)
