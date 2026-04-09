# syntax=docker/dockerfile:1

FROM docker.io/library/node:22-alpine

ARG TARGETARCH
ARG VERSION=rolling

ENV NODE_ENV=production \
    NPM_CONFIG_UPDATE=@jhomen368/overseerr-mcp@latest

WORKDIR /app

RUN npm install -g @jhomen368/overseerr-mcp

USER nobody
EXPOSE 8085

CMD ["node", "/usr/local/bin/overseerr-mcp"]
