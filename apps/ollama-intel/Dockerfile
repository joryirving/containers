# syntax=docker/dockerfile:1

ARG TARGETARCH
ARG ARCH=${TARGETARCH/amd64/amd64}
ARG ARCH=${TARGETARCH/arm64/aarch64}

# Use Ubuntu base image to support Intel GPU libraries
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
    && rm -rf /var/lib/apt/lists/*

# Download Ollama binary
RUN ARCH=$(uname -m) && \
    if [ "$ARCH" = "x86_64" ]; then ARCH="amd64"; fi && \
    if [ "$ARCH" = "aarch64" ]; then ARCH="arm64"; fi && \
    curl -fsSL https://github.com/ollama/ollama/releases/latest/download/ollama_linux_$ARCH.tgz | tar -xz -C /tmp && \
    mv /tmp/ollama /usr/bin/ollama && \
    chmod +x /usr/bin/ollama

# Create a non-root user for running Ollama
RUN groupadd -g 1000 ollama && \
    useradd -m -u 1000 -g ollama -s /bin/bash ollama

# Create models directory with proper permissions
RUN mkdir -p /models && \
    chown ollama:ollama /models && \
    chmod 755 /models

# Final stage
FROM ubuntu:22.04

# Avoid prompts from apt
ENV DEBIAN_FRONTEND=noninteractive

# Install minimal runtime dependencies
RUN apt-get update && apt-get install -y \
    ca-certificates \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Copy Intel GPU runtime libraries from builder
COPY --from=builder /usr/lib/x86_64-linux-gnu/libigc* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libigdfcl* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libigfxcmrt* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libigdrcl* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libze* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libzex* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libOpenCL* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libva* /usr/lib/x86_64-linux-gnu/
COPY --from=builder /usr/lib/x86_64-linux-gnu/libdrm* /usr/lib/x86_64-linux-gnu/

# Copy Ollama binary
COPY --from=builder /usr/bin/ollama /usr/bin/ollama

# Copy user and group from builder
COPY --from=builder /etc/passwd /etc/passwd
COPY --from=builder /etc/group /etc/group

# Create models directory
RUN mkdir -p /models && \
    chown ollama:ollama /models

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