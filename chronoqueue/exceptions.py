class ChronoqueueError(Exception):
    """Base exception for Chronoqueue SDK."""

    pass


class ConnectionError(ChronoqueueError):
    """Raised when there's a connection issue."""

    pass


class InitializationError(ChronoqueueError):
    """Raised when there's an error during the SDK's initialization."""

    pass


class RpcOperationError(ChronoqueueError):
    """Raised when there's an error performing an RPC operation."""

    pass
