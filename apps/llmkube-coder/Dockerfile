# syntax=docker/dockerfile:1

# Build stage: cross-compile the static foreman-agent from LLMKube source.
# CGO is disabled, so the binary runs on the Python/Node runtime below with no
# Go toolchain present. Pinned to $BUILDPLATFORM + GOOS/GOARCH so the compiler
# always runs natively (arm64 never pays QEMU's interpreted-compile cost).
FROM --platform=$BUILDPLATFORM golang:1.26-bookworm@sha256:fc4332778f8745404df530b4bdef3aed280b8c8da18847baffb4d4b9dd041046 AS build
ARG VERSION
ARG TARGETOS
ARG TARGETARCH
ENV CGO_ENABLED=0
WORKDIR /build
# Resolve VERSION to the module's version string so the stamped binary reports a
# real release (the FleetNode heartbeats main.Version; an empty stamp shows as
# "dev" in `kubectl get fleetnodes`). go list -m needs a module context.
RUN mkdir -p /out /tmp/vresolve \
    && ( cd /tmp/vresolve && go mod init coderbuild >/dev/null 2>&1 \
         && go list -m -f '{{.Version}}' "github.com/defilantech/llmkube@v${VERSION}" > /out/llmkube.version ) \
    && LLMKUBE_VERSION="$(cat /out/llmkube.version)" \
    && GOOS="${TARGETOS:-linux}" GOARCH="${TARGETARCH}" go install -trimpath \
         -ldflags="-s -w -X main.Version=${LLMKUBE_VERSION} -X main.GitCommit=v${VERSION}" \
         "github.com/defilantech/llmkube/cmd/foreman-agent@v${VERSION}" \
    && cp "$(find "$(go env GOPATH)/bin" -name foreman-agent -type f | head -1)" /out/foreman-agent \
    && test -x /out/foreman-agent

# Node source stage: the official Node 22 image on the same Debian base as the
# runtime, so the copied binary is ABI-compatible.
FROM node:24-bookworm-slim@sha256:cb4e8f7c443347358b7875e717c29e27bf9befc8f5a26cf18af3c3dec80e58c5 AS node

# Runtime: Python 3.14 + Node 22 (the languages this fleet's coder self-gate
# targets) + git + the linters the gate runs. No Go: the target repos are
# Python/Node and the agent binary is static.
FROM python:3.14-slim-bookworm@sha256:4ff4b92a68355dbdb52584ab3391dff8d371a61d4e063468bfd0130e3189c6d9

LABEL org.opencontainers.image.title="llmkube-coder" \
      org.opencontainers.image.description="LLMKube foreman coder agent (built from source) with a Python + Node self-gate toolchain" \
      org.opencontainers.image.source="https://github.com/defilantech/LLMKube" \
      org.opencontainers.image.licenses="Apache-2.0"

# git for the coder workspace; libstdc++6 is Node's only runtime dep beyond the
# python-slim base.
RUN apt-get update \
    && apt-get install -y --no-install-recommends git ca-certificates libstdc++6 \
    && rm -rf /var/lib/apt/lists/*

# Node 22 + npm from the official image.
COPY --from=node /usr/local/bin/node /usr/local/bin/node
COPY --from=node /usr/local/lib/node_modules /usr/local/lib/node_modules
RUN ln -sf /usr/local/lib/node_modules/npm/bin/npm-cli.js /usr/local/bin/npm \
    && ln -sf /usr/local/lib/node_modules/npm/bin/npx-cli.js /usr/local/bin/npx \
    && node --version && npm --version

# Python self-gate linters.
# renovate: datasource=pypi depName=ruff
ARG RUFF_VERSION=0.15.20
# renovate: datasource=pypi depName=black
ARG BLACK_VERSION=26.5.1
# renovate: datasource=pypi depName=flake8
ARG FLAKE8_VERSION=7.3.0
# renovate: datasource=pypi depName=yamllint
ARG YAMLLINT_VERSION=1.38.0
RUN pip install --no-cache-dir \
      "ruff==${RUFF_VERSION}" "black==${BLACK_VERSION}" \
      "flake8==${FLAKE8_VERSION}" "yamllint==${YAMLLINT_VERSION}"

# Node self-gate linters.
# renovate: datasource=npm depName=eslint
ARG ESLINT_VERSION=10.6.0
# renovate: datasource=npm depName=prisma
ARG PRISMA_VERSION=7.8.0
# renovate: datasource=npm depName=typescript
ARG TYPESCRIPT_VERSION=6.0.3
RUN npm install -g --no-fund --no-audit \
      "eslint@${ESLINT_VERSION}" "prisma@${PRISMA_VERSION}" "typescript@${TYPESCRIPT_VERSION}" \
    && rm -rf /root/.npm

# Read-only-rootfs friendly: all writable state under /tmp, and git operates on
# the workspace regardless of the (possibly pod-overridden) uid.
ENV HOME=/tmp \
    npm_config_cache=/tmp/.npm \
    PIP_CACHE_DIR=/tmp/.pip
RUN git config --system --add safe.directory '*'

COPY --from=build /out/foreman-agent /foreman-agent
RUN chmod 0755 /foreman-agent \
    && ln -sf /foreman-agent /usr/local/bin/foreman-agent

# nobody:nogroup (repo default). The foreman pod may override the uid; the image
# is uid-agnostic — all writable state lives in /tmp and the tools are
# world-executable.
USER 65534:65534
ENTRYPOINT ["/foreman-agent"]
