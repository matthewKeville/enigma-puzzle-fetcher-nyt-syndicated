import logging

# Global


class UnimplementedError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class SchemaBuildError(Exception):
    def __init__(self, message, original_exception=None):
        super().__init__(message)
        self.original_exception = original_exception
        self.message = message


# Fetch


class FetchError(Exception):
    """Base error for fetch request"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


class FetchArgsError(FetchError):
    """Bad args for fetch method"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class FetchMethodError(FetchError):
    """Bad fetch method in fetch-request-body"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class FetchParsingError(FetchError):
    """Unable to parse crossword data"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message


class FetchUnsupportedError(FetchError):
    """Unable to parse crossword data due to unsupported features"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

# Args


class ArgsError(Exception):
    """Base error for args request"""

    def __init__(self, message):
        super().__init__(message)
        self.message = message


def logAndRaise(exception, message):
    """
        Log a message and raise an exception
        with the exception = Exception class
        or if the exception is an exception instance
        just reraise the exception.

        TODO: and an optional method parameter to specify the logging level
        I want critical errors to be logged as such
    """
    logging.error(message)
    if isinstance(exception, type):
        raise exception(message)
    else:
        raise exception
