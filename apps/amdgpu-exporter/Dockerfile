# syntax=docker/dockerfile:1

FROM docker.io/library/golang:1.27-alpine@sha256:eb61c3873c97416fff0116553fff65d67a3549f72e11d9758849a689cdd8b523 AS builder
ARG TARGETOS
ARG TARGETARCH
ARG VERSION

WORKDIR /src
COPY main.go ./main.go
RUN CGO_ENABLED=0 GOOS=${TARGETOS} GOARCH=${TARGETARCH} go build \
    -trimpath \
    -ldflags="-s -w -X main.version=${VERSION}" \
    -o /amdgpu-exporter ./main.go

FROM gcr.io/distroless/static-debian13:nonroot@sha256:aafe993665bf6200db38a02c11a9351e782a84b6a45e7f33b6695638c88e3931

COPY --from=builder /amdgpu-exporter /amdgpu-exporter

# Reading other containers' /proc/<pid>/fdinfo requires root on the host
# procfs. The pod drops all capabilities and runs read-only.
USER 0:0
EXPOSE 9494

ENTRYPOINT ["/amdgpu-exporter"]
