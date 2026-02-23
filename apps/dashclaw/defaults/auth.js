import GitHubProvider from 'next-auth/providers/github';
import GoogleProvider from 'next-auth/providers/google';
import crypto from 'crypto';
import { getSql } from './db.js';

// SECURITY: In production, require real OAuth credentials — do not fall through to mocks
const isProd = process.env.NODE_ENV === 'production';

const GITHUB_ID = process.env.GITHUB_ID || process.env.GITHUB_CLIENT_ID;
const GITHUB_SECRET = process.env.GITHUB_SECRET || process.env.GITHUB_CLIENT_SECRET;
const GOOGLE_ID = process.env.GOOGLE_ID || process.env.GOOGLE_CLIENT_ID;
const GOOGLE_SECRET = process.env.GOOGLE_SECRET || process.env.GOOGLE_CLIENT_SECRET;

const hasGitHub = GITHUB_ID && GITHUB_SECRET;
const hasGoogle = GOOGLE_ID && GOOGLE_SECRET;
const hasOIDC = process.env.OIDC_CLIENT_ID && process.env.OIDC_CLIENT_SECRET && process.env.OIDC_ISSUER_URL;

if (isProd && !hasGitHub && !hasGoogle && !hasOIDC) {
  console.error('[AUTH] FATAL: At least one authentication provider (GitHub, Google, or OIDC) must be configured in production');
}

const providers = [];
if (hasGitHub) {
  providers.push(GitHubProvider({
    clientId: GITHUB_ID,
    clientSecret: GITHUB_SECRET,
  }));
} else if (!isProd) {
  providers.push(GitHubProvider({
    clientId: 'mock_github_id',
    clientSecret: 'mock_github_secret',
  }));
}

if (hasGoogle) {
  providers.push(GoogleProvider({
    clientId: GOOGLE_ID,
    clientSecret: GOOGLE_SECRET,
  }));
} else if (!isProd) {
  providers.push(GoogleProvider({
    clientId: 'mock_google_id',
    clientSecret: 'mock_google_secret',
  }));
}

if (hasOIDC) {
  // Support explicit OIDC endpoints for providers like Authentik
  // that use global endpoints different from the issuer path
  const oidcConfig = {
    id: 'oidc',
    name: process.env.OIDC_DISPLAY_NAME || 'OIDC',
    type: 'oidc',
    issuer: process.env.OIDC_ISSUER_URL,
    clientId: process.env.OIDC_CLIENT_ID,
    clientSecret: process.env.OIDC_CLIENT_SECRET,
    authorization: { params: { scope: 'openid email profile' } },
  };
  
  // Add explicit endpoints if provided (for Authentik compatibility)
  if (process.env.OIDC_AUTHORIZATION_URL) {
    oidcConfig.authorization = { 
      url: process.env.OIDC_AUTHORIZATION_URL,
      params: { scope: 'openid email profile' }
    };
  }
  if (process.env.OIDC_TOKEN_URL) {
    oidcConfig.token = process.env.OIDC_TOKEN_URL;
  }
  if (process.env.OIDC_USERINFO_URL) {
    oidcConfig.userinfo = process.env.OIDC_USERINFO_URL;
  }
  
  providers.push(oidcConfig);
}

export const authOptions = {
  providers,
  session: { strategy: 'jwt' },
  pages: { signIn: '/login' },
  callbacks: {
    async signIn({ user, account }) {
      try {
        const sql = getSql();
        // If mock driver, skip logic
        if (!process.env.DATABASE_URL) return true;

        const now = new Date().toISOString();

        // Upsert user on every login
        const existing = await sql`
          SELECT id, org_id, role FROM users
          WHERE provider = ${account.provider}
            AND provider_account_id = ${account.providerAccountId}
          LIMIT 1
        `;

        if (existing.length > 0) {
          // Update last login + profile info
          await sql`
            UPDATE users
            SET last_login_at = ${now},
                name = ${user.name || null},
                image = ${user.image || null},
                email = ${user.email || ''}
            WHERE id = ${existing[0].id}
          `;
        } else {
          // Create new user mapped to org_default
          const userId = `usr_${crypto.randomUUID()}`;
          await sql`
            INSERT INTO users (id, org_id, email, name, image, provider, provider_account_id, role, created_at, last_login_at)
            VALUES (${userId}, 'org_default', ${user.email || ''}, ${user.name || null}, ${user.image || null}, ${account.provider}, ${account.providerAccountId}, 'member', ${now}, ${now})
          `;
        }
        return true;
      } catch (err) {
        console.error('[AUTH] signIn callback error:', err.message);
        // Allow sign-in even if DB upsert fails (graceful degradation)
        return true;
      }
    },

    async jwt({ token, account }) {
      // On initial sign-in, attach org info from DB
      if (account) {
        try {
          if (!process.env.DATABASE_URL) throw new Error('No DB');
          
          const sql = getSql();
          const rows = await sql`
            SELECT u.id, u.org_id, u.role, COALESCE(o.plan, 'free') AS plan
            FROM users u
            LEFT JOIN organizations o ON o.id = u.org_id
            WHERE u.provider = ${account.provider}
              AND u.provider_account_id = ${account.providerAccountId}
            LIMIT 1
          `;
          if (rows.length > 0) {
            token.userId = rows[0].id;
            token.orgId = rows[0].org_id;
            token.role = rows[0].role;
            token.plan = rows[0].plan;
          } else {
            token.orgId = 'org_default';
            token.role = 'member';
            token.plan = 'free';
          }
        } catch (err) {
          if (err.message !== 'No DB') console.error('[AUTH] jwt callback error:', err.message);
          token.orgId = 'org_default';
          token.role = 'member';
          token.plan = 'free';
        }
        token.orgRefreshedAt = Date.now();
      } else if (token.userId) {
        // Periodically re-query user's org so session picks up changes (e.g. after workspace creation)
        const age = Date.now() - (token.orgRefreshedAt || 0);
        if (age > 5 * 60 * 1000) {
          try {
            if (!process.env.DATABASE_URL) throw new Error('No DB');
            const sql = getSql();
            const rows = await sql`
              SELECT u.org_id, u.role, COALESCE(o.plan, 'free') AS plan
              FROM users u
              LEFT JOIN organizations o ON o.id = u.org_id
              WHERE u.id = ${token.userId} LIMIT 1
            `;
            if (rows.length > 0) {
              token.orgId = rows[0].org_id;
              token.role = rows[0].role;
              token.plan = rows[0].plan;
            }
          } catch (err) {
             if (err.message !== 'No DB') console.error('[AUTH] jwt refresh error:', err.message);
          }
          token.orgRefreshedAt = Date.now();
        }
      }
      return token;
    },


    async session({ session, token }) {
      session.user.id = token.userId || null;
      session.user.orgId = token.orgId || 'org_default';
      session.user.role = token.role || 'member';
      session.user.plan = token.plan || 'free';
      return session;
    },
  },
};
