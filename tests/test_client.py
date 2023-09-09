import pytest
import grpc
from unittest.mock import Mock
from chronoqueue.client import ChronoqueueClient
from chronoqueue.utils import PostMessageParams, \
    AcknowledgeMessageParams, PeekQueueMessagesParams, MessageState
from proto import service_pb2, service_grpc

@pytest.fixture
def mock_client():
    mock_channel = Mock(spec=grpc.Channel)
    client = ChronoqueueClient('localhost', '50051', use_tls=False)
    client.channel = mock_channel
    # Mock the ChronoQueueStub
    client.stub = Mock(spec=service_grpc.ChronoQueueStub(mock_channel))
    return client

def test_create_queue(mock_client: ChronoqueueClient):
        # Mock the gRPC response
        mock_response = service_pb2.CreateQueueResponse()
        mock_client.stub.CreateQueue.return_value = mock_response

        # Call the client's method
        response = mock_client.create_queue(name="test_queue")

        # Assert the expected behavior
        mock_client.stub.CreateQueue.assert_called_once()
        assert response == mock_response

def test_delete_queue(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.DeleteQueueResponse()
    mock_client.stub.DeleteQueue.return_value = mock_response

    # Call the client's method
    response = mock_client.delete_queue("test_queue")

    # Assert the expected behavior
    mock_client.stub.DeleteQueue.assert_called_once()
    assert response == mock_response

def test_post_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    # mock_response = service_pb2.PostMessageResponse(success=True, message_id="12345")
    mock_response = service_pb2.PostMessageResponse()
    mock_client.stub.PostMessage.return_value = mock_response

    # create required params
    msg_params = PostMessageParams(
        message_id="", 
        data={"user": "test1", "user_id":"test1_userID"}, 
        queue_name="test_queue",
    )
    response = mock_client.post_message(msg_params=msg_params)

    # Assert the expected behavior
    mock_client.stub.PostMessage.assert_called_once()
    assert response == mock_response

def test_get_next_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.GetNextMessageResponse()
    mock_client.stub.GetNextMessage.return_value = mock_response

    # Call the client's method
    response = mock_client.get_next_message(queue_name="test_queue", lease_duration=60)

    # Assert the expected behavior
    mock_client.stub.GetNextMessage.assert_called_once()
    assert response == mock_response


def test_acknowledge_message(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.AcknowledgeMessageResponse()
    mock_client.stub.AcknowledgeMessage.return_value = mock_response

    # Prepare params
    params = AcknowledgeMessageParams(message_id="12345", queue_name="test_queue", state=MessageState.COMPLETED.value)

    # Call the client's method
    response = mock_client.acknowledge_message(params=params)

    # Assert the expected behavior
    mock_client.stub.AcknowledgeMessage.assert_called_once()
    assert response == mock_response


def test_renew_message_lease(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.RenewMessageLeaseResponse()
    mock_client.stub.RenewMessageLease.return_value = mock_response

    # Call the client's method
    response = mock_client.renew_message_lease(message_id="12345", new_lease_duration=120)

    # Assert the expected behavior
    mock_client.stub.RenewMessageLease.assert_called_once()
    assert response == mock_response


def test_peek_queue_messages(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.PeekQueueMessagesResponse()
    mock_client.stub.PeekQueueMessages.return_value = mock_response

    # Prepare params
    params = PeekQueueMessagesParams(queue_name="test_queue", limit=5, priority_range=None)

    # Call the client's method
    response = mock_client.peek_queue_messages(params=params)

    # Assert the expected behavior
    mock_client.stub.PeekQueueMessages.assert_called_once()
    assert response == mock_response


def test_get_queue_state(mock_client: ChronoqueueClient):
    # Mock the gRPC response
    mock_response = service_pb2.GetQueueStateResponse()
    mock_client.stub.GetQueueState.return_value = mock_response

    # Call the client's method
    response = mock_client.get_queue_state(queue_name="test_queue")

    # Assert the expected behavior
    mock_client.stub.GetQueueState.assert_called_once()
    assert response == mock_response


def test_close(mock_client: ChronoqueueClient):
    # Call the client's method (No response is expected for this method)
    mock_client.close()

    # Assert the expected behavior
    mock_client.channel.close.assert_called_once()
