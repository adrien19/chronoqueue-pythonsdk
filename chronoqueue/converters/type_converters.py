import re
from typing import Dict
from google.protobuf.struct_pb2 import Struct, Value
from chronoqueue.api.v1 import chronoqueue_pb2
from google.protobuf.json_format import MessageToDict
from google.protobuf.duration_pb2 import Duration

def is_empty_proto_message(message):
    """
    Determines if a protobuf message is empty.

    This function checks whether a protobuf message is empty, meaning it doesn’t contain 
    any non-default values. It iterates through all fields of the message and checks 
    scalar fields, repeated fields, map fields, and nested message fields recursively 
    to ensure that they either contain default values or are empty.

    Parameters:
    ----------
    message : google.protobuf.message.Message
        The protobuf message instance to check for emptiness.

    Returns:
    -------
    bool
        True if the message is empty or contains only default values, False otherwise.

    Example:
    --------
    >>> from my_proto_package import MyMessage
    >>> message = MyMessage()
    >>> is_empty = is_empty_proto_message(message)
    >>> print(is_empty)
    True
    
    """
    if message.ByteSize() == 0:
        return True
    
    for field in message.DESCRIPTOR.fields:
        value = getattr(message, field.name)
        
        # If the field is a map field, check if it's empty
        if field.type == field.TYPE_MESSAGE and field.message_type.has_options and field.message_type.GetOptions().map_entry:
            if value:
                return False
        # If the field is another message type (and not an enum), check it recursively
        elif field.message_type and not field.enum_type:
            if not is_empty_proto_message(value):
                return False
        # If the field is a repeated field, check if it has any values
        elif field.label == field.LABEL_REPEATED:
            if value:
                return False
        # For scalar fields, check against default value
        else:
            if value not in (field.default_value, None):  # for proto3, fields have default values
                return False
    return True

# --- Struct <-> Dictionary Conversion ---

def duration_to_dict(duration: Duration) -> Dict:
    return {
        'seconds': duration.seconds,
        'nanos': duration.nanos
    }

def dict_to_duration(data_dict: Dict) -> Duration:
    duration = Duration()
    duration.seconds = data_dict.get('seconds', 0)
    duration.nanos = data_dict.get('nanos', 0)
    return duration


# --- Struct <-> Dictionary Conversion ---

def dict_to_protobuf_struct(data_dict: Dict) -> Struct:
    struct = Struct()
    struct.update(data_dict)
    return struct

def protobuf_struct_to_dict(struct: Struct) -> Dict:
    if is_empty_proto_message(struct):
        return {}
    return MessageToDict(struct)

# --- Payload Conversion ---

def payload_to_protobuf(payload: Dict) -> chronoqueue_pb2.Payload:
    metadata = {k: Value(string_value=v) for k, v in payload.get('metadata', {}).items()}
    data = dict_to_protobuf_struct(payload.get('data', {}))
    return chronoqueue_pb2.Payload(metadata=metadata, data=data)

def protobuf_to_payload(payload_protobuf: chronoqueue_pb2.Payload) -> Dict:
    metadata = {k: v.string_value for k, v in payload_protobuf.metadata.items()}
    data = protobuf_struct_to_dict(payload_protobuf.data)
    return {
        'metadata': metadata,
        'data': data
    }

# --- Message Conversion ---

def message_to_protobuf(message: Dict) -> chronoqueue_pb2.Message:
    metadata = message_metadata_to_protobuf(message.get('metadata', {}))
    return chronoqueue_pb2.Message(
        message_id=message.get('message_id', ""),
        priority=message.get('priority', 0),
        metadata=metadata
    )

def protobuf_to_message(message_protobuf: chronoqueue_pb2.Message) -> Dict:
    if is_empty_proto_message(message=message_protobuf):
        return {}
    metadata = protobuf_to_message_metadata(message_protobuf.metadata)
    return {
        'message_id': message_protobuf.message_id,
        'priority': message_protobuf.priority,
        'metadata': metadata
    }

# --- Message Metadata Conversion ---

def message_metadata_to_protobuf(metadata: Dict) -> chronoqueue_pb2.Message.Metadata:
    payload = payload_to_protobuf(metadata.get('payload', {}))
    state = chronoqueue_pb2.Message.Metadata.State.Value(metadata.get('state', "UNDEFINED"))
    return chronoqueue_pb2.Message.Metadata(
        payload=payload,
        state=state,
        invisibility_duration=metadata.get('invisibility_duration', Duration()),
        attempts_left=metadata.get('attempts_left', 0),
        lease_duration=metadata.get('lease_duration', Duration()),
        lease_expiry=metadata.get('lease_expiry', 0),
        lease_renewal_count=metadata.get('lease_renewal_count', 0),
        invisibility_expiry=metadata.get('invisibility_expiry', 0)
    )

def protobuf_to_message_metadata(metadata_protobuf: chronoqueue_pb2.Message.Metadata) -> Dict:
    if is_empty_proto_message(metadata_protobuf):
        return {}
    payload = protobuf_to_payload(metadata_protobuf.payload)
    state = chronoqueue_pb2.Message.Metadata.State.Name(metadata_protobuf.state)
    invisibility_duration = duration_to_dict(metadata_protobuf.invisibility_duration)
    lease_duration = duration_to_dict(metadata_protobuf.lease_duration)
    return {
        'payload': payload,
        'state': state,
        'invisibility_duration': invisibility_duration,
        'attempts_left': metadata_protobuf.attempts_left,
        'lease_duration': lease_duration,
        'lease_expiry': metadata_protobuf.lease_expiry,
        'lease_renewal_count': metadata_protobuf.lease_renewal_count,
        'invisibility_expiry': metadata_protobuf.invisibility_expiry
    }

# --- Queue Conversion ---

def queue_to_protobuf(queue: Dict) -> chronoqueue_pb2.Queue:
    metadata = queue_metadata_to_protobuf(queue.get('metadata', {}))
    return chronoqueue_pb2.Queue(
        name=queue.get('name', ""),
        metadata=metadata
    )

def protobuf_to_queue(queue_protobuf: chronoqueue_pb2.Queue) -> Dict:
    if is_empty_proto_message(queue_protobuf):
        return {}
    metadata = protobuf_to_queue_metadata(queue_protobuf.metadata)
    return {
        'name': queue_protobuf.name,
        'metadata': metadata
    }

# --- Queue Metadata Conversion ---

def queue_metadata_to_protobuf(metadata: Dict) -> chronoqueue_pb2.Queue.Options:
    type_ = chronoqueue_pb2.Queue.Options.Type.Value(metadata.get('type', "SIMPLE"))
    return chronoqueue_pb2.Queue.Options(
        type=type_,
        dequeue_attempts=metadata.get('dequeue_attempts', 0),
        lease_duration=metadata.get('lease_duration', Duration()),
        exclusivity_key=metadata.get('exclusivity_key', ""),
        invisibility_duration=metadata.get('invisibility_duration', Duration())
    )

def protobuf_to_queue_metadata(metadata_protobuf: chronoqueue_pb2.Queue.Options) -> Dict:
    if is_empty_proto_message(metadata_protobuf):
        return {}
    type_ = chronoqueue_pb2.Queue.Options.Type.Name(metadata_protobuf.type)
    invisibility_duration = duration_to_dict(metadata_protobuf.invisibility_duration)
    lease_duration = duration_to_dict(metadata_protobuf.lease_duration)
    return {
        'type': type_,
        'dequeue_attempts': metadata_protobuf.dequeue_attempts,
        'lease_duration': lease_duration,
        'exclusivity_key': metadata_protobuf.exclusivity_key,
        'invisibility_duration': invisibility_duration
    }


def string_to_duration(s: str) -> Duration:
    match = re.match(r"(\d+(?:\.\d+)?)([smhd])", s)
    if not match:
        raise ValueError(f"Invalid duration string: {s}")
    
    val, unit = match.groups()
    val = float(val)
    
    if unit == 's':
        return Duration(seconds=int(val))
    elif unit == 'm':
        return Duration(seconds=int(val * 60))
    elif unit == 'h':
        return Duration(seconds=int(val * 3600))
    elif unit == 'd':
        return Duration(seconds=int(val * 86400))
    

def duration_to_string(duration: Duration) -> str:
    '''
    Usage:
    ------
    >>> duration = Duration(seconds=90)  # 1.5 minutes
    >>> print(duration_to_string(duration))  # Output: 1.5m
    '''
    total_seconds = duration.seconds + duration.nanos * 1e-9
    if total_seconds % 86400 == 0:  # Divisible by the number of seconds in a day
        return f"{total_seconds // 86400}d"
    elif total_seconds % 3600 == 0:  # Divisible by the number of seconds in an hour
        return f"{total_seconds // 3600}h"
    elif total_seconds % 60 == 0:  # Divisible by the number of seconds in a minute
        return f"{total_seconds // 60}m"
    else:
        return f"{total_seconds:.1f}s" if duration.nanos else f"{total_seconds}s"
