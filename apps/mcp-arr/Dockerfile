# syntax=docker/dockerfile:1

FROM docker.io/library/node:22-alpine

ARG TARGETARCH
ARG VERSION

ENV NODE_ENV=production

WORKDIR /app

RUN npm install -g mcp-arr-server@${VERSION}

USER nobody

CMD ["node", "/usr/local/bin/mcp-arr-server"]
