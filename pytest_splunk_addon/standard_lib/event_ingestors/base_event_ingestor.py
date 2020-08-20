import abc


class EventIngestor(abc.ABC):
    """
    Base class for event ingestor.
    """

    @abc.abstractmethod
    def __init__(self, required_configs):
        pass

    @abc.abstractmethod
    def ingest(self, event_object, thread_count):
        raise NotImplementedError
