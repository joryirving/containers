# syntax=docker/dockerfile:1

FROM node:lts-slim
ARG TARGETARCH
ARG TARGETOS
ARG VERSION

WORKDIR /app

RUN apt-get update \
  && apt-get install -y --no-install-recommends ca-certificates curl \
  && curl -fsSL --create-dirs -o /app/src/epic_games.js https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/src/epic_games.js \
  && curl -fsSL -O https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/package.json \
  && curl -fsSL -O https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/package-lock.json \
  && rm -rf /var/lib/apt/lists/* \
  && npm ci

USER nobody:nogroup

COPY . /
CMD ["/entrypoint.sh"]
