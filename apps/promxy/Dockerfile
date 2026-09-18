# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:266819353c6716fd9a64ef6a72eae7a72c05055b3660a30eb89d811c2c1a5c83
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
