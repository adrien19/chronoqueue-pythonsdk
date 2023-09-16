from typing import Dict
from google.protobuf.struct_pb2 import Struct, Value
from chronoqueue.api.v1 import chronoqueue_pb2
from google.protobuf.json_format import MessageToDict


# --- Struct <-> Dictionary Conversion ---

def dict_to_protobuf_struct(data_dict: Dict) -> Struct:
    struct = Struct()
    struct.update(data_dict)
    return struct

def protobuf_struct_to_dict(struct: Struct) -> Dict:
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
        invisibility_duration=metadata.get('invisibility_duration', 0),
        attempts_left=metadata.get('attempts_left', 0),
        lease_duration=metadata.get('lease_duration', 0),
        lease_expiry=metadata.get('lease_expiry', 0)
    )

def protobuf_to_message_metadata(metadata_protobuf: chronoqueue_pb2.Message.Metadata) -> Dict:
    payload = protobuf_to_payload(metadata_protobuf.payload)
    state = chronoqueue_pb2.Message.Metadata.State.Name(metadata_protobuf.state)
    return {
        'payload': payload,
        'state': state,
        'invisibility_duration': metadata_protobuf.invisibility_duration,
        'attempts_left': metadata_protobuf.attempts_left,
        'lease_duration': metadata_protobuf.lease_duration,
        'lease_expiry': metadata_protobuf.lease_expiry
    }

# --- Queue Conversion ---

def queue_to_protobuf(queue: Dict) -> chronoqueue_pb2.Queue:
    metadata = queue_metadata_to_protobuf(queue.get('metadata', {}))
    return chronoqueue_pb2.Queue(
        name=queue.get('name', ""),
        metadata=metadata
    )

def protobuf_to_queue(queue_protobuf: chronoqueue_pb2.Queue) -> Dict:
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
        lease_duration=metadata.get('lease_duration', 0),
        exclusivity_key=metadata.get('exclusivity_key', ""),
        invisibility_duration=metadata.get('invisibility_duration', 0)
    )

def protobuf_to_queue_metadata(metadata_protobuf: chronoqueue_pb2.Queue.Options) -> Dict:
    type_ = chronoqueue_pb2.Queue.Options.Type.Name(metadata_protobuf.type)
    return {
        'type': type_,
        'dequeue_attempts': metadata_protobuf.dequeue_attempts,
        'lease_duration': metadata_protobuf.lease_duration,
        'exclusivity_key': metadata_protobuf.exclusivity_key,
        'invisibility_duration': metadata_protobuf.invisibility_duration
    }
