# Sitio corporativo F1 — spec conciliado

> Qué se construye en `suruworks.com` durante la fase F1 de [homelab-topology §9](../architecture/homelab-topology.md) y cómo se entrega a `suru-infra`. Concilia los docs de 2025 (wireframes, design system, roadmap de 6 semanas) con el portafolio real inventariado en [platform-integration §2](../architecture/platform-integration.md). Redactado 2026-09-25.

**Estado:** Propuesto. La estructura, el esquema de contenido, el contrato de despliegue y los presupuestos de calidad se pueden construir sin más insumos. El copy y la navegación final dependen de las [decisiones abiertas](#8-decisiones-abiertas), que son del dueño.

---

## 1. Alcance

**Entra en F1:**

- Sitio **estático** generado con Astro (`output: 'static'`, sin SSR, sin endpoints, sin middleware). Stack según [tech-stack-2025](../stack/tech-stack-2025.md): Astro 5, zero JS por defecto.
- **Sin auth.** No hay cuentas, login, dashboard, cuotas ni newsletter. [group-sso](../auth/group-sso.md) ya fija que el sitio Astro va sin auth.
- Páginas de proyecto para **todo el inventario Tier 1-3** de platform-integration, alimentadas por una content collection (§3).
- Estilo visual según [design-system/MASTER.md](../../design-system/MASTER.md) y los tokens de [design-system/tokens.css](../../design-system/tokens.css).

**Queda fuera de F1:**

- La plataforma comercial (F5): el MFE shell, los microservicios, el flujo de subida y procesamiento de Image-to-3D, `/auth/*` y `/dashboard`. Las partes de [ux-strategy-wireframes](../ux/ux-strategy-wireframes.md) y [pages/projects.md](../../design-system/pages/projects.md) que dependen de eso no se construyen en F1 (ver §6).
- Los servicios en vivo de F2 y F4 (`auth.`, `revscope.`, `upflow.`, `ai.`, `argos.`). El sitio solo enlaza un subdominio cuando ese servicio ya existe (regla en §3.2).
- Los proyectos Tier 4, que nunca aparecen en el sitio.

## 2. Sitemap F1

Todas las rutas son públicas y ninguna requiere sesión.

| Ruta | Contenido | Fuente |
|---|---|---|
| `/` | Hero, servicios (sección, no páginas propias), proyectos destacados, confianza, contacto, footer. Mismo orden de secciones que [pages/landing.md](../../design-system/pages/landing.md) | Copy: decisiones 1-4. Proyectos: la collection |
| `/projects/` | Grilla de todos los proyectos Tier 1-3, agrupados o filtrados por tier y etiqueta | Collection `projects` |
| `/projects/<slug>/` | Una página por proyecto (§4) | Entrada de la collection + README del repo |
| `/about/` | Qué es SURU, la sección "¿Por qué SURU?" que recomienda [brand-identity](../brand/brand-identity.md) y quiénes hacen el trabajo | Copy: decisiones 2 y 3 |
| `/contact/` | Mecanismo de contacto (decisión 5) y datos de contacto | Decisión 5 |
| `/legal/` | Aviso de privacidad y tratamiento de datos (Ley 1581/2012, si hay formulario), licencias y atribuciones (AGPL, atribución de Lumina §7(b), licencias de pesos de modelos) y oferta de código fuente de las instancias AGPL | Decisión 7 + campos `license`/`attribution` de la collection |
| `/404.html` | Página de error propia | — |
| `/sitemap-index.xml`, `/robots.txt` | Generados en el build (`@astrojs/sitemap`) con `site: 'https://suruworks.com'` | — |

Con `trailingSlash: 'always'` y `build.format: 'directory'` (el default), cada ruta termina en `<ruta>/index.html`. Los enlaces internos se escriben siempre con barra final para que nginx no tenga que redirigir (§5).

## 3. Content collection `projects`

Una entrada Markdown por proyecto en `src/content/projects/<slug>.md`. El frontmatter lleva los datos estructurados y el cuerpo el texto de la página. El inventario manda: **el sitio no agrega un proyecto que no esté en platform-integration §2**. Si hay un repo nuevo, primero se actualiza ese doc.

### 3.1 Campos

| Campo | Tipo | Obligatorio | Uso |
|---|---|---|---|
| `title` | string | sí | Nombre visible del proyecto |
| `summary` | string, ≤160 caracteres | sí | Card de `/projects/` y meta description |
| `tier` | `1` \| `2` \| `3` | sí | Mismo tier que en platform-integration §2 |
| `status` | `showcase` \| `live` \| `members-only` | sí | `showcase`: página y enlaces a repo o descargas, sin instancia. `live`: instancia pública. `members-only`: instancia tras SSO |
| `hosting` | `none` \| `node-01` \| `rig` | sí | Dónde corre la instancia, si existe |
| `license` | identificador SPDX | sí | Licencia del repo según su `LICENSE`/README |
| `links.repo` | URL | no | Repo público. Un repo privado no se enlaza |
| `links.downloads` | URL | no | Releases, APK, instalador o marketplace |
| `links.subdomain` | URL | no | Instancia en `*.suruworks.com` |
| `links.source` | URL | no | Código fuente de **la versión desplegada** (AGPL §13) |
| `attribution` | string | no | Texto de atribución visible que exige la licencia |
| `stack` | string[] | sí | Tecnologías reales del proyecto. De aquí salen las señales de confianza (§6) |
| `tags` | string[] | sí | Filtros de `/projects/`. La taxonomía es la decisión 9 |
| `readme.repo` | string | sí | Repo del que se tomó el contenido |
| `readme.commit` | SHA git | sí | Commit del README leído, para saber cuándo el texto quedó viejo |
| `order` | entero | no | Orden en la home y en `/projects/` |

`best-effort` no es un campo, se deriva: toda página con `hosting: rig` muestra el aviso de servicio best-effort que exige platform-integration §3 ("el rig no es 24/7"). Así no puede quedar una página del rig sin el aviso.

### 3.2 Reglas que el schema rechaza en el build

Se validan con `superRefine`, un predicado con nombre por regla, para que el build falle antes de publicar algo incorrecto:

1. `status` es `live` o `members-only` → `links.subdomain` es obligatorio.
2. `status` es `showcase` → `links.subdomain` debe faltar. En F1 no se enlazan servicios que todavía no existen.
3. `license` empieza por `AGPL` y hay `links.subdomain` → `links.source` es obligatorio (nota transversal de platform-integration §1).
4. `hosting: rig` → `status` no puede ser `live`. Los servicios del rig son solo para miembros (platform-integration §3).
5. `readme.repo` es `lumina-calendar` y falta `attribution` → error. La atribución §7(b) es obligatoria. La regla mira `readme.repo` porque el schema recibe los datos de la entrada, no su slug.

Boceto (Astro 5, content layer):

```ts
// src/content.config.ts
import { defineCollection } from 'astro:content';
import { glob } from 'astro/loaders';
import { z } from 'astro/zod';

const links = z.object({
  repo: z.string().url().optional(),
  downloads: z.string().url().optional(),
  subdomain: z.string().url().optional(),
  source: z.string().url().optional(),
});

const project = z.object({
  title: z.string(),
  summary: z.string().max(160),
  tier: z.union([z.literal(1), z.literal(2), z.literal(3)]),
  status: z.enum(['showcase', 'live', 'members-only']),
  hosting: z.enum(['none', 'node-01', 'rig']),
  license: z.string(),
  links: links.default({}),
  attribution: z.string().optional(),
  stack: z.array(z.string()).min(1),
  tags: z.array(z.string()).min(1),
  readme: z.object({ repo: z.string(), commit: z.string().regex(/^[0-9a-f]{7,40}$/) }),
  order: z.number().int().default(100),
});

export const collections = {
  projects: defineCollection({
    loader: glob({ pattern: '*.md', base: './src/content/projects' }),
    schema: project.superRefine(enforcePublicationRules),
  }),
};
```

`enforcePublicationRules` compone las cinco reglas de arriba, una función pura por regla, y cada una tiene su prueba unitaria.

### 3.3 Fuentes de contenido

- El cuerpo de cada página sale del **README del repo del proyecto** (clon local del dueño): qué es, qué resuelve, cómo se instala o se usa y sus límites conocidos. Se reescribe con la voz del sitio (decisión 3), no se copia entero. Las capturas salen del repo o se toman del proyecto real, nunca de stock ([brand-identity](../brand/brand-identity.md), "Iconografía de marca").
- `readme.commit` guarda el SHA leído. Actualizar una página es releer el README desde ese commit, ajustar el texto y subir el SHA.
- Si el README y platform-integration se contradicen, la página no elige ninguno de los dos: el caso se anota como decisión abierta (ejemplo: decisión 11).

## 4. Proyectos Tier 1-3 y su página en F1

La licencia sale del `LICENSE` o README de cada repo (leídos 2026-09-25). El estado F1 aplica la regla 2 de §3.2: ningún proyecto enlaza una instancia que todavía no existe.

| Proyecto | Slug | Tier | `status` en F1 | `hosting` | Licencia (repo) | Enlaces en F1 | Notas de la página |
|---|---|---|---|---|---|---|---|
| **revscope-server** | `revscope-server` | 1 | `showcase` (`revscope.` llega en F2) | node-01 | MIT | repo | Explica el modelo OIDC y su relación con la app RevScope. Licencia en discusión: decisión 11 |
| **lumina-calendar** | `lumina-calendar` | 1 | `showcase` hasta el OK del coautor, después `live` en `lumina.suruworks.com` | node-01 | AGPL-3.0 + atribución §7(b) | repo; subdominio y `links.source` solo tras el OK | Atribución visible a Diego Álvarez (coautor) obligatoria |
| **bipolar-code** | `bipolar-code` | 1 | `showcase` (`ai.` solo miembros desde F4) | rig | MIT | repo si es público | Aviso best-effort. No se documenta ni se enlaza el plano `/api/*` |
| **Upflow** | `upflow` | 1 | `showcase` (`upflow.` solo miembros desde F4) | rig | MIT | repo si es público | Aviso best-effort; capturas del estudio |
| **Argos** | `argos` | 2 | `showcase` (demo `argos.` solo miembros desde F4, footage sintético) | rig | AGPL-3.0-or-later (los pesos de modelos tienen licencias propias) | repo si es público | Ninguna imagen con footage real ni rostros reales. Explica el enforcement técnico de platform-integration §2 |
| **Leviathan** | `leviathan` | 2 | `showcase` | none | MIT | repo si es público | Solo docs. Sin cuentas ni resultados que parezcan promesa de rentabilidad |
| **STFU** | `stfu` | 3 | `showcase` | none | MIT (según el README; el repo no tiene archivo `LICENSE`) | repo, instalador | Catálogo de modelos con la licencia de cada uno |
| **OpenWinBlue** | `openwinblue` | 3 | `showcase` | none | GPL-3.0 | repo, descargas | Llamado a testers |
| **Nodo** | `nodo` | 3 | `showcase` | none | MIT (según el README; el repo no tiene archivo `LICENSE`) | repo; APK cuando haya release firmado (el README lo lista como pendiente) | Historia de ecosistema con bipolar-code y RevScope |
| **RevScope** (app Android) | `revscope` | 3 | `showcase` | none | Apache-2.0 | repo, APK o Play | Enlaza a la página de revscope-server; la conexión al servidor del grupo es F2 |
| **Ports ONNX** (GMFSS, audiosr, bs-roformer, openunmix, uvr-deecho) | `ports-onnx` | 3 | `showcase` | none | MIT (código; los pesos tienen licencias propias) | un repo y los artefactos por cada port | Una página para los cinco, con una sección por port |
| **Plugins CC** (bipolar/copilot/ollama-plugin-cc) | `plugins-cc` | 3 | `showcase` | none | MIT | repo o marketplace por plugin | Una página para los tres |
| **local-llm-homelab** | `local-llm-homelab` | 3 | `showcase` | none | sin licencia declarada (ni `LICENSE` ni sección en el README) | repo | Material de blog técnico. Revisar que no publique datos de la red de casa |

"Repo si es público": el build solo enlaza repos que respondan públicamente. Un repo privado deja la página sin `links.repo`.

## 5. Contrato de despliegue con `suru-infra`

Hoy `suru-infra` (repo privado) sirve el placeholder del sitio desde `nodes/node-01/site/html`, con un contenedor `nginx:1.29-alpine` que monta ese directorio de solo lectura detrás de Traefik. El contrato F1 es:

1. **Artefacto:** `astro build` produce `dist/`, que es 100 % estático: HTML, CSS, JS de islas si hubiera, fuentes e imágenes. No depende de Node en runtime.
2. **Entrega:** el contenido de `dist/` reemplaza el contenido de `nodes/node-01/site/html/` en node-01. El placeholder actual desaparece. El volumen se monta como directorio, así que un `mv` de carpeta no llega al contenedor ya corriendo: hay que sincronizar en el sitio (`rsync --delete`) o recrear el contenedor después de cambiar la carpeta. Quién hace la entrega (manual, CI o Komodo) es la decisión 6.
3. **Config de `astro.config`:** `site: 'https://suruworks.com'`, `output: 'static'`, `trailingSlash: 'always'`, `build.format: 'directory'`. Los assets con hash van en `/_astro/`.
4. **Cambios que necesita `suru-infra`** (se hacen allá, no en este repo): un `default.conf` de nginx montado de solo lectura con
   - `error_page 404 /404.html;`: la config por defecto de la imagen no usa la 404 de Astro;
   - `absolute_redirect off;`: detrás de Traefik, nginx arma redirecciones con `http://`, y así se evitan saltos de esquema;
   - `gzip on` para `text/html`, `text/css`, `application/javascript`, `image/svg+xml`;
   - `Cache-Control: public, max-age=31536000, immutable` en `/_astro/` y `no-cache` en `*.html`;
   - cabeceras de seguridad (CSP sin `unsafe-eval`, `X-Content-Type-Options`, `Referrer-Policy`) en nginx o como middleware de Traefik.
5. **Sin terceros en runtime:** las fuentes (Space Grotesk y DM Sans) se sirven desde el propio sitio. No hay CDN de fuentes, analítica ni widgets externos salvo que el dueño los decida. Así no hay cookies ni banner de consentimiento, y Lighthouse no depende de hosts ajenos.
6. **Verificación previa a la entrega:** se prueba con la **misma imagen y la misma config** que en node-01: `docker run` de `nginx:1.29-alpine` con `dist/` y el `default.conf` montados. Lighthouse y axe (§7) corren contra ese contenedor, no contra `astro dev`.

## 6. Qué se toma de los docs existentes y qué no

| Doc | Se usa en F1 | No se usa en F1 |
|---|---|---|
| [MASTER.md](../../design-system/MASTER.md) + `tokens.css` | Tokens, tipografía, grid, breakpoints, componentes, checklist de accesibilidad, anti-patrones y pares de contraste verificados | — |
| [pages/landing.md](../../design-system/pages/landing.md) | Orden de secciones, color por sección y overrides móviles | "Stack badges" con una lista fija de tecnologías: se derivan del campo `stack` de la collection. El CTA depende de la decisión 4 |
| [pages/projects.md](../../design-system/pages/projects.md) | Layout de grilla, card y colores | "Usar ahora", demo integrada y el flujo de subida: son de F5. En F1 el CTA de cada card es "Ver proyecto" y, si existe, el repo o la descarga. Los filtros esperan la decisión 9 |
| [ux-strategy-wireframes](../ux/ux-strategy-wireframes.md) | Estructura general de home, contacto y footer | Botón "Try a Tool", rutas `/auth/*` y `/dashboard`, newsletter, límites de uso por cuenta y exit-intent |
| [roadmap](../roadmap.md), semana 2 | Lista de piezas de la home | Paquete `@suruworks/ui` como requisito previo: es del monorepo de F5 y en F1 los componentes viven en el propio sitio. Resend como formulario: es la decisión 5 |

## 7. Presupuestos de calidad (criterios de salida del build)

| Chequeo | Umbral | Dónde |
|---|---|---|
| Lighthouse, perfil móvil: Performance, Accessibility, Best Practices y SEO | **≥ 90** en cada categoría | `/`, `/projects/`, una `/projects/<slug>/` y `/contact/`, contra el contenedor nginx de §5.6 |
| axe-core (`@axe-core/playwright`, tags `wcag2a`, `wcag2aa`, `wcag21aa`, `wcag22aa`) | **0 violaciones** de impacto `serious` o `critical` | Todas las rutas del sitemap, en 375 px y 1440 px |
| Contraste de tokens | `python scripts/check_contrast.py` sale con 0 | Este repo; el sitio importa los mismos tokens |
| `astro check` | 0 errores | Repo del sitio |
| Schema de la collection | El build falla si una entrada rompe §3.2; cada regla tiene su prueba | Repo del sitio |
| Enlaces internos | 0 rotos en `dist/` | Repo del sitio |
| JavaScript | 0 KB por defecto. Una isla se justifica en su PR | Repo del sitio |

## 8. Decisiones abiertas

Son del dueño. El build puede montar estructura, collection, estilos y despliegue sin ellas, pero no puede publicar copy ni navegación final hasta que estén respondidas las decisiones 1-6.

1. **Idioma primario.** Los docs de 2025 dicen inglés primario ([brand-identity](../brand/brand-identity.md), "Tono oficial"; spec y wireframes), pero el placeholder en vivo, este repo y los CTAs de landing.md están en español. Opciones: (a) inglés con español después; (b) español con inglés después; (c) bilingüe desde el día 1 con rutas `/en/` o `/es/` (i18n de Astro), que duplica el copy y las pruebas. Cambia el `lang` del HTML, las rutas y el texto de cada proyecto.
2. **Nombre visible.** "SURUworks" siempre (checklist de brand-identity), "SURU" solo (recomendación opcional del mismo doc) o "SURU." (placeholder en vivo). Cambia logo, `<title>`, meta y footer.
3. **Voz.** Fundador en primera persona singular ("Hablar con Santiago", "Things I've built", franja de fundador en los wireframes) o grupo con miembros ("nosotros"; docs de 2026-08 y group-sso). Cambia `/about`, el CTA y los textos de cada proyecto.
4. **CTA principal sin herramienta pública.** El CTA de los wireframes era probar Image-to-3D, que es F5. Opciones: (a) contacto o consultoría; (b) "Ver proyectos"; (c) Lumina en vivo, que requiere el OK explícito del coautor; (d) descargas de STFU u OpenWinBlue.
5. **Mecanismo de contacto.** nginx estático no procesa un POST. Opciones: (a) `mailto:` (cero infraestructura; expone la dirección); (b) servicio de formularios de un tercero (sin infraestructura propia; agrega un procesador de datos personales); (c) contenedor propio en node-01 que envía con Resend o SMTP (más superficie en el nodo Tier-0 y otra API key en custodia); (d) el buzón de correo que ya existe en el dominio. Con (b) o (c) hace falta la autorización de tratamiento de datos de Ley 1581 en el formulario y en `/legal`.
6. **Repo y pipeline del sitio.** Opciones de repo: (a) repo nuevo en la org `suru-works`; (b) `apps/corporate-mfe` dentro del monorepo Nx de F5, que todavía no existe. Opciones de entrega: build local + `rsync`, CI que publica un artefacto que node-01 descarga, o imagen propia en lugar del volumen de nginx. Opciones de visibilidad: público o privado.
7. **Titular legal y contenido de `/legal`.** Persona natural o empresa constituida como responsable del tratamiento de datos. Dirección y canal para ejercer derechos de habeas data. Si hay términos de uso o solo aviso de privacidad y licencias.
8. **Servicios.** Sección en la home (propuesta de este spec) o páginas `/services/*` como en el sitemap del wireframe. Las páginas propias exigen copy por servicio, incluido "Impresión y modelado 3D".
9. **Taxonomía de filtros y señales de confianza.** Hay tres taxonomías en los docs (projects.md, roadmap y wireframe) y ninguna encaja con el inventario real. Hay que elegir etiquetas (por ejemplo por área, por plataforma o por tier). También hay que decidir si las señales de confianza muestran el stack derivado de `stack` o una selección curada.
10. **Lumina en F1.** Si se pide ya el OK del coautor para publicar `lumina.suruworks.com` en F1, como dice homelab-topology, o si Lumina entra como `showcase` hasta tenerlo.
11. **Licencia de revscope-server.** platform-integration §2 lo describe como AGPL ("link al fuente desde la instancia"), pero el `LICENSE` y el README del repo dicen MIT. Hay que decidir cuál vale y corregir el otro.
12. **Proyectos fuera del inventario.** Hay repos con forma de Tier 3 que platform-integration §2 no lista, como otros ports ONNX y antigravity-plugin-cc. Por la regla de §3, no entran al sitio hasta que el dueño actualice el inventario.
13. **Copy, foto, bio, redes y agenda.** Texto final, foto y bio (si la voz es de fundador), enlaces a redes y si se enlaza una agenda tipo Calendly.
