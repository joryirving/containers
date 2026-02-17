# syntax=docker/dockerfile:1

# Dependencies
FROM node:20-alpine AS deps

ARG VERSION
ARG SOURCE

WORKDIR /build

RUN apk add --no-cache git && \
    git clone --depth 1 --branch ${VERSION} ${SOURCE} /build/source

WORKDIR /build/source
RUN npm install

# Builder
FROM node:20-alpine AS builder

ARG VERSION
ARG SOURCE
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /build/source /app
RUN npm run build

# Runner
FROM node:20-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 dashclaw

COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./

USER dashclaw
EXPOSE 3000

CMD ["npm", "start"]
