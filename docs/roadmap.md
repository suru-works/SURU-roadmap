# SURUworks — Roadmap de Implementación

> Plan MVP → escalable. Basado en el design spec 2025-05-02.
> Estimado para un desarrollador solo (40h/semana).

---

## Principios de implementación

1. **Entregar valor primero**: el usuario ve algo real al final de cada semana
2. **Progresividad**: no construir infraestructura que no se necesita aún
3. **Microservicios reducidos al inicio**: Auth + Image3D + Content en 1 monolito, separar cuando sea necesario
4. **Testing desde el inicio**: cada servicio tiene tests antes de ir a producción

---

## Dependencias de bloqueo

Resolver estas antes de comenzar la Semana 1:

| Dependencia | Bloquea | Acción previa |
|-------------|---------|---------------|
| Auth Service | Todos los demás servicios | Construir primero (Semana 1) |
| PostgreSQL | Todos los servicios | Disponible desde Docker Compose Día 1 |
| TripoSR weights (~2 GB) | Image-to-3D service | Descargar de Hugging Face antes de Semana 3 |
| Resend API key | Email + Contact form | Registrar gratis antes de Semana 1 Día 5 |
| Dominio `suruworks.com` | Deploy Semana 2 | Registrar ASAP si aún no está registrado |

---

## Plan semana a semana

### Semana 1: Infraestructura base + Auth MVP

**Objetivo**: `docker compose up -d` levanta todo. Register/login funciona.

**Día 1–2 · Setup**
- [ ] Nx monorepo init
- [ ] Docker Compose: Traefik + PostgreSQL + Redis + NATS + MinIO
- [ ] Flyway migrations setup
- [ ] Estructura `apps/` y `libs/` en Nx

**Día 3–4 · Auth Service**
- [ ] Spring Boot 3.4 + Java 21 + Spring Authorization Server
- [ ] `POST /auth/register` (Argon2id)
- [ ] `POST /auth/login` (JWT RS256)
- [ ] `POST /auth/refresh` (rotación de tokens)
- [ ] `POST /auth/logout`
- [ ] `GET /.well-known/jwks.json`

**Día 5 · Email + Tests**
- [ ] Integración con Resend
- [ ] Flujo de verificación de email
- [ ] Unit tests para los flujos críticos de auth

**Entregable**: API de auth funcional localmente, todos los endpoints verificados con Bruno.

---

### Semana 2: Corporate Site (Astro 5)

**Objetivo**: Homepage live y deployable.

**Día 1 · Paquete `@suruworks/ui`**
- [ ] Vite en modo library
- [ ] Componentes: Button, Card, Badge, Input, Typography
- [ ] CSS variables del design system

**Día 2–3 · Homepage**
- [ ] Hero section (fondo navy, formas geométricas CSS)
- [ ] Sección de servicios (4 cards)
- [ ] Preview de herramientas (2 cards placeholder)
- [ ] Strip About/fundador
- [ ] Banner CTA
- [ ] Footer con formulario de newsletter

**Día 4 · Contact + About**
- [ ] Formulario de contacto → Resend
- [ ] Página About
- [ ] Estados de éxito

**Día 5 · Responsive + Deploy**
- [ ] Responsive mobile (375 px, 768 px)
- [ ] Deploy en Railway

**Entregable**: `suruworks.com` vive con homepage completa.

---

### Semana 3: Image-to-3D Backend

**Objetivo**: API de Image-to-3D funcional (sin UI aún).

**Día 1–2 · Python FastAPI service**
- [ ] FastAPI + Docker
- [ ] Integración de TripoSR (pesos desde Hugging Face, CPU fallback habilitado)
- [ ] Creación de jobs + tracking de estado (PostgreSQL)

**Día 3 · Queue + SSE**
- [ ] Cola de jobs con Celery + Redis
- [ ] Integración con MinIO (upload/download)
- [ ] Publisher NATS en `job.image3d.completed`

**Día 4 · Spring WebFlux SSE**
- [ ] Endpoint SSE en Spring WebFlux
- [ ] Subscripción a Redis pub/sub
- [ ] Streaming de estado del job al cliente

**Día 5 · Tests + Integración con Auth**
- [ ] Validación JWT desde el auth service (caché JWKS)
- [ ] Integration tests (anónimo + autenticado)

**Entregable**: `curl -F image=@foto.jpg http://localhost:8001/tools/image-to-3d/jobs` retorna un archivo GLB.

---

### Semana 4: Image-to-3D Frontend (MFE)

**Objetivo**: Herramienta completa usable desde el browser.

**Día 1 · Shell App**
- [ ] Next.js 15 + Rspack + Module Federation
- [ ] `remotes.config.ts` (URLs locales y producción)
- [ ] Auth context (estado JWT)
- [ ] Layout compartido (nav, footer)

**Día 2–3 · MFE Image-to-3D (React 19)**
- [ ] Panel de upload: zona drag-and-drop (react-dropzone)
- [ ] Opciones: calidad, formato de salida
- [ ] Botón Generate + estado de carga

**Día 4 · Output + 3D Viewer**
- [ ] Visor GLB con Three.js + orbit controls
- [ ] Barra de progreso conectada a SSE
- [ ] Labels de etapa: "Generando malla...", etc.
- [ ] Botones de descarga (GLB, OBJ)

**Día 5 · UX + Upsell**
- [ ] Estados de error (timeout, imagen inválida, error de servidor)
- [ ] Card de upsell post-resultado
- [ ] Testing mobile (375 px, controles táctiles)

**Entregable**: `suruworks.com/tools/image-to-3d` funciona completamente.

---

### Semana 5: Projects Showcase + Auth UI

**Objetivo**: Grid de `/projects` funcional. Login/signup integrados.

**Día 1–2 · Project Registry Service**
- [ ] Spring Boot service
- [ ] Schema PostgreSQL (tabla `projects`)
- [ ] REST API: `GET /projects`, `GET /projects/:id`
- [ ] Endpoints admin para CRUD

**Día 3 · Showcase MFE (Astro 5)**
- [ ] Página grid `/projects`
- [ ] Página individual `/projects/image-to-3d`
- [ ] Barra de filtros (All, AI, Web, 3D)
- [ ] Redirect al MFE de cada herramienta

**Día 4–5 · Auth UI MFE**
- [ ] Modal de login (inline, sin redirect)
- [ ] Modal de signup
- [ ] Recordatorio de verificación de email
- [ ] Almacenamiento JWT: refresh token en cookie HttpOnly, access token en memoria JS

**Entregable**: Flujo completo — visitar `/projects` → probar Image-to-3D → ver upsell → crear cuenta.

---

### Semana 6: Services Pages + Polish

**Objetivo**: Sitio corporativo completo. v1.0 listo.

**Día 1–2 · Services Pages (Astro 5)**
- [ ] `/services` overview (4 bloques con ilustraciones)
- [ ] `/services/software-development`
- [ ] `/services/ai-solutions`
- [ ] `/services/ux-design`
- [ ] `/services/3d-printing`
- [ ] Acordeón de FAQ
- [ ] Strip de proceso en 4 pasos

**Día 3 · Performance**
- [ ] Audit Lighthouse (objetivo: 90+ en todas las categorías — ver Métricas)
- [ ] Imágenes WebP
- [ ] `font-display: swap`
- [ ] Lazy loading del contenido below-the-fold
- [ ] Meta tags + OG tags

**Día 4 · Accesibilidad**
- [ ] Audit WCAG AA (axe-core)
- [ ] Navegación con teclado
- [ ] Alt text en todas las imágenes
- [ ] Focus states visibles
- [ ] ARIA labels en botones solo-ícono

**Día 5 · Deploy**
- [ ] Docker Compose producción (sin Traefik dashboard)
- [ ] TLS automático vía Let's Encrypt
- [ ] Smoke tests de todos los endpoints críticos
- [ ] Tag `v1.0` en git

**Entregable**: SURUworks v1.0 en producción.

---

## Backlog (Post v1.0)

### Semana 7–8: Admin + Dashboard
- Admin panel MFE (React 19)
- Dashboard de usuario: historial de jobs
- Analytics básico: page views, tool usage
- Google OAuth2 como social login

### Semana 9–10: Growth
- Newsletter con Resend
- Blog (Content Service + Astro Content Layer)
- Observabilidad: Prometheus + Grafana
- SEO: sitemap, robots.txt, schema.org markup

### Semana 11–12: Segunda Herramienta
- Seleccionar la segunda herramienta
- Arquitectura del nuevo microservicio
- Deploy independiente
- Cross-linking entre herramientas

### Mes 4+: Infraestructura
- Migración a k3s (si hay tráfico real)
- Toggle de idioma ES/EN (traducción manual)
- MFA (TOTP)
- Terraform IaC para plan de migración a cloud

---

## Métricas de éxito v1.0

| Métrica | Target | Medición |
|---------|--------|---------|
| Lighthouse Performance | ≥ 90 | Homepage + tool page |
| Lighthouse Accessibility | ≥ 90 | Todas las páginas |
| Time to First Byte | < 200 ms | Homepage |
| Image-to-3D job time | < 120 s (CPU) | Promedio de jobs |
| Contact form submission | > 0 | Primer mes |
| Tool usage | > 10 jobs | Primera semana |

---

## Herramientas de desarrollo recomendadas

| Área | Herramienta |
|------|-------------|
| IDE | IntelliJ IDEA (Java) + VS Code (TS/Python) |
| API testing | Bruno (open source) |
| DB GUI | TablePlus o DBeaver |
| Contenedores | Docker Desktop |
| Git GUI | GitKraken o Fork |
| Diseño | Figma |
| Diagramas | Excalidraw |
