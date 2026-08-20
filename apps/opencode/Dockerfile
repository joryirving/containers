# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:fd791d74b68913cbb027c6546007b3f0d3bc45125f797758156952bc2d6daf40
ARG VERSION
ARG TARGETARCH

ENV BUN_RUNTIME_TRANSPILER_CACHE_PATH=0 \
    HOME=/home/opencode

RUN \
    apk add --no-cache \
        bash \
        ca-certificates \
        curl \
        fd \
        git \
        github-cli \
        jq \
        libgcc \
        libstdc++ \
        openssh-client \
        ripgrep \
        tzdata \
        yq \
    && \
    case "${TARGETARCH}" in \
        'amd64') ASSET='opencode-linux-x64-baseline-musl' ;; \
        'arm64') ASSET='opencode-linux-arm64-musl' ;; \
        *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://github.com/sst/opencode/releases/download/${VERSION}/${ASSET}.tar.gz" \
        | tar -xz -C /usr/local/bin \
    && chmod +x /usr/local/bin/opencode \
    && \
    adduser -D -u 1000 -h "${HOME}" opencode \
    && mkdir -p "${HOME}" \
    && chown -R opencode:opencode "${HOME}" \
    && rm -rf /tmp/*

USER opencode
WORKDIR /home/opencode
RUN opencode --version

ENTRYPOINT ["opencode"]
