# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:132c5416901054a60a6c1f9f5073fd16dc91c8f3de1693f6be93b5912cf3ee71
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
        'amd64') TARGET='linux-x64-baseline-musl' ;; \
        'arm64') TARGET='linux-arm64-musl' ;; \
        *) echo "unsupported arch ${TARGETARCH}" && exit 1 ;; \
    esac \
    && curl -fsSL "https://registry.npmjs.org/@opencode/cli-${TARGET}/-/cli-${TARGET}-${VERSION}.tgz" \
        | tar -xz -C /usr/local/bin --strip-components=2 package/bin/opencode \
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
