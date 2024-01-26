FROM node:lts-slim as build

ARG TARGETPLATFORM
ARG TARGETARCH
ARG TARGETOS

LABEL dev.LilDrunkenSmurf.image.target_platform=$TARGETPLATFORM
LABEL dev.LilDrunkenSmurf.image.target_architecture=$TARGETARCH
LABEL dev.LilDrunkenSmurf.image.target_os=$TARGETOS
LABEL org.opencontainers.image.source="https://github.com/j6nca/free-game-notifier"

WORKDIR /app

RUN wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/src/epic_games.js -P /app/src \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/package.json -p /app \
  && wget https://raw.githubusercontent.com/j6nca/free-game-notifier/main/package-lock.json -p /app \
  && npm ci

COPY package*.json /app/
COPY node_modules /app/node_modules
COPY src /app/src

CMD ["npm run start"]
