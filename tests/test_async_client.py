"""
Tests for AsyncChronoqueueClient - async/await version of the client.

These tests verify that all async operations work correctly and match
the functionality of the synchronous client.
"""

import asyncio
from unittest.mock import AsyncMock, MagicMock, patch

import pytest

from chronoqueue.async_client import AsyncChronoqueueClient
from chronoqueue.exceptions import RpcOperationError
from chronoqueue.utils import (
    AcknowledgeMessageParams,
    PeekQueueMessagesParams,
    PostMessageParams,
    QueueOptions,
    ScheduleOptions,
    SchemaOptions,
    TlsConfig,
)


@pytest.fixture
async def async_client():
    """Create an AsyncChronoqueueClient instance for testing."""
    client = AsyncChronoqueueClient(
        host="localhost",
        port=50051,
        use_tls=False,
        heartbeat_max_duration=120,
        heartbeat_max_count=500,
    )
    yield client
    # Cleanup
    if client.channel:
        await client.close()


@pytest.mark.asyncio
async def test_async_client_initialization():
    """Test async client can be initialized without TLS."""
    client = AsyncChronoqueueClient(
        host="localhost",
        port=50051,
        use_tls=False,
    )
    assert client.host == "localhost"
    assert client.port == 50051
    assert client._use_tls is False
    assert client._heartbeat_max_duration == 300  # default
    assert client._heartbeat_max_count == 1000  # default


@pytest.mark.asyncio
async def test_async_client_context_manager():
    """Test async client works as an async context manager."""
    async with AsyncChronoqueueClient(host="localhost", port=50051, use_tls=False) as client:
        assert client is not None
        assert isinstance(client, AsyncChronoqueueClient)


@pytest.mark.asyncio
async def test_create_queue_success(async_client):
    """Test create_queue async method."""
    # Mock the stub
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.CreateQueue = AsyncMock(return_value=mock_response)

    options = QueueOptions(
        max_attempts=5,
        lease_duration="5m",
        exclusivity_key="test_key",
    )

    response = await async_client.create_queue("test_queue", options)
    assert response is not None
    async_client.stub.CreateQueue.assert_called_once()


@pytest.mark.asyncio
async def test_delete_queue_success(async_client):
    """Test delete_queue async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.DeleteQueue = AsyncMock(return_value=mock_response)

    response = await async_client.delete_queue("test_queue")
    assert response is not None
    async_client.stub.DeleteQueue.assert_called_once()


@pytest.mark.asyncio
async def test_post_message_success(async_client):
    """Test post_message async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.PostMessage = AsyncMock(return_value=mock_response)

    params = PostMessageParams(
        queue_name="test_queue",
        message_id="msg123",
        data={"key": "value"},
    )

    response = await async_client.post_message(params)
    assert response is not None
    async_client.stub.PostMessage.assert_called_once()


@pytest.mark.asyncio
async def test_acknowledge_message_success(async_client):
    """Test acknowledge_message async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.AcknowledgeMessage = AsyncMock(return_value=mock_response)

    params = AcknowledgeMessageParams(
        queue_name="test_queue",
        message_id="msg123",
        state=0,
    )

    response = await async_client.acknowledge_message(params)
    assert response is not None
    async_client.stub.AcknowledgeMessage.assert_called_once()


@pytest.mark.asyncio
async def test_renew_message_lease_success(async_client):
    """Test renew_message_lease async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.RenewMessageLease = AsyncMock(return_value=mock_response)

    response = await async_client.renew_message_lease("msg123", "10m")
    assert response is not None
    async_client.stub.RenewMessageLease.assert_called_once()


@pytest.mark.asyncio
async def test_peek_queue_messages_success(async_client):
    """Test peek_queue_messages async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.PeekQueueMessages = AsyncMock(return_value=mock_response)

    params = PeekQueueMessagesParams(
        queue_name="test_queue",
        limit=10,
        priority_range=None,
    )

    response = await async_client.peek_queue_messages(params)
    assert response is not None
    async_client.stub.PeekQueueMessages.assert_called_once()


@pytest.mark.asyncio
async def test_get_queue_state_success(async_client):
    """Test get_queue_state async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetQueueState = AsyncMock(return_value=mock_response)

    response = await async_client.get_queue_state("test_queue")
    assert response is not None
    async_client.stub.GetQueueState.assert_called_once()


@pytest.mark.asyncio
async def test_send_message_heartbeat_success(async_client):
    """Test send_message_heartbeat async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.SendMessageHeartbeat = AsyncMock(return_value=mock_response)

    response = await async_client.send_message_heartbeat("test_queue", "msg123")
    assert response is not None
    async_client.stub.SendMessageHeartbeat.assert_called_once()


@pytest.mark.asyncio
async def test_create_schedule_success(async_client):
    """Test create_schedule async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.CreateSchedule = AsyncMock(return_value=mock_response)

    options = ScheduleOptions(
        queue_name="test_queue",
        payload={"data": "value"},
        cron_schedule="0 0 * * *",
    )

    response = await async_client.create_schedule("schedule123", options)
    assert response is not None
    async_client.stub.CreateSchedule.assert_called_once()


@pytest.mark.asyncio
async def test_delete_schedule_success(async_client):
    """Test delete_schedule async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.DeleteSchedule = AsyncMock(return_value=mock_response)

    response = await async_client.delete_schedule("schedule123")
    assert response is not None
    async_client.stub.DeleteSchedule.assert_called_once()


@pytest.mark.asyncio
async def test_get_schedule_success(async_client):
    """Test get_schedule async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetSchedule = AsyncMock(return_value=mock_response)

    response = await async_client.get_schedule("schedule123")
    assert response is not None
    async_client.stub.GetSchedule.assert_called_once()


@pytest.mark.asyncio
async def test_list_schedules_success(async_client):
    """Test list_schedules async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.ListSchedules = AsyncMock(return_value=mock_response)

    response = await async_client.list_schedules(prefix="daily_")
    assert response is not None
    async_client.stub.ListSchedules.assert_called_once()


@pytest.mark.asyncio
async def test_get_schedule_history_success(async_client):
    """Test get_schedule_history async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetScheduleHistory = AsyncMock(return_value=mock_response)

    response = await async_client.get_schedule_history("schedule123", limit=20)
    assert response is not None
    async_client.stub.GetScheduleHistory.assert_called_once()


@pytest.mark.asyncio
async def test_pause_schedule_success(async_client):
    """Test pause_schedule async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.PauseSchedule = AsyncMock(return_value=mock_response)

    response = await async_client.pause_schedule("schedule123")
    assert response is not None
    async_client.stub.PauseSchedule.assert_called_once()


@pytest.mark.asyncio
async def test_resume_schedule_success(async_client):
    """Test resume_schedule async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.ResumeSchedule = AsyncMock(return_value=mock_response)

    response = await async_client.resume_schedule("schedule123")
    assert response is not None
    async_client.stub.ResumeSchedule.assert_called_once()


@pytest.mark.asyncio
async def test_register_schema_success(async_client):
    """Test register_schema async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.RegisterSchema = AsyncMock(return_value=mock_response)

    options = SchemaOptions(
        name="Test Schema",
        description="A test schema",
        content='{"type": "object"}',
        content_type="json-schema",
    )

    response = await async_client.register_schema("schema123", options)
    assert response is not None
    async_client.stub.RegisterSchema.assert_called_once()


@pytest.mark.asyncio
async def test_get_schema_success(async_client):
    """Test get_schema async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetSchema = AsyncMock(return_value=mock_response)

    response = await async_client.get_schema("schema123", version=1)
    assert response is not None
    async_client.stub.GetSchema.assert_called_once()


@pytest.mark.asyncio
async def test_list_schemas_success(async_client):
    """Test list_schemas async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.ListSchemas = AsyncMock(return_value=mock_response)

    response = await async_client.list_schemas(prefix="test_", limit=50)
    assert response is not None
    async_client.stub.ListSchemas.assert_called_once()


@pytest.mark.asyncio
async def test_delete_schema_success(async_client):
    """Test delete_schema async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.DeleteSchema = AsyncMock(return_value=mock_response)

    response = await async_client.delete_schema("schema123", version=1)
    assert response is not None
    async_client.stub.DeleteSchema.assert_called_once()


@pytest.mark.asyncio
async def test_validate_payload_success(async_client):
    """Test validate_payload async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.ValidatePayload = AsyncMock(return_value=mock_response)

    payload = '{"orderId": "123", "amount": 50.0}'
    response = await async_client.validate_payload("schema123", payload, version=1)
    assert response is not None
    async_client.stub.ValidatePayload.assert_called_once()


@pytest.mark.asyncio
async def test_get_dlq_messages_success(async_client):
    """Test get_dlq_messages async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetDLQMessages = AsyncMock(return_value=mock_response)

    response = await async_client.get_dlq_messages("test_dlq", limit=50)
    assert response is not None
    async_client.stub.GetDLQMessages.assert_called_once()


@pytest.mark.asyncio
async def test_requeue_from_dlq_success(async_client):
    """Test requeue_from_dlq async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.RequeueFromDLQ = AsyncMock(return_value=mock_response)

    response = await async_client.requeue_from_dlq("test_dlq", "msg123", "target_queue")
    assert response is not None
    async_client.stub.RequeueFromDLQ.assert_called_once()


@pytest.mark.asyncio
async def test_delete_from_dlq_success(async_client):
    """Test delete_from_dlq async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.DeleteFromDLQ = AsyncMock(return_value=mock_response)

    response = await async_client.delete_from_dlq("test_dlq", "msg123")
    assert response is not None
    async_client.stub.DeleteFromDLQ.assert_called_once()


@pytest.mark.asyncio
async def test_purge_dlq_success(async_client):
    """Test purge_dlq async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.PurgeDLQ = AsyncMock(return_value=mock_response)

    response = await async_client.purge_dlq("test_dlq")
    assert response is not None
    async_client.stub.PurgeDLQ.assert_called_once()


@pytest.mark.asyncio
async def test_get_dlq_stats_success(async_client):
    """Test get_dlq_stats async method."""
    async_client.stub = AsyncMock()
    mock_response = MagicMock()
    async_client.stub.GetDLQStats = AsyncMock(return_value=mock_response)

    response = await async_client.get_dlq_stats("test_dlq")
    assert response is not None
    async_client.stub.GetDLQStats.assert_called_once()


@pytest.mark.asyncio
async def test_heartbeat_observability(async_client):
    """Test heartbeat observability methods."""
    # Initially no heartbeats
    assert async_client.get_active_heartbeat_count() == 0
    assert async_client.get_heartbeat_stats() == {}
    assert async_client.get_active_heartbeats() == []


@pytest.mark.asyncio
async def test_stop_heartbeat(async_client):
    """Test stop_heartbeat method."""
    # Create a fake heartbeat entry
    msg_id = "test_msg_123"
    async_client._heartbeat_stop_events[msg_id] = asyncio.Event()

    # Stop it
    result = await async_client.stop_heartbeat(msg_id)
    assert result is True

    # Stopping non-existent heartbeat returns False
    result = await async_client.stop_heartbeat("nonexistent")
    assert result is False
