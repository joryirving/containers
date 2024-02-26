FROM node:lts-slim

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.joryirving.image.target_platform=$TARGETPLATFORM
LABEL dev.joryirving.image.target_architecture=$TARGETARCH
LABEL dev.joryirving.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/j6nca/free-game-notifier"

WORKDIR /app

RUN apt update \
  && apt install wget -y \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/src/epic_games.js -P /app/src \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/package.json \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/package-lock.json \
  && npm ci

COPY ./entrypoint.sh /entrypoint.sh
CMD ["/entrypoint.sh"]
