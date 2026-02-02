# Chronoqueue Python SDK

[![CI](https://github.com/adrien19/chronoqueue-pythonsdk/workflows/CI/badge.svg)](https://github.com/adrien19/chronoqueue-pythonsdk/actions/workflows/ci.yml)
[![PyPI version](https://badge.fury.io/py/chronoqueue.svg)](https://badge.fury.io/py/chronoqueue)
[![Python Versions](https://img.shields.io/pypi/pyversions/chronoqueue.svg)](https://pypi.org/project/chronoqueue/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

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

### Optional: Install with Pydantic Support

For better type safety and IDE autocomplete, install with Pydantic:

```bash
pip install chronoqueue-sdk[pydantic]
# or
pip install chronoqueue-sdk pydantic
```

Ensure you also hvr `grcpcio`installed:
```bash
pip install grpcio
```

## Setup

### For Development

1. Install Poetry for dependency management:

    ```bash 
    poetry install
    ```
   
   Or use the Makefile:
   
    ```bash
    make install-dev
    ```

2. Update proto definitions from the chronoqueue repository:

    ```bash
    # Download latest proto definitions
    make update-proto
    ```

3. Generate the necessary gRPC classes from proto files:

    ```bash
    make gen-proto
    ```

### Available Make Targets

The project includes a comprehensive Makefile for common development tasks:

- `make install` - Install production dependencies only
- `make install-dev` - Install all dependencies including dev tools
- `make update-proto` - Download latest proto definitions from chronoqueue repo
- `make gen-proto` - Generate Python gRPC classes from proto files
- `make clean` - Remove generated files and cache
- `make test` - Run unit tests
- `make test-coverage` - Run tests with coverage reporting
- `make lint` - Run linting checks (flake8, mypy)
- `make format` - Format code with black and isort
- `make typecheck` - Run type checking with mypy
- `make build` - Build package distribution
- `make ci` - Run all CI checks (lint + test)
- `make all` - Complete setup (install-dev)

### CI/CD

The project uses GitHub Actions for continuous integration and deployment:

- **CI Pipeline** (`.github/workflows/ci.yml`):
  - Runs on push to main, develop branches and pull requests
  - Tests across Python 3.10, 3.11, 3.12, and 3.14
  - Performs linting, type checking, and testing
  - Generates coverage reports
  - Builds the package

- **Release Pipeline** (`.github/workflows/release.yml`):
  - Triggers on new GitHub releases
  - Builds and publishes to PyPI
  - Supports manual dispatch to TestPyPI

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

### Working with Responses

The SDK provides two ways to work with responses:

#### Option 1: Dictionary Output (Legacy, Always Available)

```python
response = client.get_next_message("my_queue", "5m")
data = response.to_dict()  # Returns Dict[str, Any]
msg_id = data.get("message", {}).get("messageId")  # No type hints
```

#### Option 2: Typed Pydantic Models (Recommended, Requires Pydantic)

```python
response = client.get_next_message("my_queue", "5m")
msg = response.to_model()  # Returns GetNextMessageResponse (fully typed!)

# Full IDE autocomplete and type checking
print(msg.message.message_id)  # Type: str
print(msg.message.metadata.state)  # Type: str
print(msg.message.metadata.payload.data)  # Type: Dict[str, Any]

# Easy serialization
json_str = msg.model_dump_json()  # Convert to JSON string
dict_data = msg.model_dump()  # Convert to dict with validation
```

**Benefits of Pydantic models:**
- ✅ Full IDE autocomplete
- ✅ Type checking with mypy/pylance
- ✅ Data validation
- ✅ Easy JSON serialization
- ✅ Better developer experience

### Interacting with Queues
With the client, you can interact with the Chronoqueue service:

* Creating a Queue:
    ```python
    response = client.create_queue(name="my_queue")
    
    # Legacy dict approach
    success = response.to_dict().get("success")
    
    # Typed model approach (requires pydantic)
    result = response.to_model()
    success = result.success  # IDE knows this is bool
    ```

* Delete a Queue:
    ```python
    response = client.delete_queue(name="my_queue")
    
    # With Pydantic
    result = response.to_model()
    if result.success:
        print("Queue deleted successfully")
    ```

* Post a Message:
    ```python
    from chronoqueue.utils import PostMessageParams
    msg_params = PostMessageParams(message_id="12345", data={"key": "value"}, queue_name="my_queue")
    response = client.post_message(msg_params)
    
    # With Pydantic
    result = response.to_model()
    print(f"Message posted: {result.success}")
    ```

* Get Next Message:
    ```python
    response = client.get_next_message("my_queue", lease_duration="5m")
    
    # With Pydantic - full type safety
    result = response.to_model()
    if result.message:
        print(f"Message ID: {result.message.message_id}")
        print(f"State: {result.message.metadata.state}")
        print(f"Data: {result.message.metadata.payload.data}")
    else:
        print("Queue is empty")
    ```

* Peek Queue Messages:
    ```python
    from chronoqueue.utils import PeekQueueMessagesParams
    params = PeekQueueMessagesParams(queue_name="my_queue", limit=10)
    response = client.peek_queue_messages(params)
    
    # With Pydantic
    result = response.to_model()
    for msg in result.messages:
        print(f"Message {msg.message_id}: {msg.metadata.payload.data}")
    ```

* Get Queue State:
    ```python
    response = client.get_queue_state("my_queue")
    
    # With Pydantic
    state = response.to_model()
    print(f"Pending: {state.state_counts.get('PENDING', 0)}")
    print(f"Running: {state.state_counts.get('RUNNING', 0)}")
    print(f"Completed: {state.state_counts.get('COMPLETED', 0)}")
    ```

## Example 
Here's a comprehensive example demonstrating how to use the SDK:

```python
from chronoqueue import ChronoqueueClient
from chronoqueue.utils import PostMessageParams, PostMessageOptions, MessageState

# Create a client instance
client = ChronoqueueClient(host='localhost', port=50051, use_tls=False)

# Create a new queue
response = client.create_queue(name="test_queue")
print(f"Queue created: {response.to_model().success}")

# Post a message to the queue
msg_params = PostMessageParams(
    message_id="12345",
    data={"task": "process_data", "priority": "high"},
    queue_name="test_queue",
    options=PostMessageOptions(priority=10)
)
response = client.post_message(msg_params)
print(f"Message posted: {response.to_model().success}")

# Get next message (with type safety using Pydantic)
response = client.get_next_message("test_queue", lease_duration="5m")
msg = response.to_model()

if msg.message:
    print(f"Processing message: {msg.message.message_id}")
    print(f"Data: {msg.message.metadata.payload.data}")
    
    # Acknowledge the message
    from chronoqueue.utils import AcknowledgeMessageParams
    ack_params = AcknowledgeMessageParams(
        message_id=msg.message.message_id,
        queue_name="test_queue",
        state=MessageState.COMPLETED
    )
    ack_response = client.acknowledge_message(ack_params)
    print(f"Message acknowledged: {ack_response.to_model().success}")
else:
    print("No messages in queue")

# Check queue state
state_response = client.get_queue_state("test_queue")
state = state_response.to_model()
print(f"Queue state: {state.state_counts}")

# Clean up by deleting the queue
delete_response = client.delete_queue(name="test_queue")
print(f"Queue deleted: {delete_response.to_model().success}")

# Close the client
client.close()
```

### Legacy Dictionary Example (Without Pydantic)

If you prefer to work with dictionaries instead of typed models:

```python
from chronoqueue import ChronoqueueClient
from chronoqueue.utils import PostMessageParams

client = ChronoqueueClient(host='localhost', port=50051, use_tls=False)

# Create queue - using .to_dict()
response = client.create_queue(name="test_queue")
data = response.to_dict()
print(f"Queue created: {data.get('success')}")

# Post message
msg_params = PostMessageParams(message_id="123", data={"key": "value"}, queue_name="test_queue")
response = client.post_message(msg_params)
print(f"Message posted: {response.to_dict().get('success')}")

# Get message - using .to_dict()
response = client.get_next_message("test_queue", "5m")
msg_dict = response.to_dict()
if msg_dict.get("message"):
    message_id = msg_dict["message"]["messageId"]
    print(f"Got message: {message_id}")

client.close()
```

## Pytest
The tests are written in /tests. To trigget then, use use below command: 
```bash 
poetry run pytest
```

## Documentation

Further documentation can be found in the docs/ directory, including:

* User Guide: Step-by-step instructions on setting up and using the SDK.
* API Reference: Detailed information on each method and its parameters.
* Tutorials: In-depth guides and use-cases to help you make the most of Chronoqueue.

## License

MIT
