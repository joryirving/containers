ARG VERSION
FROM node:lts-alpine AS build

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/CorentinTh/it-tools"

RUN \
  apk add --no-cache curl git \
  && git clone -b v${VERSION} --single-branch https://github.com/CorentinTh/it-tools.git /app \
  && cd /app \
  && corepack enable  \
  && corepack install \
  && corepack prepare pnpm --activate \
  && pnpm install --prefer-offline \
  && pnpm build

  FROM ghcr.io/joryirving/caddy-scratch:2.9.1@sha256:bd4640fe5de8cbd13ecc39147f78d007d69b1208a914ca872954cfe4f2afcf59
  COPY --chown=1000:1000 --from=build /app/dist/ /app
  CMD ["file-server", "--root", "/app", "--listen", ":8080"]
