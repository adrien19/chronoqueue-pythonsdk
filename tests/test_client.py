import pytest
import grpc
from unittest.mock import Mock
from chronoqueue.client import ChronoqueueClient
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
        response = mock_client.create_queue("test_queue")

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

    # Call the client's method
    content = {
        "message_id":"1345_message_id",
        "payload": {
            "user": "test1",
            "user_id":"test1_userID"
        }
    }
    response = mock_client.post_message(queue_name="test_queue", content=content)

    # Assert the expected behavior
    mock_client.stub.PostMessage.assert_called_once()
    assert response == mock_response
