import abc


class EventIngestor(abc.ABC):
    """
    Base class for event ingestor.
    """

    @abc.abstractmethod
    def __init__(self, uri, token):
        pass

    @abc.abstractmethod
    def ingest(self, data):
        raise NotImplementedError
