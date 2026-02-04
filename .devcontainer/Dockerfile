# Base image: Python 3.14.2 on Debian Bookworm
FROM python:3.14.2-bookworm

# Avoid warnings by switching to noninteractive
ENV DEBIAN_FRONTEND=noninteractive

ARG USERNAME=vscode
ARG USER_UID=1000
ARG USER_GID=$USER_UID
ARG WITR_VERSION=0.2.6
ARG WITR_SHA256=0f8d6ed4419747bd30e2e5b0412e6d497e8cc9fd990d291b787f775d57625cbd
ARG DOCKER_GID=1001

# Update and install prerequisites
RUN apt-get update && apt-get install -y \
    apt-transport-https \
    ca-certificates \
    curl \
    gnupg \
    gnupg-agent \
    software-properties-common \
    sudo \
    && apt-get -y install --no-install-recommends apt-utils dialog 2>&1 \
    # Verify git, process tools, lsb-release (common in install instructions for CLIs) installed
    && apt-get -y install git openssh-client less iproute2 procps lsb-release \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/* \
    #
    # Add Docker's official GPG key and repository
    && mkdir -p /etc/apt/keyrings \
    && curl -fsSL https://download.docker.com/linux/debian/gpg | gpg --dearmor -o /etc/apt/keyrings/docker.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/etc/apt/keyrings/docker.gpg] https://download.docker.com/linux/debian $(lsb_release -cs) stable" \
    | tee /etc/apt/sources.list.d/docker.list > /dev/null \
    # Install Docker CI
    && apt-get update && apt-get install -y docker-ce-cli && apt-get clean && rm -rf /var/lib/apt/lists/* \
    #
    # Install pylint
    && pip --disable-pip-version-check --no-cache-dir install pylint \
    #
    # Update Python environment based on requirements.txt
    # && pip --disable-pip-version-check --no-cache-dir install -r /tmp/pip-tmp/requirements.txt \
    # && rm -rf /tmp/pip-tmp \
    #
    # Install witr (Why is This Running tool) with SHA256 verification
    && curl -fsSL "https://github.com/pranshuparmar/witr/releases/download/v${WITR_VERSION}/witr-linux-amd64" -o /usr/local/bin/witr \
    && echo "${WITR_SHA256}  /usr/local/bin/witr" | sha256sum -c - \
    && chmod +x /usr/local/bin/witr \
    #
    # Create a non-root user `vscode` and add to `docker` group
    && groupadd --gid $USER_GID $USERNAME \
    && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME \
    && echo $USERNAME ALL=\(root\) NOPASSWD:ALL > /etc/sudoers.d/$USERNAME \
    && chmod 0440 /etc/sudoers.d/$USERNAME \
    #
    # Add `docker` group with configurable GID, then add `vscode` to it
    && if getent group docker; then \
         groupmod -g $DOCKER_GID docker 2>/dev/null || true; \
       else \
         groupadd -g $DOCKER_GID docker; \
       fi \
    && usermod -aG docker $USERNAME

# Switch back to dialog for any ad-hoc use of apt-get
ENV DEBIAN_FRONTEND=dialog

