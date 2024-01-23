FROM rust:1.75.0-bookworm as builder

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL repository="https://github.com/morphy2k/rss-forwarder"
LABEL maintainer="Markus Wiegand <mail@morphy2k.dev>"
LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/morphy2k/rss-forwarder"

ENV PKG_CONFIG_ALLOW_CROSS=1

WORKDIR /usr/src/rss-forwarder

RUN wget https://github.com/morphy2k/rss-forwarder/archive/refs/tags/v${VERSION}.tar.gz \
    && tar -xvf v${VERSION}.tar.gz \
    && cd rss-forwarder-${VERSION} \
    && cargo install --path .

FROM gcr.io/distroless/cc-debian12

COPY --from=builder /usr/local/cargo/bin/rss-forwarder /usr/local/bin/rss-forwarder

CMD ["rss-forwarder", "/data/config.toml"]
