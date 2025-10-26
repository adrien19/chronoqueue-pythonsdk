"""
Chronoqueue Python SDK

A Python client library for interacting with the Chronoqueue distributed task queue service.

Basic Usage:
    >>> from chronoqueue import ChronoqueueClient
    >>> from chronoqueue.utils import PostMessageParams
    >>>
    >>> client = ChronoqueueClient(host='localhost', port=50051, use_tls=False)
    >>> client.create_queue(name="my_queue")
    >>> params = PostMessageParams(message_id="123", data={"key": "value"}, queue_name="my_queue")
    >>> response = client.post_message(params)
    >>> msg = response.to_dict()  # Legacy dict output
    >>> # Or with Pydantic (requires: pip install pydantic)
    >>> msg = response.to_model()  # Typed model output

For more information, see the documentation at:
https://github.com/adrien19/chronoqueue-pythonsdk
"""

from .client import ChronoqueueClient
from .exceptions import InitializationError, RpcOperationError
from .utils import (
    AcknowledgeMessageParams,
    MessageState,
    PeekQueueMessagesParams,
    PostMessageOptions,
    PostMessageParams,
    QueueOptions,
    QueueType,
    ResponseWrapper,
    TlsConfig,
)

# Optionally export Pydantic models if available
try:
    from . import models
    from .models import (
        AcknowledgeMessageResponse,
        CreateQueueResponse,
        DeleteQueueResponse,
        GetNextMessageResponse,
        GetQueueStateResponse,
        Message,
        MessageMetadata,
        MessagePayload,
        PeekQueueMessagesResponse,
        PostMessageResponse,
        RenewMessageLeaseResponse,
        SendMessageHeartBeatResponse,
    )

    __all__ = [
        # Client
        "ChronoqueueClient",
        # Utils and params
        "TlsConfig",
        "PostMessageParams",
        "PostMessageOptions",
        "AcknowledgeMessageParams",
        "PeekQueueMessagesParams",
        "QueueOptions",
        "QueueType",
        "MessageState",
        "ResponseWrapper",
        # Exceptions
        "InitializationError",
        "RpcOperationError",
        # Pydantic models (optional)
        "CreateQueueResponse",
        "DeleteQueueResponse",
        "PostMessageResponse",
        "GetNextMessageResponse",
        "AcknowledgeMessageResponse",
        "RenewMessageLeaseResponse",
        "PeekQueueMessagesResponse",
        "GetQueueStateResponse",
        "SendMessageHeartBeatResponse",
        "Message",
        "MessageMetadata",
        "MessagePayload",
        "models",
    ]
except ImportError:
    # Pydantic not available - export only non-model types
    __all__ = [
        # Client
        "ChronoqueueClient",
        # Utils and params
        "TlsConfig",
        "PostMessageParams",
        "PostMessageOptions",
        "AcknowledgeMessageParams",
        "PeekQueueMessagesParams",
        "QueueOptions",
        "QueueType",
        "MessageState",
        "ResponseWrapper",
        # Exceptions
        "InitializationError",
        "RpcOperationError",
    ]

__version__ = "0.1.0"
