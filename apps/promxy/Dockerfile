# syntax=docker/dockerfile:1

FROM docker.io/library/alpine:3.23@sha256:469c9ea410b9215eaee7976ba6c0639039b444be8e5d638f7abbada189971eb2
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
