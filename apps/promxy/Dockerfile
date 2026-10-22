# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:21f3e19bafab57a9ff7aa9dd571dac72f868370472c10f450cc0416cc1aca553
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
