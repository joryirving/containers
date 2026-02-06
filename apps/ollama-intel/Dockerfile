# syntax=docker/dockerfile:1

FROM docker.io/library/ubuntu:22.04
ARG TARGETARCH
ARG VERSION

ENV DEBIAN_FRONTEND="noninteractive" \
    OLLAMA_HOST="0.0.0.0" \
    OLLAMA_NUM_PARALLEL="1" \
    OLLAMA_GPU_OVERHEAD="0" \
    ZE_ENABLE_PCI_ID_DEVICE_ORDER="1"

USER root
WORKDIR /app

RUN \
    apt-get update \
    && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        ca-certificates \
        catatonit \
        curl \
        gnupg \
        lsb-release \
        pciutils \
        software-properties-common \
    && \
    # Enable universe repository (required for level-zero / libze1) \
    add-apt-repository universe \
    && \
    # Add Intel GPU repositories \
    mkdir -p /etc/apt/keyrings && \
    curl -fsSL https://repositories.intel.com/graphics/intel-graphics.key | \
    gpg --dearmor -o /etc/apt/keyrings/intel-graphics.gpg && \
    echo "deb [signed-by=/etc/apt/keyrings/intel-graphics.gpg] \
    https://repositories.intel.com/graphics/ubuntu jammy client" \
    > /etc/apt/sources.list.d/intel-gpu.list \
    && \
    apt-get update \
    && \
    apt-get install -y --no-install-recommends --no-install-suggests \
        level-zero \
        libze1 \
        intel-opencl-icd \
        intel-media-va-driver-non-free \
        clinfo \
    && \
    # Install Ollama using the official installer \
    curl -fsSL https://ollama.com/install.sh | sh \
    && \
    # Create models directory with proper permissions \
    mkdir -p /models && \
    chown 65534:65534 /models \
    && \
    apt-get purge -y --auto-remove -o APT::AutoRemove::RecommendsImportant=false \
    && apt-get autoremove -y \
    && apt-get clean \
    && rm -rf /etc/apt/keyrings/intel-graphics.gpg /etc/apt/sources.list.d/intel-gpu.list \
    && rm -rf /tmp/* /var/lib/apt/lists/* /var/tmp/

COPY . /

USER nobody:nogroup
WORKDIR /models
VOLUME ["/models"]

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]