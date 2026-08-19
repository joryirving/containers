# syntax=docker/dockerfile:1

FROM docker.io/library/golang:1.27-alpine@sha256:7d5cbf6833f7331dafd25a2e8b9673477f559759ff8ed4ca8efabe6795ad08db AS builder
ARG TARGETOS
ARG TARGETARCH
ARG VERSION

WORKDIR /src
COPY main.go ./main.go
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build \
    -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /amdgpu-exporter ./main.go

FROM gcr.io/distroless/static-debian13:nonroot@sha256:f7f8f729987ad0fdf6b05eeeae94b26e6a0f613bdf46feea7fc40f7bd72953e6

COPY --from=builder /amdgpu-exporter /amdgpu-exporter

USER 65534:65534
EXPOSE 9494

ENTRYPOINT ["/amdgpu-exporter"]
