# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:f3d55900449227ae9e237ede521e7b665d53a253b42065ba90b9db9275e198ad
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
