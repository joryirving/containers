# syntax=docker/dockerfile:1

FROM docker.io/library/golang:1.26-alpine@sha256:f23e8b227fb4493eabe03bede4d5a32d04092da71962f1fb79b5f7d1e6c2a17f AS builder
ARG TARGETOS
ARG TARGETARCH
ARG VERSION

WORKDIR /src
COPY main.go ./main.go
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build \
    -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /rocm-smi-exporter ./main.go

FROM gcr.io/distroless/static-debian13:nonroot@sha256:963fa6c544fe5ce420f1f54fb88b6fb01479f054c8056d0f74cc2c6000df5240

COPY --from=builder /rocm-smi-exporter /rocm-smi-exporter

USER 65534:65534
EXPOSE 9494

ENTRYPOINT ["/rocm-smi-exporter"]
