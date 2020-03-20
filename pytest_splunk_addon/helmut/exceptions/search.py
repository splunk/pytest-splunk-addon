class SearchFailure(RuntimeError):
    """
    This exception is raised when a search fails and returns the error through sdk get_message function.
    """

    def __init__(self, search_message):
        self.search_message = search_message
        super(SearchFailure, self).__init__(self._error_message)

    @property
    def _error_message(self):
        message = "Search failed with Error: {0}"
        return message.format(self.search_message)
