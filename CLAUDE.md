# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Repository Purpose

This is a **strategy and planning repository** for SURUworks — a Colombian tech/consulting startup. It contains architecture decisions, design specs, roadmap, and brand identity. No implementation code exists yet; all files are documentation written in Markdown.

## Documentation Map

| Path | Contents |
|------|----------|
| `docs/roadmap.md` | Week-by-week implementation plan (6 weeks to v1.0) |
| `docs/architecture/microservices-architecture.md` | Full service map, communication protocols, monorepo structure, migration path |
| `docs/architecture/docker-compose-reference.md` | Docker Compose setup reference |
| `docs/stack/tech-stack-2025.md` | Definitive technology decisions with rationale |
| `docs/auth/auth-system-spec.md` | Auth service spec (JWT RS256, refresh rotation, JWKS endpoint) — customer-facing realm |
| `docs/auth/group-sso.md` | Group SSO: Authentik IdP, groups/roles model, per-app integration patterns (internal realm) |
| `docs/architecture/homelab-topology.md` | Physical hosting topology: multi-PC nodes, home ingress (port-forward 80/443 → Traefik on public IP), OpenVPN admin plane, NAS, backups, phases |
| `docs/architecture/platform-integration.md` | Portfolio → group web integration: hostability tiers per project, subdomain map |
| `docs/ux/ux-strategy-wireframes.md` | UX strategy and wireframes |
| [`docs/site/f1-corporate-site.md`](docs/site/f1-corporate-site.md) | F1 corporate site spec (static Astro, no auth): sitemap, `projects` content collection for the Tier 1-3 portfolio, deploy contract with `suru-infra`, quality budgets, open owner decisions |
| `docs/brand/brand-identity.md` | Brand identity and tone |
| `docs/superpowers/specs/2025-05-02-suruworks-platform-design.md` | Original full-scope platform design spec |
| `design-system/MASTER.md` | Design tokens, component specs, anti-patterns |
| `design-system/pages/` | Per-page design overrides |

## Architecture at a Glance

**Monorepo tool:** Nx (supports Java + React + Python in one workspace)

**Service communication rules:**
- Frontend → Gateway → Service: REST
- JWT validation (hot path): gRPC between services
- Side effects (email, notifications): NATS JetStream events

**Services:** Auth (Java/Spring Boot) → all other services validate tokens against its `/.well-known/jwks.json`. Auth is the only source of truth for identity; every other service stores only the user UUID from the `sub` JWT claim.

**One Python exception:** `image3d-service` uses FastAPI — all other backend services are Java 21 + Spring Boot 3.4.

**Database pattern:** Single PostgreSQL instance, one database per service (separated by `DATABASE_URL` env var). No cross-service database queries.

**Infrastructure progression:** Docker Compose → k3s (on-premise) → EKS (when revenue justifies it). Migration uses Strangler Fig — no rewrite required.

**Physical hosting (2026-08):** the group's multi-PC topology (home ingress: port-forward 80/443 → Traefik on the group's public IP, OpenVPN admin plane, GPU rig, UGREEN NAS) is defined in `docs/architecture/homelab-topology.md`. Group identity (Authentik SSO, internal realm) is defined in `docs/auth/group-sso.md` and does NOT replace the custom Spring Authorization Server, which remains the customer-facing plan.

## Key Technology Decisions

These are locked. Do not suggest alternatives without strong justification:

- **API Gateway:** Traefik v3 (auto-discovers Docker containers via labels, native k8s Ingress for migration)
- **Event bus:** NATS with JetStream (not Kafka, not RabbitMQ)
- **Database:** PostgreSQL everywhere (Analytics uses TimescaleDB extension)
- **Object storage:** MinIO locally → S3 in cloud (same SDK, only URL changes)
- **Microfrontend:** Module Federation 2.0 (`@module-federation/enhanced`) on Rspack — not Single-SPA, not iframes (updated 2026-08: `@originjs/vite-plugin-federation` is unmaintained)
- **Auth:** Custom Spring Authorization Server (not Keycloak, not Auth0)
- **Frontend state:** TanStack Query v5 (server state) + Zustand 5.x (UI state)
- **Styling:** Tailwind CSS v4 + shadcn/ui + `@suruworks/ui` design system package

## Design System Rules (from `design-system/MASTER.md`)

- **Style:** Flat Design — no shadows, no gradients
- **Colors:** Use CSS custom properties only (`--color-primary`, `--color-accent`, etc.), never hardcode hex
- **Typography:** Space Grotesk (headings) + DM Sans (body)
- **Icons:** Lucide React only, stroke-width 1.5px — never emojis as structural icons
- **Anti-patterns:** no animations for decoration, no dark mode as default, no text < 12px, no hover as sole interaction

## NATS Subject Naming

```
user.registered
user.password_reset_requested
contact.form.submitted
job.image3d.submitted
job.image3d.completed
job.image3d.failed
```

## Implementation Order (from roadmap)

Auth Service must be built first — every other service depends on it. Build sequence:
1. Auth Service + Docker Compose infra stack
2. Corporate site (Astro 5)
3. Image-to-3D backend (FastAPI)
4. Image-to-3D frontend MFE (React 19 + Module Federation shell)
5. Projects showcase + Auth UI MFE
6. Services pages + production deploy
