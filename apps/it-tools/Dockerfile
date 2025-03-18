ARG VERSION
FROM node:lts-alpine AS build
ARG VERSION

RUN \
  apk add --no-cache curl git \
  && git clone -b v${VERSION} --single-branch https://github.com/CorentinTh/it-tools.git /app \
  && cd /app \
  && npm install -g corepack@latest \
  && corepack enable  \
  && corepack prepare pnpm@latest --activate \
  && pnpm install --prefer-offline \
  && pnpm build

FROM ghcr.io/joryirving/caddy-scratch:2.9.1@sha256:6cf8475c6120b07cb92b91ea911e5ef10fa02db846d1811886e7f4cf4e198a12
LABEL org.opencontainers.image.source="https://github.com/CorentinTh/it-tools"
COPY --chown=1000:1000 --from=build /app/dist/ /app
CMD ["file-server", "--root", "/app", "--listen", ":8080"]
