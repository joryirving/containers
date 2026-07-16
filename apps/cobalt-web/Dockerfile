# syntax=docker/dockerfile:1

FROM docker.io/library/node:24-alpine@sha256:a0b9bf06e4e6193cf7a0f58816cc935ff8c2a908f81e6f1a95432d679c54fbfd AS builder
ARG VERSION
ARG WEB_DEFAULT_API
ENV WEB_DEFAULT_API=${WEB_DEFAULT_API}
WORKDIR /app

ADD https://github.com/imputnet/cobalt.git#${VERSION} .

RUN corepack enable \
    && apk add --no-cache python3 alpine-sdk

RUN --mount=type=cache,id=pnpm,target=/pnpm/store \
    pnpm install --frozen-lockfile \
    && pnpm --filter @imput/cobalt-web build

FROM ghcr.io/nginxinc/nginx-unprivileged:1.27-alpine@sha256:e234d4f7e346c098f7b22245690372382aded5be988611eb2c53ae62231eece7

COPY --from=builder --chown=nginx:nginx /app/web/build /usr/share/nginx/html
USER nginx
