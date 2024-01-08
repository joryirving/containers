FROM ghcr.io/weaveworks/tf-runner:main-9ce782ce

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_CLI_VERSION=2023.1.0

USER root

RUN apk add --no-cache npm && npm i -g @bitwarden/cli@${BW_CLI_VERSION}

USER 65532:65532