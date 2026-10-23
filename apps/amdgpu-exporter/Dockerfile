# syntax=docker/dockerfile:1

FROM docker.io/library/golang:1.27-alpine@sha256:b8c9b82affbbb82a020bbcf998dad2ba9516944ac7e883524642a481a9505e9c AS builder
ARG TARGETOS
ARG TARGETARCH
ARG VERSION

WORKDIR /src
COPY main.go ./main.go
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build \
    -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /amdgpu-exporter ./main.go

FROM gcr.io/distroless/static-debian13:nonroot@sha256:18f4cc26c9ffa7f20a359298be7deadac5c607c8e03a02b8119f1a5fc2f82c99

COPY --from=builder /amdgpu-exporter /amdgpu-exporter

# Reading other containers' /proc/<pid>/fdinfo requires root on the host
# procfs. The pod drops all capabilities and runs read-only.
USER 0:0
EXPOSE 9494

ENTRYPOINT ["/amdgpu-exporter"]
