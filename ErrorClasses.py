"""Error Classes Module

This module contains the author-defined error classes used elsewhere in the
program.
"""

__author__ = 'Kaito Durkee'

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

class FileError(Error):
    """Exception raised due to file not being found.

    Attributes:
        message -- explanation of the error
    """

    def __init__(self, message):
        self.message = message
