import abc
class BaseTestGenerator(object):
    """
    Abstract class for Test Generator 
    """

    @abc.abstractmethod
    def generate_tests(self):
        raise NotImplementedError("Override this method to generate the test cases")

