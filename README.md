# Chronoqueue Python SDK

The official Python SDK for the Chronoqueue service. Seamlessly integrate and manage Chronoqueue functionalities in Python applications. Provides an intuitive interface for interacting with the Chronoqueue service using gRPC, with optional SSL/TLS support. Designed for both development and production environments.

## Key Features:

* Easy Integration: Intuitive classes and methods that align with Chronoqueue's core features.
* gRPC Support: Efficiently communicate with the Chronoqueue service using gRPC.
Optional SSL/TLS: Toggle SSL/TLS support based on your environment and security needs.
* Comprehensive Documentation: Includes a user guide, API reference, tutorials, and more to ensure smooth implementation.
* Unit Tests: Equipped with pytest based unit tests to ensure reliability and ease of development.

## Table of Contents

- [Installation](#installation)
- [Getting Started](#getting-started)
- [Usage](#usage)
  - [Creating a Client](#creating-a-client)
  - [Interacting with Queues](#interacting-with-queues)
- [Example](#example)
- [License](#license)

## Installation

To install the Chronoqueue Python SDK, you can use pip:

```bash
pip install chronoqueue-sdk
```

Ensure you also hvr `grcpcio`installed:
```bash
pip install grpcio
```

## Getting Started

Before you can interact with the Chronoqueue service, you must generate the necessary gRPC classes. Run the provided shell script to generate these:

```bash
./generate_proto_classes_from_github.sh
```

This script fetches the necessary .proto files and generates Python gRPC classes for you.

## Usage 

### Creating a Client
To create a client to interact with the Chronoqueue service:

```python
from chronoqueue import ChronoqueueClient

client = ChronoqueueClient(host='localhost', port=50051, use_tls=False)
```

If SSL/TLS is required, the `use_tls` must be set to `TRUE` and path to certificate file must be provided.

```python
from chronoqueue import ChronoqueueClient

client = ChronoqueueClient(host='localhost', port=50051, use_tls=True, cert_path='path/to/your/certificate.pem')
```

### Interacting with Queues
With the client, you can interact with the Chronoqueue service:

* Creating a Queue:
    ```python
    response = client.create_queue("my_queue")
    ```

* Delete a Queue:
    ```python
    response = client.delete_queue("my_queue")
    ```

* Post a Message:
    ```python
    response = client.post_message(queue_name="my_queue", content="Hello, Chronoqueue!")
    ```

## Example 
Here's a simple example demonstrating how to use the SDK in another Python project:

```python
from chronoqueue import ChronoqueueClient

# Create a client instance
client = ChronoqueueClient(host='localhost', port=50051, cert_path='path/to/your/certificate.pem')

# Create a new queue
response = client.create_queue("test_queue")
print(f"Queue created with response: {response}")

# Post a message to the queue
message_response = client.post_message(queue_name="test_queue", content="Hello, Chronoqueue!")
print(f"Message posted with response: {message_response}")

# Clean up by deleting the queue
delete_response = client.delete_queue("test_queue")
print(f"Queue deleted with response: {delete_response}")

```

## License
tbd