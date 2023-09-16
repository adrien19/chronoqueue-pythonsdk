from chronoqueue.api.v1 import chronoqueue_pb2
from .type_converters import protobuf_to_message

# --- CreateQueueResponse Conversion ---

def protobuf_to_create_queue_response(response_protobuf: chronoqueue_pb2.CreateQueueResponse) -> dict:
    """
    Convert a protobuf representation of CreateQueueResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.CreateQueueResponse): Protobuf representation of CreateQueueResponse.

    Returns:
    - dict: Empty dictionary as CreateQueueResponse has no fields.
    """
    return {}

# --- DeleteQueueResponse Conversion ---

def protobuf_to_delete_queue_response(response_protobuf: chronoqueue_pb2.DeleteQueueResponse) -> dict:
    """
    Convert a protobuf representation of DeleteQueueResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.DeleteQueueResponse): Protobuf representation of DeleteQueueResponse.

    Returns:
    - dict: Empty dictionary as DeleteQueueResponse has no fields.
    """
    return {}

# --- PostMessageResponse Conversion ---

def protobuf_to_post_message_response(response_protobuf: chronoqueue_pb2.PostMessageResponse) -> dict:
    """
    Convert a protobuf representation of PostMessageResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.PostMessageResponse): Protobuf representation of PostMessageResponse.

    Returns:
    - dict: Empty dictionary as PostMessageResponse has no fields.
    """
    return {}

# --- GetNextMessageResponse Conversion ---

def protobuf_to_get_next_message_response(response_protobuf: chronoqueue_pb2.GetNextMessageResponse) -> dict:
    """
    Convert a protobuf representation of GetNextMessageResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.GetNextMessageResponse): Protobuf representation of GetNextMessageResponse.

    Returns:
    - dict: Dictionary representation of GetNextMessageResponse.
    """
    message = protobuf_to_message(response_protobuf.message)
    return {
        'message': message
    }

# --- AcknowledgeMessageResponse Conversion ---

def protobuf_to_acknowledge_message_response(response_protobuf: chronoqueue_pb2.AcknowledgeMessageResponse) -> dict:
    """
    Convert a protobuf representation of AcknowledgeMessageResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.AcknowledgeMessageResponse): Protobuf representation of AcknowledgeMessageResponse.

    Returns:
    - dict: Empty dictionary as AcknowledgeMessageResponse has no fields.
    """
    return {}

# --- PeekQueueMessagesResponse Conversion ---

def protobuf_to_peek_queue_messages_response(response_protobuf: chronoqueue_pb2.PeekQueueMessagesResponse) -> dict:
    """
    Convert a protobuf representation of PeekQueueMessagesResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.PeekQueueMessagesResponse): Protobuf representation of PeekQueueMessagesResponse.

    Returns:
    - dict: Dictionary representation of PeekQueueMessagesResponse containing a list of Message representations.
    """
    return {
        'messages': [protobuf_to_message(message_protobuf) for message_protobuf in response_protobuf.messages]
    }


# --- RenewMessageLeaseResponse Conversion ---

def protobuf_to_renew_message_lease_response(response_protobuf: chronoqueue_pb2.RenewMessageLeaseResponse) -> dict:
    """
    Convert a protobuf representation of RenewMessageLeaseResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.RenewMessageLeaseResponse): Protobuf representation of RenewMessageLeaseResponse.

    Returns:
    - dict: Empty dictionary as RenewMessageLeaseResponse has no fields.
    """
    return {}

# --- GetQueueStateResponse Conversion ---

def protobuf_to_get_queue_state_response(response_protobuf: chronoqueue_pb2.GetQueueStateResponse) -> dict:
    """
    Convert a protobuf representation of GetQueueStateResponse to its dictionary counterpart.

    Args:
    - response_protobuf (chronoqueue_pb2.GetQueueStateResponse): Protobuf representation of GetQueueStateResponse.

    Returns:
    - dict: Dictionary representation of GetQueueStateResponse.
    """
    return {
        'invisible_messages_count': response_protobuf.invisible_messages_count,
        'pending_messages_count': response_protobuf.pending_messages_count,
        'running_messages_count': response_protobuf.running_messages_count,
        'completed_messages_count': response_protobuf.completed_messages_count,
        'canceled_messages_count': response_protobuf.canceled_messages_count,
        'errored_messages_count': response_protobuf.errored_messages_count,
        'earliest_deadline': response_protobuf.earliest_deadline.ToDatetime()
    }

