from chronoqueue.api.v1 import chronoqueue_pb2
from .type_converters import queue_to_protobuf, protobuf_to_queue, message_to_protobuf, protobuf_to_message


# --- CreateQueueRequest Conversion ---

def create_queue_request_to_protobuf(request: dict) -> chronoqueue_pb2.CreateQueueRequest:
    """
    Convert a dictionary representation of CreateQueueRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for CreateQueueRequest.

    Returns:
    - chronoqueue_pb2.CreateQueueRequest: Protobuf representation of CreateQueueRequest.
    """
    queue = queue_to_protobuf(request.get('queue', {}))
    return chronoqueue_pb2.CreateQueueRequest(queue=queue)

def protobuf_to_create_queue_request(request_protobuf: chronoqueue_pb2.CreateQueueRequest) -> dict:
    """
    Convert a protobuf representation of CreateQueueRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.CreateQueueRequest): Protobuf representation of CreateQueueRequest.

    Returns:
    - dict: Dictionary representation of CreateQueueRequest.
    """
    queue = protobuf_to_queue(request_protobuf.queue)
    return {
        'queue': queue
    }


# --- DeleteQueueRequest Conversion ---

def delete_queue_request_to_protobuf(request: dict) -> chronoqueue_pb2.DeleteQueueRequest:
    """
    Convert a dictionary representation of DeleteQueueRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for DeleteQueueRequest.

    Returns:
    - chronoqueue_pb2.DeleteQueueRequest: Protobuf representation of DeleteQueueRequest.
    """
    return chronoqueue_pb2.DeleteQueueRequest(name=request.get('name', ''))

def protobuf_to_delete_queue_request(request_protobuf: chronoqueue_pb2.DeleteQueueRequest) -> dict:
    """
    Convert a protobuf representation of DeleteQueueRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.DeleteQueueRequest): Protobuf representation of DeleteQueueRequest.

    Returns:
    - dict: Dictionary representation of DeleteQueueRequest.
    """
    return {
        'name': request_protobuf.name
    }

# --- PostMessageRequest Conversion ---

def post_message_request_to_protobuf(request: dict) -> chronoqueue_pb2.PostMessageRequest:
    """
    Convert a dictionary representation of PostMessageRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for PostMessageRequest.

    Returns:
    - chronoqueue_pb2.PostMessageRequest: Protobuf representation of PostMessageRequest.
    """
    message = message_to_protobuf(request.get('message', {}))
    return chronoqueue_pb2.PostMessageRequest(queue_name=request.get('queue_name', ''), message=message)

def protobuf_to_post_message_request(request_protobuf: chronoqueue_pb2.PostMessageRequest) -> dict:
    """
    Convert a protobuf representation of PostMessageRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.PostMessageRequest): Protobuf representation of PostMessageRequest.

    Returns:
    - dict: Dictionary representation of PostMessageRequest.
    """
    message = protobuf_to_message(request_protobuf.message)
    return {
        'queue_name': request_protobuf.queue_name,
        'message': message
    }

# --- GetNextMessageRequest Conversion ---

def get_next_message_request_to_protobuf(request: dict) -> chronoqueue_pb2.GetNextMessageRequest:
    """
    Convert a dictionary representation of GetNextMessageRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for GetNextMessageRequest.

    Returns:
    - chronoqueue_pb2.GetNextMessageRequest: Protobuf representation of GetNextMessageRequest.
    """
    return chronoqueue_pb2.GetNextMessageRequest(queue_name=request.get('queue_name', ''), lease_duration=request.get('lease_duration', 0), exclusivity_key=request.get('exclusivity_key', ''))

def protobuf_to_get_next_message_request(request_protobuf: chronoqueue_pb2.GetNextMessageRequest) -> dict:
    """
    Convert a protobuf representation of GetNextMessageRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.GetNextMessageRequest): Protobuf representation of GetNextMessageRequest.

    Returns:
    - dict: Dictionary representation of GetNextMessageRequest.
    """
    return {
        'queue_name': request_protobuf.queue_name,
        'lease_duration': request_protobuf.lease_duration,
        'exclusivity_key': request_protobuf.exclusivity_key
    }

# --- AcknowledgeMessageRequest Conversion ---

def acknowledge_message_request_to_protobuf(request: dict) -> chronoqueue_pb2.AcknowledgeMessageRequest:
    """
    Convert a dictionary representation of AcknowledgeMessageRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for AcknowledgeMessageRequest.

    Returns:
    - chronoqueue_pb2.AcknowledgeMessageRequest: Protobuf representation of AcknowledgeMessageRequest.
    """
    state = chronoqueue_pb2.Message.Metadata.State.Value(request.get('state', "UNDEFINED"))
    return chronoqueue_pb2.AcknowledgeMessageRequest(queue_name=request.get('queue_name', ''), message_id=request.get('message_id', ''), state=state)

def protobuf_to_acknowledge_message_request(request_protobuf: chronoqueue_pb2.AcknowledgeMessageRequest) -> dict:
    """
    Convert a protobuf representation of AcknowledgeMessageRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.AcknowledgeMessageRequest): Protobuf representation of AcknowledgeMessageRequest.

    Returns:
    - dict: Dictionary representation of AcknowledgeMessageRequest.
    """
    state = chronoqueue_pb2.Message.Metadata.State.Name(request_protobuf.state)
    return {
        'queue_name': request_protobuf.queue_name,
        'message_id': request_protobuf.message_id,
        'state': state
    }


# --- PeekQueueMessagesRequest Conversion ---

def peek_queue_messages_request_to_protobuf(request: dict) -> chronoqueue_pb2.PeekQueueMessagesRequest:
    """
    Convert a dictionary representation of PeekQueueMessagesRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for PeekQueueMessagesRequest.

    Returns:
    - chronoqueue_pb2.PeekQueueMessagesRequest: Protobuf representation of PeekQueueMessagesRequest.
    """
    priority_range = chronoqueue_pb2.PeekQueueMessagesRequest.PriorityRange(
        min=request.get('priority_range', {}).get('min', 0),
        max=request.get('priority_range', {}).get('max', 0)
    )
    return chronoqueue_pb2.PeekQueueMessagesRequest(
        queue_name=request.get('queue_name', ""),
        limit=request.get('limit', 0),
        priority_range=priority_range
    )

def protobuf_to_peek_queue_messages_request(request_protobuf: chronoqueue_pb2.PeekQueueMessagesRequest) -> dict:
    """
    Convert a protobuf representation of PeekQueueMessagesRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.PeekQueueMessagesRequest): Protobuf representation of PeekQueueMessagesRequest.

    Returns:
    - dict: Dictionary representation of PeekQueueMessagesRequest.
    """
    priority_range = {
        'min': request_protobuf.priority_range.min,
        'max': request_protobuf.priority_range.max
    }
    return {
        'queue_name': request_protobuf.queue_name,
        'limit': request_protobuf.limit,
        'priority_range': priority_range
    }


# --- RenewMessageLeaseRequest Conversion ---

def renew_message_lease_request_to_protobuf(request: dict) -> chronoqueue_pb2.RenewMessageLeaseRequest:
    """
    Convert a dictionary representation of RenewMessageLeaseRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for RenewMessageLeaseRequest.

    Returns:
    - chronoqueue_pb2.RenewMessageLeaseRequest: Protobuf representation of RenewMessageLeaseRequest.
    """
    return chronoqueue_pb2.RenewMessageLeaseRequest(
        queue_name=request.get('queue_name', ''),
        message_id=request.get('message_id', ''),
        lease_duration=request.get('lease_duration', 0)
    )

def protobuf_to_renew_message_lease_request(request_protobuf: chronoqueue_pb2.RenewMessageLeaseRequest) -> dict:
    """
    Convert a protobuf representation of RenewMessageLeaseRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.RenewMessageLeaseRequest): Protobuf representation of RenewMessageLeaseRequest.

    Returns:
    - dict: Dictionary representation of RenewMessageLeaseRequest.
    """
    return {
        'queue_name': request_protobuf.queue_name,
        'message_id': request_protobuf.message_id,
        'lease_duration': request_protobuf.lease_duration
    }

# --- GetQueueStateRequest Conversion ---

def get_queue_state_request_to_protobuf(request: dict) -> chronoqueue_pb2.GetQueueStateRequest:
    """
    Convert a dictionary representation of GetQueueStateRequest to its protobuf counterpart.

    Args:
    - request (dict): Dictionary containing fields for GetQueueStateRequest.

    Returns:
    - chronoqueue_pb2.GetQueueStateRequest: Protobuf representation of GetQueueStateRequest.
    """
    return chronoqueue_pb2.GetQueueStateRequest(
        queue_name=request.get('queue_name', '')
    )

def protobuf_to_get_queue_state_request(request_protobuf: chronoqueue_pb2.GetQueueStateRequest) -> dict:
    """
    Convert a protobuf representation of GetQueueStateRequest to its dictionary counterpart.

    Args:
    - request_protobuf (chronoqueue_pb2.GetQueueStateRequest): Protobuf representation of GetQueueStateRequest.

    Returns:
    - dict: Dictionary representation of GetQueueStateRequest.
    """
    return {
        'queue_name': request_protobuf.queue_name
    }

