# syntax=docker/dockerfile:1
ARG VERSION=0.12.0

FROM ghcr.io/getpaseo/paseo:${VERSION}@sha256:0d17dd75a51c591907a4bbcd505013102048246a0cd6e824de3b38a6057ff862

ARG VERSION
ARG OPENCODE_VERSION=2.0.32
ARG MISE_VERSION=v2026.10.10
ARG TARGETARCH

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
      libatomic1 python3 python3-yaml ripgrep unzip xz-utils \
    && rm -rf /var/lib/apt/lists/*

RUN case "${TARGETARCH}" in \
      'amd64') OPENCODE_TARGET='linux-x64-baseline' ;; \
      'arm64') OPENCODE_TARGET='linux-arm64' ;; \
      *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://registry.npmjs.org/@opencode/cli-${OPENCODE_TARGET}/-/cli-${OPENCODE_TARGET}-${OPENCODE_VERSION}.tgz" -o /tmp/opencode.tgz \
    && tar -xzOf /tmp/opencode.tgz package/bin/opencode > /usr/local/bin/opencode \
    && chmod 0755 /usr/local/bin/opencode \
    && rm -f /tmp/opencode.tgz

RUN case "${TARGETARCH}" in \
      'amd64') MISE_ARCH='linux-x64' ;; \
      'arm64') MISE_ARCH='linux-arm64' ;; \
      *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/jdx/mise/releases/download/${MISE_VERSION}/mise-${MISE_VERSION}-${MISE_ARCH}.tar.xz" -o /tmp/mise.tar.xz \
    && tar -xJf /tmp/mise.tar.xz -C /tmp \
    && install /tmp/mise/bin/mise /usr/local/bin/mise \
    && rm -rf /tmp/mise /tmp/mise.tar.xz

ENV MISE_DATA_DIR=/home/paseo/.local/share/mise \
    MISE_CACHE_DIR=/home/paseo/.cache/mise \
    MISE_STATE_DIR=/home/paseo/.local/state/mise \
    PASEO_HOME=/home/paseo/.paseo \
    PATH=/home/paseo/.local/share/mise/shims:/opt/mise/shims:/usr/local/bin:/usr/bin:/bin

COPY mise.toml /etc/mise/config.toml

RUN mkdir -p /opt/mise /tmp/mise-cache /tmp/mise-state \
    && cd /etc/mise \
    && MISE_DATA_DIR=/opt/mise MISE_CACHE_DIR=/tmp/mise-cache MISE_STATE_DIR=/tmp/mise-state mise trust \
    && MISE_DATA_DIR=/opt/mise MISE_CACHE_DIR=/tmp/mise-cache MISE_STATE_DIR=/tmp/mise-state mise install \
    && MISE_DATA_DIR=/opt/mise MISE_CACHE_DIR=/tmp/mise-cache MISE_STATE_DIR=/tmp/mise-state mise reshim \
    && opencode --version \
    && kubectl version --client \
    && flux version --client \
    && kustomize version \
    && sops --version

COPY start.sh /usr/local/bin/paseo-start
RUN chmod 0755 /usr/local/bin/paseo-start \
    && chown -R 1000:1000 /home/paseo

USER 1000:1000

CMD ["/usr/local/bin/paseo-start"]
