# syntax=docker/dockerfile:1

FROM docker.io/library/node:22-alpine

ARG TARGETARCH
ARG VERSION

ENV NODE_ENV=production

WORKDIR /app

RUN npm install -g @modelcontextprotocol/server-memory@${VERSION}

USER nobody
EXPOSE 3000

CMD ["node", "/usr/local/bin/mcp-server-memory"]
