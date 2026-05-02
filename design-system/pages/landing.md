# SURUworks Landing Page — Design Override

> Overrides del MASTER.md específicos para la página de inicio.
> Patrón: Enterprise Gateway + Trust & Authority híbrido.

---

## Pattern: Trust & Authority + Conversion

**Conversion goal:** Consulta de servicios (primario) + prueba de herramientas (secundario)

### Section Order

```
1. [HERO]          — Propuesta de valor + CTA doble
2. [SOLUCIONES]    — 4 servicios con cards
3. [PROYECTOS]     — Featured tools interactivos
4. [CONFIANZA]     — Stack, proceso, fundador
5. [CONTACTO]      — CTA final + formulario
6. [FOOTER]        — Links + social
```

---

## Hero Section Overrides

- Background: `#0F172A` (dark navy solid — Flat Design, sin gradiente)
- Text: `#F8FAFC`
- Subtitulo: `#94A3B8`
- CTA Primario: "Solicitar consultoría" → bg `#0369A1`
- CTA Secundario: "Ver proyectos" → ghost button, border `#334155`
- Ilustración: SVG abstracto geométrico (no foto de stock)

## Color Strategy per Section

| Sección | Background | Texto | Notas |
|---------|-----------|-------|-------|
| Hero | `#0F172A` | `#F8FAFC` | Impacto visual máximo |
| Servicios | `#F8FAFC` | `#020617` | Limpio, legible |
| Proyectos | `#F1F5F9` | `#020617` | Diferenciación sutil |
| Confianza | `#FFFFFF` | `#020617` | Autoridad, limpieza |
| Contacto | `#0F172A` | `#F8FAFC` | Cierra el loop del hero |
| Footer | `#020617` | `#94A3B8` | Discreto, funcional |

---

## CTA Strategy

**Primary CTA:** "Solicitar consultoría" — aparece en: hero, sección contacto, header sticky (mobile)  
**Secondary CTA:** "Ver proyectos" — aparece en: hero, sección proyectos  
**Tertiary:** "Sobre SURUworks" — solo footer/header

### CTA Copy Variants (A/B testing futuro)
- "Hablar con Santiago" (personal)
- "Empezar proyecto" (orientado a acción)
- "Agendar llamada gratis" (bajo riesgo)

---

## Trust Signals (sin logos de clientes)

Para la etapa early-stage sin portfolio de grandes clientes:

1. **Stack badges:** logos de tecnologías (React, Spring Boot, TensorFlow, etc.)
2. **Contador de proyectos:** "X proyectos completados", "X herramientas publicadas"
3. **Fragmento de código/output:** mostrar calidad técnica real
4. **GitHub activity:** contribuciones open source
5. **Tiempo de respuesta:** "Respondo en < 24h"
6. **Proceso transparente:** 4 pasos del engagement

---

## Mobile Overrides

- Hero: `display-xl` → `heading-2` en mobile (56px → 36px)
- Servicios: grid 2×2 → stack 1×4 en mobile
- CTA flotante en mobile: sticky bottom bar con "Contactar"
- Proyectos: horizontal scroll cards en mobile
