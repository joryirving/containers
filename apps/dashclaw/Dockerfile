# syntax=docker/dockerfile:1

# Dependencies
FROM node:24-alpine AS deps

ARG VERSION
ARG SOURCE
ARG VENDOR

RUN apk add --no-cache git && \
    git clone --depth 1 --branch ${VERSION} ${SOURCE} /build/source

WORKDIR /build/source

RUN npm install

# Builder
FROM node:24-alpine AS builder

ARG VERSION
ARG SOURCE
ARG VENDOR
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1
COPY --from=deps /build/source /app
COPY . /build/source/app/lib/
RUN npm run build

# Runner
FROM node:24-alpine AS runner

WORKDIR /app

ENV NODE_ENV=production
ENV NEXT_TELEMETRY_DISABLED=1
ENV PORT=3000
ENV HOSTNAME=0.0.0.0

RUN addgroup --system --gid 1001 nodejs && \
    adduser --system --uid 1001 nextjs

# Copy built app, required files, AND node_modules for npm start
COPY --from=builder /app/.next ./.next
COPY --from=builder /app/public ./public
COPY --from=builder /app/package.json ./package.json
COPY --from=builder /app/next.config.js ./next.config.js
COPY --from=builder /app/node_modules ./node_modules

# Copy scripts and drizzle config from source (deps stage)
COPY --from=deps /build/source/scripts ./scripts
COPY --from=deps /build/source/drizzle.config.* ./
COPY --from=deps /build/source/drizzle ./drizzle

# Fix permissions for nextjs user to write to cache
RUN chown -R nextjs:nodejs /app/.next

USER nextjs
EXPOSE 3000

CMD ["npm", "start"]
