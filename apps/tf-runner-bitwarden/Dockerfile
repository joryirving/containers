ARG VERSION=0.15.1
ARG TARGETPLATFORM

# renovate: datasource=github-releases depName=hashicorp/terraform versioning=docker
FROM hashicorp/terraform:1.6.6 as terraform

# renovate: datasource=github-releases depName=weaveworks/tf-runner versioning=docker
FROM ghcr.io/weaveworks/tf-runner:v${VERSION} as runner
USER root

# renovate: datasource=npm depName=@bitwarden/cli versioning=npm
ARG BW_VERSION=2024.1.0

RUN apk add --no-cache npm

RUN rm -rf ~/.node-gyp/ \
  && rm -r node_modules/.bin/; \
  && rm -r build/

RUN npm i -g node-gyp \
  && npm i -g node-pre-gyp \
  && npm i -g @bitwarden/cli@${BW_VERSION}

COPY --from=terraform --chown=65532:65532 /bin/terraform /usr/local/bin/terraform

USER 65532:65532
