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

FROM public.ecr.aws/docker/library/caddy:2.9.1-builder-alpine
LABEL org.opencontainers.image.source="https://github.com/CorentinTh/it-tools"
COPY --chown=1000:1000 --from=build /app/dist/ /app
CMD ["file-server", "--root", "/app", "--listen", ":8080"]
