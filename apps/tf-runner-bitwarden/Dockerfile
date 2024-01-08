FROM hashicorp/terraform:1.5.4 as tf
FROM ghcr.io/weaveworks/tf-runner:main-9ce782ce

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_CLI_VERSION=2023.12.1

USER root

RUN apk add --no-cache npm && npm i -g @bitwarden/cli@${BW_CLI_VERSION}

COPY --from=tf /bin/terraform /usr/local/bin/terraform

USER 65532:65532