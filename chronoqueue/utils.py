from dataclasses import dataclass, field
from typing import Optional, Dict, Any
from enum import Enum
from .api.v1 import chronoqueue_pb2
from .converters.type_converters import dict_to_protobuf_struct
from google.protobuf.struct_pb2 import Struct, Value
from google.protobuf.json_format import MessageToJson, ParseDict


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
    INVISIBLE = chronoqueue_pb2.Message.Metadata.State.INVISIBLE
    PENDING = chronoqueue_pb2.Message.Metadata.State.PENDING
    RUNNING = chronoqueue_pb2.Message.Metadata.State.RUNNING
    COMPLETED = chronoqueue_pb2.Message.Metadata.State.COMPLETED
    CANCELED = chronoqueue_pb2.Message.Metadata.State.CANCELED
    ERRORED = chronoqueue_pb2.Message.Metadata.State.ERRORED

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
    """
    message_id: str
    data: dict
    queue_name: str = "default_queue"

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
    invisibility_duration : int, optional (default=0)
        Duration (in seconds) for which the message should remain invisible.
    attempts_left : int, optional (default=3)
        Number of processing attempts left for the message.
    data_metadata : Dict, optional
        Metadata associated with the message's payload.
    """
    priority: int = 0
    state: MessageState = chronoqueue_pb2.Message.Metadata.State.INVISIBLE
    invisibility_duration: int = 0
    attempts_left: int = 3
    data_metadata: Dict = field(default_factory=dict)

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
    priority_range: Optional[MessagePriorityRange]
    queue_name: str = "default_queue"
    limit: int = 5

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
    SIMPLE = chronoqueue_pb2.Queue.Options.Type.SIMPLE
    EXCLUSIVE = chronoqueue_pb2.Queue.Options.Type.EXCLUSIVE

@dataclass
class QueueOptions:
    """
    Data class representing the options for creating a new queue in the Chronoqueue service.

    Attributes:
    ----------
    type : QueueType
        The type of queue to be created. It can be SIMPLE or EXCLUSIVE.

    exclusivity_key : str
        The key used to ensure message exclusivity in the queue.

    dequeue_attempts : Optional[int]
        The number of times a message can be dequeued before it is considered failed.

    lease_duration : Optional[int]
        The duration (in seconds) a message remains leased after being dequeued.

    invisibility_duration : Optional[int]
        The duration (in seconds) a message remains invisible in the queue before being dequeued.
    """
    type: QueueType
    exclusivity_key: str
    dequeue_attempts: Optional[int]
    lease_duration: Optional[int]
    invisibility_duration: Optional[int]


def _create_post_message_request(params: PostMessageParams, options: PostMessageOptions) -> chronoqueue_pb2.PostMessageRequest:
    """
    Creates a PostMessageRequest object given options.

    Args:
        params (PostMessageParams): required parameters for posting a message
        options (dict): Additional options for the message, such as priority, state, etc.

    Returns:
        PostMessageRequest: The populated protobuf request object.
    """

    # Convert Python dict to Struct
    # data_struct = ParseDict(params.data, Struct())
    data_struct = dict_to_protobuf_struct(params.data)

    # Convert Python dict to map<string, Value>
    metadata_map = {k: Value(string_value=v) for k, v in options.data_metadata.items()}

    # Create the Payload message with the provided data and an empty metadata.
    payload = chronoqueue_pb2.Payload(metadata=metadata_map, data=data_struct)

    # Create the Message's Metadata using provided options or default values.
    metadata = chronoqueue_pb2.Message.Metadata(
        payload=payload,
        state=options.state,
        invisibility_duration=options.invisibility_duration,
        attempts_left=options.attempts_left,
    )

    # Create the main Message using provided message_id, options or default values.
    message = chronoqueue_pb2.Message(
        message_id=params.message_id,
        priority=options.priority,
        metadata=metadata
    )

    # Finally, create the PostMessageRequest with a default queue_name or from options.
    post_message_request = chronoqueue_pb2.PostMessageRequest(
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

    Additionally, the ResponseWrapper contains fields like `remaining_lease_time` and `stop_event`
    which can be used in the context of certain operations, such as message leasing and heartbeats.

    Args:
        response_protobuf: The gRPC protobuf response object.
            This is the raw response received from the gRPC service.
        converter_func: A callable that converts the protobuf response to a dictionary.
            This function should accept a single argument (the protobuf response) and return a dictionary.

    Attributes:
        remaining_lease_time (float, optional): The remaining time (in seconds) for a leased message.
            This can be used in conjunction with heartbeats to determine when to renew a message's lease.
            By default, this is set to None, indicating it's not used.
        stop_event (threading.Event, optional): An event that can be set to signal operations (like heartbeats)
            to stop. By default, this is set to None.

    """

    def __init__(self, response_protobuf, converter_func):
        """
        Initializes the ResponseWrapper with the provided protobuf response and converter function.
        """
        self._response_protobuf = response_protobuf
        self._converter_func = converter_func
        self.remaining_lease_time = None
        self.stop_event = None

    def to_dict(self) -> Dict:
        """
        Converts the wrapped protobuf response to a dictionary using the provided converter function.

        Returns:
            dict: The converted dictionary representation of the protobuf response.
        """
        return self._converter_func(response_protobuf=self._response_protobuf)

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
    
    def __enter__(self):
        return self

    def __exit__(self, exc_type, exc_value, traceback):
        if hasattr(self, "stop_event") and self.stop_event is not None and not self.stop_event.is_set():
            self.stop_event.set()
    
    def __del__(self):
        if hasattr(self, "stop_event") and self.stop_event is not None and not self.stop_event.is_set():
            self.stop_event.set()
