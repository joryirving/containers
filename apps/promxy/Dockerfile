# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:132c5416901054a60a6c1f9f5073fd16dc91c8f3de1693f6be93b5912cf3ee71
ARG VERSION
ARG TARGETARCH
ARG SOURCE

RUN apk add --no-cache \
        ca-certificates \
    && wget "https://github.com/jacksontj/promxy/releases/download/${VERSION}/promxy-${VERSION}-linux-${TARGETARCH}" \
        -O /tmp/promxy \
    && echo "$(grep "promxy-${VERSION}-linux-${TARGETARCH}" <(wget -qO- "https://github.com/jacksontj/promxy/releases/download/${VERSION}/SHA256SUMS") | cut -d' ' -f1)  /tmp/promxy" | sha256sum -c - \
    && chmod +x /tmp/promxy \
    && mv /tmp/promxy /bin/promxy \
    && mkdir -p /etc/promxy \
    && rm -rf /tmp/*

USER nobody
ENTRYPOINT ["/bin/promxy"]
CMD ["--config=/etc/promxy/config.yaml"]
