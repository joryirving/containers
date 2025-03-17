FROM cgr.dev/chainguard/rust:latest-dev as builder
LABEL org.opencontainers.image.source="https://github.com/redlib-org/redlib"
ARG TARGETPLATFORM
ARG VERSION

WORKDIR /app

RUN \
  git clone --depth 1 --branch "v${VERSION}" -c advice.detachedHead=false https://github.com/redlib-org/redlib.git /app && \
  cargo build --release

FROM cgr.dev/chainguard/wolfi-base:latest

# trunk-ignore(hadolint/DL3018)
RUN apk update && \
  apk add --no-cache \
    coreutils \
    libgcc \
    jo \
    tini \
    trurl \
    wget

USER nonroot

COPY --from=builder /app/target/release/redlib /app/redlib

WORKDIR /app

EXPOSE 8080

HEALTHCHECK --interval=1m --timeout=3s CMD wget --spider --quiet http://localhost:8080/settings || exit 1

CMD ["tini", "--", "/app/redlib", "--address", "0.0.0.0"]
