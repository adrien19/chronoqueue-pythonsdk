import logging
import os
import threading
import time
from collections import deque
from random import randint

import grpc
from google.protobuf.duration_pb2 import Duration

from .api.message.v1 import message_pb2
from .api.message.v1.message_pb2 import Message
from .api.queue.v1 import queue_pb2
from .api.queueservice.v1 import request_response_pb2, service_pb2_grpc
from .exceptions import InitializationError, RpcOperationError
from .utils import (
    AcknowledgeMessageParams,
    PeekQueueMessagesParams,
    PostMessageParams,
    QueueOptions,
    ResponseWrapper,
    TlsConfig,
    _create_post_message_request,
    string_to_duration,
)

# Initialize logging
logging.basicConfig(level=logging.INFO)


class ChronoqueueClient:
    """
    A client for interacting with the Chronoqueue distributed task queue via gRPC.

    Chronoqueue is a distributed task queue that facilitates the sending, processing,
    and acknowledgment of messages across distributed systems. `ChronoqueueClient` serves
    as the Python SDK to interact with Chronoqueue, offering an API to perform various
    operations such as enqueueing messages, processing them, and maintaining their state.

    The client connects to a Chronoqueue service instance, enabling to perform
    operations on the queue programmatically, ensuring robust communication and error handling
    to facilitate interactions with the service.

    Attributes:
    ----------
    host : str
        The hostname or IP address of the Chronoqueue service to connect to.
    port : int
        The port number on which the Chronoqueue service is listening.
    use_tls : bool, optional
        A flag indicating whether to use TLS for the connection, by default True.
    tls_config : TlsConfig, optional
        Configuration for TLS, providing paths to CA, client certificate, and client key, by default None.
    channel : grpc.Channel
        The gRPC channel used to communicate with the Chronoqueue service.
    stub : chronoqueue_pb2_grpc.ChronoQueueStub
        A gRPC stub to interact with the Chronoqueue service using the gRPC protocol.

    Examples:
    --------
    # Initialize the client for a secure connection
    >>> client = ChronoqueueClient(host="localhost", port=50051, use_tls=True, tls_config=my_tls_config)

    # Create a new queue
    >>> client.create_queue(CreateQueueParams(name="my_new_queue"))

    # Post a message to a queue
    >>> msg_params = PostMessageParams(message_id="12345", data={"key": "value"})
    >>> client.post_message(msg_params)
    """

    def __init__(self, host: str, port: int, use_tls=True, tls_config: TlsConfig = None):
        """
        Initialize the ChronoqueueClient.

        Establishes a connection to the Chronoqueue service, using either a secure or insecure
        channel, based on the provided parameters. It initializes the gRPC channel and stub,
        facilitating further interactions with the Chronoqueue service.

        Parameters:
        ----------
        host : str
            The hostname or IP address of the Chronoqueue service.
        port : int
            The port number on which the Chronoqueue service is running.
        use_tls : bool, optional
            Indicates whether to use TLS for the connection, by default True.
        tls_config : TlsConfig, optional
            Configuration for TLS connectivity, providing paths to CA, client certificate,
            and client key. Required if `use_tls` is True, by default None.

        Raises:
        ------
        InitializationError
            If `use_tls` is True but `tls_config` is not provided or the file paths within
            `tls_config` do not exist.
        """
        self.host = host
        self.port = port
        self._use_tls = use_tls
        self._tls_config = tls_config

        if self._use_tls:
            if self._tls_config is None:
                raise InitializationError("TLS is enabled but no TlsConfig provided")

            # Check for the existence of the files before trying to read them.
            for path in [tls_config.ca_path, tls_config.client_crt_path, tls_config.client_key_path]:
                if not os.path.exists(path):
                    raise InitializationError(f"File {path} does not exist.")

            with open(tls_config.ca_path, "rb") as f:
                ca = f.read()
            with open(tls_config.client_crt_path, "rb") as f:
                client_crt = f.read()
            with open(tls_config.client_key_path, "rb") as f:
                client_key = f.read()
            credentials = grpc.ssl_channel_credentials(ca, client_key, client_crt)
            self.channel = grpc.secure_channel(f"{host}:{port}", credentials)
        else:
            self.channel = grpc.insecure_channel(f"{host}:{port}")
        self.stub = service_pb2_grpc.QueueServiceStub(self.channel)
        self._heartbeat_data = deque()
        self.lock = threading.Lock()
        self._stop_heartbeat = threading.Event()  # Signal to stop the heartbeat thread

    def _handle_error(self, error, handler=None):
        """Internal method to handle errors. Calls the custom error handler if set."""
        if handler:
            handler(error)
        else:
            # Default behavior is to raise the error
            raise error

    def create_queue(self, name: str, options: QueueOptions = None, error_handler=None) -> ResponseWrapper:
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
        ResponseWrapper
            A wrapper around the gRPC response from the Chronoqueue service, containing details
            about the CreateQueueResponse queue and facilitating type-safe access to response fields.

        Raises:
        ------
        RpcOperationError
            If the gRPC operation encounters an error and no custom error handler is provided.

        Example:
        --------
        >>> from chronoqueuesdk import QueueOptions
        >>> options = QueueOptions(type=QueueType.SIMPLE, exclusivity_key="key123", dequeue_attempts=3)
        >>> client.create_queue(name="my_new_queue", options=options)

        Notes:
        -----
        - `QueueOptions` allows you to customize behaviors like message invisibility duration,
        which defines how long a message will stay invisible (unavailable to workers) after
        being dequeued and before being requeued again if not acknowledged.
        - Ensure `name` adheres to any naming conventions or limitations imposed by the Chronoqueue service.
        """
        try:
            metadata = None
            if options is not None:
                metadata = queue_pb2.QueueMetadata(
                    type=options.type.value,
                    dequeue_attempts=options.dequeue_attempts,
                    lease_duration=string_to_duration(options.lease_duration),
                    exclusivity_key=options.exclusivity_key,
                    invisibility_duration=string_to_duration(options.invisibility_duration),
                )
            request = request_response_pb2.CreateQueueRequest(name=name, metadata=metadata)
            response = self.stub.CreateQueue(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error creating queue: {e.details()}")
            error = RpcOperationError(f"Failed to create queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def delete_queue(self, name: str, error_handler=None) -> ResponseWrapper:
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
        ResponseWrapper
            A wrapper around the gRPC response from the Chronoqueue service, containing details
            about the DeleteQueueResponse and facilitating type-safe access to response fields.

        Raises:
        ------
        RpcOperationError:
            If the gRPC operation encounters an error and no custom error handler is provided.

        Example:
        --------
        >>> client.delete_queue(name="my_queue_to_delete")

        """
        try:
            request = request_response_pb2.DeleteQueueRequest(name=name)
            response = self.stub.DeleteQueue(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error deleting queue: {e.details()}")
            error = RpcOperationError(f"Failed to delete queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def post_message(self, msg_params: PostMessageParams, error_handler=None) -> ResponseWrapper:
        """
        Post a message to a specified queue in the Chronoqueue service.

        Utilizing this method, messages, can be dispatched to a queue in Chronoqueue. The `msg_params` parameter allows you to
        specify the core attributes of a message, whereas any error during the message posting process can
        be managed through a custom or default error handling approach.

        Parameters:
        ----------
        msg_params : PostMessageParams
            Parameters defining the essentials of the message, inclusive of:
            - `message_id` (str): A unique identifier for the message.
            - `data` (dict): The message content, represented as a dictionary.
            - `queue_name` (str): The queue to which the message will be posted.

        error_handler : callable, optional
            A custom function to manage errors during the message posting process. This function should
            accept an error/exception object as a parameter. If omitted, the SDK’s default error handling
            is employed, by default None.

        Returns:
        -------
        ResponseWrapper
            A wrapper around the gRPC response from the Chronoqueue service, providing a type-safe means
            to access response details and containing insights about the dispatched message.

        Raises:
        ------
        RpcOperationError
            If the gRPC operation encounters an error and no custom error handler is defined.

        Example:
        --------
        >>> msg_params = PostMessageParams(message_id="12345", data={"key": "value"}, queue_name="my_queue")
        >>> def custom_error_handler(error):
        ...     print(f"Custom error handler: {error}")
        >>> client.post_message(msg_params, error_handler=custom_error_handler)

        """
        try:
            request = _create_post_message_request(params=msg_params)
            response = self.stub.PostMessage(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error posting message: {e.details()}")
            error = RpcOperationError(f"Failed to post message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def get_next_message(
        self,
        queue_name: str,
        lease_duration: str,
        exclusivity_key: str = "",
        enable_heartbeat=False,
        error_handler=None,
    ) -> ResponseWrapper:
        """
        Retrieve the next message from a specified queue in the Chronoqueue service.

        This method obtains the subsequent available message from a queue, making it
        inaccessible to other consumers for a stipulated period (defined by the lease duration).
        Optionally, the SDK can manage the message lease by automatically sending heartbeats
        to the service, based on the `enable_heartbeat` parameter. In the event of errors
        during message retrieval, custom or default error-handling mechanisms can be employed.

        Parameters:
        ----------
        queue_name : str
            The name of the queue from which to fetch the next message.

        lease_duration : str
            Duration (in seconds) to lease the message, during which it will be inaccessible to other consumers.

        exclusivity_key : str, optional
            An exclusive key required for queues of exclusive type, by default "".

        enable_heartbeat : bool, optional
            A flag to enable/disable the automatic sending of heartbeats for managing message leases, by default False.

        error_handler : callable, optional
            An optional custom function for error management during message retrieval. It should accept an error/exception
            object as its parameter. If not provided, the SDK’s default error handling will be employed, by default None.

        Returns:
        -------
        ResponseWrapper
            A wrapper of the response from the Chronoqueue service, providing insights and details about the retrieved message.

        Raises:
        ------
        RpcOperationError
            If the gRPC operation fails and no custom error handler is set.

        Example:
        --------
        >>> message = client.get_next_message(queue_name="my_queue", lease_duration="300").to_dict()  # To obtain a dictionary response
        >>> message = client.get_next_message(queue_name="my_queue", lease_duration="300").to_proto()  # To obtain a grpc response

        Notes:
        -----
        - Ensure `queue_name` corresponds to an existing and accessible queue in the Chronoqueue service.
        - The `lease_duration` should be set considering the processing time required for a message to avoid early lease expiration.
        - The `exclusivity_key` is pivotal when dealing with exclusive type queues and should be managed securely.
        - Utilizing `enable_heartbeat` can be beneficial for maintaining the lease of long-processing messages and mitigating premature visibility.
        """
        try:
            pb_release_duration: Duration = string_to_duration(lease_duration)

            request = request_response_pb2.GetNextMessageRequest(
                queue_name=queue_name, lease_duration=pb_release_duration, exclusivity_key=exclusivity_key
            )
            response = self.stub.GetNextMessage(request)
            response_wrapper = ResponseWrapper(response_protobuf=response)

            if len(response_wrapper.to_dict()) != 0 and enable_heartbeat:
                message_id = response_wrapper.to_dict().get("message_id")

                max_reconnect_attempts = response_wrapper.to_dict().get("max_reconnect_attempts", 3)
                heartbeat_frequency = response_wrapper.to_dict().get("heartbeat_frequency", 1)

                if heartbeat_frequency:
                    with self.lock:
                        self._heartbeat_data.append(
                            {
                                "queue_name": queue_name,
                                "message_id": message_id,
                                "max_reconnect_attempts": max_reconnect_attempts,
                                "heartbeat_frequency": heartbeat_frequency,
                            }
                        )
                    if not hasattr(self, "_heartbeat_manager_thread") or not self._heartbeat_manager_thread.is_alive():
                        self._heartbeat_manager_thread = threading.Thread(target=self.__manage_heartbeats)
                        self._heartbeat_manager_thread.start()

            return response_wrapper
        except grpc.RpcError as e:
            logging.error(f"Error getting next message: {e.details()}")
            error = RpcOperationError(f"Failed to get next message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def __manage_heartbeats(self):
        """
        Manage the heartbeats for leased messages in the Chronoqueue service.

        This private method manages the heartbeats for messages obtained from the Chronoqueue service.
        It ensures that the lease on a message is maintained by periodically sending heartbeat messages
        to the service, thereby extending the lease duration and preventing premature message visibility
        to other consumers.

        This method runs in a separate thread and continuously monitors the `heartbeat_data` deque for
        items to process. For each item, it sends a heartbeat message to the Chronoqueue service at
        regular intervals specified by the `heartbeat_frequency` parameter within the item.

        In the case of failures or errors during the heartbeat message sending (like network issues),
        the method employs an exponential back-off strategy with jitter to retry the heartbeat message
        sending, up to a specified number of attempts defined by `max_reconnect_attempts` in the item.

        Note:
        ----
        This method is intended to run in a dedicated thread and should not be called directly in normal
        SDK usage. It's pivotal in maintaining message leases during long-running message processing tasks
        and ensures coherent and reliable message consumption from the Chronoqueue service.

        Warning:
        -------
        Mismanagement or premature termination of the heartbeat manager thread can lead to issues
        with message lease maintenance and might result in a message becoming visible to other consumers
        before it's fully processed. Ensure to manage SDK termination and error handling adequately to
        prevent such scenarios.
        """
        while self._heartbeat_data and not self._stop_heartbeat.is_set():
            item = self._heartbeat_data.popleft()
            reconnect_attempts = 0
            if not isinstance(item, dict):
                logging.error(f"Unexpected item in heartbeat_data: {item}")
                continue  # Skip this iteration and move to the next item
            while reconnect_attempts < item.get("max_reconnect_attempts", 3):
                try:
                    heartbeat_request = request_response_pb2.SendMessageHeartBeatRequest(
                        queue_name=item.get("queue_name"), message_id=item.get("message_id")
                    )
                    heartbeat_resp = self.stub.SendMessageHeartBeat(heartbeat_request)
                    if heartbeat_resp.state != Message.Metadata.State.RUNNING:
                        break
                    time.sleep(item.get("heartbeat_frequency", 1))
                    reconnect_attempts = 0  # reset the counter if sending was successful
                except grpc.RpcError as e:
                    # Handle errors with exponential back-off
                    reconnect_attempts += 1
                    backoff_time = (2**reconnect_attempts) + randint(1, 10)  # exponential back-off with jitter
                    time.sleep(backoff_time)

    def acknowledge_message(self, params: AcknowledgeMessageParams, error_handler=None) -> ResponseWrapper:
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
        ResponseWrapper
            A wrapper of the response from the Chronoqueue service, providing insights and details about the acknowledged message.

        Raises:
        ------
        RpcOperationError
            If the gRPC operation fails and no custom error handler is set.

        Example:
        --------
        >>> from chronoqueuesdk.utils import AcknowledgeMessageParams
        >>> params = AcknowledgeMessageParams(message_id="12345", queue_name="my_queue", state=MessageState.COMPLETED)
        >>> client.acknowledge_message(params)

        """
        try:
            # Send the acknowledgment to Chronoqueue
            ack_request = request_response_pb2.AcknowledgeMessageRequest(
                message_id=params.message_id, queue_name=params.queue_name, state=params.state
            )
            response = self.stub.AcknowledgeMessage(ack_request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error acknowledging message: {e.details()}")
            error = RpcOperationError(f"Failed to acknowlege message due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def renew_message_lease(self, message_id: str, new_lease_duration: str, error_handler=None) -> ResponseWrapper:
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

        new_lease_duration : str
            The desired new lease duration for the message, represented as a string with a time unit
            suffix ("s" for seconds, "m" for minutes, "h" for hours, and "d" for days).
            E.g., "5s" for 5 seconds or "2m" for 2 minutes.

        error_handler : callable, optional
            A custom error handling function that will be invoked if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be utilized.

        Returns:
        -------
        response : ResponseWrapper
            A wrapper containing the RenewMessageLeaseResponse from the Chronoqueue service, offering
            details about the status and any relevant information about the lease renewal process.
            The ResponseWrapper allows response data to be accessed in different formats (e.g., dict or proto).

        Raises:
        ------
        RpcOperationError:
            If an error occurs during the gRPC operation and no custom error handler is provided.

        Example:
        --------
        # Renew the lease duration of a message for an additional 300 seconds (5 minutes)
        >>> client.renew_message_lease(message_id="12345", new_lease_duration="5m")

        Note:
        ----
        Ensuring the accurate renewal of message leases is critical for maintaining coherent processing
        workflows, especially in distributed systems where multiple consumers might be interacting with
        the same queue. Always ensure to handle errors and edge cases effectively to prevent message
        processing conflicts and ensure the reliable operation of your application.

        """
        try:
            pb_release_duration: Duration = string_to_duration(new_lease_duration)

            request = request_response_pb2.RenewMessageLeaseRequest(
                message_id=message_id, lease_duration=pb_release_duration
            )
            response = self.stub.RenewMessageLease(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error renewing message lease: {e.details()}")
            error = RpcOperationError(f"Failed to renew message lease due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def peek_queue_messages(self, params: PeekQueueMessagesParams, error_handler=None) -> ResponseWrapper:
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

        Returns:
        -------
        response : ResponseWrapper
            A wrapper containing the PeekQueueMessagesResponse from the Chronoqueue service, offering
            details about the the peeked messages and related details.
            The ResponseWrapper allows response data to be accessed in different formats (e.g., dict or proto).

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
            request = request_response_pb2.PeekQueueMessagesRequest(
                queue_name=params.queue_name, limit=params.limit, priority_range=params.priority_range
            )
            response = self.stub.PeekQueueMessages(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error peeking queue messages: {e.details()}")
            error = RpcOperationError(f"Failed to peek queue due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def get_queue_state(self, queue_name, error_handler=None) -> ResponseWrapper:
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
        response : ResponseWrapper
            A wrapper containing the GetQueueStateResponse from the Chronoqueue service, offering
            details about about the state of the specified queue.
            The ResponseWrapper allows response data to be accessed in different formats (e.g., dict or proto).

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> client.get_queue_state("my_queue")

        """
        try:
            request = request_response_pb2.GetQueueStateRequest(queue_name=queue_name)
            response = self.stub.GetQueueState(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error getting queue state: {e.details()}")
            error = RpcOperationError(f"Failed to get queue state due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def send_message_heartbeat(self, queue_name, message_id, error_handler=None) -> ResponseWrapper:
        """
        Manually sends a heartbeat for a specified message to the Chronoqueue service.

        Sending a heartbeat for a message signals to the Chronoqueue service that the message is still
        being processed and its lease should be maintained. This method allows you to manually send
        heartbeats for a message, which might be necessary in long-running tasks to prevent the message
        from becoming visible and being redelivered to another consumer.

        Note: The SDK provides a built-in heartbeat mechanism that can automatically send heartbeats
        for fetched messages. Consider using this built-in feature when fetching messages to simplify
        message lease management and avoid manually managing heartbeats.

        Parameters:
        ----------
        queue_name : str
            The name of the queue from which the message was fetched.

        message_id : str
            The unique identifier of the message for which the heartbeat is being sent.

        error_handler : callable, optional
            A custom error handling function that will be called if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be used.

        Returns:
        -------
        response : ResponseWrapper
            The wrapper containing SendMessageHeartBeatResponse from the Chronoqueue service,
            providing details about the status of the heartbeat operation.

        Raises:
        ------
        RpcOperationError:
            If there's an error performing the gRPC operation and no custom error handler is provided.

        Example:
        --------
        >>> client.send_message_heartbeat(queue_name="my_queue", message_id="12345")

        """
        try:
            request = request_response_pb2.SendMessageHeartBeatRequest(queue_name=queue_name, message_id=message_id)
            response = self.stub.SendMessageHeartBeat(request)
            return ResponseWrapper(response_protobuf=response)
        except grpc.RpcError as e:
            logging.error(f"Error sending heartbeat for message {message_id}: {e.details()}")
            error = RpcOperationError(f"Failed to send heartbeat due to: {e.details()}")
            self._handle_error(error, handler=error_handler)

    def close(self, error_handler=None) -> None:
        """
        Gracefully closes the gRPC channel and stops the heartbeat manager.

        Closes the gRPC channel used by the SDK to communicate with the Chronoqueue service, ensuring
        that resources are released and open connections to the service are terminated. If the SDK
        is configured to manage message heartbeats, it also stops the heartbeat manager thread. It is
        recommended to invoke this method when the SDK is no longer needed, such as when your
        application is terminating, to cleanly shut down the SDK components. If an error occurs during
        the closing process, it can be handled using a custom error handler or the SDK's default mechanism.

        Parameters:
        ----------
        error_handler : callable, optional
            A custom error handling function that will be invoked if an error occurs during the operation.
            The function should accept a single argument, which is the error/exception object.
            If not provided, the SDK's default error handling mechanism will be utilized.

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
            if (
                self.channel
                and self.channel._channel.check_connectivity_state(True) != grpc.ChannelConnectivity.SHUTDOWN
            ):
                # Signal the heartbeat thread to stop
                self._stop_heartbeat.set()
                # Wait for the heartbeat thread to finish
                self._heartbeat_manager_thread.join()
                return self.channel.close()
        except grpc.RpcError as e:
            logging.error(f"Error closing rpc channel: {e.details()}")
            error = RpcOperationError(f"Failed to close RPC channel due to: {e.details()}")
            self._handle_error(error, handler=error_handler)
