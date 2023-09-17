#!/bin/bash

# # URL to the raw .proto file on GitHub
# PROTO_URL="https://raw.githubusercontent.com/adrien19/chronoqueue/develop/api/chronoqueue/v1/service.proto"
PROTO_PATH="./proto"
OUTPUT_PATH="./chronoqueue/api/v1"  # This path should reflect the package structure

# Create the directories if they don't exist
mkdir -p $PROTO_PATH
mkdir -p $OUTPUT_PATH
touch ./chronoqueue/api/__init__.py
touch $OUTPUT_PATH/__init__.py

# # Provide your Personal Access Token (PAT) for GitHub
# # WARNING: Keep your PAT confidential. Do not hard-code it in scripts or expose it.
# echo "Enter your GitHub Personal Access Token:"
# read -s TOKEN

# # Fetch the .proto file using curl
# curl -H "Authorization: token $TOKEN" -o $PROTO_PATH/chronoqueue.proto $PROTO_URL

# Use the grpc_tools.protoc command to generate Python classes and gRPC stubs
python -m grpc_tools.protoc -I=$PROTO_PATH \
                 --python_out=$OUTPUT_PATH \
                 --grpc_python_out=$OUTPUT_PATH \
                 $PROTO_PATH/chronoqueue.proto
                #  --mypy_out=$OUTPUT_PATH \

# Replace the import inside the grpc file
# Determine the platform
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    sed -i '' 's/import chronoqueue_pb2 as chronoqueue__pb2/from . import chronoqueue_pb2 as chronoqueue__pb2/' $OUTPUT_PATH/chronoqueue_pb2_grpc.py
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux
    sed -i 's/import chronoqueue_pb2 as chronoqueue__pb2/from . import chronoqueue_pb2 as chronoqueue__pb2/' $OUTPUT_PATH/chronoqueue_pb2_grpc.py
else
    echo "Platform not supported or unknown: $OSTYPE"
    exit 1
fi

echo "Python classes generated successfully!"




