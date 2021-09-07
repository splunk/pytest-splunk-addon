class AttrDict(dict):
    """A dictionary for which keys are also accessible as attributes."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.__dict__ = self
