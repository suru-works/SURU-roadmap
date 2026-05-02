# SURUworks — Microservices + Microfrontends Architecture
## Technical Design Document v1.0

> Investigado y diseñado el 2025-05-02 por agente especializado.
> Stack primario: React + Java/Spring Boot. Arquitectura: Microservices + Module Federation.

---

## Executive Summary

This document defines the complete architecture for SURUworks: a personal tech platform that starts lean on a single server and scales to cloud without rewrites. The guiding principle is **progressive complexity** — every decision made today must survive a team of 10 and cloud migration without forcing a rewrite.

**Core bets:**
- Traefik as API Gateway (zero-config service discovery)
- Module Federation with Vite Plugin Federation (React-native, no framework lock-in)
- NATS for async messaging (lighter than Kafka, simpler than RabbitMQ for a solo dev)
- PostgreSQL everywhere possible (one mental model, one ops skill)
- Docker Compose Day 1, k3s on-premise, EKS when revenue justifies it

---

## 1. Service Map

### 1.1 API Gateway — Traefik

**Purpose:** Single entry point for all HTTP traffic. Routes requests to downstream services, handles TLS termination, rate limiting, and basic auth header forwarding.

**Technology:** Traefik v3
**Reasoning:** Auto-discovers Docker containers via labels. Zero YAML routing config needed Day 1. Has built-in Let's Encrypt. Spring Cloud Gateway is Java-native but overkill solo; Kong is powerful but heavy; nginx requires manual config for every route. Traefik pays off immediately.

**Exposes:** HTTP/HTTPS ingress only. Never exposed directly to services — it is the external face.

**Dependencies:** Docker socket (for discovery), all downstream services.

**Database:** None. Stateless.

---

### 1.2 Auth Service

**Purpose:** Centralized authentication and authorization. Issues JWTs, manages sessions, handles OAuth2 social logins (GitHub, Google).

**Technology:** Java 21 + Spring Boot 3 + Spring Security
**Reasoning:** Founder already knows Java. Spring Security is the most battle-tested auth library in the JVM ecosystem. Do not use Keycloak until you have a team — it is operationally complex for a solo dev. Custom-built gives you full control over the token structure and claims.

**Exposes:** REST (`/auth/login`, `/auth/refresh`, `/auth/logout`, `/auth/me`), and an internal gRPC endpoint for token validation used by other services.

**Dependencies:** None external. Internal: PostgreSQL (users, sessions), Redis (token blacklist / refresh token store).

**Database:**
- PostgreSQL: user credentials, roles, oauth_accounts table
- Redis: refresh token store with TTL, session blacklist

**JWT Strategy:** Short-lived access tokens (15 min), long-lived refresh tokens stored server-side in Redis with a rotation policy. On logout, add the JTI to the Redis blacklist.

---

### 1.3 User Profile Service

**Purpose:** Stores and serves user profile data (display name, avatar, preferences, project history). Auth Service owns identity; this service owns personalization.

**Technology:** Java 21 + Spring Boot 3

**Exposes:** REST (`/users/{id}`, `/users/{id}/preferences`). Subscribes to `user.registered` events from Auth Service via NATS.

**Dependencies:** Auth Service (JWT validation via gRPC), NATS (consumes user.registered events).

**Database:** PostgreSQL.

---

### 1.4 Content / CMS Service

**Purpose:** Manages all editorial content: blog posts, service descriptions, team bios, case studies — the "corporate website" layer.

**Technology:** Java 21 + Spring Boot 3 with a headless CMS approach. No WordPress. Store content as structured JSON documents.

**Exposes:** REST (`/content/pages/{slug}`, `/content/posts`, `/content/posts/{slug}`). Admin endpoints protected by JWT role `ROLE_ADMIN`.

**Database:** PostgreSQL with JSONB columns for flexible content blocks.

---

### 1.5 Project Registry Service

**Purpose:** Catalog of all interactive tools and projects. Stores metadata: name, description, thumbnail, deployment URL, tech stack, status, required auth level.

**Technology:** Java 21 + Spring Boot 3

**Database:** PostgreSQL.

---

### 1.6 Email Service

**Purpose:** Transactional emails only (welcome email, password reset, contact form confirmations).

**Technology:** Java 21 + Spring Boot 3 + Resend API
**Email Provider:** Resend (resend.com) — clean API, 3000 free emails/month, excellent deliverability.

**Exposes:** No public HTTP endpoints. Consumes NATS events: `user.registered`, `user.password_reset_requested`, `contact.form.submitted`.

**Database:** PostgreSQL (email audit log).

---

### 1.7 Analytics / Telemetry Service

**Technology:** Java 21 + Spring Boot 3

**Database:** PostgreSQL with TimescaleDB extension (turns Postgres into time-series — no need for ClickHouse until 10M+ events/day).

---

### 1.8 Image-to-3D Tool Service (Example AI Microservice)

**Technology:** Python 3.12 + FastAPI

**Reasoning:** AI/ML tooling is Python-native. This is the ONE place outside Java, and it is justified. FastAPI is the right Python web framework for 2025: async, typed, auto-docs.

**Exposes:** REST (`POST /tools/image-to-3d/jobs`, `GET /tools/image-to-3d/jobs/{id}`). Async — job submission returns immediately, results polled or pushed via WebSocket.

**Dependencies:** Auth Service (JWT validation), NATS (publishes `job.completed` events), MinIO (object storage).

**Database:** PostgreSQL (job records, status, result URLs). Redis (job queue).

---

### 1.9 Admin Service (BFF)

**Purpose:** Backend-for-Frontend — aggregates admin operations. Pure orchestration layer, no own database.

**Technology:** Java 21 + Spring Boot 3

---

## 2. Microfrontend Strategy

### Decision: Vite Plugin Federation (Module Federation)

**Rejected alternatives:**
- **Single-SPA:** Too much boilerplate. Module Federation has overtaken it for React shops in 2025.
- **Astro Islands:** Poor fit for interactive tools requiring React state management.
- **iframes:** True isolation but terrible UX. Only for truly untrusted third-party embeds.

**Tool:** `@originjs/vite-plugin-federation`

### Shell Application (Host)

`suruworks-shell` is a React app that:
1. Owns the global navigation bar, footer, and auth state
2. Lazy-loads remote microfrontend modules at runtime
3. Manages the top-level React Router instance
4. Provides the auth context (JWT token) to all loaded remotes via React Context

```typescript
// remotes.config.ts — service discovery
export const remotes = {
  corporateSite: import.meta.env.VITE_REMOTE_CORPORATE_URL,
  projectShowcase: import.meta.env.VITE_REMOTE_SHOWCASE_URL,
  imageToThreeD: import.meta.env.VITE_REMOTE_IMAGE3D_URL,
  adminPanel: import.meta.env.VITE_REMOTE_ADMIN_URL,
};
```

### Microfrontend List

| MFE Name | Route | Notes |
|---|---|---|
| `suruworks-corporate` | `/`, `/about`, `/services`, `/contact` | SSG via Next.js or Astro |
| `suruworks-showcase` | `/projects`, `/projects/:id` | Dynamic React |
| `suruworks-image3d` | `/tools/image-to-3d` | Heavy React, WebGL viewer |
| `suruworks-admin` | `/admin/*` | Protected, ROLE_ADMIN |
| `suruworks-auth-ui` | `/login`, `/signup`, `/profile` | Shared auth flows |

### Shared Design System

**Package:** `@suruworks/ui` — private npm package in the monorepo.

Build with Vite in library mode. Contains: Button, Input, Card, Badge, Modal, Typography tokens, color tokens, spacing tokens.

### CSS Isolation Strategy

CSS Modules + scoped class names per MFE. Global design tokens as CSS custom properties in the shell (`--color-primary`, `--spacing-4`, etc.). All remotes inherit these.

---

## 3. Communication Patterns

### Protocol Decision Matrix

| Scenario | Protocol | Reason |
|---|---|---|
| Frontend → Gateway → Service | REST | Standard, debuggable, cacheable |
| Service validates JWT with Auth (hot path) | gRPC | Binary, typed, low latency |
| User registers → Email Service sends welcome | NATS (async) | Not on critical path |
| Image-to-3D job completed → notify | NATS (async) | Long-running job result |

**Rule:** Synchronous calls on the user request path → REST or gRPC. Side effects → NATS events.

### Event Bus: NATS

**Decision: NATS with JetStream (not RabbitMQ, not Kafka, not Redis Streams)**

- **Kafka:** Operational overhead unjustifiable for a startup. Add when you have a data team.
- **RabbitMQ:** More moving parts than NATS. AMQP is complex.
- **Redis Streams:** Conflates cache layer with message bus.
- **NATS:** Single binary, sub-millisecond latency, JetStream for persistence, zero dependencies, 20MB RAM, first-class Java client.

**NATS Subject naming convention:**
```
user.registered
user.password_reset_requested
contact.form.submitted
job.image3d.submitted
job.image3d.completed
job.image3d.failed
```

### API Gateway: Traefik v3

**Decision: Traefik v3 (not nginx, not Kong, not Spring Cloud Gateway)**

Reads Docker labels. Auto-discovers services. Native Kubernetes Ingress support for migration. One label = one route.

---

## 4. On-Premise → Cloud Migration Path

### Day 1: Docker Compose

```
suruworks/
├── docker-compose.yml
├── docker-compose.override.yml    ← dev overrides (hot reload, debug ports)
├── .env.example
├── traefik/
│   ├── traefik.yml                ← static config
│   └── dynamic/                   ← dynamic config (TLS, middleware)
├── services/
│   ├── auth-service/              ← Java/Spring Boot
│   ├── user-profile-service/      ← Java/Spring Boot
│   ├── content-service/           ← Java/Spring Boot
│   ├── project-registry-service/  ← Java/Spring Boot
│   ├── email-service/             ← Java/Spring Boot
│   ├── analytics-service/         ← Java/Spring Boot + TimescaleDB
│   ├── image3d-service/           ← Python/FastAPI
│   └── admin-service/             ← Java/Spring Boot
├── apps/
│   ├── shell/                     ← React MFE Shell
│   ├── corporate-mfe/
│   ├── showcase-mfe/
│   ├── admin-mfe/
│   └── image3d-mfe/
├── libs/
│   └── ui/                        ← @suruworks/ui design system
└── infrastructure/
    ├── postgres/
    │   └── init-dbs.sql           ← CREATE DATABASE per service
    ├── redis/
    ├── nats/
    └── minio/
```

### Step 2: k3s (On-Premise Kubernetes)

When you have 2+ servers or need rollout strategies:

```bash
# Install k3s on the primary node
curl -sfL https://get.k3s.io | sh -
```

**Migration strategy — Strangler Fig:**
1. Start with stateless services (Admin, Content, Project Registry)
2. Migrate Auth and User Profile (requires PVCs for PostgreSQL)
3. Migrate Image-to-3D last (GPU node affinity rules needed)
4. Keep Docker Compose running during migration. Route traffic gradually via weights.

### Step 3: Cloud (EKS/GKE)

**Infrastructure as Code: Terraform**

```
infrastructure/
├── terraform/
│   ├── modules/
│   │   ├── eks-cluster/
│   │   ├── rds-postgres/
│   │   ├── elasticache-redis/
│   │   └── s3-bucket/
│   ├── environments/
│   │   ├── staging/
│   │   └── production/
│   └── global/
│       └── ecr-repositories/
```

**Making migration reversible:** Every service has a `DATABASE_URL` environment variable. On Docker Compose → local Postgres. On EKS → RDS. Zero application code changes.

---

## 5. Data Architecture

### Database Per Service

| Service | Database | Extension |
|---|---|---|
| Auth Service | PostgreSQL | `pgcrypto` |
| User Profile Service | PostgreSQL | Standard |
| Content Service | PostgreSQL | JSONB for content blocks |
| Project Registry | PostgreSQL | Standard |
| Email Service | PostgreSQL | Audit log only |
| Analytics Service | PostgreSQL | TimescaleDB |
| Image-to-3D Service | PostgreSQL + Redis | Jobs + queue |
| Admin Service | None | BFF |

**Single PostgreSQL instance, multiple databases** on Day 1. One Postgres container, one DB per service (`init-dbs.sql`). Extract to dedicated instances when needed — only `DATABASE_URL` env var changes.

### Shared Identity Pattern

Auth Service is the **source of truth for identity**. Other services store only the user UUID (from `sub` JWT claim).

**Public key distribution:** Auth Service exposes `GET /auth/.well-known/jwks.json`. All services download and cache the JWKS on startup → token validation is local, no network call per request.

### Caching Strategy

| Use Case | Service | TTL |
|---|---|---|
| JWT refresh token store | Auth Service | 30 days |
| JWT blacklist (on logout) | Auth Service | 15 min (access token TTL) |
| Image-to-3D job queue | Image3D Service | Ephemeral |
| Content page cache | Content Service | 5 min |
| Project list cache | Project Registry | 1 min |

Single Redis instance with logical DB separation on Day 1. Each service owns its keyspace prefix.

---

## 6. Architecture Diagram

```
                              INTERNET
                                 │
                    ┌────────────▼────────────┐
                    │         TRAEFIK         │
                    │    (TLS, Rate Limit,    │
                    │    Auth Middleware)      │
                    └────────────┬────────────┘
                                 │
          ┌──────────────────────┼──────────────────────┐
          │                      │                      │
          ▼                      ▼                      ▼
  ┌───────────────┐    ┌─────────────────┐    ┌─────────────────┐
  │  MFE SHELL    │    │    REST APIs    │    │  STATIC ASSETS  │
  │  (React Host) │    │                 │    │  (MFE Bundles)  │
  └───────┬───────┘    └────────┬────────┘    └─────────────────┘
          │ Module Fed           │
  ┌───────▼──────────────┐      │
  │  Remote Loading      │      │
  │  / → corporate       │      │
  │  /projects → showcase│      │
  │  /tools/* → tools    │      │
  │  /admin/* → admin    │      │
  └──────────────────────┘      │
                                 │
          ┌──────────────────────┼──────────────────────────────┐
          │                      │                              │
          ▼                      ▼                              ▼
  ┌───────────────┐    ┌─────────────────┐          ┌─────────────────┐
  │  AUTH SERVICE │    │ CONTENT SERVICE │          │  PROJECT REG.   │
  │  Java/Spring  │    │  Java/Spring    │          │  Java/Spring    │
  │  REST + gRPC  │    │  REST           │          │  REST           │
  ├───────────────┤    └────────┬────────┘          └────────┬────────┘
  │  postgres     │    ┌────────▼────────┐          ┌────────▼────────┐
  │  auth_db      │    │  postgres       │          │  postgres       │
  ├───────────────┤    │  content_db     │          │  registry_db    │
  │  redis        │    └─────────────────┘          └─────────────────┘
  │  (tokens)     │
  └───────────────┘

  ┌───────────────┐    ┌─────────────────┐          ┌─────────────────┐
  │  USER PROFILE │    │ IMAGE-TO-3D     │          │  ANALYTICS      │
  │  Java/Spring  │    │  Python/FastAPI │          │  Java/Spring    │
  │  REST         │    │  REST + WS      │          │  REST (ingest)  │
  ├───────────────┤    ├─────────────────┤          ├─────────────────┤
  │  postgres     │    │  postgres       │          │  postgres +     │
  │  profiles_db  │    │  image3d_db     │          │  TimescaleDB    │
  └───────────────┘    ├─────────────────┤          └─────────────────┘
                        │  redis (queue)  │
                        ├─────────────────┤
                        │  minio (files)  │
                        └─────────────────┘

  ┌───────────────┐    ┌─────────────────┐
  │  EMAIL        │    │  ADMIN SERVICE  │
  │  Java/Spring  │    │  Java/Spring    │
  │  NATS consumer│    │  REST (BFF)     │
  └───────┬───────┘    └─────────────────┘
          ▼
  ┌───────────────┐
  │  Resend API   │
  │  (external)   │
  └───────────────┘

  ┌────────────────────────────────────────┐
  │            NATS (JetStream)            │
  │  user.registered | job.image3d.*       │
  │  contact.form.submitted                │
  └────────────────────────────────────────┘

  ┌────────────────────────────────────────┐
  │           INFRASTRUCTURE               │
  │  Docker Compose → k3s → EKS           │
  │  Terraform (IaC) | GitHub Actions CI  │
  │  OpenTelemetry → Grafana + Prometheus  │
  └────────────────────────────────────────┘
```

---

## 7. Monorepo: Nx

**Decision: Monorepo with Nx** (not Turborepo, not polyrepo)

**Reasoning:** Nx supports Java (`@nx/gradle`), React, and Python in the same workspace. Affected-build intelligence — only rebuilds/retests what changed. Solo developer does not want 10 separate repositories with 10 CI pipelines.

```
suruworks/                        ← Nx workspace root
├── nx.json
├── package.json
├── settings.gradle               ← Root Gradle for Java services
├── apps/
│   ├── shell/                    ← React MFE host
│   ├── corporate-mfe/
│   ├── showcase-mfe/
│   ├── admin-mfe/
│   ├── image3d-mfe/
│   ├── auth-service/             ← Spring Boot
│   ├── content-service/
│   ├── project-registry-service/
│   ├── image3d-service/          ← FastAPI (Python)
│   └── admin-service/
├── libs/
│   ├── ui/                       ← @suruworks/ui design system
│   ├── auth-client/              ← Shared JWT utilities (JS)
│   └── shared-java/              ← Shared DTOs / utils (Gradle lib)
└── infrastructure/
    ├── docker-compose.yml
    ├── terraform/
    └── k8s/
```

---

## 8. 2025 Best Practices

1. **Vertical slicing** — each service owns full stack from DB to API
2. **Platform Engineering mindset from Day 1** — treat infrastructure as a product
3. **OpenTelemetry** is the standard — instrument with OTel, route to any backend
4. **GitHub Actions** for CI/CD — not Jenkins, not CircleCI
5. **Boring technology wins** — PostgreSQL, Redis, Docker are boring and that is a feature
6. **Don't microservice prematurely** — start with 3 services, extract as needed
7. **Structured logging from Day 1** — JSON to stdout, aggregate with Loki
8. **Feature flags over branches** — Unleash self-hosted for trunk-based development

---

## Summary: The 10 Architecture Decisions

| Decision | Choice | Review trigger |
|---|---|---|
| API Gateway | Traefik v3 | 50+ services |
| Auth | Custom Spring Security | Enterprise SSO (SAML) |
| Microfrontend | Vite Plugin Federation | React replacement |
| Event Bus | NATS with JetStream | 10M+ events/day |
| Database | PostgreSQL everywhere | AI needs vector DB |
| Object Storage | MinIO → S3 | Always (same API) |
| Monorepo tool | Nx | Team preference |
| Container orchestration | Docker Compose → k3s → EKS | Revenue justifies managed K8s |
| IaC | Terraform | Team is TypeScript-only |
| Observability | OpenTelemetry → Grafana stack | Always (vendor-neutral) |

---

*Architecture v1.0 — SURUworks, 2025-05-02. Review at team ≥ 4 or 10K DAU.*
