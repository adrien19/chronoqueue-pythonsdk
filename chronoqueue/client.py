import grpc
import json
import logging
from proto import service_grpc, service_pb2

# Initialize logging
logging.basicConfig(level=logging.INFO)

class ChronoqueueClient:
    def __init__(self, host, port, use_tls=True, cert_path=None):
        self.host = host
        self.port = port

        if use_tls:
            if cert_path is None:
                raise ValueError("cert_path must be provided if use_tls is True")
            credentials = grpc.ssl_channel_credentials(open(cert_path, 'rb').read())
            self.channel = grpc.secure_channel(f"{host}:{port}", credentials)
        else:
            self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = service_grpc.ChronoQueueStub(self.channel)

    def create_queue(self, name):
        try:
            queueInfo = service_pb2.Queue(name=name)
            request = service_pb2.CreateQueueRequest(queue=queueInfo)
            response = self.stub.CreateQueue(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error creating queue: {e.details()}")
            return None

    def delete_queue(self, name):
        try:
            request = service_pb2.DeleteQueueRequest(name=name)
            response = self.stub.DeleteQueue(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error deleting queue: {e.details()}")
            return None
    
    def post_message(self, queue_name, content):
        try:
            byte_data = json.dumps(content.get("payload")).encode('utf-8')
            meta_payload = service_pb2.Payload(data=byte_data)
            msg_metadata = service_pb2.Message.Metadata(payload=meta_payload, state=1)
            message = service_pb2.Message(message_id=content.get("message_id"), metadata=msg_metadata)
            request = service_pb2.PostMessageRequest(queue_name=queue_name, message=message)
            response = self.stub.PostMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error posting message: {e.details()}")
            return None

    def get_next_message(self, queue_name):
        try:
            request = service_pb2.GetNextMessageRequest(queue_name=queue_name)
            response = self.stub.GetNextMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error getting next message: {e.details()}")
            return None

    def acknowledge_message(self, message_id):
        try:
            request = service_pb2.AcknowledgeMessageRequest(message_id=message_id)
            response = self.stub.AcknowledgeMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error acknowledging message: {e.details()}")
            return None

    def renew_message_lease(self, message_id, new_lease_duration):
        try:
            request = service_pb2.RenewMessageLeaseRequest(message_id=message_id, new_lease_duration=new_lease_duration)
            response = self.stub.RenewMessageLease(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error renewing message lease: {e.details()}")
            return None

    def peek_queue_messages(self, queue_name, max_messages):
        try:
            request = service_pb2.PeekQueueMessagesRequest(queue_name=queue_name, max_messages=max_messages)
            response = self.stub.PeekQueueMessages(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error peeking queue messages: {e.details()}")
            return None

    def get_queue_state(self, queue_name):
        try:
            request = service_pb2.GetQueueStateRequest(queue_name=queue_name)
            response = self.stub.GetQueueState(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error getting queue state: {e.details()}")
            return None

    def close(self):
        if self.channel:
            self.channel.close()