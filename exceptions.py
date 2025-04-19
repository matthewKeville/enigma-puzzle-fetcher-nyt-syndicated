import logging

class FetchError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class ArgsError(Exception):
    """Either arguments are wrong, or break internal rules"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class FetchMethodError(Exception):
    """Bad fetch method"""
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class UnsupportedFeatureError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class FetcherParseError(Exception):
    def __init__(self, message):
        super().__init__(message)
        self.message = message

class UnimplementedError(Exception):
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

