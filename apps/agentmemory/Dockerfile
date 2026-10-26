# syntax=docker/dockerfile:1

ARG VERSION
ARG III_VERSION

FROM docker.io/iiidev/iii:0.25.0@sha256:810e5faaca6ba2438d4b52f72211cc9e72d958bcf806f97df9b85447523ca72b AS iii-engine

FROM docker.io/library/node:24-slim

ARG TARGETARCH
ARG VERSION
ARG III_VERSION

# STATE_VERSION and HTTP_VERSION pin the iii state and http workers the
# engine supervises via worker-compose.yaml. Keep them in sync with
# III_VERSION per upstream deploy/Dockerfile in the agentmemory repo.
ENV \
    AGENTMEMORY_DATA_DIR=/data \
    III_COMPOSE_STATE_DIR=/data/compose-state \
    III_ENGINE_PORT=49134 \
    III_REST_PORT=3111 \
    III_VIEWER_PORT=3113 \
    III_TELEMETRY_ENABLED=false \
    STATE_VERSION=0.22.20 \
    HTTP_VERSION=0.22.7 \
    MALLOC_ARENA_MAX=2

USER root
WORKDIR /opt/agentmemory

RUN apt-get update && \
    apt-get install -y --no-install-recommends \
        ca-certificates \
        catatonit \
        openssl \
        tzdata && \
    npm pack --pack-destination /tmp "@agentmemory/agentmemory@${VERSION}" && \
    tar -xzf /tmp/agentmemory-*.tgz -C /opt/agentmemory --strip-components=1 && \
    rm -f /tmp/agentmemory-*.tgz && \
    npm install --omit=optional --omit=dev --no-fund --no-audit && \
    ln -s /opt/agentmemory/dist/cli.mjs /usr/local/bin/agentmemory && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

COPY --from=iii-engine /app/iii /usr/local/bin/iii

COPY runtime/iii.worker.yaml runtime/worker-compose.yaml /opt/agentmemory/

COPY --chmod=0755 entrypoint.sh /entrypoint.sh

RUN iii --version 2>&1 | grep -qF "${III_VERSION}" || \
        { echo "ERROR: iii engine does not report version ${III_VERSION}; the FROM digest and III_VERSION are out of sync" >&2; exit 1; } && \
    grep -q 'file_path: /data/state_store.db' /opt/agentmemory/worker-compose.yaml || \
        { echo "ERROR: worker-compose.yaml is not using absolute /data paths; the engine would persist to the ephemeral overlay and lose all memory on restart" >&2; exit 1; } && \
    mkdir -p /data && \
    chown -R node:node /data /opt/agentmemory

USER node:node

EXPOSE 3111 3113

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]
