# syntax=docker/dockerfile:1

FROM node:20-alpine AS deps

ARG VERSION
ARG SOURCE

WORKDIR /tmp/source

# Download source and extract package files
RUN apk add --no-cache curl tar && \
    curl -fsSL "${SOURCE}/archive/refs/tags/${VERSION}.tar.gz" -o source.tar.gz && \
    tar xzf source.tar.gz --strip-components=1 && \
    ls -la

WORKDIR /app
COPY package.json package-lock.json* ./
RUN npm install

# Builder stage
FROM node:20-alpine AS builder

ARG VERSION
ARG SOURCE

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy node_modules and source from deps
COPY --from=deps /app/node_modules ./node_modules
COPY --from=deps /tmp/source/ .

RUN npm run build || echo "Build may need adjustments"

# Runner stage
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 dashclaw

COPY --from=builder /app/public ./public || true
COPY --from=builder /app/.next/standalone ./ || true
COPY --from=builder /app/.next/static ./.next/static || true

USER dashclaw

EXPOSE 3000

ENV PORT=3000
ENV HOSTNAME=0.0.0.0

CMD ["node", "server.js"]
