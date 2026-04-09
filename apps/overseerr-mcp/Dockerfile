# syntax=docker/dockerfile:1

FROM docker.io/library/node:22-alpine

ARG TARGETARCH
ARG VERSION

ENV NODE_ENV=production

WORKDIR /app

RUN npm install -g @jhomen368/overseerr-mcp@${VERSION}

USER nobody
EXPOSE 8085

CMD ["node", "/usr/local/bin/overseerr-mcp"]
