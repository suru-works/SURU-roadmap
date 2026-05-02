# SURUworks Projects/Tools Page — Design Override

> Overrides del MASTER.md específicos para el showcase de proyectos/herramientas.

---

## Layout Pattern: Tool Showcase Grid

```
[HEADER]
  ↓
[HERO SECTION]
  Título: "Herramientas que construí"
  Subtítulo: "Proyectos reales, disponibles para usar ahora"
  
[FILTER BAR]
  Tags: Todos | AI | Utilidades | 3D | Productividad
  
[TOOLS GRID]
  Cards 3×N en desktop, 2×N tablet, 1×N mobile
  Cada card: thumbnail, nombre, descripción, tags, "Usar ahora" CTA
  
[FEATURED TOOL]
  Tool destacado con demo integrada (iframe o componente)
  
[CTA BOTTOM]
  "¿Tienes una idea para una herramienta?"
  → Link a contacto
```

---

## Tool Card Design

```css
/* Card container */
bg: #FFFFFF
border: 1px solid #E2E8F0
radius: 16px
padding: 0  /* imagen sin padding, contenido con padding */
overflow: hidden
transition: border-color 200ms ease

/* Card hover */
border-color: #0369A1
cursor: pointer

/* Card thumbnail */
height: 200px
bg: #F1F5F9
object-fit: cover

/* Card content */
padding: 20px 24px 24px

/* Tag badges */
bg: #EFF6FF
text: #0369A1
font-size: 12px
padding: 2px 8px
radius: 9999px
```

---

## Tool Page (Individual Project)

Para una herramienta como Image-to-3D:

### Sections

1. **Hero de herramienta**: nombre, descripción, "Usar gratis"
2. **Demo interactiva**: zona de interacción principal
3. **Cómo funciona**: 3 pasos visuales
4. **Especificaciones**: límites, formatos soportados
5. **Código fuente**: link a GitHub (si open source)

### Demo UX Flow (Image-to-3D)

```
[Estado 1: Vacío]
  ┌─────────────────────────────────┐
  │     Arrastra tu imagen aquí      │
  │         o haz clic para          │
  │          seleccionar             │
  │    [Formatos: JPG, PNG, WebP]    │
  │    [Tamaño máx: 10MB]            │
  └─────────────────────────────────┘
  
[Estado 2: Procesando]
  ┌─────────────────────────────────┐
  │  🔄 Procesando imagen...         │
  │  ████████░░░░░░░░  45%           │
  │  Generando modelo 3D             │
  │  Tiempo estimado: ~60s           │
  └─────────────────────────────────┘
  
[Estado 3: Resultado]
  ┌─────────────────────────────────┐
  │  [Visor 3D interactivo]          │
  │  [Rotar] [Zoom] [Reset]          │
  │                                  │
  │  [Descargar .OBJ] [Descargar .GLB]│
  │  [Procesar otra imagen]          │
  └─────────────────────────────────┘
```

### Sin login requerido para primera prueba
- Límite sin cuenta: 1 procesamiento gratis
- Con cuenta gratuita: 5/mes
- Con cuenta pro: ilimitado

---

## Color Overrides

| Elemento | Color | Razón |
|---------|-------|-------|
| Background | `#F8FAFC` | Más claro que FFFFFF para notar las cards |
| Tags activos | `#0369A1` | Consistente con CTA |
| Tags inactivos | `#E2E8F0` | Discreto |
| Progress bar | `#0369A1` | Familiar, tranquilizador |
| Success state | `#059669` | Verde, no alarmar |
| Error state | `#DC2626` | Rojo standard destructivo |
