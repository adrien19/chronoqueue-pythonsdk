#!/bin/bash -e

echo "Setting up environment..."

# Add .local/bin to PATH for the vscode user
export PATH="$PATH:/home/vscode/.local/bin"

# Persist this PATH change for future sessions
echo "export PATH=\$PATH:/home/vscode/.local/bin" >> /home/vscode/.bashrc


# Test Docker access
if ! docker ps > /dev/null 2>&1; then
  echo "Docker is not accessible. Please check the Docker socket or user permissions."
  exit 1
fi

# Check if Docker socket is accessible
if [ ! -S /var/run/docker.sock ]; then
    echo "ERROR: Docker socket (/var/run/docker.sock) not found. Check if Docker is running and socket is mounted."
    exit 1
fi

# Check permissions on the socket
if ! [ -w /var/run/docker.sock ]; then
    echo "ERROR: Docker socket (/var/run/docker.sock) is not writable. Adjust permissions on the host."
    ls -l /var/run/docker.sock
    exit 1
fi

# Test Docker access
if ! docker ps > /dev/null 2>&1; then
    echo "ERROR: Docker is not accessible by the current user. Check group membership."
    id
    groups
    exit 1
fi

########### DOCKER COMPOSE SETUP ###########
# Ensure docker-compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo "Installing docker-compose..."
    sudo curl -L "https://github.com/docker/compose/releases/download/v2.20.2/docker-compose-$(uname -s)-$(uname -m)" -o /usr/local/bin/docker-compose
    sudo chmod +x /usr/local/bin/docker-compose
fi

########### Start docker-compose services ###########
echo "Starting docker-compose services..."
docker-compose -f .devcontainer/docker-compose.yaml up -d

# Verify services
if ! docker ps | grep -q dev_redis; then
    echo "Redis container failed to start. Check logs for more details."
    docker logs dev_redis
    exit 1
fi

echo "PostgreSQL and Redis are up and running."

# Upgrade pip and setuptools
pip install --upgrade pip setuptools

# Install required packages
pip install -r .devcontainer/requirements.txt

echo "Post-create commands completed successfully."
