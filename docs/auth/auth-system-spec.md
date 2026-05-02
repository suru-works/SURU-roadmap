# SURUworks — Centralized Auth System Specification

> Especificación técnica del sistema de autenticación y gestión de usuarios.
> Sistema custom (no Auth0, no Keycloak) construido con Java + Spring Security.

---

## 1. Technology Stack Decision

### Recommendation: Java 21 + Spring Boot 3.4 + Spring Authorization Server 1.4+

**Reasoning:**

| Criterion | Java/Spring | Node.js + custom JWT | Go + custom JWT |
|---|---|---|---|
| Team expertise | ✅ Native | ❌ New stack | ❌ New stack |
| OAuth2/OIDC compliance | ✅ Spring Authorization Server (RFC compliant) | ⚠️ Manual implementation | ⚠️ Manual implementation |
| Ecosystem maturity | ✅ Largest | Good | Growing |
| Future extensibility | ✅ SAML, enterprise SSO ready | Rebuild needed | Rebuild needed |
| Spring ecosystem integration | ✅ Native | ❌ None | ❌ None |

**Why custom over Keycloak:**
- Keycloak runs a full Java EE container — minimum 512MB RAM, complex admin console
- For a startup, Keycloak's operational overhead exceeds its benefit
- Custom auth gives full control over token claims, UX flows, and data model
- Custom built on Spring Authorization Server IS RFC-compliant OAuth2/OIDC — not reinventing the wheel

**When to migrate to managed auth (Keycloak/Auth0):**
- Team grows to 5+ engineers AND auth becomes a maintenance burden
- Enterprise SSO (SAML 2.0, LDAP) requirements appear
- Compliance requirements (SOC2, ISO27001) where managed vendors simplify audits

---

## 2. Token Strategy

### Access Token: JWT (RS256)

**Why RS256 over HS256 for microservices:**

| | RS256 (Asymmetric) | HS256 (Symmetric) |
|---|---|---|
| Signing | Private key (auth service only) | Shared secret (all services) |
| Verification | Public key (any service, no call needed) | Shared secret (risky to distribute) |
| Key compromise | Only private key is sensitive | Shared secret exposure compromises all services |
| Key rotation | Publish new public key via JWKS | Must update all services simultaneously |

With RS256: any microservice validates tokens independently using the public key from the JWKS endpoint. No network call to auth service per request. The private key never leaves the auth service.

**Access token TTL: 15 minutes**

Rationale: Short enough to limit damage if stolen; long enough to not degrade UX (a 15-minute sliding window means most active users never see a re-login prompt if refresh is working correctly).

**JWT payload structure:**

```json
{
  "iss": "https://suruworks.com",
  "sub": "usr_01HXYZ123456",
  "email": "user@example.com",
  "email_verified": true,
  "name": "Santiago Quiroz",
  "roles": ["USER"],
  "plan": "free",
  "iat": 1746144000,
  "exp": 1746144900,
  "jti": "tok_01HXYZ789ABC"
}
```

**Minimal claims philosophy:** Only include what downstream services need to function. Do not put UI preferences, extended profile, or billing details in the JWT — those are fetched from their respective services.

### Refresh Token: Opaque + Redis

**Type:** Opaque (random UUID stored server-side in Redis)

**Why not JWT refresh tokens:**
- JWT refresh tokens cannot be revoked without a distributed blacklist
- Opaque tokens can be instantly invalidated by deleting from Redis
- Opaque tokens contain no information — if intercepted they reveal nothing

**Refresh token TTL:** 30 days (sliding window — extended on each use)

**Rotation strategy:** Single-use rotation
- Each `/auth/refresh` call issues a NEW refresh token and invalidates the old one
- Redis: `SET rt:{jti} {user_id} EX 2592000`
- If a refresh token is used twice, it indicates token theft → revoke all user sessions

**JWKS Endpoint:**

```
GET /auth/.well-known/jwks.json
```

Response: RSA public key in JWK Set format. All microservices download and cache this on startup. Cache TTL: 24 hours, with async refresh.

### Token Revocation Strategy

**Access tokens (15 min TTL):** Short TTL is the primary defense. Do not blacklist access tokens on each request (Redis call per API call = unacceptable latency).

**Exception: force-logout.** On explicit logout or account suspension: add the JTI to Redis blacklist with TTL = access token remaining lifetime.

```
Redis key: bl:tok:{jti}
Redis value: "1"
Redis TTL: (access token expiry - now) seconds
```

Microservices check this blacklist only for operations requiring strong security guarantees (e.g., payment, admin actions). Normal read operations do not check the blacklist.

---

## 3. Password Security

### Algorithm: Argon2id

**Decision: Argon2id over bcrypt and scrypt**

| | Argon2id | bcrypt | scrypt |
|---|---|---|---|
| Year | 2015 (PHC winner) | 1999 | 2009 |
| Memory-hard | ✅ Both time and memory | ❌ Time only | ✅ Memory |
| Side-channel resistance | ✅ Best (id variant) | Good | Good |
| Spring Security support | ✅ Native | ✅ Native | ✅ Native |

**Recommended parameters (2025 OWASP):**
- `m = 19456` (19 MiB memory)
- `t = 2` (2 iterations)
- `p = 1` (1 thread)
- Output: 32 bytes

Spring Security implementation:
```java
PasswordEncoder encoder = new Argon2PasswordEncoder(
    16,     // salt length
    32,     // hash length
    1,      // parallelism
    19456,  // memory
    2       // iterations
);
```

### Password Policy

- Minimum 8 characters
- No maximum length cap (hash the password, not the length)
- Must not be in HIBP breach database (checked asynchronously on registration)
- Common passwords blocked via local wordlist (top 10K most common)
- No forced periodic resets (NIST SP 800-63B guidance)

### Brute Force Protection

```
Rate limits (per IP):
- /auth/login: 10 attempts per 15 minutes → 429 Too Many Requests
- /auth/forgot-password: 3 requests per hour

Account lockout (per user):
- 5 failed attempts → progressive delay (CAPTCHA prompt)
- 10 failed attempts → account locked for 30 minutes (auto-unlock)
- Send security email on lockout

Implementation: Redis counters with TTL
  login_attempts:{ip}    INCR + EXPIRE 900
  login_attempts:{email} INCR + EXPIRE 900
```

### Breach Detection

```java
// Asynchronous HIBP check on registration and password change
@Async
public CompletableFuture<Boolean> isPasswordBreached(String password) {
    String sha1 = sha1(password).toUpperCase();
    String prefix = sha1.substring(0, 5);
    String suffix = sha1.substring(5);
    
    // k-Anonymity: only send first 5 chars of SHA1
    HttpResponse response = hibpClient.get("/range/" + prefix);
    return response.body().contains(suffix);
}
```

If breached: prompt user to choose a different password with clear explanation. Do not silently reject.

---

## 4. Database Schema

### PostgreSQL Schema

```sql
-- ────────────────────────────────────────────────────────
-- Users table: identity source of truth
-- ────────────────────────────────────────────────────────
CREATE TABLE users (
    id              VARCHAR(26) PRIMARY KEY,           -- ULID: usr_01HXYZ...
    email           VARCHAR(255) UNIQUE NOT NULL,
    email_verified  BOOLEAN NOT NULL DEFAULT FALSE,
    password_hash   TEXT,                              -- NULL for OAuth-only users
    name            VARCHAR(255),
    avatar_url      TEXT,
    plan            VARCHAR(20) NOT NULL DEFAULT 'free',
    status          VARCHAR(20) NOT NULL DEFAULT 'active', -- active|suspended|deleted
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at      TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────
-- Roles table: role definitions
-- ────────────────────────────────────────────────────────
CREATE TABLE roles (
    id    SERIAL PRIMARY KEY,
    name  VARCHAR(50) UNIQUE NOT NULL  -- USER, ADMIN, SERVICE
);

INSERT INTO roles (name) VALUES ('USER'), ('ADMIN'), ('SERVICE');

-- ────────────────────────────────────────────────────────
-- User roles: many-to-many
-- ────────────────────────────────────────────────────────
CREATE TABLE user_roles (
    user_id VARCHAR(26) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    role_id INTEGER    NOT NULL REFERENCES roles(id),
    PRIMARY KEY (user_id, role_id)
);

-- ────────────────────────────────────────────────────────
-- OAuth accounts: social login connections
-- ────────────────────────────────────────────────────────
CREATE TABLE oauth_accounts (
    id              VARCHAR(26) PRIMARY KEY,
    user_id         VARCHAR(26) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    provider        VARCHAR(20) NOT NULL,              -- google, github
    provider_user_id VARCHAR(255) NOT NULL,
    access_token    TEXT,
    refresh_token   TEXT,
    expires_at      TIMESTAMPTZ,
    created_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    UNIQUE (provider, provider_user_id)
);

-- ────────────────────────────────────────────────────────
-- Email verifications
-- ────────────────────────────────────────────────────────
CREATE TABLE email_verifications (
    id          VARCHAR(26) PRIMARY KEY,
    user_id     VARCHAR(26) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token       VARCHAR(64) UNIQUE NOT NULL,           -- cryptographically random
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────
-- Password reset tokens
-- ────────────────────────────────────────────────────────
CREATE TABLE password_reset_tokens (
    id          VARCHAR(26) PRIMARY KEY,
    user_id     VARCHAR(26) NOT NULL REFERENCES users(id) ON DELETE CASCADE,
    token_hash  VARCHAR(64) UNIQUE NOT NULL,           -- hashed with SHA-256
    expires_at  TIMESTAMPTZ NOT NULL,
    used_at     TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- ────────────────────────────────────────────────────────
-- Audit log: immutable security log
-- ────────────────────────────────────────────────────────
CREATE TABLE auth_audit_log (
    id          BIGSERIAL PRIMARY KEY,
    user_id     VARCHAR(26),                           -- NULL for anonymous events
    event_type  VARCHAR(50) NOT NULL,                  -- LOGIN, LOGOUT, REGISTER, etc.
    ip_address  INET,
    user_agent  TEXT,
    metadata    JSONB,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX idx_audit_user_id ON auth_audit_log(user_id);
CREATE INDEX idx_audit_created_at ON auth_audit_log(created_at);

-- ────────────────────────────────────────────────────────
-- API keys: service-to-service auth
-- ────────────────────────────────────────────────────────
CREATE TABLE api_keys (
    id          VARCHAR(26) PRIMARY KEY,
    name        VARCHAR(100) NOT NULL,
    key_hash    VARCHAR(64) UNIQUE NOT NULL,           -- SHA-256 of the raw key
    key_prefix  VARCHAR(8) NOT NULL,                   -- first 8 chars for display
    service_id  VARCHAR(26) REFERENCES users(id),      -- NULL = not tied to user
    scopes      TEXT[],                               -- e.g. {read:projects, write:jobs}
    expires_at  TIMESTAMPTZ,
    last_used_at TIMESTAMPTZ,
    revoked_at  TIMESTAMPTZ,
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);
```

---

## 5. Email System

### Provider: Resend

**Decision: Resend (resend.com)**

| Provider | Free tier | Deliverability | API quality | LATAM servers |
|---|---|---|---|---|
| **Resend** ← recommended | 3,000/month | Excellent | ⭐⭐⭐⭐⭐ | Good |
| SendGrid | 100/day | Good | ⭐⭐⭐⭐ | Good |
| Postmark | 100/month | Excellent | ⭐⭐⭐⭐ | Limited |
| AWS SES | 62K/month (EC2) | Good | ⭐⭐⭐ | Requires setup |

Resend has the cleanest API, first-class React/HTML email support, and the best developer experience. 3,000 free emails per month is sufficient for MVP.

### Transactional Emails Needed

| Event | Subject | Trigger |
|---|---|---|
| Registration | "Bienvenido a SURUworks — confirma tu email" | POST /auth/register |
| Email verification | "Confirma tu dirección de email" | POST /auth/verify-email/send |
| Password reset | "Restablece tu contraseña" | POST /auth/forgot-password |
| Password changed | "Tu contraseña fue cambiada" | POST /auth/reset-password (success) |
| Account locked | "Actividad inusual en tu cuenta" | After 10 failed login attempts |
| New device login | "Nuevo inicio de sesión detectado" | Login from new IP/device (Phase 2) |
| Welcome email | "¡Ya tienes cuenta en SURUworks!" | 24h after email verified |

### Email Verification Flow

```
1. User registers → account created with email_verified = false
2. Auth Service creates email_verification record (token, expires_at = NOW() + 24h)
3. Email Service sends verification email with link:
   https://suruworks.com/auth/verify-email?token={token}
4. User clicks link
5. Auth Service: finds token, checks not expired, not used
6. Updates users.email_verified = true
7. Marks email_verification.used_at = NOW()
8. Redirects to /dashboard with success toast
9. Triggers user.registered NATS event → other services
```

---

## 6. Service-to-Service Auth

### Pattern: API Keys (not mTLS, not client credentials for now)

**Why not mTLS at startup:**
- Requires certificate management, CA setup, cert rotation
- Docker Compose internal networking is trusted — mTLS adds ops overhead with no additional security benefit within the same Docker network

**Why not OAuth2 Client Credentials:**
- Adds a token exchange call per service start
- Overkill for Docker Compose internal traffic

**API Key pattern:**
```
Format: sw_{environment}_{random}
Example: sw_prod_01HXYZ1234567890ABCDEFGH

Storage:
  - Raw key shown once to admin
  - Hash: key_hash = SHA-256(rawKey)
  - Prefix: key_prefix = rawKey.substring(0, 8) (for display/identification)

Validation:
  Service sends: Authorization: ApiKey sw_prod_01HXYZ...
  Auth Service: SHA-256(receivedKey) → compare to stored hash
  Response: { valid: true, scopes: ["read:projects", ...], service: "image3d" }
```

**Cache validation responses in Redis** — 60 second TTL. Avoids DB call on every inter-service request.

**Migration to mTLS:** When moving to Kubernetes, Istio service mesh handles mTLS automatically. At that point, API keys can be retired for service-to-service traffic; OAuth2 client credentials can be used for structured authorization.

---

## 7. Security Hardening

### CORS Configuration

```java
@Bean
public CorsConfigurationSource corsConfigurationSource() {
    CorsConfiguration config = new CorsConfiguration();
    config.setAllowedOrigins(List.of(
        "https://suruworks.com",
        "https://app.suruworks.com",
        "https://admin.suruworks.com"
    ));
    config.setAllowedMethods(List.of("GET", "POST", "PUT", "DELETE", "OPTIONS"));
    config.setAllowedHeaders(List.of("Authorization", "Content-Type", "X-Request-ID"));
    config.setAllowCredentials(true);         // for cookie-based refresh tokens
    config.setMaxAge(3600L);

    UrlBasedCorsConfigurationSource source = new UrlBasedCorsConfigurationSource();
    source.registerCorsConfiguration("/auth/**", config);
    return source;
}
```

In development: add `http://localhost:3000`, `http://localhost:5173` to allowed origins.

### Security Headers

```java
http.headers(headers -> headers
    .xssProtection(xss -> xss.enable(true))
    .contentSecurityPolicy(csp -> csp.policyDirectives(
        "default-src 'self'; " +
        "script-src 'self'; " +
        "style-src 'self' 'unsafe-inline' fonts.googleapis.com; " +
        "font-src 'self' fonts.gstatic.com; " +
        "img-src 'self' data: https:; " +
        "connect-src 'self'"
    ))
    .frameOptions(frame -> frame.deny())
    .httpStrictTransportSecurity(hsts -> hsts
        .maxAgeInSeconds(31536000)
        .includeSubDomains(true)
    )
);
```

### CSRF

CSRF protection is only relevant for cookie-based sessions. Since auth uses bearer tokens (JWT in `Authorization` header), CSRF is not a risk for API calls. However, if using HttpOnly cookies for the refresh token (recommended for XSS protection):
- Issue: refresh token in HttpOnly cookie → CSRF vulnerability on `/auth/refresh`
- Solution: `SameSite=Strict` on the refresh token cookie + additional CSRF token for the refresh endpoint only

### Rate Limiting

Implemented at Traefik level (no need for Spring middleware):

```yaml
# traefik dynamic config
http:
  middlewares:
    rate-limit-auth:
      rateLimit:
        average: 10      # 10 requests per second
        burst: 20        # burst of 20 allowed
        period: 1s
    rate-limit-login:
      rateLimit:
        average: 1       # 1 request per second per IP
        burst: 5
```

Additional per-user rate limiting implemented in Spring for the login endpoint (using Redis counters as described in section 3).

---

## 8. API Surface

### Complete Endpoint Reference

```
POST   /auth/register
  Body: { email, password, name }
  Response: 201 { userId, email, message: "Check your email to verify your account" }
  Errors: 409 email already exists, 400 validation

POST   /auth/login
  Body: { email, password }
  Response: 200 { accessToken, expiresIn: 900, refreshToken (HttpOnly cookie) }
  Errors: 401 invalid credentials, 403 email not verified, 423 account locked

POST   /auth/logout
  Headers: Authorization: Bearer {accessToken}
  Response: 204
  Action: invalidates refresh token + adds JTI to blacklist

POST   /auth/refresh
  Cookie: refreshToken
  Response: 200 { accessToken, expiresIn: 900, new refreshToken (HttpOnly cookie) }
  Errors: 401 invalid/expired refresh token

POST   /auth/verify-email/send
  Body: { email }
  Response: 200 { message: "Verification email sent" }
  Rate limit: 3 per hour per email

GET    /auth/verify-email?token={token}
  Response: 302 redirect to /dashboard (success) or /auth/verify-email?error=expired

POST   /auth/forgot-password
  Body: { email }
  Response: 200 { message: "If that email exists, a reset link was sent" }  (always 200 to prevent email enumeration)
  Rate limit: 3 per hour per IP

POST   /auth/reset-password
  Body: { token, newPassword }
  Response: 200 { message: "Password updated successfully" }
  Errors: 400 token expired/invalid, 400 password too weak

GET    /auth/me
  Headers: Authorization: Bearer {accessToken}
  Response: 200 { id, email, name, roles, emailVerified, plan }

PUT    /auth/me/password
  Headers: Authorization: Bearer {accessToken}
  Body: { currentPassword, newPassword }
  Response: 200 + invalidates all sessions

GET    /.well-known/jwks.json
  Response: 200 { keys: [{ kty, use, kid, alg, n, e }] }
  Cache-Control: max-age=86400

# Admin endpoints (ROLE_ADMIN required)
GET    /auth/admin/users
GET    /auth/admin/users/{id}
PUT    /auth/admin/users/{id}/status
GET    /auth/admin/audit-log

# Service endpoints (API Key required)
POST   /auth/internal/validate-token
  Body: { token }
  Response: 200 { valid, userId, email, roles } or 401
```

---

## 9. Key Code Snippets

### JWT Generation (Spring Boot)

```java
@Service
public class JwtService {

    private final RSAPrivateKey privateKey;
    private final RSAPublicKey publicKey;
    private final String issuer = "https://suruworks.com";

    public String generateAccessToken(User user) {
        Instant now = Instant.now();
        List<String> roles = user.getRoles().stream()
            .map(Role::getName)
            .toList();

        return JWT.create()
            .withIssuer(issuer)
            .withSubject(user.getId())
            .withClaim("email", user.getEmail())
            .withClaim("email_verified", user.isEmailVerified())
            .withClaim("name", user.getName())
            .withClaim("roles", roles)
            .withClaim("plan", user.getPlan())
            .withIssuedAt(now)
            .withExpiresAt(now.plus(15, ChronoUnit.MINUTES))
            .withJWTId(generateJti())         // for blacklisting
            .sign(Algorithm.RSA256(null, privateKey));
    }
}
```

### JWKS Endpoint

```java
@RestController
@RequestMapping("/.well-known")
public class JwksController {

    private final RSAPublicKey publicKey;

    @GetMapping("/jwks.json")
    @Cacheable("jwks")
    public Map<String, Object> jwks() {
        RSAKey rsaKey = new RSAKey.Builder(publicKey)
            .keyID("auth-key-1")
            .keyUse(KeyUse.SIGNATURE)
            .algorithm(JWSAlgorithm.RS256)
            .build();

        JWKSet jwkSet = new JWKSet(rsaKey);
        return jwkSet.toJSONObject();
    }
}
```

### Token Validation in Downstream Services

```java
@Component
public class JwtAuthFilter extends OncePerRequestFilter {

    private final JWKSource<SecurityContext> jwkSource;

    @Override
    protected void doFilterInternal(HttpServletRequest request,
                                    HttpServletResponse response,
                                    FilterChain chain) throws ServletException, IOException {

        String authHeader = request.getHeader("Authorization");
        if (authHeader == null || !authHeader.startsWith("Bearer ")) {
            chain.doFilter(request, response);
            return;
        }

        String token = authHeader.substring(7);
        try {
            // Verify signature using cached JWKS (no network call on each request)
            JWTClaimsSet claims = jwtProcessor.process(token, null);

            // Check blacklist only for sensitive operations
            // (omitted from non-sensitive endpoints for performance)

            Authentication auth = new JwtAuthentication(claims);
            SecurityContextHolder.getContext().setAuthentication(auth);
        } catch (JOSEException | BadJOSEException e) {
            response.setStatus(HttpServletResponse.SC_UNAUTHORIZED);
            return;
        }

        chain.doFilter(request, response);
    }
}
```

---

## 10. Implementation Roadmap

### MVP — Week 1-2

**Goal:** Registration, login, email verification, JWT issuance

Deliverables:
- `POST /auth/register` with Argon2id password hashing
- `POST /auth/login` with JWT + refresh token
- `POST /auth/refresh` with rotation
- `POST /auth/logout`
- `GET /.well-known/jwks.json`
- `GET /auth/me`
- Email verification flow (Resend integration)
- Basic rate limiting (Redis counters)
- Audit log
- Password reset flow
- PostgreSQL schema (Flyway migrations)

### Phase 2 — Month 2

**Goal:** Social login, MFA preparation, admin panel

Deliverables:
- Google OAuth2 (`POST /auth/oauth/google`)
- GitHub OAuth2 (`POST /auth/oauth/github`)
- HIBP breach detection (async check on registration)
- Admin endpoints (`/auth/admin/*`)
- Account suspension capability
- API key management

### Phase 3 — Month 4+

**Goal:** Enterprise-grade security, compliance preparation

Deliverables:
- TOTP-based MFA (Google Authenticator, Authy)
- New device login notifications
- Session management UI (see all active sessions, revoke)
- IP-based anomaly detection
- Export compliance (GDPR right-to-be-forgotten)
- Comprehensive audit log UI

---

## Security Checklist (pre-launch)

- [ ] Argon2id with correct parameters (not bcrypt default)
- [ ] Access token TTL ≤ 15 minutes
- [ ] Refresh token rotation enabled (single-use)
- [ ] JWKS endpoint publicly accessible and cached
- [ ] Rate limiting on all auth endpoints
- [ ] Email enumeration prevention on forgot-password
- [ ] CORS configured for production domains only
- [ ] Security headers (HSTS, CSP, X-Frame-Options)
- [ ] All passwords hashed — no plaintext anywhere (check logs)
- [ ] Audit log on all auth events
- [ ] Refresh token in HttpOnly, Secure, SameSite=Strict cookie
- [ ] Token JTI stored in blacklist on logout
- [ ] Private key never logged, never committed to git
- [ ] HIBP check on registration
- [ ] Account lockout after 10 failed attempts

---

*Auth System v1.0 — SURUworks, 2025-05-02. Reviewed against OWASP Auth Cheat Sheet and NIST SP 800-63B.*
