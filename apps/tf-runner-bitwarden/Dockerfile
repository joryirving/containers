FROM ghcr.io/weaveworks/tf-runner:main-19027da5

# renovate: datasource=github-releases depName=@bitwarden/cli versioning=npm
ARG BW_CLI_VERSION=2023.1.0

USER root

RUN apk add --no-cache npm && npm i -g @bitwarden/cli@${BW_CLI_VERSION}

USER 65532:65532