FROM node:lts-slim

ARG TARGETARCH
ARG TARGETOS
ARG VERSION

WORKDIR /app

RUN apt update \
  && apt install wget -y \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/src/epic_games.js -P /app/src \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/package.json \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/refs/tags/${VERSION}/bot/package-lock.json \
  && npm ci

USER nobody:nogroup

COPY . /
CMD ["/entrypoint.sh"]
