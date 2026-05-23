# syntax=docker/dockerfile:1

ARG VERSION
ARG III_VERSION=0.11.2

FROM docker.io/library/node:22-slim

ARG TARGETARCH
ARG VERSION
ARG III_VERSION

ENV \
    AGENTMEMORY_DATA_DIR=/data \
    AGENTMEMORY_HMAC_FILE=/data/.hmac \
    III_REST_PORT=3111 \
    NODE_ENV=production

USER root
WORKDIR /app

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        catatonit \
        curl \
        openssl \
        tzdata && \
    case "${TARGETARCH}" in \
        amd64) iii_target="x86_64-unknown-linux-gnu" ;; \
        arm64) iii_target="aarch64-unknown-linux-gnu" ;; \
        *) echo "unsupported arch ${TARGETARCH}"; exit 1 ;; \
    esac && \
    curl -fsSL "https://github.com/iii-hq/iii/releases/download/iii%2Fv${III_VERSION}/iii-${iii_target}.tar.gz" \
        | tar -xz -C /usr/local/bin && \
    chmod +x /usr/local/bin/iii && \
    iii --version && \
    npm install -g --omit=optional --no-fund --no-audit \
        "@agentmemory/agentmemory@${VERSION}" && \
    find /usr/local/lib/node_modules/@agentmemory/agentmemory \
        -name 'iii-config.yaml' -print0 \
        | xargs -0 -r sed -i 's/host: 127\.0\.0\.1/host: 0.0.0.0/g' && \
    find /usr/local/lib/node_modules/@agentmemory/agentmemory \
        -type f \( -name '*.js' -o -name '*.mjs' -o -name '*.cjs' \) -print0 \
        | xargs -0 -r sed -i 's/\.listen(port, "127\.0\.0\.1"/.listen(port, "0.0.0.0"/g' && \
    mkdir -p /data && \
    chown -R node:node /data /app && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/* /root/.npm

COPY --chmod=0755 entrypoint.sh /entrypoint.sh

USER node:node

EXPOSE 3111 3112 3113

ENTRYPOINT ["/entrypoint.sh"]