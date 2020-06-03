import abc


class BaseTable(abc.ABC):
    """
    Interface for CIM report.
    """

    @abc.abstractmethod
    def __init__(self, table_title, header_list):
        pass

    @abc.abstractmethod
    def set_description(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def add_row(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def set_note(self, string):
        raise NotImplementedError()

    @abc.abstractmethod
    def return_table_str(self):
        raise NotImplementedError()
