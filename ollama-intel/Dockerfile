# Dockerfile for Ollama with Intel GPU support
# Based on Ubuntu 22.04 LTS
FROM ubuntu:22.04 AS builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies needed for Intel GPU support
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    git \
    && rm -rf /var/lib/apt/lists/*

# Add Intel GPU repositories
RUN wget -O- https://repositories.intel.com/graphics/intel-graphics.key | gpg --dearmor -o /usr/share/keyrings/intel-graphics.gpg
RUN echo "deb [arch=amd64 signed-by=/usr/share/keyrings/intel-graphics.gpg] https://repositories.intel.com/graphics/ubuntu $(lsb_release -cs) main" | tee /etc/apt/sources.list.d/intel.gpu.list

# Install Intel GPU runtime libraries
RUN apt-get update && apt-get install -y \
    intel-opencl-icd \
    intel-level-zero-gpu \
    intel-media-va-driver \
    intel-gmmlib \
    intel-igc-core \
    intel-igc-opencl \
    level-zero \
    level-zero-dev \
    && rm -rf /var/lib/apt/lists/*

# Download Ollama binary directly from GitHub releases
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi && \
    if [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; fi && \
    curl -fsSL https://github.com/ollama/ollama/releases/latest/download/ollama_linux_$ARCH.tgz | tar -xz -C /tmp && \
    mv /tmp/ollama /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

# Create a non-root user for running Ollama
RUN useradd -m -u 1000 -s /bin/bash ollama

# Create models directory with proper permissions
RUN mkdir -p /models && \
    chown ollama:ollama /models && \
    chmod 755 /models

# Switch to non-root user
USER ollama

# Set working directory
WORKDIR /home/ollama

# Expose port
EXPOSE 11434

# Create startup script
RUN echo '#!/bin/bash\n\
export OLLAMA_HOST=0.0.0.0\n\
export OLLAMA_INTEL_GPU=true\n\
export OLLAMA_NUM_GPU=999\n\
export OLLAMA_CONTEXT_LENGTH=65536\n\
export ZES_ENABLE_SYSMAN=1\n\
export no_proxy=localhost,127.0.0.1\n\
exec /usr/bin/ollama serve' > /home/ollama/startup.sh && \
chmod +x /home/ollama/startup.sh

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/version || exit 1

# Entry point
ENTRYPOINT ["/home/ollama/startup.sh"]