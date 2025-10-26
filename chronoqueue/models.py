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

    # Schedule Models

    class ScheduleMetadata(BaseModel):
        """
        Metadata for a schedule.

        Proto source: proto/schedule/v1/schedule.proto::Schedule.Metadata
        """

        payload: Optional[Dict[str, Any]] = Field(None, description="Schedule payload data")
        state: str = Field(..., description="Schedule state (SCHEDULED, CANCELED, ERRORED, PAUSED)")
        cron_schedule: Optional[str] = Field(None, description="Cron expression for schedule")
        calendar_schedule: Optional[Dict[str, Any]] = Field(None, description="Calendar schedule configuration")
        queue_name: str = Field(..., description="Target queue name")
        message_ids: List[str] = Field(default_factory=list, description="Generated message IDs")
        next_run: Optional[str] = Field(None, description="Next scheduled run time")
        last_run: Optional[str] = Field(None, description="Last run time")
        created_at: Optional[str] = Field(None, description="Creation timestamp")
        updated_at: Optional[str] = Field(None, description="Last update timestamp")
        exclusivity_key: Optional[str] = Field(None, description="Message exclusivity key")
        state_message: Optional[str] = Field(None, description="State description/error message")
        priority: int = Field(0, description="Message priority")
        max_messages: Optional[int] = Field(None, description="Max messages per execution")
        lease_duration: Optional[str] = Field(None, description="Message lease duration")
        timezone: Optional[str] = Field(None, description="Schedule timezone")
        next_runs: List[str] = Field(default_factory=list, description="Upcoming run times")

        model_config = ConfigDict(from_attributes=True)

    class Schedule(BaseModel):
        """
        A schedule for automated message posting.

        Proto source: proto/schedule/v1/schedule.proto::Schedule
        """

        schedule_id: str = Field(..., description="Unique schedule identifier")
        metadata: ScheduleMetadata = Field(..., description="Schedule metadata and configuration")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_schedule):
            """Create from Schedule protobuf."""
            from chronoqueue.api.schedule.v1 import schedule_pb2

            # Get state enum name
            state_enum = proto_schedule.metadata.state
            state_name = schedule_pb2.Schedule.Metadata.State.Name(state_enum)

            # Extract payload data
            payload = None
            if proto_schedule.metadata.HasField("payload") and proto_schedule.metadata.payload.data:
                from google.protobuf import json_format

                payload = json_format.MessageToDict(proto_schedule.metadata.payload.data)

            # Helper to convert Timestamp to string
            def timestamp_to_str(ts):
                if ts and ts.seconds:
                    return ts.ToJsonString()
                return None

            metadata = ScheduleMetadata(
                payload=payload,
                state=state_name,
                cron_schedule=proto_schedule.metadata.cron_schedule if proto_schedule.metadata.cron_schedule else None,
                calendar_schedule=None,  # TODO: Parse calendar schedule if needed
                queue_name=proto_schedule.metadata.queue_name,
                message_ids=list(proto_schedule.metadata.message_ids),
                next_run=timestamp_to_str(proto_schedule.metadata.next_run),
                last_run=timestamp_to_str(proto_schedule.metadata.last_run),
                created_at=timestamp_to_str(proto_schedule.metadata.created_at),
                updated_at=timestamp_to_str(proto_schedule.metadata.updated_at),
                exclusivity_key=proto_schedule.metadata.exclusivity_key
                if proto_schedule.metadata.exclusivity_key
                else None,
                state_message=proto_schedule.metadata.state_message if proto_schedule.metadata.state_message else None,
                priority=proto_schedule.metadata.priority,
                max_messages=proto_schedule.metadata.max_messages if proto_schedule.metadata.has_max_messages else None,
                lease_duration=str(proto_schedule.metadata.lease_duration)
                if proto_schedule.metadata.HasField("lease_duration")
                else None,
                timezone=proto_schedule.metadata.timezone if proto_schedule.metadata.timezone else None,
                next_runs=list(proto_schedule.metadata.next_runs),
            )

            return cls(
                schedule_id=proto_schedule.schedule_id,
                metadata=metadata,
            )

    class ScheduleHistoryEntry(BaseModel):
        """
        A single execution entry in schedule history.

        Proto source: proto/schedule/v1/schedule.proto::ScheduleHistory
        """

        execution_time: Optional[str] = Field(None, description="When the schedule executed")
        success: bool = Field(False, description="Whether execution succeeded")
        error_message: Optional[str] = Field(None, description="Error message if failed")
        message_ids: List[str] = Field(default_factory=list, description="Created message IDs")

        model_config = ConfigDict(from_attributes=True)

    class CreateScheduleResponse(BaseModel):
        """
        Response from create_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::CreateScheduleResponse
        """

        success: bool = Field(True, description="Whether creation succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from CreateScheduleResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(success=data.get("success", True))

    class DeleteScheduleResponse(BaseModel):
        """
        Response from delete_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::DeleteScheduleResponse
        """

        success: bool = Field(True, description="Whether deletion succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from DeleteScheduleResponse protobuf."""
            return cls(success=True)

    class GetScheduleResponse(BaseModel):
        """
        Response from get_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::GetScheduleResponse
        """

        schedule: Optional[Schedule] = Field(None, description="Retrieved schedule")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from GetScheduleResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            schedule = None
            if "schedule" in data:
                from chronoqueue.api.schedule.v1 import schedule_pb2

                schedule_proto = proto_response.schedule
                schedule = Schedule.from_proto(schedule_proto)

            return cls(schedule=schedule)

    class ListSchedulesResponse(BaseModel):
        """
        Response from list_schedules operation.

        Proto source: proto/queueservice/v1/request_response.proto::ListSchedulesResponse
        """

        schedules: List[Schedule] = Field(default_factory=list, description="List of schedules")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from ListSchedulesResponse protobuf."""
            schedules = []
            for schedule_proto in proto_response.schedules:
                schedules.append(Schedule.from_proto(schedule_proto))

            return cls(schedules=schedules)

    class GetScheduleHistoryResponse(BaseModel):
        """
        Response from get_schedule_history operation.

        Proto source: proto/queueservice/v1/request_response.proto::GetScheduleHistoryResponse
        """

        schedule_id: Optional[str] = Field(None, description="Schedule ID")
        messages: List[Message] = Field(default_factory=list, description="Messages created by schedule")
        next_run: Optional[str] = Field(None, description="Next scheduled run")
        last_run: Optional[str] = Field(None, description="Last run time")
        created_at: Optional[str] = Field(None, description="Creation timestamp")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from GetScheduleHistoryResponse protobuf."""

            # Helper to convert Timestamp to string
            def timestamp_to_str(ts):
                if ts and ts.seconds:
                    return ts.ToJsonString()
                return None

            messages = []
            if hasattr(proto_response, "schedule_history") and proto_response.schedule_history:
                history = proto_response.schedule_history
                for msg_proto in history.messages:
                    messages.append(Message.from_proto(msg_proto))

                return cls(
                    schedule_id=history.schedule_id if history.schedule_id else None,
                    messages=messages,
                    next_run=timestamp_to_str(history.next_run),
                    last_run=timestamp_to_str(history.last_run),
                    created_at=timestamp_to_str(history.created_at),
                )

            return cls(messages=[])

    class PauseScheduleResponse(BaseModel):
        """
        Response from pause_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::PauseScheduleResponse
        """

        success: bool = Field(True, description="Whether pause succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from PauseScheduleResponse protobuf."""
            return cls(success=True)

    class ResumeScheduleResponse(BaseModel):
        """
        Response from resume_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::ResumeScheduleResponse
        """

        success: bool = Field(True, description="Whether resume succeeded")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from ResumeScheduleResponse protobuf."""
            return cls(success=True)

    class ValidateCalendarScheduleResponse(BaseModel):
        """
        Response from validate_calendar_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::ValidateCalendarScheduleResponse
        """

        valid: bool = Field(False, description="Whether the calendar schedule is valid")
        error_message: Optional[str] = Field(None, description="Validation error message if invalid")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from ValidateCalendarScheduleResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(
                valid=data.get("valid", False),
                error_message=data.get("error_message"),
            )

    class PreviewCalendarScheduleResponse(BaseModel):
        """
        Response from preview_calendar_schedule operation.

        Proto source: proto/queueservice/v1/request_response.proto::PreviewCalendarScheduleResponse
        """

        execution_times: List[str] = Field(default_factory=list, description="Upcoming execution times")

        model_config = ConfigDict(from_attributes=True)

        @classmethod
        def from_proto(cls, proto_response):
            """Create from PreviewCalendarScheduleResponse protobuf."""
            data = json_format.MessageToDict(proto_response, preserving_proto_field_name=True)
            return cls(execution_times=data.get("execution_times", []))

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

    # Schedule model placeholders
    class Schedule:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class ScheduleMetadata:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class ScheduleHistoryEntry:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class CreateScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class DeleteScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class GetScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class ListSchedulesResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class GetScheduleHistoryResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class PauseScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class ResumeScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class ValidateCalendarScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass

    class PreviewCalendarScheduleResponse:
        """Pydantic not installed. Install with: pip install pydantic"""

        pass


__all__ = [
    "PYDANTIC_AVAILABLE",
    # Queue and Message responses
    "CreateQueueResponse",
    "DeleteQueueResponse",
    "PostMessageResponse",
    "GetNextMessageResponse",
    "AcknowledgeMessageResponse",
    "RenewMessageLeaseResponse",
    "PeekQueueMessagesResponse",
    "GetQueueStateResponse",
    "SendMessageHeartBeatResponse",
    # Message models
    "Message",
    "MessageMetadata",
    "MessagePayload",
    # Schedule responses
    "CreateScheduleResponse",
    "DeleteScheduleResponse",
    "GetScheduleResponse",
    "ListSchedulesResponse",
    "GetScheduleHistoryResponse",
    "PauseScheduleResponse",
    "ResumeScheduleResponse",
    "ValidateCalendarScheduleResponse",
    "PreviewCalendarScheduleResponse",
    # Schedule models
    "Schedule",
    "ScheduleMetadata",
    "ScheduleHistoryEntry",
]
