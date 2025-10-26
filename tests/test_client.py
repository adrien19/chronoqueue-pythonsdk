import threading
from collections import deque
from unittest.mock import Mock

import grpc
import pytest

from chronoqueue.api.queueservice.v1 import request_response_pb2, service_pb2_grpc
from chronoqueue.client import ChronoqueueClient
from chronoqueue.exceptions import RpcOperationError
from chronoqueue.utils import AcknowledgeMessageParams, MessageState, PeekQueueMessagesParams, PostMessageParams


@pytest.fixture
def mock_client():
    mock_channel = Mock(spec=grpc.Channel)
    mock_channel._channel = Mock()
    mock_channel._channel.check_connectivity_state = Mock()
    client = ChronoqueueClient("localhost", 50051, use_tls=False)
    client.channel = mock_channel
    # Mock the QueueServiceStub
    client.stub = Mock(spec=service_pb2_grpc.QueueServiceStub(mock_channel))
    client._heartbeat_data = Mock(spec=deque)
    client._stop_heartbeat = Mock(spec=threading.Event)
    client._heartbeat_manager_thread = Mock(spec=threading.Thread)
    return client


class MockRpcError(grpc.RpcError):
    def __init__(self, details):
        self._details = details

    def details(self):
        return self._details


def test_create_queue(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.CreateQueueResponse()
    mock_client.stub.CreateQueue.return_value = mock_response

    # Call the client's method
    response = mock_client.create_queue(name="test_queue")

    # Assert the expected behavior
    mock_client.stub.CreateQueue.assert_called_once()
    assert response.to_proto() == mock_response


def test_error_scenario(mock_client: ChronoqueueClient):
    # Mock gRPC method to raise an RpcError
    mock_client.stub.CreateQueue.side_effect = MockRpcError("An error occurred")

    # Check if the error handler is properly invoked or the exception is raised
    with pytest.raises(RpcOperationError):
        mock_client.create_queue(name="test_queue")


def test_delete_queue(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.DeleteQueueResponse()
    mock_client.stub.DeleteQueue.return_value = mock_response

    # Call the client's method
    response = mock_client.delete_queue("test_queue")

    # Assert the expected behavior
    mock_client.stub.DeleteQueue.assert_called_once()
    assert response.to_proto() == mock_response


def test_post_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    # mock_response = request_response_pb2.PostMessageResponse(success=True, message_id="12345")
    mock_response = request_response_pb2.PostMessageResponse()
    mock_client.stub.PostMessage.return_value = mock_response

    # create required params
    msg_params = PostMessageParams(
        message_id="message_id",
        data={"user": "test1", "user_id": "test1_userID"},
        queue_name="test_queue",
    )
    response = mock_client.post_message(msg_params=msg_params)

    # Assert the expected behavior
    mock_client.stub.PostMessage.assert_called_once()
    assert response.to_proto() == mock_response


def test_get_next_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.GetNextMessageResponse()
    mock_client.stub.GetNextMessage.return_value = mock_response

    # Call the client's method
    response = mock_client.get_next_message(queue_name="test_queue", lease_duration="60s")

    # Assert the expected behavior
    mock_client.stub.GetNextMessage.assert_called_once()
    assert response.to_proto() == mock_response


def test_heartbeat_management(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.SendMessageHeartBeatResponse()
    mock_client.stub.SendMessageHeartBeat.return_value = mock_response

    # Test data
    queue_name = "test_queue"
    message_id = "12345"

    # Call the method (Assuming you have a method that handles heartbeats)
    # This might involve threading and time.sleep which could be mocked for unit testing
    response = mock_client.send_message_heartbeat(queue_name, message_id)

    # Assert the expected behavior
    mock_client.stub.SendMessageHeartBeat.assert_called_once()
    assert response.to_proto() == mock_response


def test_acknowledge_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.AcknowledgeMessageResponse()
    mock_client.stub.AcknowledgeMessage.return_value = mock_response

    # Prepare params
    params = AcknowledgeMessageParams(message_id="12345", queue_name="test_queue", state=MessageState.COMPLETED.value)

    # Call the client's method
    response = mock_client.acknowledge_message(params=params)

    # Assert the expected behavior
    mock_client.stub.AcknowledgeMessage.assert_called_once()
    assert response.to_proto() == mock_response


def test_renew_message_lease(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.RenewMessageLeaseResponse()
    mock_client.stub.RenewMessageLease.return_value = mock_response

    # Call the client's method
    response = mock_client.renew_message_lease(message_id="12345", new_lease_duration="40s")

    # Assert the expected behavior
    mock_client.stub.RenewMessageLease.assert_called_once()
    assert response.to_proto() == mock_response


def test_peek_queue_messages(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.PeekQueueMessagesResponse()
    mock_client.stub.PeekQueueMessages.return_value = mock_response

    # Prepare params
    params = PeekQueueMessagesParams(queue_name="test_queue", limit=5, priority_range=None)

    # Call the client's method
    response = mock_client.peek_queue_messages(params=params)

    # Assert the expected behavior
    mock_client.stub.PeekQueueMessages.assert_called_once()
    assert response.to_proto() == mock_response


def test_get_queue_state(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = request_response_pb2.GetQueueStateResponse()
    mock_client.stub.GetQueueState.return_value = mock_response

    # Call the client's method
    response = mock_client.get_queue_state(queue_name="test_queue")

    # Assert the expected behavior
    mock_client.stub.GetQueueState.assert_called_once()
    assert response.to_proto() == mock_response


def test_close_and_succeed(mock_client: ChronoqueueClient):
    """
    Test the happy path where the channel is open and can be closed without issues.
    """
    mock_client.channel._channel.check_connectivity_state.return_value = grpc.ChannelConnectivity.READY

    # Call close and check
    mock_client.close()

    # Ensure the heartbeat manager was signaled to stop and the thread was joined
    mock_client._stop_heartbeat.set.assert_called_once()
    mock_client._heartbeat_manager_thread.join.assert_called_once()

    # Ensure the channel was checked and closed
    mock_client.channel._channel.check_connectivity_state.assert_called_once_with(True)
    mock_client.channel.close.assert_called_once()


def test_close_channel_already_closed_or_none(mock_client: ChronoqueueClient):
    """
    Test trying to close a channel that's either already closed or is None.
    """
    mock_client.channel._channel.check_connectivity_state.return_value = grpc.ChannelConnectivity.SHUTDOWN

    # Call close and check
    mock_client.close()

    # Ensure the channel was checked and not closed
    mock_client.channel._channel.check_connectivity_state.assert_called_once_with(True)

    # Ensure the heartbeat manager was signaled to stop and the thread was joined
    mock_client._stop_heartbeat.set.assert_not_called()
    mock_client._heartbeat_manager_thread.join.assert_not_called()

    mock_client.channel.close.assert_not_called()


def test_close_with_error(mock_client: ChronoqueueClient):
    """
    Test the scenario where an error is raised when trying to close the channel.
    """
    mock_client.channel._channel.check_connectivity_state.return_value = grpc.ChannelConnectivity.READY
    mock_client.channel.close.side_effect = MockRpcError("Error occured")

    # Call close and check
    with pytest.raises(RpcOperationError):
        mock_client.close()

    # Ensure the channel was checked and a close attempt was made
    mock_client.channel._channel.check_connectivity_state.assert_called_once_with(True)
    mock_client.channel.close.assert_called_once()

    # Ensure the heartbeat manager was signaled to stop and the thread was joined
    mock_client._stop_heartbeat.set.assert_called_once()
    mock_client._heartbeat_manager_thread.join.assert_called_once()
