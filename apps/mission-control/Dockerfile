# syntax=docker/dockerfile:1

FROM node:24-slim AS base
WORKDIR /app

FROM base AS deps
ARG VERSION
ARG SOURCE

RUN apt-get update \
    && apt-get install -y --no-install-recommends ca-certificates git python3 make g++ \
    && rm -rf /var/lib/apt/lists/*

RUN git clone --depth 1 --branch ${VERSION} ${SOURCE} /build/source
WORKDIR /build/source
RUN corepack enable \
    && corepack prepare pnpm@10.23.0 --activate \
    && pnpm install --frozen-lockfile

FROM base AS build
COPY --from=deps /build/source /app
RUN corepack enable \
    && corepack prepare pnpm@10.23.0 --activate \
    && pnpm build

FROM node:24-slim AS runner
WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN apt-get update \
    && apt-get install -y --no-install-recommends curl \
    && rm -rf /var/lib/apt/lists/*

COPY --from=build /app/.next/standalone ./
COPY --from=build /app/.next/static ./.next/static
COPY --from=build /app/src/lib/schema.sql ./src/lib/schema.sql

RUN mkdir -p /app/.data \
    && chown -R nobody:nogroup /app

USER nobody:nogroup
EXPOSE 3000

HEALTHCHECK --interval=30s --timeout=5s --start-period=10s --retries=3 \
  CMD curl -f http://127.0.0.1:${PORT:-3000}/login || exit 1

CMD ["node", "server.js"]
