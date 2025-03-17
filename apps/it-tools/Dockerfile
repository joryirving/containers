ARG VERSION
FROM node:lts-alpine AS build

LABEL org.opencontainers.image.source="https://github.com/CorentinTh/it-tools"

ARG VERSION
ARG TARGETARCH
ARG TARGETOS

RUN \
  apk add --no-cache curl git \
  && git clone -b v${VERSION} --single-branch https://github.com/CorentinTh/it-tools.git /app \
  && cd /app \
  && npm install -g corepack@latest \
  && corepack enable  \
  && corepack prepare pnpm@latest --activate \
  && pnpm install --prefer-offline \
  && pnpm build

  FROM ghcr.io/joryirving/caddy-scratch:2.9.1@sha256:e8b04c4c599689092cabbec26fcf14180038973abad10a826e677f93b99f4f0f
COPY --chown=1000:1000 --from=build /app/dist/ /app
CMD ["file-server", "--root", "/app", "--listen", ":8080"]
