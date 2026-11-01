# syntax=docker/dockerfile:1

FROM docker.io/library/golang:1.27-alpine@sha256:d200d2dd76b03a99b52651fd1325aff7dcd35422c35c01bac56571b0507f3deb AS builder
ARG TARGETOS
ARG TARGETARCH
ARG VERSION

WORKDIR /src
COPY main.go ./main.go
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build \
    -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /amdgpu-exporter ./main.go

FROM gcr.io/distroless/static-debian13:nonroot@sha256:25ac8f0c3b2334a9eb05452266bd4697864a8c8ef0ef71e5e6480d7f92868329

COPY --from=builder /amdgpu-exporter /amdgpu-exporter

# Reading other containers' /proc/<pid>/fdinfo requires root on the host
# procfs. The pod drops all capabilities and runs read-only.
USER 0:0
EXPOSE 9494

ENTRYPOINT ["/amdgpu-exporter"]
