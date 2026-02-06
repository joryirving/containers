# syntax=docker/dockerfile:1
FROM ubuntu:22.04
ENV DEBIAN_FRONTEND=noninteractive

# ---- Base deps ----
RUN apt-get update && apt-get install -y \
    curl \
    ca-certificates \
    gnupg \
    lsb-release \
    pciutils \
    clinfo \
    && rm -rf /var/lib/apt/lists/*

# ---- Intel GPU runtime ----
RUN mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://repositories.intel.com/graphics/intel-graphics.key | \
    gpg --dearmor -o /etc/apt/keyrings/intel-graphics.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/intel-graphics.gpg] \
    https://repositories.intel.com/graphics/ubuntu jammy client" \
    > /etc/apt/sources.list.d/intel-gpu.list

RUN apt-get update && apt-get install -y \
    intel-opencl-icd \
    intel-level-zero-gpu \
    intel-media-va-driver-non-free \
    libze-loader1 \
    && rm -rf /var/lib/apt/lists/*

# ---- Install Ollama ----
RUN curl -fsSL https://ollama.com/install.sh | sh

# ---- Create models directory ----
RUN mkdir -p /models && \
    chown ollama:ollama /models && \
    chmod 755 /models

# ---- Runtime env ----
ENV OLLAMA_HOST=0.0.0.0
ENV OLLAMA_NUM_PARALLEL=1
ENV OLLAMA_GPU_OVERHEAD=0
ENV ZE_ENABLE_PCI_ID_DEVICE_ORDER=1

# Expose port
EXPOSE 11434

# Volume for models
VOLUME ["/models"]

# Entry point
ENTRYPOINT ["ollama"]
CMD ["serve"]