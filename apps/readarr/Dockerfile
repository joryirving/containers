ARG VERSION
FROM docker.io/library/golang:1.22-alpine as envsubst
ARG VERSION
ARG TARGETOS
ARG TARGETARCH
ARG TARGETVARIANT=""
ARG TARGETPLATFORM
ENV CGO_ENABLED=0 \
    GOOS=${TARGETOS} \
    GOARCH=${TARGETARCH} \
    GOARM=${TARGETVARIANT}
RUN go install -ldflags="-s -w" github.com/drone/envsubst/cmd/envsubst@latest

FROM docker.io/library/alpine:3.20

ARG VERSION
ARG CHANNEL
ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/Readarr/Readarr"

ENV \
    COMPlus_EnableDiagnostics="0" \
    READARR__INSTANCE_NAME="Readarr" \
    READARR__BRANCH="${CHANNEL}" \
    READARR__PORT="8787" \
    READARR__ANALYTICS_ENABLED="False"

ENV UMASK="0002" \
    TZ="Etc/UTC"

USER root
WORKDIR /app

#hadolint ignore=DL3018,DL3059
RUN \
    apk add --no-cache \
        bash \
        ca-certificates \
        catatonit \
        curl \
        icu-libs \
        jq \
        libintl \
        nano \
        sqlite-libs \
        tzdata \
        xmlstarlet \
    && \
    case "${TARGETPLATFORM}" in \
        'linux/amd64') export ARCH='x64' ;; \
        'linux/arm64') export ARCH='arm64' ;; \
    esac \
    && \
    mkdir -p /app/bin \
    && \
    curl -fsSL "https://readarr.servarr.com/v1/update/${READARR__BRANCH}/updatefile?version=${VERSION}&os=linuxmusl&runtime=netcore&arch=${ARCH}" \
        | tar xzf - -C /app/bin --strip-components=1 \
    && \
    rm -rf /app/bin/Readarr.Update \
    && \
    printf "UpdateMethod=docker\nBranch=%s\nPackageVersion=%s\nPackageAuthor=[joryirving](https://github.com/joryirving)\n" "${READARR__BRANCH}" "${VERSION}" > /app/package_info \
    && chown -R root:root /app \
    && chmod -R 755 /app \
    && rm -rf /tmp/*

COPY ./config.xml.tmpl /app/config.xml.tmpl
COPY ./entrypoint.sh /entrypoint.sh
COPY --from=envsubst /go/bin/envsubst /usr/local/bin/envsubst

USER nobody:nogroup
WORKDIR /config
VOLUME ["/config"]

ENTRYPOINT ["/usr/bin/catatonit", "--"]
CMD ["/entrypoint.sh"]
