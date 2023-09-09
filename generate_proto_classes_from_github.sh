#!/bin/bash

# # URL to the raw .proto file on GitHub
# PROTO_URL="https://raw.githubusercontent.com/adrien19/chronoqueue/develop/api/chronoqueue/v1/service.proto"
# # OUTPUT_PATH="./client"
PROTO_PATH="./proto"

# # Provide your Personal Access Token (PAT) for GitHub
# # WARNING: Keep your PAT confidential. Do not hard-code it in scripts or expose it.
# echo "Enter your GitHub Personal Access Token:"
# read -s TOKEN

# # Fetch the .proto file using curl
# curl -H "Authorization: token $TOKEN" -o $PROTO_PATH/chronoqueue.proto $PROTO_URL

# Use the protoc compiler to generate the Python classes
protoc -I=$PROTO_PATH --python_out=$PROTO_PATH $PROTO_PATH/chronoqueue.proto
# protoc -I=$PROTO_PATH --grpc_python_out=$PROTO_PATH --plugin=protoc-gen-grpc_python=$(which grpc_python_plugin) $PROTO_PATH/chronoqueue.proto
# protoc -I=$PROTO_PATH --grpc_python_out=$PROTO_PATH --plugin=protoc-gen-grpc_python=./.venv/bin/protoc-gen-grpclib_python $PROTO_PATH/chronoqueue.proto
protoc -I=$PROTO_PATH --grpc_python_out=$PROTO_PATH --plugin=protoc-gen-grpc_python=./.venv/bin/protoc-gen-python_grpc $PROTO_PATH/chronoqueue.proto

echo "Python classes generated successfully!"




