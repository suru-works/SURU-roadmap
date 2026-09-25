# SURUworks Design System — MASTER

> Source of Truth para todos los componentes visuales de la plataforma SURUworks.
> Generado con ui-ux-pro-max el 2025-05-02.

---

## Pattern: Enterprise Gateway + Trust & Authority

### Conversion Focus
- Path selection ("I am a...") para visitantes de negocio vs. desarrolladores
- Trust signals prominentes antes del CTA
- CTA principal: "Solicitar consultoría" | CTA secundario: "Ver proyectos"

### Section Order (Landing)
1. Hero (misión + CTA fuerte)
2. Soluciones por área (Dev, AI, Diseño, 3D)
3. Proyectos destacados (herramientas interactivas)
4. Señales de confianza (tecnologías, proceso, sobre el fundador)
5. Contacto / CTA final

---

## Style: Flat Design

| Atributo | Valor |
|---------|-------|
| Modo | 2D, sin sombras, sin gradientes |
| Soporte dark mode | Completo |
| Performance | Excelente |
| Accesibilidad | WCAG 2.2 AA (pares verificados con `scripts/check_contrast.py`) |
| Keywords | minimalist, bold colors, clean lines, simple shapes, typography-focused |

---

## Color Palette

| Role | Hex | CSS Variable |
|------|-----|--------------|
| Primary | `#0F172A` | `--color-primary` |
| On Primary | `#FFFFFF` | `--color-on-primary` |
| Secondary | `#334155` | `--color-secondary` |
| On Secondary | `#FFFFFF` | `--color-on-secondary` |
| Accent / CTA | `#0369A1` | `--color-accent` |
| Accent Hover | `#075985` | `--color-accent-hover` |
| On Accent | `#FFFFFF` | `--color-on-accent` |
| Accent on Dark (links y focus en secciones oscuras) | `#7DD3FC` | `--color-accent-on-dark` |
| Background | `#F8FAFC` | `--color-background` |
| Foreground | `#020617` | `--color-foreground` |
| Card | `#FFFFFF` | `--color-card` |
| Card Foreground | `#020617` | `--color-card-foreground` |
| Muted | `#E8ECF1` | `--color-muted` |
| Muted Foreground | `#475569` | `--color-muted-foreground` |
| Border (separadores decorativos) | `#E2E8F0` | `--color-border` |
| Input Border | `#64748B` | `--color-input-border` |
| Destructive | `#DC2626` | `--color-destructive` |
| Ring / Focus | `#0369A1` | `--color-ring` |

**Notas:** Navy profesional + CTA blue — comunica confianza, autoridad técnica, modernidad.
Los valores viven también en [`tokens.css`](tokens.css); `python scripts/check_contrast.py` falla si ambos se desalinean o si un par pierde el contraste mínimo.

### Pares de contraste verificados (WCAG 2.2 AA)

Mínimo 4.5:1 para texto (1.4.3) y 3:1 para bordes de controles y focus rings (1.4.11). Los fondos literales son los de las secciones de [`pages/landing.md`](pages/landing.md) y el hover del botón ghost.

| Uso | Primer plano | Fondo | Ratio | Mínimo |
|-----|--------------|-------|-------|--------|
| Texto base | `--color-foreground` (`#020617`) | `--color-background` (`#F8FAFC`) | 19.28:1 | 4.5:1 |
| Texto en card | `--color-card-foreground` (`#020617`) | `--color-card` (`#FFFFFF`) | 20.17:1 | 4.5:1 |
| Botón secundario (hover) | `--color-primary` (`#0F172A`) | `--color-background` (`#F8FAFC`) | 17.06:1 | 4.5:1 |
| Texto en sección navy | `--color-on-primary` (`#FFFFFF`) | `--color-primary` (`#0F172A`) | 17.85:1 | 4.5:1 |
| Texto en secondary | `--color-on-secondary` (`#FFFFFF`) | `--color-secondary` (`#334155`) | 10.35:1 | 4.5:1 |
| Botón primario | `--color-on-accent` (`#FFFFFF`) | `--color-accent` (`#0369A1`) | 5.93:1 | 4.5:1 |
| Botón primario (hover) | `--color-on-accent` (`#FFFFFF`) | `--color-accent-hover` (`#075985`) | 7.56:1 | 4.5:1 |
| Texto secundario | `--color-muted-foreground` (`#475569`) | `--color-background` (`#F8FAFC`) | 7.24:1 | 4.5:1 |
| Texto secundario en card | `--color-muted-foreground` (`#475569`) | `--color-card` (`#FFFFFF`) | 7.58:1 | 4.5:1 |
| Texto secundario en muted | `--color-muted-foreground` (`#475569`) | `--color-muted` (`#E8ECF1`) | 6.39:1 | 4.5:1 |
| Texto secundario en sección Proyectos | `--color-muted-foreground` (`#475569`) | `#F1F5F9` | 6.92:1 | 4.5:1 |
| Link | `--color-accent` (`#0369A1`) | `--color-background` (`#F8FAFC`) | 5.67:1 | 4.5:1 |
| Link en card | `--color-accent` (`#0369A1`) | `--color-card` (`#FFFFFF`) | 5.93:1 | 4.5:1 |
| Link en sección Proyectos | `--color-accent` (`#0369A1`) | `#F1F5F9` | 5.42:1 | 4.5:1 |
| Botón ghost (hover) | `--color-accent` (`#0369A1`) | `#EFF6FF` | 5.45:1 | 4.5:1 |
| Link en sección navy | `--color-accent-on-dark` (`#7DD3FC`) | `--color-primary` (`#0F172A`) | 10.71:1 | 4.5:1 |
| Link en footer | `--color-accent-on-dark` (`#7DD3FC`) | `#020617` | 12.10:1 | 4.5:1 |
| Texto de error | `--color-destructive` (`#DC2626`) | `--color-background` (`#F8FAFC`) | 4.62:1 | 4.5:1 |
| Texto de error en card | `--color-destructive` (`#DC2626`) | `--color-card` (`#FFFFFF`) | 4.83:1 | 4.5:1 |
| Borde de input | `--color-input-border` (`#64748B`) | `--color-card` (`#FFFFFF`) | 4.76:1 | 3.0:1 |
| Borde de input sobre fondo | `--color-input-border` (`#64748B`) | `--color-background` (`#F8FAFC`) | 4.55:1 | 3.0:1 |
| Borde de input en sección Proyectos | `--color-input-border` (`#64748B`) | `#F1F5F9` | 4.34:1 | 3.0:1 |
| Borde de input (focus) | `--color-accent` (`#0369A1`) | `--color-card` (`#FFFFFF`) | 5.93:1 | 3.0:1 |
| Borde de input (error) | `--color-destructive` (`#DC2626`) | `--color-card` (`#FFFFFF`) | 4.83:1 | 3.0:1 |
| Focus ring en Servicios | `--color-ring` (`#0369A1`) | `--color-background` (`#F8FAFC`) | 5.67:1 | 3.0:1 |
| Focus ring en Confianza / cards | `--color-ring` (`#0369A1`) | `--color-card` (`#FFFFFF`) | 5.93:1 | 3.0:1 |
| Focus ring en Proyectos | `--color-ring` (`#0369A1`) | `#F1F5F9` | 5.42:1 | 3.0:1 |
| Focus ring en Hero / Contacto | `--color-accent-on-dark` (`#7DD3FC`) | `--color-primary` (`#0F172A`) | 10.71:1 | 3.0:1 |
| Focus ring en Footer | `--color-accent-on-dark` (`#7DD3FC`) | `#020617` | 12.10:1 | 3.0:1 |
| Focus ring en banner CTA | `--color-accent-on-dark` (`#7DD3FC`) | `--color-accent` (`#0369A1`) | 3.56:1 | 3.0:1 |

### Dark Mode Palette (futura implementación)

| Role | Hex |
|------|-----|
| Background | `#0F172A` |
| Foreground | `#F8FAFC` |
| Card | `#1E293B` |
| Primary | `#38BDF8` |
| Accent | `#7DD3FC` |
| Border | `#334155` |

---

## Typography

### Font Pairing: Tech Startup

| Rol | Fuente | Pesos |
|----|--------|-------|
| Headings | **Space Grotesk** | 400, 500, 600, 700 |
| Body | **DM Sans** | 400, 500, 700 |

**Mood:** tech, startup, modern, innovative, bold, futuristic  
**Ideal para:** empresas tech, startups, SaaS, herramientas para devs, productos AI

```css
/* Google Fonts Import */
@import url('https://fonts.googleapis.com/css2?family=DM+Sans:wght@400;500;700&family=Space+Grotesk:wght@400;500;600;700&display=swap');
```

```js
// Tailwind Config
fontFamily: {
  heading: ['Space Grotesk', 'sans-serif'],
  body: ['DM Sans', 'sans-serif'],
}
```

### Escala tipográfica

| Token | Tamaño | Peso | Line-height | Uso |
|-------|--------|------|-------------|-----|
| `display-xl` | 72px | 700 | 1.1 | Hero headline (desktop) |
| `display-lg` | 56px | 700 | 1.15 | Hero headline (mobile) |
| `heading-1` | 48px | 700 | 1.2 | Título de página |
| `heading-2` | 36px | 600 | 1.25 | Sección principal |
| `heading-3` | 28px | 600 | 1.3 | Subsección |
| `heading-4` | 22px | 600 | 1.35 | Títulos de card |
| `body-lg` | 18px | 400 | 1.6 | Párrafos principales |
| `body-md` | 16px | 400 | 1.6 | Cuerpo de texto base |
| `body-sm` | 14px | 400 | 1.5 | Texto secundario |
| `caption` | 12px | 500 | 1.4 | Labels, metadata |
| `code` | 14px | 400 | 1.6 | Código (monospace) |

---

## Spacing System (8pt base)

```
4px  → space-1  (micro separaciones)
8px  → space-2  (padding compacto)
12px → space-3
16px → space-4  (padding estándar)
24px → space-6  (separación de elementos)
32px → space-8  (separación de grupos)
48px → space-12 (separación de secciones)
64px → space-16 (separación mayor)
96px → space-24 (secciones hero)
```

---

## Layout & Breakpoints

| Breakpoint | Ancho | Gutter | Container max-width |
|-----------|-------|--------|---------------------|
| Mobile | 375px+ | 16px | 100% |
| Tablet | 768px+ | 24px | 720px |
| Desktop | 1024px+ | 32px | 960px |
| Wide | 1440px+ | 40px | 1280px |

---

## Effects & Interactions

- **Sombras:** ninguna (Flat Design) — usar `border` para delimitar elementos
- **Border radius:** 8px standard, 12px cards, 4px botones
- **Hover states:** color shift + `cursor-pointer` (sin shadow)
- **Transitions:** `150ms ease-out` para micro-interacciones, `200ms ease` para modales
- **Focus ring:** 2px solid `var(--color-ring)`, offset 2px; en secciones oscuras (navy, footer, banner CTA) usar `var(--color-accent-on-dark)`

---

## Component Standards

### Botones

```css
/* Primary */
bg: #0369A1 | text: #FFFFFF | hover: #075985 | radius: 6px | padding: 12px 24px

/* Secondary */
bg: transparent | border: 1px #E2E8F0 | text: #0F172A | hover: bg #F8FAFC

/* Ghost */
bg: transparent | text: #0369A1 | hover: bg #EFF6FF
```

### Cards

```css
bg: #FFFFFF | border: 1px solid #E2E8F0 | radius: 12px | padding: 24px
```

### Inputs

```css
border: 1px solid #64748B | focus: border #0369A1 | radius: 6px | height: 44px min
```

---

## Icons

- Librería: **Lucide React** (stroke-width: 1.5px, tamaño estándar: 20px)
- Nunca usar emojis como íconos estructurales
- Íconos de navegación: siempre con label de texto

---

## Accessibility Checklist

- [ ] Contraste mínimo 4.5:1 para texto normal
- [ ] Contraste mínimo 3:1 para texto grande (18px+ bold)
- [ ] Contraste mínimo 3:1 para bordes de inputs y focus rings contra su fondo
- [ ] Focus rings visibles en todos los interactivos
- [ ] Alt text en todas las imágenes significativas
- [ ] `aria-label` en botones solo-ícono
- [ ] Orden tab = orden visual
- [ ] `prefers-reduced-motion` respetado
- [ ] Touch targets ≥ 44×44px en mobile

---

## Anti-patterns (NUNCA hacer)

- Animaciones excesivas o decorativas
- Dark mode por defecto (iniciar en light)
- Emojis como íconos de navegación
- Sombras o gradientes (rompen el flat design)
- Texto < 12px en el body
- Colores hardcodeados en componentes (usar CSS variables)
- Hover como única interacción (accessibility fail)
