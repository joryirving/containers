# syntax=docker/dockerfile:1

# Define VERSION argument early
ARG VERSION

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

# Download Ollama binary for AMD64 using VERSION variable
RUN if [ -z "${VERSION}" ]; then \
        echo "ERROR: VERSION variable is not set, defaulting to 0.5.4" && \
        export VERSION="0.5.4"; \
    fi && \
    echo "Downloading Ollama version: ${VERSION}" && \
    curl -fsSL https://github.com/ollama/ollama/releases/download/v${VERSION}/ollama-linux-amd64 -o /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

# Download Intel GPU runtime libraries
RUN mkdir -p /opt/intel-gpu && \
    cd /opt/intel-gpu && \
    # Download Intel GPU packages to be installed in final stage \
    wget -q https://github.com/intel/gmmlib/releases/download/intel-gmmlib-22.3.0/libigdgmm12_22.3.0_amd64.deb && \
    wget -q https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-core_2.0.0+ubuntu22.04_amd64.deb && \
    wget -q https://github.com/intel/intel-graphics-compiler/releases/download/v2.0.0/intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    wget -q https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/libze-intel-gpu_23.20.26949.10_amd64.deb && \
    wget -q https://github.com/intel/compute-runtime/releases/download/23.20.26949.10/intel-opencl-icd_23.20.26949.10_amd64.deb

# Final stage - use Ubuntu 24.04
FROM ubuntu:24.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install Intel GPU runtime libraries in final stage
RUN apt-get update && apt-get install -y \
    ca-certificates \
    wget \
    pciutils \
    && rm -rf /var/lib/apt/lists/*

# Copy Intel GPU packages from builder
COPY --from=builder /opt/intel-gpu /tmp/gpu

# Install Intel GPU runtime libraries
RUN cd /tmp/gpu && \
    # Install opencl-icd-dev which provides OpenCL support \
    apt-get update && apt-get install -y --no-install-recommends opencl-icd-opencl-dev ocl-icd-libopencl1 || true && \
    # Install packages in dependency order to avoid conflicts \
    apt-get install -y --no-install-recommends ./libigdgmm12_22.3.0_amd64.deb && \
    apt-get install -y --no-install-recommends ./intel-igc-core_2.0.0+ubuntu22.04_amd64.deb ./intel-igc-opencl_2.0.0+ubuntu22.04_amd64.deb && \
    apt-get install -y --no-install-recommends ./libze-intel-gpu_23.20.26949.10_amd64.deb && \
    apt-get install -y --no-install-recommends ./intel-opencl-icd_23.20.26949.10_amd64.deb || true && \
    # Clean up downloaded packages \
    rm -rf /tmp/gpu && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Copy Ollama binary - VERSION is not needed in final stage
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