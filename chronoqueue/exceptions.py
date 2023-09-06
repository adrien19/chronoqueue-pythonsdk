class ChronoqueueException(Exception):
    """Base exception for Chronoqueue SDK."""
    pass

class ConnectionException(ChronoqueueException):
    """Raised when there's a connection issue."""
    pass

# Other custom exceptions can be added similarly...