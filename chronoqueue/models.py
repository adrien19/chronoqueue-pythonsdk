"""
Pydantic models for type-safe response handling.

This module provides optional Pydantic models that offer:
- Type safety and IDE autocomplete
- Data validation
- Easy serialization to JSON/dict
- Better developer experience compared to raw protobuf or untyped dicts

All models include a `from_proto()` class method to convert from protobuf responses.

Example:
    >>> response = client.get_next_message("my_queue", "5m")
    >>> msg = response.to_model()  # Returns MessageResponse (typed!)
    >>> print(msg.message_id)  # IDE autocomplete works
    >>> json_str = msg.model_dump_json()  # Easy serialization
"""

try:
    from datetime import datetime
    from typing import Any, Dict, List, Optional

    from google.protobuf import json_format
    from pydantic import BaseModel, ConfigDict, Field

    PYDANTIC_AVAILABLE = True
except ImportError:
    PYDANTIC_AVAILABLE = False
    BaseModel = object  # Fallback for type hints


if PYDANTIC_AVAILABLE:

    class MessageMetadata(BaseModel):
        """
        Metadata associated with a message.

        Proto source: proto/message/v1/message.proto::Message.Metadata
        """

        state: str = Field(..., description="Current state of the message")
        priority: int = Field(default=0, description="Message priority level")
        attempts_left: int = Field(default=0, description="Remaining processing attempts")
        max_attempts: int = Field(default=0, description="Maximum allowed attempts")
        lease_expiry: Optional[int] = Field(None, description="Lease expiration timestamp")
        invisibility_expiry: Optional[int] = Field(None, description="Invisibility expiration timestamp")
        lease_renewal_count: int = Field(default=0, description="Number of times lease was renewed")
        payload: Optional["MessagePayload"] = Field(None, description="Message payload")

        model_config = ConfigDict(from_attributes=True)

    class MessagePayload(BaseModel):
        """
        Message payload containing the actual data.

        Proto source: proto/common/v1/common.proto::Payload
        """

        data: Dict[str, Any] = Field(default_factory=dict, description="Payload data")
        metadata: Dict[str, Any] = Field(default_factory=dict, description="Payload metadata")

        model_config = ConfigDict(from_attributes=True)

    class Message(BaseModel):
        """
        Complete message structure.

        Proto source: proto/message/v1/message.proto::Message
        """

        message_id: str = Field(..., description="Unique message identifier")
        metadata: Optional[MessageMetadata] = Field(None, description="Message metadata including payload")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_msg):
            """
            Create a Message from a protobuf Message object.

            Args:
                proto_msg: Protobuf Message object

            Returns:
                Message: Pydantic Message model
            """
            data = json_format.MessageToDict(proto_msg, preserving_proto_field_name=True)

            # Extract metadata
            metadata_data = data.get("metadata", {})

            # Extract payload from metadata
            payload_data = metadata_data.get("payload", {})

            # Create MessagePayload if it exists
            payload_model = None
            if payload_data:
                payload_model = MessagePayload(**payload_data)

            # Create MessageMetadata with payload
            metadata_model = None
            if metadata_data:
                # Remove payload from metadata_data to avoid duplication
                metadata_dict = {k: v for k, v in metadata_data.items() if k != "payload"}
                if payload_model:
                    metadata_dict["payload"] = payload_model
                metadata_model = MessageMetadata(**metadata_dict)

            return cls(
                message_id=data.get("message_id", ""),
                metadata=metadata_model,
            )

    class CreateQueueResponse(BaseModel):
        """
        Response from create_queue operation.

        Proto source: proto/queueservice/v1/request_response.proto::CreateQueueResponse
        """

        success: bool = Field(..., description="Whether queue creation succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from CreateQueueResponse protobuf."""
            return cls(success=proto_response.success)

    class DeleteQueueResponse(BaseModel):
        """
        Response from delete_queue operation.

        Proto source: proto/queueservice/v1/request_response.proto::DeleteQueueResponse
        """

        success: bool = Field(..., description="Whether queue deletion succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from DeleteQueueResponse protobuf."""
            return cls(success=proto_response.success)

    class PostMessageResponse(BaseModel):
        """
        Response from post_message operation.

        Proto source: proto/queueservice/v1/request_response.proto::PostMessageResponse
        """

        success: bool = Field(..., description="Whether message posting succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from PostMessageResponse protobuf."""
            return cls(success=proto_response.success)

    class GetNextMessageResponse(BaseModel):
        """
        Response from get_next_message operation containing the fetched message.

        Proto source: proto/queueservice/v1/request_response.proto::GetNextMessageResponse
        """

        message: Optional[Message] = Field(None, description="The fetched message, if available")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from GetNextMessageResponse protobuf."""
            if proto_response.HasField("message"):
                message = Message.from_proto(proto_response.message)
            else:
                message = None

            return cls(message=message)

    class AcknowledgeMessageResponse(BaseModel):
        """
        Response from acknowledge_message operation.

        Proto source: proto/queueservice/v1/request_response.proto::AcknowledgeMessageResponse
        """

        success: bool = Field(..., description="Whether acknowledgment succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from AcknowledgeMessageResponse protobuf."""
            return cls(success=proto_response.success)

    class RenewMessageLeaseResponse(BaseModel):
        """
        Response from renew_message_lease operation.

        Proto source: proto/queueservice/v1/request_response.proto::RenewMessageLeaseResponse
        """

        remaining_time: Optional[str] = Field(None, description="Remaining lease time")
        state: str = Field(..., description="Current message state")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from RenewMessageLeaseResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(
                remaining_time=data.get("remaining_time"),
                state=data.get("state", "UNKNOWN"),
            )

    class PeekQueueMessagesResponse(BaseModel):
        """
        Response from peek_queue_messages operation.

        Proto source: proto/queueservice/v1/request_response.proto::PeekQueueMessagesResponse
        """

        messages: List[Message] = Field(default_factory=list, description="List of peeked messages")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from PeekQueueMessagesResponse protobuf."""
            messages = [Message.from_proto(msg) for msg in proto_response.messages]
            return cls(messages=messages)

    class GetQueueStateResponse(BaseModel):
        """
        Response from get_queue_state operation containing queue statistics.

        Proto source: proto/queueservice/v1/request_response.proto::GetQueueStateResponse
        """

        state_counts: Dict[str, int] = Field(default_factory=dict, description="Count of messages in each state")
        earliest_deadline: Optional[str] = Field(None, description="Earliest message deadline timestamp")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from GetQueueStateResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(
                state_counts=data.get("state_counts", {}),
                earliest_deadline=data.get("earliest_deadline"),
            )

    class SendMessageHeartBeatResponse(BaseModel):
        """
        Response from send_message_heartbeat operation.

        Proto source: proto/queueservice/v1/request_response.proto::SendMessageHeartBeatResponse
        """

        remaining_time: Optional[str] = Field(None, description="Remaining lease time")
        state: str = Field(..., description="Current message state")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from SendMessageHeartBeatResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(
                remaining_time=data.get("remaining_time"),
                state=data.get("state", "UNKNOWN"),
            )

else:
    # Pydantic not available - create placeholder classes
    class CreateQueueResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class DeleteQueueResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class PostMessageResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class GetNextMessageResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class AcknowledgeMessageResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class RenewMessageLeaseResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class PeekQueueMessagesResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class GetQueueStateResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class SendMessageHeartBeatResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class Message:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class MessageMetadata:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class MessagePayload:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass


__all__ = [
    "PYDANTIC_AVAILABLE",
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
]
