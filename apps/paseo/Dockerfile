# syntax=docker/dockerfile:1
ARG VERSION=0.14.0

FROM ghcr.io/getpaseo/paseo:${VERSION}@sha256:2a370238230689406d7123e44b218ede221fd77dd23200a18672ed03873682b0

ARG VERSION
ARG OPENCODE_VERSION=2.0.32
# renovate: datasource=github-releases depName=jdx/mise
ARG MISE_VERSION=v2026.10.22
ARG TARGETARCH

USER root

RUN apt-get update && apt-get install -y --no-install-recommends \
      build-essential libatomic1 libffi-dev libjpeg-dev libsqlite3-dev libssl-dev \
pkg-config python3 python3-dev python3-pip python3-venv python3-yaml \
ripgrep unzip xz-utils zlib1g-dev \
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
COPY mise.lock /etc/mise/mise.lock
# npm-backed tools (oxfmt) lock via a dependency sidecar next to the lockfile.
COPY .mise/locks /etc/mise/.mise/locks

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
