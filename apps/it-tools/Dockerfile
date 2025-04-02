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

FROM ghcr.io/joryirving/caddy-scratch:2.9.1@sha256:a0509435eaf99c6a1b4bf55f2c18be59f4c28c174d3320980ca3033e1ad2f7e8

COPY --chown=1000:1000 --from=build /app/dist/ /app
CMD ["file-server", "--root", "/app", "--listen", ":8080"]
