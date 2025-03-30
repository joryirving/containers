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

FROM ghcr.io/joryirving/caddy-scratch:2.9.1@sha256:9441f535542f3bffd53ece94e7142a804eb200aa54052f6906d02c7f2b135750

COPY --chown=1000:1000 --from=build /app/dist/ /app
CMD ["file-server", "--root", "/app", "--listen", ":8080"]
