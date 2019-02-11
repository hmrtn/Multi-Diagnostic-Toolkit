class Error(Exception):
    """Base class for exceptions in this module."""
    pass

class NotImplementedError(Error):
    """Exception raised due to feature not yet being implemented.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
