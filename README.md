# SURUworks — Platform Strategy & Architecture

**SURUworks** es una startup de tecnología y consultoría con sede en Colombia.

## Servicios

- Desarrollo de software a la medida
- Inteligencia Artificial
- Diseño UX/UI y gráfico
- Impresión y modelado 3D

## Este repositorio

Contiene el plan estratégico completo de la plataforma: arquitectura, diseño, brand, y roadmap de implementación.

El sitio corporativo de la fase F1 (estático, sin auth) tiene su spec en [docs/site/f1-corporate-site.md](docs/site/f1-corporate-site.md).

## Estructura

```
SURU-roadmap/
├── README.md
├── CLAUDE.md                                  # Guía para asistentes AI (AGENTS.md apunta aquí)
├── docs/
│   ├── roadmap.md                             # Plan de implementación de la plataforma
│   ├── superpowers/specs/
│   │   └── 2025-05-02-suruworks-platform-design.md  # Design spec original
│   ├── brand/brand-identity.md                # Identidad y tono de marca
│   ├── architecture/
│   │   ├── microservices-architecture.md      # Mapa de servicios de la plataforma comercial
│   │   ├── docker-compose-reference.md        # Compose de referencia
│   │   ├── homelab-topology.md                # Topología física del grupo (fases F0-F5)
│   │   └── platform-integration.md            # Portafolio → web del grupo, subdominios
│   ├── auth/
│   │   ├── auth-system-spec.md                # Auth de clientes (Spring Authorization Server)
│   │   └── group-sso.md                       # SSO interno del grupo (Authentik)
│   ├── ux/ux-strategy-wireframes.md           # Estrategia UX y wireframes
│   ├── site/f1-corporate-site.md              # Spec del sitio corporativo F1
│   └── stack/tech-stack-2025.md               # Decisiones de stack
├── design-system/
│   ├── MASTER.md                              # Design system master
│   ├── tokens.css                             # Tokens de color (CSS custom properties)
│   └── pages/                                 # Overrides por página
└── scripts/
    └── check_contrast.py                      # Verificador de contraste WCAG de los tokens
```

Documentos clave de la infraestructura del grupo: [homelab-topology.md](docs/architecture/homelab-topology.md), [platform-integration.md](docs/architecture/platform-integration.md) y [group-sso.md](docs/auth/group-sso.md).

## Investigación generada por IA (2026-05-02)

Este plan fue generado usando múltiples agentes de IA especializados investigando en paralelo:
- Investigación lingüística del nombre SURU
- Arquitectura de microservicios y microfrontends
- Sistema de autenticación centralizado
- Tendencias de stack tecnológico 2024-2025
- Estrategia UX e información arquitectónica

> **Nota sobre el año:** los documentos de esa tanda (y el nombre del spec en `docs/superpowers/specs/`) dicen 2025-05-02, pero el historial de git los fecha el 2026-05-02; muy probablemente un error de año del agente generador. Los nombres de archivo se conservan para no romper enlaces.

---

*Generado el 2026-05-02 — SURUworks Platform Strategy v1.0*
