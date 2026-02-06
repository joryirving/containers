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
    # Install opencl-icd-dev which provides OpenCL support \
    apt-get install -y opencl-icd-dev opencl-icd-libopencl1 || true && \
    # If the specific package isn't available, continue with installation \
    # Install packages in dependency order to avoid conflicts \
    wget https://github.com/intel/gmmlib/releases/download/intel-gmmlib-22.3.0/libigdgmm12_22.3.0_amd64.deb && \
    apt-get install -y ./libigdgmm12_22.3.0_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-core_2.0.0+ubuntu22.04_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    apt-get install -y ./intel-igc-core_2.0.0+ubuntu22.04_amd64.deb ./intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/libze-intel-gpu_23.20.26949.10_amd64.deb && \
    apt-get install -y ./libze-intel-gpu_23.20.26949.10_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/intel-opencl-icd_23.20.26949.10_amd64.deb && \
    apt-get install -y ./intel-opencl-icd_23.20.26949.10_amd64.deb || true && \
    # If intel-opencl-icd fails to install due to missing dependencies, try installing without it \
    # and just rely on the other Intel GPU components \
    rm -rf /tmp/gpu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Download Ollama binary for AMD64 using VERSION variable (since we only have AMD64 nodes with Intel GPUs)
RUN curl -fsSL https://github.com/ollama/ollama/releases/download/v${VERSION}/ollama-linux-amd64 -o /tmp/ollama && \
    chmod +x /tmp/ollama && \
    mv /tmp/ollama /usr/bin/ollama

# Final stage - use Ubuntu 24.04
FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Intel GPU runtime libraries in final stage
RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    && rm -rf /var/lib/apt/lists/* && \
    # Install opencl-icd-dev which provides OpenCL support \
    apt-get install -y opencl-icd-dev opencl-icd-libopencl1 || true && \
    mkdir -p /tmp/gpu && \
    cd /tmp/gpu && \
    # Install packages in dependency order to avoid conflicts \
    wget https://github.com/intel/gmmlib/releases/download/intel-gmmlib-22.3.0/libigdgmm12_22.3.0_amd64.deb && \
    apt-get install -y ./libigdgmm12_22.3.0_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-core_2.0.0+ubuntu22.04_amd64.deb && \
    wget https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    apt-get install -y ./intel-igc-core_2.0.0+ubuntu22.04_amd64.deb ./intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/libze-intel-gpu_23.20.26949.10_amd64.deb && \
    apt-get install -y ./libze-intel-gpu_23.20.26949.10_amd64.deb && \
    wget https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/intel-opencl-icd_23.20.26949.10_amd64.deb && \
    apt-get install -y ./intel-opencl-icd_23.20.26949.10_amd64.deb || true && \
    # If intel-opencl-icd fails to install due to missing dependencies, try installing without it \
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