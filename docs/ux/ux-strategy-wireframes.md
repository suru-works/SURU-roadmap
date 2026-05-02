# SURUworks — UX Strategy & Information Architecture

> Diseñado por agente UX especializado el 2025-05-02.
> Design system aplicado: Flat Design, #0F172A navy, #0369A1 blue CTA, Space Grotesk + DM Sans.

---

## 1. Information Architecture

### Sitemap

```
SURUworks
├── / (Home)
├── /services
│   ├── /services/software-development
│   ├── /services/ai-solutions
│   ├── /services/ux-design
│   └── /services/3d-printing
├── /projects
│   └── /projects/:slug (individual project/tool page)
├── /about
├── /contact
└── Auth (headless, no dedicated page)
    ├── /auth/signup (modal or inline)
    └── /auth/login (modal or inline)
```

### Public vs. Protected

| URL | Public | Auth Required |
|---|---|---|
| / | yes | — |
| /services/* | yes | — |
| /projects | yes | — |
| /projects/:slug (view + limited trial) | yes | — |
| /projects/:slug (full tool usage, save results) | — | yes |
| /about | yes | — |
| /contact | yes | — |
| /dashboard (saved results, history) | — | yes |

### Primary Navigation (6 items)

```
Logo  |  Services  Projects  About  |  Contact  [Try a Tool →]
```

Items: **Services · Projects · About · Contact** + CTA button **"Try a Tool"** (accent blue, siempre visible en header).

### Footer Sitemap

```
Company          Services              Tools                Legal
About            Software Dev          Image to 3D          Privacy Policy
Contact          AI Solutions          [tool 2]             Terms of Use
Blog             UX / UI Design        [tool 3]
                 3D Printing
```

---

## 2. ASCII Wireframes

### A) Landing / Home — 1440px Desktop

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ HEADER (sticky, 64px tall, bg #0F172A)                                                            │
│  ┌─────────────┐                                                                                  │
│  │ SURU works  │   Services    Projects    About    Contact              [ Try a Tool → ]          │
│  └─────────────┘                                                         (bg #0369A1, pill btn)   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  HERO (full-width, bg #0F172A, min-height 92vh)                                                   │
│                                                                                                   │
│  ┌──────────────────────────────────────────┐   ┌────────────────────────────────────────┐       │
│  │                                          │   │                                        │       │
│  │  [TAG PILL: "Open to new projects →"]    │   │   ╔══════════════════════════════╗     │       │
│  │                                          │   │   ║  [ animated abstract shape   ║     │       │
│  │  We build software that                  │   │   ║    flat geometric, bold lines ║     │       │
│  │  thinks, looks great,                    │   │   ║    navy + blue tones,         ║     │       │
│  │  and ships fast.                         │   │   ║    CSS keyframe animation ]   ║     │       │
│  │  (Space Grotesk, 64px, white)            │   │   ╚══════════════════════════════╝     │       │
│  │                                          │   │                                        │       │
│  │  Custom software · AI · Design · 3D      │   │                                        │       │
│  │  (DM Sans, 18px, #94A3B8)               │   │                                        │       │
│  │                                          │   │                                        │       │
│  │  [ Book a Consultation ]  [ Try our Tools]  │                                        │       │
│  │   (solid #0369A1, lg)     (outline, white)  │                                        │       │
│  └──────────────────────────────────────────┘   └────────────────────────────────────────┘       │
│                                                                                                   │
│  ┌──────────────── SCROLL INDICATOR ────────────────────────────────────────────────────────┐    │
│  │                      ↓  scroll                                                           │    │
│  └──────────────────────────────────────────────────────────────────────────────────────────┘    │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  TRUST BAR (bg #F1F5F9, 72px)                                                                    │
│  Built with:  Python   FastAPI   React   TypeScript   OpenAI   AWS   Three.js   Figma            │
│               (grayscale logos, 28px tall, evenly spaced)                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  SERVICES SECTION (bg #F8FAFC, padding 96px 0)                                                   │
│                                                                                                   │
│  What we do   (Space Grotesk, 40px, #0F172A, centered)                                           │
│                                                                                                   │
│  ┌───────────────┐ ┌───────────────┐ ┌───────────────┐ ┌───────────────┐                        │
│  │  [ ICON ]     │ │  [ ICON ]     │ │  [ ICON ]     │ │  [ ICON ]     │                        │
│  │               │ │               │ │               │ │               │                        │
│  │ Software Dev  │ │ AI Solutions  │ │ UX / Design   │ │ 3D Printing   │                        │
│  │               │ │               │ │               │ │               │                        │
│  │ Description 3 │ │ Description 3 │ │ Description 3 │ │ Description 3 │                        │
│  │ lines max     │ │ lines max     │ │ lines max     │ │ lines max     │                        │
│  │               │ │               │ │               │ │               │                        │
│  │ [Learn more→] │ │ [Learn more→] │ │ [Learn more→] │ │ [Learn more→] │                        │
│  └───────────────┘ └───────────────┘ └───────────────┘ └───────────────┘                        │
│   (card: white, 1px border #E2E8F0, 16px radius, hover: blue border-left accent)                 │
│                                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  FEATURED PROJECTS / LIVE TOOLS (bg #0F172A, padding 96px 0)                                     │
│                                                                                                   │
│  Try something now.           →  [See all projects]                                              │
│  (white, 40px)                   (text link, #0369A1)                                            │
│                                                                                                   │
│  ┌──────────────────────────────────────┐  ┌──────────────────────────────────────┐              │
│  │  [  PROJECT THUMBNAIL / PREVIEW   ]  │  │  [  PROJECT THUMBNAIL / PREVIEW   ]  │              │
│  │  Image → 3D                          │  │  [Tool Name 2]                       │              │
│  │  Upload any photo, get a 3D model    │  │  Short description                   │              │
│  │  [AI] [3D] [Free]                    │  │  [TAG] [TAG]                         │              │
│  │               [ Try it free → ]      │  │                [ Try it free → ]     │              │
│  └──────────────────────────────────────┘  └──────────────────────────────────────┘              │
│   (card: bg #1E293B, 16px radius, hover: scale 1.02)                                              │
│                                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│                                                                                                   │
│  ABOUT / FOUNDER STRIP (bg #F8FAFC, padding 96px 0)                                              │
│  ┌───────────────────────┐  ┌──────────────────────────────────────────────────────────────┐     │
│  │  [FOUNDER PHOTO]      │  │  Made by a builder who ships.  (Space Grotesk, 36px)         │     │
│  │  [social links]       │  │  Engineer by training, designer by obsession...              │     │
│  └───────────────────────┘  │  ● X years experience  ● N projects  ● Based in Colombia   │     │
│                              │                                         [ Read my story → ] │     │
│                              └──────────────────────────────────────────────────────────────┘     │
│                                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PROCESS STRIP (bg white, padding 64px 0)                                                        │
│  01 Discover ── 02 Define ── 03 Build ── 04 Ship & Support                                       │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  CTA BANNER (bg #0369A1, centered, padding 80px 0)                                               │
│  Have a project in mind?   (Space Grotesk, 48px, white)                                          │
│  Let's build it together — no agency overhead, direct communication.                             │
│                     [ Book a free 30-min call ]   (bg white, text #0369A1)                       │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  FOOTER (bg #0F172A, padding 64px 0)                                                             │
│  Company | Services | Tools | [Newsletter signup input] [Subscribe]                              │
│  © 2025 SURUworks · Privacy · Terms          Made in Colombia                                   │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### B) Projects / Portfolio Page

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER — same sticky nav]                                                                        │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PAGE HEADER (bg #0F172A, padding 80px 0)                                                        │
│  Projects & Tools  (Space Grotesk, 56px, white)                                                  │
│  Things I've built. Most of them are live — try them right here.                                  │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  FILTER BAR (sticky below header, 56px, bg #F8FAFC)                                              │
│  [ All ]  [ AI Tools ]  [ Web Apps ]  [ 3D / Design ]  [ Open Source ]          [Search 🔍]     │
│   (pill tabs, active = bg #0369A1 white, inactive = outline #E2E8F0)                             │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PROJECT GRID (3 columns, padding 64px 0)                                                        │
│  ┌─────────────────────────┐  ┌─────────────────────────┐  ┌─────────────────────────┐           │
│  │ [PREVIEW IMAGE 240px]   │  │ [PREVIEW IMAGE 240px]   │  │ [PREVIEW IMAGE 240px]   │           │
│  │ [AI] [Free]             │  │ [Web] [Open Source]     │  │ [3D] [Paid]             │           │
│  │ Image → 3D              │  │ Project Name            │  │ Project Name            │           │
│  │ Description 2 lines max │  │ Description 2 lines max │  │ Description 2 lines max │           │
│  │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │  │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │  │ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─ ─  │           │
│  │ [ Try it free → ]       │  │ [ View project → ]      │  │ [ Try it → ]            │           │
│  └─────────────────────────┘  └─────────────────────────┘  └─────────────────────────┘           │
│  [Load more]  (centered, outline, solo si >9 proyectos)                                           │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### C) Individual Project Page — Image-to-3D Tool

```
┌──────────────────────────────────────────────────────────────────────────────────────────────────┐
│ [HEADER — sticky]                                                                                 │
│ BREADCRUMB: Projects / Image → 3D                                                                │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  PAGE HEADER (bg #0F172A, padding 64px 0)                                                        │
│  Image → 3D    [AI] [Free tier] [Beta]                                                           │
│  Upload any photo. Get a 3D model ready for printing or rendering.                               │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  TOOL INTERFACE (bg #F8FAFC, padding 64px 0)                                                     │
│                                                                                                   │
│  ┌────────────────────────────────────────┐  ┌──────────────────────────────────────────────┐   │
│  │  UPLOAD PANEL                          │  │  OUTPUT PANEL                                │   │
│  │                                        │  │                                              │   │
│  │  ┌──────────────────────────────────┐  │  │  ┌──────────────────────────────────────┐   │   │
│  │  │  Drag & drop your image here     │  │  │  │                                      │   │   │
│  │  │  — or —                          │  │  │  │  [THREE.JS 3D VIEWER                 │   │   │
│  │  │  [ Browse files ]                │  │  │  │   interactive, orbit controls        │   │   │
│  │  │  JPG · PNG · WEBP · Max 10 MB    │  │  │  │   bg: dark, model centered]          │   │   │
│  │  └──────────────────────────────────┘  │  │  │                                      │   │   │
│  │  (dashed border, hover: solid blue)    │  │  │  [ ↻ rotate ] [ ⤢ fullscreen ]       │   │   │
│  │                                        │  │  └──────────────────────────────────────┘   │   │
│  │  OPTIONS ▾                             │  │                                              │   │
│  │  Output quality: Draft · Standard · HD │  │  [ Download .glb ]   [ Download .obj ]      │   │
│  │  Output format:  ☑ GLB  ☐ OBJ  ☐ FBX  │  │  (solid #0369A1)     (outline)              │   │
│  │                                        │  │                                              │   │
│  │  [ Generate 3D Model ]                 │  │  ┌──────────────────────────────────────┐   │   │
│  │  (solid #0369A1, full width, 48px)     │  │  │  Want to save this? [ Create account]│   │   │
│  │                                        │  │  └──────────────────────────────────────┘   │   │
│  └────────────────────────────────────────┘  └──────────────────────────────────────────────┘   │
│                                                                                                   │
│  PROCESSING STATE (replaces output panel during 30-120s):                                        │
│  ████████████████████░░░░░░░░  68%  — Generating mesh from image...                              │
│  This usually takes 30–90 seconds.                                                               │
│                                                                                                   │
├──────────────────────────────────────────────────────────────────────────────────────────────────┤
│  HOW IT WORKS:  01 Upload  →  02 AI processes  →  03 Download                                    │
│  RELATED TOOLS: ← [Previous]                                          [Next] →                  │
└──────────────────────────────────────────────────────────────────────────────────────────────────┘
```

---

### D) Services Page

```
PAGE HEADER → What we build together / The fastest path from idea to shipped product.

SERVICE BLOCK (alternating image/text layout):
  Left: Flat illustration (480×360) | Right: Service title, bullet capabilities, CTA
  (alternates: image right for block 2, left for block 3, right for block 4)

PROCESS (bg #0F172A):
  01 Discover → 02 Define → 03 Build → 04 Ship & Support

FAQ (accordion, bg #F8FAFC):
  ▾ Do you work with international clients?
  ▾ What is your pricing model?
  ▾ How long does a typical project take?
  ▾ Can I hire you for a specific task only?

CTA BANNER (same as homepage)
```

---

### E) Contact Page

```
PAGE HEADER → Let's talk about your project. / No commitment. Just a conversation.

┌────────────────────────────────────────┐  ┌────────────────────────────────┐
│  CONTACT FORM                          │  │  SIDEBAR INFO                  │
│  Name | Email | Service type (radio)   │  │  What happens next? (4 steps)  │
│  Project description (textarea)        │  │  ─────────────────────────────  │
│  Budget range (optional select)        │  │  Prefer a call?                │
│  [ Send message ]  (solid #0369A1)     │  │  [ Book on Calendly → ]        │
│  "I'll reply within 24 hours."         │  │  hello@suruworks.co            │
└────────────────────────────────────────┘  └────────────────────────────────┘

SUCCESS STATE: ✓ Message received. I'll be in touch within 24 hours.
  [ Back to home ]   [ Browse projects while you wait → ]
```

---

## 3. Navigation Strategy

### Primary Nav Items

```
[Logo]   Services   Projects   About   Contact   [Try a Tool →]
```

**Sticky Header Behavior:**
- Default: semi-transparent dark header with `backdrop-filter: blur`.
- On scroll past hero: fully opaque `#0F172A`, 1px bottom border.

**Mobile Navigation:**
- Hamburger icon (44×44px, top-right)
- Full-screen slide-down overlay (not sidebar drawer — more flat-design aligned)
- Overlay bg `#0F172A`, items stacked vertically at 56px tall
- CTA pinned at bottom of mobile overlay

---

## 4. Hero Section Strategy

### Primary Message

```
We build software that
thinks, looks great, and ships fast.
```

- **Primary CTA**: "Book a free 30-min call" → Calendly or contact form
- **Secondary CTA**: "Try a free tool" → /projects

**Background**: CSS/SVG animated geometric composition (flat shapes, no video, no stock photo). Zero performance cost, loads instantly.

---

## 5. Trust Building — Pre-Portfolio Stage

1. **Technology expertise bar** — specific logos (TripoSR, LangChain, Three.js, FastAPI, CUDA), not generic
2. **Live tools as proof of craft** — working Image-to-3D is more persuasive than case study slides
3. **Founder transparency** — real photo, real LinkedIn, first person About copy
4. **Process documentation** — 4-step scope-to-ship on Services page
5. **Open source contributions** — GitHub link, active repos
6. **Testimonials slot** — structure ready, first ones from collaborators/technical reviewers
7. **Country and availability** — "Based in Colombia, available globally" signals competitive rate

---

## 6. Project Showcase UX Patterns

### Upload UX — Image-to-3D

- Drag-and-drop zone fills the left panel
- Formats listed inside zone before upload: `JPG · PNG · WEBP · Max 10 MB`
- On drag-enter: bg changes to `#EFF6FF`, border goes solid blue
- On file select: thumbnail shown immediately (FileReader API)
- Invalid file: inline error below zone, border turns red
- Never silently accept and fail server-side

### Processing State (30-120s wait)

```
State 1 (0-3s):    Skeleton placeholder — animated shimmer, 3D viewer outline
State 2 (3s+):     Progress bar (indeterminate → determinate as API reports progress)
                   Label: "Generating mesh…" → "Applying textures…" → "Finalizing…"
State 3 (done):    3D viewer fades in, controls active
```

Page title changes to: `"Processing… | SURUworks"` so tabbed-away users know status.

### Error Messages

| Error | Message shown |
|---|---|
| API timeout | "This one took too long. Try a simpler image or try again." |
| Unsupported content | "We couldn't generate a model from this image. Try a clear, single-subject photo." |
| Server error | "Something went wrong on our end. We've logged it — try again in a few minutes." |
| No internet | "Check your connection and try again." |

---

## 7. User Flows

### Flow 1: Potential Client → Books Consultation

```
Lands on homepage → reads hero → scrolls to Services → clicks service card
→ reads service detail → clicks "Book a scoping call" → /contact
→ fills form → submits → success state → auto-response email (5min)
→ personal reply within 24h with Calendly link
```

**Critical drop-off**: Services page must answer "Is this person real and capable?" before user contacts.

### Flow 2: Developer → Discovers Tool → Creates Account → Returns

```
Finds Image-to-3D (social/HN) → lands on /projects/image-to-3d
→ scrolls to tool (no account needed) → uploads image
→ waits 45s, sees progress bar → 3D viewer loads → downloads .glb
→ sees upsell card → clicks "Create free account" → Google OAuth (2 clicks)
→ result saved automatically
→ returns next day via utility email "Your model is ready"
```

**Retention hook**: first email is a utility action email, not a newsletter. Highest-converting re-engagement.

### Flow 3: Visitor → Reads About → Subscribes

```
Lands via search → reads homepage → About strip catches attention
→ clicks "Read my story" → /about
→ no immediate project need → sees footer newsletter
→ subscribes → confirmation email
→ monthly digest: 1 new tool + 1 technical post + 1 open project slot
→ 3 months later: client or referral source
```

---

## 8. Content Strategy

### Tone of Voice

**Use:** Direct, confident, first/second person ("We build", "You get", "I'll reply in 24h"). Specific numbers. Active verbs.

**Avoid:** "Innovative", "cutting-edge", "world-class", "passionate about". Jargon. Exclamation points. Superlatives without proof.

### Language Strategy

**Primary: English.** Secondary: Spanish (manual translation, not machine).

- Language toggle in header (EN | ES), persistent via localStorage
- About page can have Spanish as "native" version
- Do not launch Spanish until all copy is manually translated

### Key Messages Per Page

| Page | Primary message | Secondary message |
|---|---|---|
| Home | "We build software that thinks, looks great, and ships fast" | "Try a free AI tool right now" |
| Services | "From scope to ship — no agency overhead" | "Here's exactly how a project works" |
| Projects | "These tools are live. Try them." | "Built to show what's possible" |
| Project (tool) | "Upload an image, get a 3D model" | "No account needed to try" |
| About | "A real person who ships real products" | "Here's my background and how I work" |
| Contact | "Let's talk about your project" | "No commitment, just a conversation" |

### Hero Copy Recommendation

**Recommended (Option A — capability-first):**
```
We build software that
thinks, looks great, and ships fast.
```
Subtitle: Custom software · AI solutions · Design · 3D — from a single trusted partner.

---

## 9. Mobile-First Decisions

| Element | Desktop | Mobile |
|---|---|---|
| Hero illustration | right column | hidden (text only, centered) |
| Services section | 4-column grid | 1-column stack |
| Project grid | 3 columns | 1 column |
| Service blocks | side-by-side | image above, text below |
| Footer | 4 columns | 2 then 1 |
| Tool options | visible default | collapsed under accordion |
| Nav | full horizontal | hamburger overlay |

### 3D Viewer on Mobile

- Height: `min(280px, 40vh)`
- Single-finger drag = orbit, pinch = zoom
- First-load tooltip: "Touch to rotate" (3s then fades)
- Fullscreen: native `requestFullscreen` API
- Fallback: static render image if WebGL unavailable

---

## 10. Conversion Optimization

### Consulting Visitors (Primary Goal)

- CTA in header, mobile menu, hero, services page end, about page inline
- Exit-intent on /services and /contact: appear after 30s if mouse moves toward close
- Lead magnet: "Project scoping checklist" PDF (highest converting for consulting visitors)

### Tool Users (Secondary Goal)

- Upsell card appears only after successful generation (never before value delivered)
- Account creation as inline modal — user keeps seeing their result
- Google OAuth as primary sign-up (2 clicks)
- After sign-up: immediate confirmation "Your model is saved"

### Email Capture Points

| Location | Trigger | Value prop |
|---|---|---|
| Footer | Always visible | "Monthly digest: new tools + project notes" |
| After tool use (anonymous) | After download | "Get notified when new tools drop" |
| Exit intent (/services) | Mouse toward close | "Get the project scoping checklist" (lead magnet) |

---

## Implementation Priority Order

```
Phase 1 — Foundation (Week 1-2)
  /            Homepage (hero + services + one featured tool + about + CTA)
  /contact     Contact form + success state
  /about       Founder page
  Design system (tokens, components)

Phase 2 — Tools (Week 3-4)
  /projects         Project grid
  /projects/:slug   Image-to-3D tool fully functional

Phase 3 — Services depth + Auth (Week 5-6)
  /services          Services overview + detail blocks
  Auth modal         Google OAuth sign-up/login
  /dashboard         Saved results

Phase 4 — Growth (Week 7+)
  Email capture + digest
  Blog
  Additional tools
  Language toggle (ES)
```
