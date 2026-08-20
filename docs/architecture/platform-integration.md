# Integración del portafolio en la web del grupo

> Qué proyectos individuales se integran a `suruworks.com`, cómo, y cuáles solo se muestran. Complementa [homelab-topology.md](homelab-topology.md) (dónde corre cada cosa) y [../auth/group-sso.md](../auth/group-sso.md) (quién accede a qué). Inventario levantado 2026-08-20 leyendo los READMEs de todos los repos; revisado con pase adversario el mismo día.

**Estado:** Decidido 2026-08-20.

---

## 1. Tesis

La tesis de marca de SURU ya lo dice ([brand-identity](../brand/brand-identity.md)): **las herramientas son el portafolio** — "prueba antes de contratar". La web del grupo no es un catálogo de screenshots: los proyectos hosteables se usan en vivo con la cuenta del grupo, y el resto se presenta con página propia + descargas.

Nota de licencias transversal: **toda app AGPL hosteada en red obliga a ofrecer el código fuente de la versión desplegada** — footer/endpoint con link al repo desde cada instancia.

## 2. Inventario por tier

### Tier 1 — Hosteables directo bajo el dominio

| Proyecto | Qué es | Stack | Auth actual | Nota de integración |
|---|---|---|---|---|
| **revscope-server** | Backend social/colaborativo de RevScope: reportes de huecos crowdsourced, salas de rodada con posiciones live, ghosts compartidos | FastAPI + PostgreSQL/PostGIS, Docker | `AUTH_MODE` none/token/**oidc** (sin user-DB propia) | **La app modelo.** Diseñada para esto; OIDC contra el IdP del grupo. Primera app con SSO (F2). AGPL: link al fuente desde la instancia |
| **lumina-calendar** | PWA calendario/tareas local-first (coautoría con Diego Álvarez) | TS + Vite PWA, sin backend | Ninguna (by design) | Build estático en node-01. El win más barato. **AGPL-3.0 + atribución §7(b): atribución visible obligatoria y OK explícito del coautor antes de hostearla bajo la marca** |
| **bipolar-code** | Gateway LLM personal (llama.cpp multi-GPU + proveedores cloud, API Anthropic/OpenAI) | FastAPI + React, corre nativo en el rig | API key única (`UI_API_KEY`); README dice LAN-only | Solo-miembros. **Régimen especial: solo `/v1/*` se publica; `/api/*` (control plane del rig) jamás — y keys por miembro antes de F4.** Ver [group-sso §5](../auth/group-sso.md) |
| **Upflow** | Estudio multimedia IA: upscaling, interpolación, stems, TTS, generación | FastAPI + React, GPU (Vulkan/DirectML), nativo en el rig | **Multi-user real**: `AUTH_MODE=multi`, scopes, cuotas | Solo-miembros. Gate SSO delante + cuentas internas (doble credencial asumida; la cuenta interna se crea en el onboarding) |

### Tier 2 — Hosteable pero con riesgo que lo condiciona

| Proyecto | Riesgo | Decisión |
|---|---|---|
| **Argos** | Analítica de comportamiento/identidad sobre cámaras: pose, re-ID, cara, gait. **Biometría = dato sensible bajo Ley 1581/2012 (habeas data)**; multi-tenant con API key compartida inaceptable | **Nunca público con footage real — con enforcement técnico, no solo política**: la instancia demo se despliega con allowlist fija de fuentes sintéticas empaquetadas y sin capacidad de agregar cámaras (flag horneado al deploy, no toggle de UI); firewall de host impide al proceso demo alcanzar la VLAN de cámaras/puertos RTSP. Instancias con footage real: solo locales de cada miembro, jamás al ingress público, y con base legal documentada |
| **Leviathan** | Bot de trading MT5. Lo que toca dinero no se comparte hosteado | Showcase + docs. Como mucho, explorador de backtests read-only con data de muestra, sin cuentas |

### Tier 3 — Showcase (página + releases, nada que hostear)

| Proyecto | Ángulo en la web |
|---|---|
| **STFU** | Cancelación de ruido IA para Windows (alternativa Krisp). Página + instalador + catálogo de modelos |
| **OpenWinBlue** | Códecs Bluetooth (LDAC/aptX) libres para Windows. Página + descargas + llamado a testers |
| **Nodo** | LLMs on-device Android con endpoint OpenAI-compatible. Historia de ecosistema: gemelo móvil de bipolar-code; integración verificada con RevScope |
| **RevScope (app Android)** | Telemetría OBD2 + radares + pico y placa. APK/Play + se conecta al revscope-server hosteado |
| **Ports ONNX** (GMFSS, audiosr, bs-roformer, openunmix, uvr-deecho) | "Primeros ports ONNX conocidos" — credencial técnica AMD/DirectML. Docs + artefactos |
| **Plugins CC** (bipolar/copilot/ollama-plugin-cc) | Ecosistema de delegación multi-agente. Docs + marketplaces |
| **local-llm-homelab** | Bitácora del rig — material de blog técnico |

### Tier 4 — No se integra

| Proyecto | Razón |
|---|---|
| **free-claude-code** | Superseded por bipolar-code. Solo historia |
| **codex-companion-dashboard** | Herramienta loopback-only; una instancia pública no significa nada |
| Carpeta `keys/` en c:\personal | ⚠️ Keystore y credenciales reales — **jamás cerca de un deploy ni de un repo**. Migrarla fuera del rig antes de F4 (gate de aislamiento) |

## 3. Mapa de subdominios (plano público)

| Subdominio | Servicio | Acceso | Nodo |
|---|---|---|---|
| `suruworks.com` | Sitio Astro corporativo + showcase | Público | node-01 |
| `lumina.suruworks.com` | Lumina Calendar PWA | Público | node-01 |
| `status.suruworks.com` | Uptime Kuma — **solo la status page dedicada** (dashboard: VPN) | Público (read-only) | node-01 |
| `auth.suruworks.com` | IdP del grupo (Authentik) | Público (es el login; MFA obligatorio) | node-01 → nas |
| `revscope.suruworks.com` | revscope-server API | Público con OIDC (la app móvil habla directo) | node-01 |
| `upflow.suruworks.com` | Upflow | Miembros (forward-auth + auth interna) | rig |
| `ai.suruworks.com` | bipolar-code — **solo `/v1/*`**; `/api/*` jamás público | Miembros (forward-auth UI; API keys por miembro) | rig |
| `argos.suruworks.com` | Argos demo (footage sintético, enforcement técnico §2) | Miembros | rig |
| `app.` / `admin.` | **Reservados** para la plataforma comercial SURUworks ([auth-system-spec](../auth/auth-system-spec.md) ya los fija en CORS) | — | futuro |

**Fuera del plano público (solo VPN/LAN, sin subdominio en el mapa):** Komodo, dashboard completo de Uptime Kuma, UIs del NAS, llama-server directo, dashboard de Traefik. Regla en [homelab-topology §3](homelab-topology.md); la config de Traefik es declarativa en `suru-infra` y un cron en node-01 alerta ante rutas públicas no aprobadas.

Reglas: los servicios del rig declaran en su página que son best-effort (el rig no es 24/7).

## 4. Orden de integración

1. **F1:** `suruworks.com` (Astro) + `lumina.` + `status.` en node-01 — ingress en casa (port-forward 80/443 → Traefik, IP pública propia).
2. **F2a — server:** `auth.` + `revscope.` con OIDC; verificable con curl/JWT sin la app.
3. **F2b — cliente Android:** trabajo real en la app RevScope (flujo AppAuth contra Authentik + wiring del contrato offline-first, que hoy no existe en la app). Entregable propio con su alcance — el server no se declara "completo" esperando esto, ni F2 se cierra sin el cliente real.
4. **F4:** `upflow.` + `ai.` + `argos.` (demo) — servicios GPU solo-miembros, tras el gate de aislamiento del rig.
5. **Continuo:** páginas showcase de Tier 3 se agregan al sitio Astro sin dependencias de infra.

## 5. Qué NO se decidió aquí

- Diseño/copy de las páginas showcase → [design-system/MASTER.md](../../design-system/MASTER.md) y [ux-strategy-wireframes](../ux/ux-strategy-wireframes.md).
- Detalle de grupos/roles, onboarding/offboarding y el régimen de API de bipolar → [../auth/group-sso.md](../auth/group-sso.md).
- La plataforma comercial (9 microservicios Java, Image-to-3D) no cambia: sigue su propio roadmap; esta integración es del **portafolio existente** y corre en la misma topología.
