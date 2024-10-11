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
  apk add --no-cache curl git jq \
  && fullversion=$(curl -sX GET "https://api.github.com/repos/CorentinTh/it-tools/releases/latest" | jq --raw-output '.tag_name') \
  && git clone https://github.com/CorentinTh/it-tools.git /app \
  && cd /app \
  && git checkout "$fullversion"

WORKDIR /app

RUN \
  corepack enable  \
  && corepack prepare pnpm@latest --activate \
  && pnpm install --prefer-offline \
  && pnpm build

FROM nginxinc/nginx-unprivileged:alpine

USER root
RUN \
  apk add --no-cache \
  catatonit

USER nginx

COPY --chown=101:101 --from=build /app/dist/ /usr/share/nginx/html/
COPY --chown=101:101 --from=build /app/nginx.conf /etc/nginx/conf.d/default.conf
COPY ./entrypoint.sh /entrypoint.sh

RUN \
  sed -i "s/worker_processes  auto;/worker_processes  2;/g" /etc/nginx/nginx.conf \
  && sed -i "s/80;/8080;/g" /etc/nginx/conf.d/default.conf

ENTRYPOINT ["/usr/bin/catatonit", "--", "/entrypoint.sh"]
