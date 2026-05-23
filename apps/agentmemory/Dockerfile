# syntax=docker/dockerfile:1

ARG VERSION
ARG III_VERSION=0.11.2
ARG AGENTMEMORY_VERSION

FROM docker.io/iiidev/iii:${III_VERSION} AS iii-image

FROM docker.io/node:24-slim

ARG TARGETARCH
ARG VERSION
ARG III_VERSION
ARG AGENTMEMORY_VERSION

RUN apt-get update && \
    apt-get install -y --no-install-recommends openssl ca-certificates gosu curl && \
    rm -rf /var/lib/apt/lists/*

COPY --from=iii-image /app/iii /usr/local/bin/iii

WORKDIR /opt/agentmemory

RUN printf '{"name":"agentmemory-deploy","version":"1.0.0","private":true,"overrides":{"iii-sdk":"%s"}}\n' "${III_VERSION}" > package.json && \
    npm install "@agentmemory/agentmemory@${AGENTMEMORY_VERSION}" --omit=optional --no-fund --no-audit && \
    ln -s /opt/agentmemory/node_modules/.bin/agentmemory /usr/local/bin/agentmemory

ENV AGENTMEMORY_III_VERSION=${III_VERSION} \
    TINI_SUBREAPER=1 \
    AGENTMEMORY_DATA_DIR=/data

COPY --chmod=0755 entrypoint.sh /usr/local/bin/agentmemory-entrypoint.sh

USER nobody:nogroup

EXPOSE 3111 3112 3113

ENTRYPOINT ["/usr/bin/tini", "--", "/usr/local/bin/agentmemory-entrypoint.sh"]