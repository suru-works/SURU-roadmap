# SURUworks Platform — Master Design Spec

**Date:** 2025-05-02  
**Version:** 1.0  
**Status:** Approved for implementation  
**Author:** Claude (multi-agent research) + Santiago Quiroz upegui  

---

## Overview

SURUworks es una plataforma empresarial para una startup de tecnología colombiana. Combina un sitio corporativo de consultoría con un showcase interactivo de herramientas y proyectos de IA, todo sobre una arquitectura de microservicios y microfrontends escalable de on-premise a nube.

---

## Scope

Este spec cubre la implementación completa de la plataforma v1.0:

1. Sitio corporativo (landing, servicios, about, contacto)
2. Showcase de proyectos/herramientas (Image-to-3D como primer proyecto)
3. Sistema de autenticación centralizado custom
4. Arquitectura de microservicios (8 servicios)
5. Shell de microfrontends con Module Federation
6. Sistema de email transaccional
7. Infraestructura on-premise con Docker Compose

---

## Brand

**Nombre:** SURUworks  
**Origen:** する (suru) = japonés para "to do" / "to make things happen"  
**Tagline:** "We build software that thinks, looks great, and ships fast."  
**Idioma primario:** Inglés (español futuro)  
**Alternativas evaluadas:** FORJA (LATAM), KRAVIO (global) — mantener SURU  

---

## Design System

### Paleta de colores

| Token | Hex | Uso |
|-------|-----|-----|
| `--color-primary` | `#0F172A` | Navy principal, hero background |
| `--color-secondary` | `#334155` | Texto secundario, elementos de apoyo |
| `--color-accent` | `#0369A1` | CTAs, links, highlights |
| `--color-background` | `#F8FAFC` | Background general |
| `--color-foreground` | `#020617` | Texto principal |
| `--color-card` | `#FFFFFF` | Fondo de cards |
| `--color-muted` | `#E8ECF1` | Elementos inactivos |
| `--color-border` | `#E2E8F0` | Bordes y separadores |
| `--color-destructive` | `#DC2626` | Errores, acciones destructivas |

### Tipografía

| Rol | Fuente | Pesos |
|-----|--------|-------|
| Headings | Space Grotesk | 400, 500, 600, 700 |
| Body | DM Sans | 400, 500, 700 |

```css
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
```

### Estilo

**Flat Design**: sin gradientes, sin sombras, colores sólidos, bordes limpios, transiciones 150-200ms.

**Componentes base:** shadcn/ui (new-york variant) + Tailwind CSS v4 con tokens del design system.

---

## Architecture

### Service Map

| # | Servicio | Tech | DB | Notas |
|---|---------|------|-----|-------|
| 1 | API Gateway | Traefik v3 | — | Auto-discovery, TLS, rate limit |
| 2 | Auth Service | Java 21 + Spring Boot | PostgreSQL + Redis | JWT RS256, Spring Auth Server |
| 3 | User Profile | Java 21 + Spring Boot | PostgreSQL | NATS consumer |
| 4 | Content/CMS | Java 21 + Spring Boot | PostgreSQL JSONB | Headless CMS |
| 5 | Project Registry | Java 21 + Spring Boot | PostgreSQL | Catalogo de herramientas |
| 6 | Email Service | Java 21 + Spring Boot | PostgreSQL | Resend API, NATS consumer |
| 7 | Analytics | Java 21 + Spring Boot | PostgreSQL + TimescaleDB | Event ingestion |
| 8 | Image-to-3D | Python 3.12 + FastAPI | PostgreSQL + Redis | TripoSR, async jobs |
| 9 | Admin BFF | Java 21 + Spring Boot | — | Orchestrator solo |

### Microfrontend Architecture

**Shell:** Next.js 15 + Rspack + Module Federation 2.0

| MFE | Route | Framework |
|-----|-------|-----------|
| Corporate site | `/`, `/about`, `/services`, `/contact` | Astro 5 |
| Project showcase | `/projects`, `/projects/:slug` | Astro 5 |
| Image-to-3D tool | `/tools/image-to-3d` | React 19 |
| Admin panel | `/admin/*` | React 19 + Next.js |
| Auth UI | `/login`, `/signup` | React 19 |

**Shared design system:** `@suruworks/ui` (private npm package, Vite library mode)

### Communication

- **Sync:** REST (external) + gRPC (token validation, internal hot path)
- **Async:** NATS JetStream (eventos de dominio: user.registered, job.image3d.completed, etc.)
- **Real-time:** Server-Sent Events (Spring WebFlux) para progreso de jobs AI

### Monorepo

**Tool:** Nx workspace

```
suruworks/
├── apps/
│   ├── shell/              ← Next.js MFE host
│   ├── corporate-mfe/      ← Astro 5
│   ├── showcase-mfe/       ← Astro 5
│   ├── image3d-mfe/        ← React 19
│   ├── admin-mfe/          ← React 19
│   └── [8 Java/Python services]
├── libs/
│   ├── ui/                 ← @suruworks/ui
│   ├── auth-client/        ← JWT utilities (JS)
│   └── shared-java/        ← DTOs compartidos
└── infrastructure/
    ├── docker-compose.yml
    └── terraform/
```

### Deployment Path

```
Day 1:    Docker Compose (single server on-premise)
Step 2:   k3s (multi-server on-premise, rolling deploys)
Step 3:   EKS/GKE (cloud, Terraform IaC)
```

---

## Auth System

### Token Strategy

- **Access token:** JWT (RS256), TTL = 15 minutes
- **Refresh token:** Opaque (UUID in Redis), TTL = 30 days, single-use rotation
- **JWKS:** `GET /auth/.well-known/jwks.json` — all services cache and validate locally
- **Revocation:** Redis blacklist for logout (JTI-based), short TTL = defense for theft

### Password Security

- Algorithm: **Argon2id** (m=19456, t=2, p=1)
- Brute force: Redis rate limiting (10 attempts/15min per IP)
- Breach detection: HIBP k-Anonymity API (async, non-blocking)

### Email Provider

**Resend** — 3,000 free emails/month, cleanest API, best developer experience in 2025.

### Social Login (Phase 2)

Google OAuth2 + GitHub OAuth2 via Spring Authorization Server client registration.

---

## Information Architecture

```
/                       Landing (hero + services + tools preview + founder + CTA)
/services               Services overview
  /services/software-development
  /services/ai-solutions
  /services/ux-design
  /services/3d-printing
/projects               Project/tool grid
  /projects/:slug       Individual tool (e.g., image-to-3d)
/about                  Founder story
/contact                Contact form + Calendly
/dashboard              Saved results (auth required)
/admin/*                Admin panel (ROLE_ADMIN required)
```

---

## UX Key Decisions

### Hero Section

- Background: CSS/SVG animated geometric shapes (navy + blue tones, no video)
- Primary CTA: "Book a free 30-min call"
- Secondary CTA: "Try a free tool"
- Copy: "We build software that thinks, looks great, and ships fast."

### Navigation

- Desktop: Logo + Services · Projects · About · Contact + [Try a Tool →]
- Mobile: Hamburger → full-screen overlay (not sidebar drawer)

### Trust Building (pre-portfolio)

1. Technology expertise logos (specific: TripoSR, LangChain, Three.js, FastAPI)
2. Live interactive tools (Image-to-3D as proof of craft)
3. Founder photo + first-person copy
4. 4-step process documentation
5. GitHub open source contributions
6. Response time signal ("Reply within 24h")

### Image-to-3D Tool UX

- Anonymous first use: no login required
- Upload: drag-and-drop zone, immediate thumbnail preview
- Processing: progress bar with stage labels (30-120s)
- Result: Three.js interactive 3D viewer + download buttons
- Upsell: card appears after first success, NOT before

### Conversion Strategy

- **Consulting**: CTA in header, hero, services page end, about page
- **Tools**: inline sign-up modal after first result (never before)
- **Email capture**: footer newsletter + post-tool download + exit-intent lead magnet

---

## Tech Stack Summary

| Layer | Technology | Version |
|-------|-----------|---------|
| Corporate site | Astro | 5.x |
| Shell / tools | Next.js | 15.x |
| Tool MFEs | React | 19.x |
| Build tool | Rspack | latest |
| Server state | TanStack Query | v5 |
| Client state | Zustand | 5.x |
| Styling | Tailwind CSS | v4 |
| Components | shadcn/ui | latest |
| Backend | Spring Boot | 3.4.x |
| Java | Java 21 LTS | 21 |
| AI service | Python FastAPI | 0.115+ |
| AI model (3D) | TripoSR | latest |
| Event bus | NATS JetStream | 2.10 |
| API gateway | Traefik | v3 |
| Primary DB | PostgreSQL | 17 |
| Cache | Redis | 7.x |
| DB migrations | Flyway | 10.x |
| Monorepo | Nx | latest |
| CI/CD | GitHub Actions | — |
| Containers | Docker Compose → k3s | — |
| Observability | Prometheus + Grafana | latest |
| Object storage | MinIO → S3 | latest |
| Email | Resend | — |

---

## Implementation Order

### Phase 1 — Foundation (Semanas 1-2)

- [ ] Nx monorepo setup con workspaces básicos
- [ ] `@suruworks/ui` design system package con tokens base
- [ ] Docker Compose infrastructure stack (Traefik, PostgreSQL, Redis, NATS)
- [ ] Auth Service MVP: register, login, JWT, refresh, email verify
- [ ] Corporate MFE homepage (Astro 5): hero, services, featured tool, about, CTA
- [ ] Contact form funcional (email via Resend)

### Phase 2 — First Tool (Semanas 3-4)

- [ ] Project Registry Service
- [ ] Showcase MFE: grid de proyectos
- [ ] Image-to-3D MFE: upload, processing state, Three.js viewer
- [ ] Image-to-3D Python FastAPI service con TripoSR
- [ ] MinIO para almacenamiento de archivos
- [ ] Job queue con Redis + SSE progress via Spring WebFlux

### Phase 3 — Full Services + Auth UI (Semanas 5-6)

- [ ] Services detail pages (Astro 5)
- [ ] About page
- [ ] Auth UI MFE: login/signup modal (inline, no redirect)
- [ ] Google OAuth2 social login
- [ ] User dashboard: historial de jobs
- [ ] Admin panel MVP

### Phase 4 — Growth (Semanas 7+)

- [ ] Email newsletter (Resend lista)
- [ ] Blog (Content Service + Astro)
- [ ] Segunda herramienta
- [ ] Language toggle ES/EN
- [ ] Observability (Prometheus + Grafana)
- [ ] k3s migration plan

---

## Risks & Mitigations

| Riesgo | Probabilidad | Impacto | Mitigación |
|--------|-------------|---------|-----------|
| TripoSR requiere GPU que no tenemos | Media | Alto | CPU fallback soportado (30-120s aceptable); roadmap de GPU |
| Module Federation aumenta complejidad | Alta | Medio | Empezar con 2-3 MFEs; no sobrecomplicar Day 1 |
| NATS aprendizaje para eventos | Baja | Bajo | Documentación excelente; alternativa Redis Pub/Sub |
| Astro 5 para el corporate site es nuevo stack | Media | Bajo | Muy simple de aprender; si falla, Next.js es fallback |
| Auth custom requiere mantenimiento de seguridad | Alta | Alto | Seguir el roadmap de Spring Authorization Server; auditar periódicamente |

---

## Definition of Done (v1.0)

- [ ] Homepage live con hero, servicios, 1 herramienta destacada, about, contacto
- [ ] Image-to-3D funcional: upload → proceso → descarga GLB/OBJ
- [ ] Auth funcional: registro, login, email verify, logout
- [ ] Contact form envía email real vía Resend
- [ ] Mobile-responsive en 375px y 768px mínimo
- [ ] WCAG AA compliance en páginas principales
- [ ] Docker Compose: `docker compose up -d` levanta todo

---

*Spec generated by multi-agent AI research on 2025-05-02. Agents: architecture, auth, UX strategy, tech stack trends, brand research. Reviewed and compiled by Claude Sonnet 4.6.*
