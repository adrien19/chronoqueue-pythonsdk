import re
from dataclasses import dataclass, field
from typing import Optional, Dict, Any, Callable
from enum import Enum
from google.protobuf.duration_pb2 import Duration
from google.protobuf.struct_pb2 import Value, Struct
from google.protobuf import json_format
from .api.message.v1.message_pb2 import Message
from .api.queue.v1.queue_pb2 import QueueType
from .api.common.v1.common_pb2 import Payload
from .api.queueservice.v1.request_response_pb2 import PostMessageRequest


@dataclass
class TlsConfig:
    """
    TlsConfig represents the configuration required for setting up a secure TLS connection.
    
    Attributes:
        ca_path (str): Path to the Certificate Authority (CA) certificate.
        client_crt_path (str): Path to the client's certificate.
        client_key_path (str): Path to the client's private key.
    """
    ca_path: str
    client_crt_path: str
    client_key_path: str

class MessageState(Enum):
    """
    Enumeration representing the possible states of a message in Chronoqueue.

    Attributes:
    ----------
    INVISIBLE : MessageState
        Message is not visible for processing.
    PENDING : MessageState
        Message is pending and waiting for processing.
    RUNNING : MessageState
        Message is currently being processed.
    COMPLETED : MessageState
        Message processing has completed.
    CANCELED : MessageState
        Message processing was canceled.
    ERRORED : MessageState
        An error occurred during message processing.
    """
    INVISIBLE = Message.Metadata.State.INVISIBLE
    PENDING = Message.Metadata.State.PENDING
    RUNNING = Message.Metadata.State.RUNNING
    COMPLETED = Message.Metadata.State.COMPLETED
    CANCELED = Message.Metadata.State.CANCELED
    ERRORED = Message.Metadata.State.ERRORED


def string_to_duration(s: str) -> Duration:
    """
    Convert a string representation of duration to a protobuf Duration object.
    
    Args:
        s: Duration string in format "[number]unit" (e.g., "5s", "2m", "3h", "1d")
        
    Returns:
        Duration: Protobuf Duration object
    """
    if not s:
        return Duration(seconds=0)
    
    unit_map = {'s': 1, 'm': 60, 'h': 3600, 'd': 86400}
    match = re.match(r'^(\d+(?:\.\d+)?)([smhd])$', s)
    if not match:
        raise ValueError(f"Invalid duration format: {s}")
    
    value, unit = match.groups()
    seconds = float(value) * unit_map[unit]
    return Duration(seconds=int(seconds), nanos=int((seconds % 1) * 1e9))


def dict_to_protobuf_struct(data: Dict[str, Any]) -> Struct:
    """Convert a Python dict to a protobuf Struct."""
    struct = Struct()
    struct.update(data)
    return struct


@dataclass
class PostMessageOptions:
    """
    Optional settings for posting a message to a Chronoqueue.

    Attributes:
    ----------
    priority : int, optional (default=0)
        Priority level of the message.
    state : MessageState, optional (default=INVISIBLE)
        Initial state of the message.
    lease_duration : str, optional (default="0s")
        Duration for which the message should be processed for by a worker. Must be in format "[number]unit", 
        for example: "5s", "2m", "3.5m", or "3d".
    invisibility_duration : str, optional (default="0s")
        Duration for which the message should remain invisible. Must be in format "[number]unit", 
        for example: "5s", "2m", "3.5m", or "3d".
    attempts_left : int, optional (default=3)
        Number of processing attempts left for the message.
    data_metadata : Dict, optional
        Metadata associated with the message's payload.
    """
    priority: int = 0
    state: MessageState = MessageState.INVISIBLE
    lease_duration: str = "0s"
    invisibility_duration: str = "0s"
    attempts_left: int = 3
    data_metadata: Dict = field(default_factory=dict)

    def __post_init__(self):
        duration_pattern = re.compile(r"^\d+(\.\d+)?[smhd]$")
        if self.lease_duration and not duration_pattern.match(self.lease_duration):
            raise ValueError("lease_duration must be in format '[number]unit', e.g., '5s', '2m', '3.5m', '3d'.")
        if not duration_pattern.match(self.invisibility_duration):
            raise ValueError("invisibility_duration must be in format '[number]unit', e.g., '5s', '2m', '3.5m', '3d'.")


@dataclass
class PostMessageParams:
    """
    Parameters required for posting a message to a Chronoqueue.

    Attributes:
    ----------
    message_id : str
        Unique identifier for the message.
    data : dict
        Payload data for the message.
    queue_name : str, optional (default="default_queue")
        Name of the queue to post the message to.
    options : PostMessageOptions, optional
        Optional settings for posting a message. If not provided, defaults will be used.
    """
    message_id: str
    data: dict
    queue_name: str 
    options: Optional[PostMessageOptions] = field(default_factory=PostMessageOptions)


@dataclass
class AcknowledgeMessageParams:
    """
    Parameters required for acknowledging the processing status of a message in Chronoqueue.

    Attributes:
    ----------
    message_id : str
        Unique identifier for the message being acknowledged.
    queue_name : str, optional (default="default_queue")
        Name of the queue containing the message.
    state : MessageState
        Updated state for the message.
    """
    message_id: str
    state: MessageState
    queue_name: str = "default_queue"

@dataclass
class MessagePriorityRange:
    """
    Priority range for fetching messages from a Chronoqueue.

    Attributes:
    ----------
    min : str, optional (default="-inf")
        Minimum priority level.
    max : str, optional (default="+inf")
        Maximum priority level.
    """
    min: str = "-inf"
    max: str = "+inf"


@dataclass
class PeekQueueMessagesParams:
    """
    Parameters required for peeking at messages in a Chronoqueue without dequeuing them.

    Attributes:
    ----------
    queue_name : str, optional (default="default_queue")
        Name of the queue to peek into.
    limit : int, optional (default=5)
        Maximum number of messages to retrieve.
    priority : MessagePriority, optional
        Priority range for filtering the messages.
    """
    queue_name: str
    limit: int = 5
    priority_range: Optional[MessagePriorityRange] = field(default_factory=MessagePriorityRange)


class QueueType(Enum):
    """
    Enum representing the types of queues that can be created in the Chronoqueue service.
    
    Attributes:
    ----------
    SIMPLE : QueueType
        A standard queue type.
        
    EXCLUSIVE : QueueType
        An exclusive queue type that supports specific features such as unique messages.
    """
    SIMPLE = 0
    EXCLUSIVE = 1

@dataclass
class QueueOptions:
    """
    Data class representing the options for creating a new queue in the Chronoqueue service.

    Attributes:
    ----------
    type : QueueType, default[SIMPLE]
        The type of queue to be created. It can be SIMPLE or EXCLUSIVE.

    exclusivity_key : Optional[str]
        The key used to ensure message exclusivity in the queue.

    dequeue_attempts : Optional[int]
        The number of times a message can be dequeued before it is considered failed.

    lease_duration : Optional[str]
        The duration a message remains leased after being dequeued. Must be in format "[number]unit", 
        for example: "5s", "2m", "3.5m", or "3d".

    invisibility_duration : Optional[str]
        The duration a message remains invisible in the queue before being dequeued. Must be in format "[number]unit",
        for example: "5s", "2m", "3.5m", or "3d".
    """
    dequeue_attempts: Optional[int]
    lease_duration: Optional[str] 
    invisibility_duration: Optional[str]
    type: QueueType = QueueType.SIMPLE
    exclusivity_key: Optional[str] = ""

    def __post_init__(self):
        duration_pattern = re.compile(r"^\d+(\.\d+)?[smhd]$")
        if self.lease_duration and not duration_pattern.match(self.lease_duration):
            raise ValueError("lease_duration must be in format '[number]unit', e.g., '5s', '2m', '3.5m', '3d'.")
        if self.invisibility_duration and not duration_pattern.match(self.invisibility_duration):
            raise ValueError("invisibility_duration must be in format '[number]unit', e.g., '5s', '2m', '3.5m', '3d'.")


def _create_post_message_request(params: PostMessageParams) -> PostMessageRequest:
    """
    Creates a PostMessageRequest object given options.

    Args:
        params (PostMessageParams): required parameters for posting a message

    Returns:
        PostMessageRequest: The populated protobuf request object.
    """

    data_struct = dict_to_protobuf_struct(params.data)

    metadata_map = {}
    if params.options and params.options.data_metadata:
        metadata_map = {k: Value(string_value=v) for k, v in params.options.data_metadata.items()}

    payload = Payload(metadata=metadata_map, data=data_struct)

    if params.options:
        metadata = Message.Metadata(
            payload=payload,
            state=params.options.state.value if isinstance(params.options.state, MessageState) else params.options.state,
            lease_duration=string_to_duration(params.options.lease_duration),
            invisibility_duration=string_to_duration(params.options.invisibility_duration),
            attempts_left=params.options.attempts_left,
            priority=params.options.priority,
        )
    else:
        metadata = Message.Metadata(payload=payload)

    message = Message(
        message_id=params.message_id,
        metadata=metadata
    )

    post_message_request = PostMessageRequest(
        queue_name=params.queue_name,
        message=message
    )

    return post_message_request


class ResponseWrapper:
    """
    A wrapper for gRPC protobuf responses that provides utility methods for converting
    the response to other formats, such as a dictionary, and for accessing the raw protobuf response.

    The ResponseWrapper acts as a bridge between the raw gRPC protobuf response and a more
    user-friendly dictionary format. The provided converter function will be used to transform
    the protobuf response into a dictionary when needed.

    Args:
        response_protobuf: The gRPC protobuf response object.
            This is the raw response received from the gRPC service.
        converter_func: Optional callable that converts the protobuf response to a dictionary.
            If not provided, uses protobuf's built-in JSON conversion.

    """

    def __init__(self, response_protobuf, converter_func: Optional[Callable] = None):
        """
        Initializes the ResponseWrapper with the provided protobuf response and converter function.
        """
        self._response_protobuf = response_protobuf
        self._converter_func = converter_func

    def to_dict(self) -> Dict:
        """
        Converts the wrapped protobuf response to a dictionary using the provided converter function.

        Returns:
            dict: The converted dictionary representation of the protobuf response.
        """
        if self._converter_func:
            return self._converter_func(response_protobuf=self._response_protobuf)
        else:
            return json_format.MessageToDict(self._response_protobuf)

    def to_proto(self) -> Any:
        """
        Retrieves the raw gRPC protobuf response.

        Returns:
            The raw gRPC protobuf response object.
        """
        return self._response_protobuf

    def __getattr__(self, name):
        """
        Delegates attribute access to the underlying protobuf object. This allows for direct access
        to the fields of the wrapped protobuf response.

        Args:
            name (str): The name of the attribute to access.

        Returns:
            The value of the specified attribute in the wrapped protobuf response.
        """
        return getattr(self._response_protobuf, name)
