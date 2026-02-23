# syntax=docker/dockerfile:1

# Dependencies
FROM node:24-alpine AS deps

ARG VERSION
ARG SOURCE
ARG VENDOR

RUN apk add --no-cache git && \
    git clone --depth 1 --branch ${VERSION} ${SOURCE} /build/source

WORKDIR /build/source

# Apply OIDC patch for Authentik compatibility
# Patch auth.js to support explicit OIDC endpoints
RUN cat > /tmp/oidc.patch << 'PATCH_EOF'
--- a/app/lib/auth.js
+++ b/app/lib/auth.js
@@ -32,11 +32,23 @@ if (hasGoogle) {
 }
 
 if (hasOIDC) {
+  // Support explicit OIDC endpoints for providers like Authentik
+  // that use global endpoints different from the issuer path
+  const authorizationUrl = process.env.OIDC_AUTHORIZATION_URL;
+  const tokenUrl = process.env.OIDC_TOKEN_URL;
+  const userinfoUrl = process.env.OIDC_USERINFO_URL;
+  
   providers.push({
     id: 'oidc',
     name: process.env.OIDC_DISPLAY_NAME || 'OIDC',
     type: 'oidc',
     issuer: process.env.OIDC_ISSUER_URL,
     clientId: process.env.OIDC_CLIENT_ID,
     clientSecret: process.env.OIDC_CLIENT_SECRET,
-    authorization: { params: { scope: 'openid email profile' } },
+    authorization: { 
+      url: authorizationUrl,
+      params: { scope: 'openid email profile' }
+    },
+    token: tokenUrl,
+    userinfo: userinfoUrl,
   });
 }
PATCH_EOF
RUN git apply /tmp/oidc.patch || echo "Patch already applied or not needed"

RUN npm install

# Builder
FROM node:24-alpine AS builder

ARG VERSION
ARG SOURCE
ARG VENDOR
WORKDIR /app

ENV NEXT_TELEMETRY_DISABLED=1

COPY --from=deps /build/source /app
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

# Fix permissions for nextjs user to write to cache
RUN chown -R nextjs:nodejs /app/.next

USER nextjs
EXPOSE 3000

CMD ["npm", "start"]
