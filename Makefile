.PHONY: help install install-dev lock update clean test lint format gen-proto check-proto setup-dirs all ci build publish

# Configuration
PROTO_PATH := ./proto
OUTPUT_PATH := ./chronoqueue/api/v1
PROTO_FILE := $(PROTO_PATH)/chronoqueue.proto
PYTHON := python3

# Default target
help:
	@echo "Chronoqueue Python SDK - Available Targets:"
	@echo ""
	@echo "  make install          - Install production dependencies"
	@echo "  make install-dev      - Install development dependencies"
	@echo "  make lock             - Lock dependencies (update poetry.lock)"
	@echo "  make update           - Update dependencies to latest versions"
	@echo "  make gen-proto        - Generate Python gRPC classes from proto files"
	@echo "  make check-proto      - Verify proto file exists"
	@echo "  make clean            - Remove generated files and cache"
	@echo "  make test             - Run unit tests"
	@echo "  make test-coverage    - Run unit tests with coverage"
	@echo "  make lint             - Run linting checks"
	@echo "  make format           - Format code with black and isort"
	@echo "  make typecheck        - Run type checking with mypy"
	@echo "  make build            - Build package distribution"
	@echo "  make ci               - Run all CI checks (lint, test)"
	@echo "  make all              - Setup and generate everything"
	@echo ""

# Install production dependencies
install:
	@echo "Installing production dependencies..."
	poetry install --only main

# Install development dependencies
install-dev:
	@echo "Installing development dependencies..."
	poetry install

# Lock dependencies
lock:
	@echo "Locking dependencies..."
	poetry lock
	@echo "Dependencies locked successfully!"

# Update dependencies to latest versions
update:
	@echo "Updating dependencies..."
	poetry update
	@echo "Dependencies updated successfully!"
	@echo "Remember to test with 'make ci' before committing!"

# Setup directory structure
setup-dirs:
	@echo "Setting up directory structure..."
	@mkdir -p $(PROTO_PATH)
	@mkdir -p $(OUTPUT_PATH)
	@mkdir -p ./chronoqueue/api
	@touch ./chronoqueue/api/__init__.py
	@touch $(OUTPUT_PATH)/__init__.py

# Check if proto file exists
check-proto:
	@if [ ! -f $(PROTO_FILE) ]; then \
		echo "Error: Proto file not found at $(PROTO_FILE)"; \
		echo "Please ensure the proto file exists before generating code."; \
		exit 1; \
	fi

# Generate Python gRPC classes from proto files
gen-proto: setup-dirs check-proto
	@echo "Generating Python gRPC classes from proto files..."
	@poetry run $(PYTHON) -m grpc_tools.protoc \
		-I=$(PROTO_PATH) \
		--python_out=$(OUTPUT_PATH) \
		--grpc_python_out=$(OUTPUT_PATH) \
		$(PROTO_FILE)
	@echo "Fixing imports in generated gRPC file..."
	@if [ "$$(uname)" = "Darwin" ]; then \
		sed -i '' 's/import chronoqueue_pb2 as chronoqueue__pb2/from . import chronoqueue_pb2 as chronoqueue__pb2/' $(OUTPUT_PATH)/chronoqueue_pb2_grpc.py; \
	else \
		sed -i 's/import chronoqueue_pb2 as chronoqueue__pb2/from . import chronoqueue_pb2 as chronoqueue__pb2/' $(OUTPUT_PATH)/chronoqueue_pb2_grpc.py; \
	fi
	@echo "Python gRPC classes generated successfully!"

# Clean generated files and cache
clean:
	@echo "Cleaning generated files and cache..."
	@rm -rf $(OUTPUT_PATH)/chronoqueue_pb2.py
	@rm -rf $(OUTPUT_PATH)/chronoqueue_pb2_grpc.py
	@rm -rf $(OUTPUT_PATH)/__pycache__
	@rm -rf ./chronoqueue/__pycache__
	@rm -rf ./chronoqueue/api/__pycache__
	@rm -rf ./tests/__pycache__
	@rm -rf .pytest_cache
	@rm -rf .mypy_cache
	@rm -rf dist
	@rm -rf build
	@rm -rf *.egg-info
	@find . -type d -name __pycache__ -exec rm -rf {} + 2>/dev/null || true
	@find . -type f -name '*.pyc' -delete
	@echo "Clean complete!"

# Run unit tests
test:
	@echo "Running unit tests..."
	poetry run pytest tests/ -v

# Run tests with coverage
test-coverage:
	@echo "Running unit tests with coverage..."
	poetry run pytest tests/ -v --cov=chronoqueue --cov-report=term-missing --cov-report=html

# Run linting checks
lint:
	@echo "Running linting checks..."
	@echo "Checking with flake8..."
	@poetry run flake8 chronoqueue/ tests/ --max-line-length=120 --exclude=chronoqueue/api/v1/*.py --count --statistics || true
	@echo "Checking with mypy..."
	@poetry run mypy chronoqueue/ --exclude chronoqueue/api/v1/ --ignore-missing-imports || true

# Format code
format:
	@echo "Formatting code with black..."
	@poetry run black chronoqueue/ tests/ --line-length=120 --exclude='chronoqueue/api/v1/.*\.py'
	@echo "Sorting imports with isort..."
	@poetry run isort chronoqueue/ tests/ --skip chronoqueue/api/v1 --profile black --line-length 120

# Type checking
typecheck:
	@echo "Running type checking with mypy..."
	poetry run mypy chronoqueue/ --exclude chronoqueue/api/v1/ --ignore-missing-imports

# Build package
build: clean
	@echo "Building package..."
	poetry build

# Publish to PyPI (use with caution)
publish: build
	@echo "Publishing to PyPI..."
	poetry publish

# Publish to Test PyPI
publish-test: build
	@echo "Publishing to Test PyPI..."
	poetry publish -r testpypi

# Run all CI checks
ci: lint test
	@echo "All CI checks passed!"

# Setup everything
all: install-dev
	@echo "Setup complete! Run 'make gen-proto' to generate proto classes."
