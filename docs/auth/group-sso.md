# SSO del grupo — identidad centralizada para el portafolio

> Cómo se autentican los miembros de SURU en los servicios hosteados bajo `suruworks.com`. Complementa [auth-system-spec.md](auth-system-spec.md) (que sigue vigente para otra cosa — ver §2), [../architecture/homelab-topology.md](../architecture/homelab-topology.md) y [../architecture/platform-integration.md](../architecture/platform-integration.md). Revisado con pase adversario 2026-08-20.

**Estado:** Decidido 2026-08-20. Implementación en Fase 2 de la topología.

---

## 1. Problema

El portafolio llega con auth inconsistente, todo pensado para LAN:

- Tokens estáticos compartidos: bipolar-code (`UI_API_KEY`), Argos (API key), free-claude-code (secreto literal `"freecc"`).
- Usuario/contraseña propio con scopes: solo Upflow.
- OIDC contra issuer configurable: solo revscope-server (el único listo para identidad de grupo).
- Nada: lumina (by design), showcase apps.

Para una web de grupo se necesita: **una sola cuenta por miembro, passkey/MFA, y control por app de quién entra** — sin inventar una base de usuarios por servicio.

## 2. Dos realms — esta decisión NO toca el auth-system-spec

| Realm | Quién | Solución | Estado |
|---|---|---|---|
| **Interno / grupo** (este doc) | Miembros de SURU usando las herramientas del portafolio | IdP off-the-shelf: **Authentik** | Decidido, Fase 2 |
| **Comercial / clientes** | Usuarios de la plataforma SURUworks (Image-to-3D, etc.) | **Custom Spring Authorization Server** según [auth-system-spec.md](auth-system-spec.md) — decisión locked intacta | Diferido hasta que la plataforma se construya |

El deseo de largo plazo de un proyecto de auth propio para todos los servicios sigue en pie: es el realm comercial. La regla puente (ya practicada en revscope-server): **toda app valida OIDC contra un issuer configurable y no guarda usuarios propios.** El día que el auth propio exista, se cambia el issuer y nada más.

## 3. Decisión: Authentik como IdP del grupo

`auth.suruworks.com`, corriendo en **node-01 (interino) → NAS (final)** — nunca en el rig (es Windows y por diseño apagable). Stack actual (verificado 2026-08): **server + worker + PostgreSQL — 3 contenedores; Authentik eliminó Redis en la release 2025.10**. Presupuestar **~1.5-2GB RAM** (el mínimo declarado es 2GB y el worker solo consume ~1GB) y tener en cuenta que sin Redis el consumo de conexiones a PostgreSQL subió (~50% más) al dimensionar node-01/NAS.

### Por qué (comparativa evaluada 2026-08)

| Opción | A favor | En contra | Veredicto |
|---|---|---|---|
| **Authentik** | OIDC + SAML + LDAP + proxy provider (**forward-auth integrado** para apps sin auth), invitaciones, passkeys, UI de flows; consenso 2026 "sweet spot para equipos" | ~1.5-2GB RAM, cadencia de upgrades a respetar | **Elegido** — el único que resuelve IdP + forward-auth en una pieza |
| Pocket ID | Un contenedor, ~256MB, passkey-first, bellísimo de operar | Solo OIDC (sin forward-auth, sin passwords); necesitaría oauth2-proxy aparte para apps legacy | Plan B si Authentik pesa demasiado en la práctica |
| Keycloak | Todo el poder enterprise | El propio auth-system-spec ya lo descartó por overhead operativo; nada cambió | No |
| Custom (Spring) | Control total | Es el realm comercial; construirlo AHORA bloquea la web del grupo meses | No para este realm |

Contexto que refuerza poseer el IdP: el "SSO tax" se consolidó en 2026 (Planka quitó SSO de su community edition en agosto). IdP propio + preferir apps con OIDC libre es la defensa.

### Dependencia dura: SMTP

Invitaciones y recovery de Authentik **requieren correo saliente**. Decisión F2: proveedor SMTP transaccional (Resend — ya previsto en el stack de la plataforma — o SES/Mailgun; US$0-1/mes a este volumen) + registros SPF/DKIM/DMARC en el plan DNS de F0. Mientras no exista: las invitaciones se entregan como enlaces copiados manualmente por el operador y recovery = break-glass. Sin decidir esto, F2 se atasca en el primer miembro.

## 4. Modelo de grupos y roles

Grupos en Authentik → claim `groups` en el token → cada app o gate decide:

| Grupo | Significado |
|---|---|
| `suru-admins` | Administración del IdP, Komodo, acceso a todo |
| `suru-members` | Miembro del grupo: acceso a apps solo-miembros (Upflow, bipolar, Argos demo) |
| `app-<nombre>` | Acceso fino por app para invitar a alguien a UNA sola cosa (ej. `app-revscope` para un amigo motero que no es miembro SURU) |

Reglas duras:

1. Cuentas personales, nunca compartidas.
2. **MFA obligatorio (passkey o TOTP) para TODA cuenta que pertenezca a cualquier grupo `suru-*` o `app-*`** — con un puñado de miembros no cuesta nada operativamente y el login es público. Passkey como método preferido.
3. Políticas anti-brute-force/reputación de Authentik activas en el flow público + alerta ante fallos repetidos.
4. App nueva del grupo ⇒ nace con OIDC contra issuer configurable (patrón revscope-server). Ninguna app introduce user-DB propia.
5. Acceso admin (Komodo, Authentik admin, NAS) exige `suru-admins` y plano-VPN.
6. **Break-glass:** admin local de Authentik (fuera de SSO) con **MFA también** y un flow policy que solo acepta login local desde IPs de VPN/LAN — la página pública jamás acepta ese usuario. Credencial en dos custodias: gestor del operador + copia sellada (impresa o vault de un segundo miembro de confianza), documentando quién la tiene. Backup nightly de la DB de Authentik → B2 desde el día 1 de F2 ([topología §6](../architecture/homelab-topology.md)). Si el IdP muere, el plano-VPN sigue entrando a todo.

## 5. Patrones de integración por app

Tres patrones, del mejor al más pragmático. Regla estructural previa ([topología §1.6](../architecture/homelab-topology.md)): un backend detrás de gate es inalcanzable sin el gate (bind al túnel/localhost o firewall de host), y el edge hace strip de headers de identidad entrantes.

- **(a) OIDC nativo** — la app habla OIDC ella misma y lee `groups`. Aplica: revscope-server (`AUTH_MODE=oidc`), Komodo.
- **(b) Forward-auth en el edge** — Pangolin/Traefik consulta al proxy provider de Authentik antes de dejar pasar; la app ni se entera. Aplica: bipolar-code UI, Argos demo, cualquier dashboard. **Validar la cadena Pangolin→forward-auth→Authentik en F2 con un servicio trivial y guardar la config de referencia en `suru-infra`; fallback documentado: oauth2-proxy.**
- **(c) Gate SSO + auth interna** — forward-auth decide QUIÉN entra; la auth interna de la app maneja permisos finos/cuotas. Aplica: Upflow. Implica **doble credencial asumida** (SSO + login interno de Upflow); la cuenta interna se crea como paso del onboarding (§6). Evaluar trusted-header auth si Upflow lo llega a soportar.

| App | Patrón | Grupo requerido |
|---|---|---|
| revscope-server | a | login OIDC público (o `app-revscope` si se cierra) |
| Komodo | a | `suru-admins` — **solo VPN, sin subdominio público** |
| bipolar-code | b para la UI + régimen especial de API (abajo) | `suru-members` |
| Argos (demo) | b | `suru-members` |
| Upflow | c | `suru-members` |
| Uptime Kuma | status page dedicada pública; dashboard completo solo VPN (nunca split por path — la API socket.io no vive bajo `/admin`) | `suru-admins` |
| Sitio Astro, Lumina | sin auth | — |

### bipolar-code: régimen especial de API (hallazgo CRITICAL del pase de seguridad)

El `/api/*` de bipolar-code no es solo inferencia: **arranca/mata llama-server, reescribe `~/.claude/settings.json` y el registro de Windows del rig**. Con la API key única compartida eso sería control remoto del rig con una sola key filtrada. Reglas duras para `ai.suruworks.com`:

1. **Solo `/v1/*` (inferencia) se publica por el túnel. `/api/*` (control plane) jamás sale de LAN/VPN.** Cómo se configura la exención por path en Pangolin/Traefik se verifica en F1 con el túnel de prueba; si no se puede por path, se publican hostnames separados y solo el de inferencia sale.
2. **Una API key por miembro** (feature a agregar en bipolar-code antes de F4) — revocación individual, no grupal. Mientras exista una sola key: rotación documentada y ligada al offboarding.
3. Rate-limiting en el edge (middleware Traefik del VPS) para los endpoints con API key.
4. Ingresos no-navegador de bipolar (bot de Telegram, BYOK `/v1/chat/completions`) quedan **fuera de la instancia grupal**: el bot es personal-only y nunca se tunela; el BYOK usa las keys por miembro.

Nota API-first general: forward-auth protege navegadores. Clientes programáticos (app Android RevScope, `ANTHROPIC_BASE_URL` → bipolar) usan su mecanismo propio (JWT del IdP; API key por miembro). No forzar OIDC interactivo donde no hay navegador. Inventariar **todos** los ingresos no-navegador de cada app antes de publicarla.

## 6. Operación

**Onboarding de un miembro:**
1. Invitación de Authentik (correo vía SMTP, o enlace manual) → registra passkey → grupos asignados.
2. Si usará Upflow: el operador crea su cuenta interna de Upflow (patrón c).
3. Si usará bipolar programático: se le emite su API key propia.
4. Si necesita plano admin: perfil WireGuard por dispositivo con `AllowedIPs` acotados a lo que necesita (emitido por el operador desde el router; entrega del `.conf` por canal seguro — QR presencial o vault compartido, nunca chat plano).

**Offboarding (checklist — ejecutar el mismo día):**
1. Authentik: desactivar cuenta + revocar todas las sesiones.
2. Router: eliminar su(s) peer(s) WireGuard.
3. Upflow: desactivar cuenta interna.
4. bipolar-code: revocar su API key (o rotar la compartida mientras no haya per-member keys).
5. Verificar que no queda en ningún grupo `app-*`.

**Mantenimiento:**
- Upgrades de Authentik: manuales, leyendo release notes, con backup previo (nunca Watchtower).
- Backup: DB de Authentik → B2 desde F2, + NAS desde F3 ([topología §6](../architecture/homelab-topology.md)).
- Simulacro semestral: restore de Authentik desde B2 usando solo secretos del escrow, partiendo de "el disco no existe".
