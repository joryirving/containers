# syntax=docker/dockerfile:1
# Add portable skills without changing the pinned upstream Courier executor.
ARG VERSION=0.1.12
FROM ghcr.io/misospace/courier-opencode:${VERSION}

COPY --chown=65532:65532 agent-skills/simple-english /home/courier/.agents/skills/simple-english
