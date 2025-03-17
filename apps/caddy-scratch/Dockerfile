ARG VERSION
FROM public.ecr.aws/docker/library/caddy:builder AS build

ARG VERSION
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/caddyserver/caddy"

RUN \
  xcaddy build "v${VERSION}" --with "github.com/caddyserver/replace-response" \
  && setcap -r /usr/bin/caddy

FROM scratch
LABEL org.opencontainers.image.source="https://github.com/caddyserver/caddy"
COPY --chown=1000:1000 --chmod=555 --from=build /usr/bin/caddy /caddy
ENV XDG_CONFIG_HOME=/config/rendered
ENV XDG_DATA_HOME=/config/data
USER 1000:1000
WORKDIR /config/rendered
WORKDIR /config/data
WORKDIR /config
ENTRYPOINT ["/caddy"]
