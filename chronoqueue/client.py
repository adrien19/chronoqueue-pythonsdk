import grpc
import logging
from .exceptions import InitializationError, RpcOperationError
from .utils import TlsConfig, PostMessageParams, PostMessageOptions, \
    AcknowledgeMessageParams, PeekQueueMessagesParams, QueueOptions, _create_post_message_request
from .api.v1 import chronoqueue_pb2_grpc, chronoqueue_pb2

# Initialize logging
logging.basicConfig(level=logging.INFO)

class ChronoqueueClient:
    """
    Client for interacting with the Chronoqueue service using gRPC.

    The `ChronoqueueClient` provides an interface to interact with the Chronoqueue service. It wraps 
    the gRPC methods and offers additional functionality and error handling to simplify the interaction 
    with the service.

    This client supports various operations, such as creating and deleting queues, posting messages to 
    queues, retrieving messages from queues, and managing message leases, among others.

    Attributes:
    ----------
    host (str): The host address of the Chronoqueue service.
    port (int): The port number of the Chronoqueue service.
    use_tls (bool, optional): Flag to determine if TLS should be used. Defaults to True.
    tls_config (TlsConfig, optional): The TLS configuration for secure connections.

    channel : grpc.Channel
        The gRPC channel used for communication with the Chronoqueue service.

    stub : chronoqueue_pb2_grpc.ChronoQueueStub
        The gRPC stub generated from the protobuf definitions, enabling direct interaction with 
        the Chronoqueue service.

    Examples:
    --------
    # Initialize the client for a secure connection
    >>> client = ChronoqueueClient(host="localhost", port=50051, use_tls=True, cert_path="/path/to/cert.crt")

    # Create a new queue
    >>> client.create_queue(CreateQueueParams(name="my_new_queue"))

    # Post a message to a queue
    >>> msg_params = PostMessageParams(message_id="12345", data={"key": "value"})
    >>> client.post_message(msg_params)

    """

    def __init__(self, host, port, use_tls=True, tls_config: TlsConfig = None):
        """
        Initializes the Chronoqueue SDK client.

        This constructor establishes a connection to the Chronoqueue service either over a secure 
        (TLS) channel or an insecure channel based on the provided parameters.

        Parameters:
        ----------
            host (str): The host address of the Chronoqueue service.
            port (int): The port number of the Chronoqueue service.
            use_tls (bool, optional): Flag to determine if TLS should be used. Defaults to True.
            tls_config (TlsConfig, optional): The TLS configuration for secure connections.

        Raises:
        ------
        InitializationError:
            If `use_tls` is True but `cert_path` is not provided.

        Example:
        --------
        # For a secure connection
        >>> client = ChronoqueueClient(host="localhost", port=50051, use_tls=True, cert_path="/path/to/cert.crt")

        # For an insecure connection
        >>> client = ChronoqueueClient(host="localhost", port=50051, use_tls=False)

        """
        self.host = host
        self.port = port

        if use_tls:
            if tls_config is None:
                raise InitializationError("TLS is enabled but no TlsConfig provided")
            
            with open(tls_config.ca_path, 'rb') as f:
                ca = f.read()
            with open(tls_config.client_crt_path, 'rb') as f:
                client_crt = f.read()
            with open(tls_config.client_key_path, 'rb') as f:
                client_key = f.read()
            credentials = grpc.ssl_channel_credentials(ca, client_key, client_crt)
            self.channel = grpc.secure_channel(f"{host}:{port}", credentials)
        else:
            self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = chronoqueue_pb2_grpc.ChronoQueueStub(self.channel)

    def _handle_error(self, error, handler=None):
        """Internal method to handle errors. Calls the custom error handler if set."""
        if handler:
            handler(error)
        else:
            # Default behavior is to raise the error
            raise error

    def create_queue(self, name: str, options: QueueOptions = None, error_handler=None) -> chronoqueue_pb2.CreateQueueResponse:
        """
        Creates a new queue in the Chronoqueue service with the specified parameters.

        This method facilitates the creation of a new queue with specific configurations
        as defined by the `QueueOptions` parameter. If any error occurs during the 
        queue creation, it can be handled using a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        name : string
            The required parameter for creating the new queue with the given name.
        options : QueueOptions
            The optional configurations for creating the new queue.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : CreateQueueResponse
            The response from the Chronoqueue service, containing details about the created queue.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> from chronoqueuesdk import QueueOptions
        >>> options = QueueOptions(type=QueueType.SIMPLE, exclusivity_key="key123")
        >>> client.create_queue(name="my_new_queue", options=options)

        """
        try:
            queueOptions = chronoqueue_pb2.Queue.Options(type=options.type.value, dequeue_attempts=options.dequeue_attempts, lease_duration=options.lease_duration, exclusivity_key=options.exclusivity_key, invisibility_duration=options.invisibility_duration) if options is not None else chronoqueue_pb2.Queue.Options()
            queueInfo = chronoqueue_pb2.Queue(name=name, metadata=queueOptions)
            request = chronoqueue_pb2.CreateQueueRequest(queue=queueInfo)
            response = self.stub.CreateQueue(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error creating queue: {e.details()}")
            error = RpcOperationError(f"Failed to create queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def delete_queue(self, name, error_handler=None) -> chronoqueue_pb2.DeleteQueueResponse:
        """
        Deletes a specified queue from the Chronoqueue service.

        This method provides functionality to delete a queue by its name. Once deleted, 
        the messages and metadata associated with the queue will be permanently removed.
        If any error arises during the deletion process, it can be managed using a custom 
        error handler or the SDK's default mechanism.

        Parameters:
        ----------
        name : str
            The name of the queue to be deleted.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : DeleteQueueResponse
            The response from the Chronoqueue service, confirming the deletion of the queue.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> client.delete_queue("my_queue_to_delete")

        """
        try:
            request = chronoqueue_pb2.DeleteQueueRequest(name=name)
            response = self.stub.DeleteQueue(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error deleting queue: {e.details()}")
            error = RpcOperationError(f"Failed to delete queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
    
    def post_message(self, msg_params: PostMessageParams, msg_options=PostMessageOptions(), error_handler=None) -> chronoqueue_pb2.PostMessageResponse:
        """
        Posts a new message to the Chronoqueue service.

        This method allows to send a message to the Chronoqueue service, providing flexibility in terms of message
        parameters and additional options. Errors encountered during the operation can be handled using a custom error handler
        or the SDK's default mechanism.

        Parameters:
        ----------
        msg_params : PostMessageParams
            Contains the core parameters for the message, such as `message_id`, `data`, and `queue_name`.
            - `message_id` (str): The unique identifier for the message.
            - `data` (dict): The data to be sent as a message, represented as a dictionary.
            - `queue_name` (str): The name of the queue to post the message to. Default is "default_queue".

        msg_options : PostMessageOptions, optional (default=PostMessageOptions())
            Contains additional options and configurations for the message.
            - `priority` (int): The priority level of the message. Default is 0.
            - `state` (MessageState): The initial state of the message. Default is INVISIBLE.
            - `invisibility_duration` (int): Duration (in seconds) the message should remain invisible. Default is 0.
            - `attempts_left` (int): Number of delivery attempts left for the message. Default is 3.
            - `data_metadata` (dict): The metadata option that can be attached to the data sent as a message, represented as a dictionary. Default is an empty dictionary.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : PostMessageResponse
            The response from the Chronoqueue service, containing details about the posted message.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> msg_params = PostMessageParams(message_id="12345", data={"key": "value"}, queue_name="my_queue")
        >>> options = PostMessageOptions(priority=5, state=MessageState.PENDING)
        >>> def custom_error_handler(error):
        ...     print(f"Error encountered: {error}")
        >>> client.post_message(msg_params, msg_options, error_handler=custom_error_handler)

        """
        try:
            request = _create_post_message_request(params=msg_params, options=msg_options)
            response = self.stub.PostMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error posting message: {e.details()}")
            error = RpcOperationError(f"Failed to post message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
        

    def get_next_message(self, queue_name: str, lease_duration: int, error_handler=None) -> chronoqueue_pb2.GetNextMessageResponse:
        """
        Retrieves the next message from the specified queue in the Chronoqueue service.

        This method fetches the next available message from the queue, making it unavailable 
        for other consumers for a certain period of time (defined by the lease duration). 
        If an error occurs during the message retrieval, it can be handled using a custom error handler 
        or the SDK's default mechanism.

        Parameters:
        ----------
        queue_name : str
            The name of the queue from which the next message is to be fetched.
        lease_duration : int
            The number (in seconds) a message will be leased for.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : GetNextMessageResponse
            The response from the Chronoqueue service, containing details about the fetched message.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> message = client.get_next_message(queue_name="my_queue", lease_duration=300)

        """
        try:
            request = chronoqueue_pb2.GetNextMessageRequest(queue_name=queue_name, lease_duration=lease_duration)
            response = self.stub.GetNextMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error getting next message: {e.details()}")
            error = RpcOperationError(f"Failed to get next message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
        

    def acknowledge_message(self, params: AcknowledgeMessageParams, error_handler=None) -> chronoqueue_pb2.AcknowledgeMessageResponse:
        """
        Acknowledges a message in the Chronoqueue service.

        This method allows users to acknowledge a previously fetched message, indicating that the message
        has been processed successfully or requires a change in its state. If the method encounters an error, 
        it can be handled using a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        params : AcknowledgeMessageParams
            Contains the parameters required to acknowledge the message.
            - `message_id` (str): The unique identifier for the message.
            - `queue_name` (str): The name of the queue from which the message was fetched.
            - `state` (MessageState): The new state for the message after acknowledgment.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : AcknowledgeMessageResponse
            The response from the Chronoqueue service, containing details about the acknowledgment status.
            As of version 1, this returns empty AcknowledgeMessageResponse.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> from chronoqueuesdk.utils import AcknowledgeMessageParams
        >>> params = AcknowledgeMessageParams(message_id="12345", queue_name="my_queue", state=MessageState.COMPLETED)
        >>> client.acknowledge_message(params)

        """
        try:
            request = chronoqueue_pb2.AcknowledgeMessageRequest(
                message_id=params.message_id, 
                queue_name=params.queue_name,
                state=params.state
            )
            response = self.stub.AcknowledgeMessage(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error acknowledging message: {e.details()}")
            error = RpcOperationError(f"Failed to acknowlege message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
        

    def renew_message_lease(self, message_id: str, new_lease_duration: int, error_handler=None) -> chronoqueue_pb2.RenewMessageLeaseResponse:
        """
        Renews the lease duration of a specified message in the Chronoqueue service.

        In scenarios where a message is being processed but needs more time than the original 
        lease duration allowed, this method can be used to extend the lease. By renewing the lease, 
        the message remains invisible to other consumers for the new lease duration. If any error 
        occurs during the lease renewal, it can be handled using a custom error handler or the SDK's 
        default mechanism.

        Parameters:
        ----------
        message_id : str
            The unique identifier of the message whose lease is to be renewed.

        new_lease_duration : int
            The new lease duration (in seconds) for the message.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : RenewMessageLeaseResponse
            The response from the Chronoqueue service, containing details about the renewed lease status.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> client.renew_message_lease(message_id="12345", new_lease_duration=300)

        """
        try:
            request = chronoqueue_pb2.RenewMessageLeaseRequest(message_id=message_id, lease_duration=new_lease_duration)
            response = self.stub.RenewMessageLease(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error renewing message lease: {e.details()}")
            error = RpcOperationError(f"Failed to renew message lease due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
        

    def peek_queue_messages(self, params: PeekQueueMessagesParams, error_handler=None) -> chronoqueue_pb2.PeekQueueMessagesResponse:
        """
        Peeks messages from a specified queue in the Chronoqueue service.

        This method allows users to retrieve a specified number of messages from a queue without removing them from the queue. 
        It's useful for previewing the content of a queue or for use cases where messages need to be read but not immediately acknowledged.
        If the method encounters an error, it can be handled using a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        params : PeekQueueMessagesParams
            Contains the parameters required to peek the messages from a queue.
            - `queue_name` (str): The name of the queue to peek messages from.
            - `limit` (int): The maximum number of messages to retrieve.
            - `priority` (int): Optionally specify a priority level to filter messages.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : PeekQueueMessagesResponse
            The response from the Chronoqueue service, containing the peeked messages and related details.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> from chronoqueuesdk.utils import PeekQueueMessagesParams
        >>> params = PeekQueueMessagesParams(queue_name="my_queue", limit=10, priority=5)
        >>> client.peek_queue_messages(params)

        """
        try:
            request = chronoqueue_pb2.PeekQueueMessagesRequest(
                queue_name=params.queue_name, 
                limit=params.limit, 
                priority_range=params.priority_range
            )
            response = self.stub.PeekQueueMessages(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error peeking queue messages: {e.details()}")
            error = RpcOperationError(f"Failed to peek queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
        

    def get_queue_state(self, queue_name, error_handler=None) -> chronoqueue_pb2.GetQueueStateResponse:
        """
        Retrieves the state of a specified queue in the Chronoqueue service.

        This method allows users to get the current state and statistics of a specified queue, 
        which can include details like the number of pending messages, the number of running messages, 
        and other relevant metrics. If the method encounters an error, it can be handled using 
        a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        queue_name : str
            The name of the queue whose state is to be retrieved.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : GetQueueStateResponse
            The response from the Chronoqueue service, containing details about the state of the specified queue.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> client.get_queue_state("my_queue")

        """
        try:
            request = chronoqueue_pb2.GetQueueStateRequest(queue_name=queue_name)
            response = self.stub.GetQueueState(request)
            return response
        except grpc.RpcError as e:
            logging.error(f"Error getting queue state: {e.details()}")
            error = RpcOperationError(f"Failed to get queue state due to: {e.details()}")
            self._handle_error(error, handler=error_handler)



    def close(self, error_handler=None) -> None:
        """
        Closes the gRPC channel used by the SDK to communicate with the Chronoqueue service.

        This method ensures that resources are properly released and the SDK cleans up any 
        open connections to the Chronoqueue service. It is recommended to call this method 
        once you are done using the SDK. If any error occurs during the closing process, 
        it can be handled using a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        None

        Raises:
        ------
        RpcOperationError:
            If there's an error closing the gRPC channel and no custom error handler is provided.

        Example:
        --------
        >>> client = ChronoqueueClient(host="localhost", port=50051)
        >>> # ... perform operations ...
        >>> client.close()

        """
        try:
            if self.channel:
                return self.channel.close()
        except grpc.RpcError as e:
            logging.error(f"Error closing rpc channel: {e.details()}")
            error = RpcOperationError(f"Failed to close RPC channel due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
