# syntax=docker/dockerfile:1

# Use Ubuntu base image to support Intel GPU libraries
FROM ubuntu:24.04 AS builder

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install dependencies needed for Intel GPU support
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    ca-certificates \
    gnupg \
    && rm -rf /var/lib/apt/lists/*

# Download and install Intel GPU runtime libraries directly from Intel releases
RUN mkdir -p /tmp/gpu && \
    cd /tmp/gpu && \
    apt-get update && \
    apt-get install -y wget && \
    wget https://github.com/oneapi-src/level-zero/releases/download/v1.21.9/level-zero_1.21.9+u24.04_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.8.3/intel-igc-core_2.8.3+18762_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.8.3/intel-igc-opencl_2.8.3+18762_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/25.09.32961.7/intel-level-zero-gpu_1.6.32961.7_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/25.09.32961.7/intel-opencl-icd_25.09.32961.7_amd64.deb && \
    wget https://github.com/intel/gmmlib/releases/download/intel-gmmlib-22.6.0/libigdgmm12_22.6.0_amd64.deb && \
    dpkg -i *.deb && \
    rm -rf /tmp/gpu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download Ollama binary for AMD64 (since we only have AMD64 nodes with Intel GPUs)
RUN curl -fsSL https://github.com/ollama/ollama/releases/latest/download/ollama_linux_amd64.tgz | tar -xz -C /tmp && \
    mv /tmp/ollama /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

# Final stage - use Ubuntu 24.04
FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Intel GPU runtime libraries in final stage
RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/* && \
    mkdir -p /tmp/gpu && \
    cd /tmp/gpu && \
    wget https://github.com/oneapi-src/level-zero/releases/download/v1.21.9/level-zero_1.21.9+u24.04_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.8.3/intel-igc-core_2.8.3+18762_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.8.3/intel-igc-opencl_2.8.3+18762_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/25.09.32961.7/intel-level-zero-gpu_1.6.32961.7_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/25.09.32961.7/intel-opencl-icd_25.09.32961.7_amd64.deb && \
    wget https://github.com/intel/gmmlib/releases/download/intel-gmmlib-22.6.0/libigdgmm12_22.6.0_amd64.deb && \
    dpkg -i *.deb && \
    rm -rf /tmp/gpu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Ollama binary
COPY --from=builder /usr/bin/ollama /usr/bin/ollama

# Create a non-root user for running Ollama
RUN groupadd -g 1000 ollama && \
    useradd -m -u 1000 -g ollama -s /bin/bash ollama

# Create models directory with proper permissions
RUN mkdir -p /models && \
    chown ollama:ollama /models && \
    chmod 755 /models

# Switch to non-root user
USER ollama:ollama

# Set working directory
WORKDIR /home/ollama

# Expose port
EXPOSE 11434

# Create startup script
RUN echo '#!/bin/bash\n\
export OLLAMA_HOST="${OLLAMA_HOST:-0.0.0.0}"\n\
export OLLAMA_INTEL_GPU="${OLLAMA_INTEL_GPU:-true}"\n\
export OLLAMA_NUM_GPU="${OLLAMA_NUM_GPU:-999}"\n\
export OLLAMA_CONTEXT_LENGTH="${OLLAMA_CONTEXT_LENGTH:-65536}"\n\
export ZES_ENABLE_SYSMAN="${ZES_ENABLE_SYSMAN:-1}"\n\
export no_proxy="${no_proxy:-localhost,127.0.0.1}"\n\
exec /usr/bin/ollama serve' > /home/ollama/startup.sh && \
chmod +x /home/ollama/startup.sh

# Set health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:11434/api/version || exit 1

# Volume for models
VOLUME ["/models"]

# Entry point
ENTRYPOINT ["/home/ollama/startup.sh"]