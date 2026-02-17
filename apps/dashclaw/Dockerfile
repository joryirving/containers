# syntax=docker/dockerfile:1

# Stage 1: Dependencies - download source here
FROM node:20-alpine AS deps

ARG VERSION
ARG SOURCE

WORKDIR /build

# Download and extract full source
RUN apk add --no-cache git && \
    git clone --depth 1 --branch ${VERSION} ${SOURCE} /build/source

WORKDIR /build/source
RUN npm install

# Stage 2: Builder
FROM node:20-alpine AS builder

ARG VERSION
ARG SOURCE

WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

# Copy from deps stage
COPY --from=deps /build/source /app

RUN npm run build

# Stage 3: Runner  
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
