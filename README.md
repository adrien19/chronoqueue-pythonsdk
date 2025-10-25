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

2. Generate the necessary gRPC classes from proto files:

    ```bash
    make gen-proto
    ```

### Available Make Targets

The project includes a comprehensive Makefile for common development tasks:

- `make install` - Install production dependencies only
- `make install-dev` - Install all dependencies including dev tools
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
  - Tests across Python 3.10, 3.11, and 3.12
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

### Interacting with Queues
With the client, you can interact with the Chronoqueue service:

* Creating a Queue:
    ```python
    response = client.create_queue(name="my_queue")
    ```

* Delete a Queue:
    ```python
    response = client.delete_queue(name="my_queue")
    ```

* Post a Message:
    ```python
    from chronoqueue.utils import PostMessageParams
    msg_params = PostMessageParams(message_id="12345", data={"key": "value"}, queue_name="my_queue")
    response = client.post_message(msg_params)
    ```

## Example 
Here's a simple example demonstrating how to use the SDK in another Python project:

```python
from chronoqueue import ChronoqueueClient

# Create a client instance
client = ChronoqueueClient(host='localhost', port=50051, use_tls=True, cert_path='path/to/your/certificate.pem')

# Create a new queue
response = client.create_queue(name="test_queue")
print(f"Queue created with response: {response}")

# Post a message to the queue
msg_params = PostMessageParams(message_id="12345", data={"greetings": "Hello, Chronoqueue!"}, queue_name="test_queue")
message_response = client.post_message(msg_params)
print(f"Message posted with response: {message_response}")

# Clean up by deleting the queue
delete_response = client.delete_queue(name="test_queue")
print(f"Queue deleted with response: {delete_response}")

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
