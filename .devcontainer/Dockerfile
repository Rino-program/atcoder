 # Devcontainer Dockerfile for C++23 with GCC 15.x
 # Base image: Ubuntu LTS
 FROM ubuntu:24.04

 ENV DEBIAN_FRONTEND=noninteractive

 # Install prerequisites and GCC-15 toolchain from the ubuntu-toolchain-r PPA
 RUN apt-get update \
     && apt-get install -y --no-install-recommends software-properties-common ca-certificates wget gnupg lsb-release build-essential \
     && add-apt-repository ppa:ubuntu-toolchain-r/test -y \
     && apt-get update \
     && apt-get install -y --no-install-recommends \
         gcc-15 g++-15 gdb cmake ninja-build git pkg-config ca-certificates \
         libstdc++-15-dev libboost-all-dev libgmp-dev zlib1g-dev libbz2-dev liblzma-dev libssl-dev \
     && update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-15 100 \
     && update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-15 100 \
     && apt-get clean \
     && rm -rf /var/lib/apt/lists/*

 # Create a non-root user vscode to match VS Code defaults
 ARG USERNAME=vscode
 ARG USER_UID=1000
 ARG USER_GID=$USER_UID
 RUN groupadd --gid $USER_GID $USERNAME || true \
     && useradd -s /bin/bash --uid $USER_UID --gid $USER_GID -m $USERNAME || true \
     && apt-get update && apt-get install -y sudo
 RUN echo "$USERNAME ALL=(ALL) NOPASSWD:ALL" > /etc/sudoers.d/$USERNAME

 # Set locale to avoid related warnings
 RUN apt-get update && apt-get install -y --no-install-recommends locales && locale-gen en_US.UTF-8 >/dev/null || true
 ENV LANG=en_US.UTF-8 LC_ALL=en_US.UTF-8

 # Workdir
 WORKDIR /workspaces/atcoder

 # Default shell
 ENV SHELL=/bin/bash

 # Install some helpful tools for development (optional but small)
 RUN apt-get update && apt-get install -y --no-install-recommends tree htop file less && rm -rf /var/lib/apt/lists/*

 # Ensure permissions for workspace (in container) are friendly to vscode user
 RUN chown -R $USERNAME:$USERNAME /workspaces || true

 USER $USERNAME

 # Default entrypoint - keep standard shell
 CMD ["/bin/bash"]
FROM gcc:15

# Install common build deps and common C++ libs useful for competitive programming
RUN apt-get update \
 && DEBIAN_FRONTEND=noninteractive apt-get install -y --no-install-recommends \
    build-essential cmake git pkg-config ca-certificates \
    python3 python3-pip python3-venv curl wget unzip \
    clang clang-format ninja-build \
    libboost-all-dev libgmp-dev libprotobuf-dev protobuf-compiler \
    zlib1g-dev libbz2-dev liblzma-dev libre2-dev libeigen3-dev \
 && apt-get clean \
 && rm -rf /var/lib/apt/lists/*

# Provide an atcoder install_dir placeholder as /usr by default
RUN mkdir -p /etc/atcoder && echo "/usr" > /etc/atcoder/install_dir.txt

WORKDIR /workspace

CMD ["bash"]
