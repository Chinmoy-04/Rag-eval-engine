# HelixForge RAG Eval — Design System Brief (for Stitch)

Use this document as the source of truth when generating **light theme** screens and brand assets. The **dark theme already exists** (Stitch project `7329311300505357317`); light mode should feel like the same product, not a different app.

---

## Product summary

**HelixForge RAG Eval** is an internal evaluation dashboard for a retrieval-augmented generation (RAG) system. Users:

- **Ask** — chat with company documents (live RAG)
- **Runs** — browse evaluation campaigns stored in SQLite
- **Compare** — compare pipeline quality (Ragas metrics + latency)

**Audience:** Engineers first, but copy and UI should stay understandable to non-technical stakeholders (HR, ops, leadership reviewing eval results).

**Tagline (header):** “Ask about company policies — see how well the system answers.”

**Tech context (do not show in UI):** React + Vite frontend, FastAPI backend, Chroma vector index, Ragas metrics.

---

## Brand

| Element | Spec |
|--------|------|
| **Product name** | HelixForge |
| **Product line** | RAG Eval (always secondary, below logo) |
| **Wordmark** | `HELI` + stylized helix **X** + `FORGE` (geometric sans, interlocking ribbon X) |
| **Icon mark** | Teal hexagon with interlocking helix paths inside |
| **Voice** | Precise, technical, trustworthy — not playful, not “AI startup purple” |

### Brand assets to export (light theme)

1. **HelixForge Wordmark (Dark)** — for light backgrounds (charcoal or near-black letterforms + teal helix X)
2. **HelixForge Icon Mark** — same hex icon; confirm contrast on light `#F5F7FA`-style background
3. Optional: **Theme toggle** icon/state (sun/moon) in header

Existing dark assets live in `design/stitch/brand/` (white wordmark + teal icon).

---

## Typography

| Role | Font | Notes |
|------|------|--------|
| **UI / headings** | [Space Grotesk](https://fonts.google.com/specimen/Space+Grotesk) | 400–700 |
| **Labels / metrics / code** | [JetBrains Mono](https://fonts.google.com/specimen/JetBrains+Mono) | Uppercase labels, table numbers, pipeline ids |

### Type scale (match dark theme)

| Token | Size | Weight | Use |
|-------|------|--------|-----|
| Page title | 24px | 600 | Ask / Runs / Compare H1 |
| Body | 14–16px | 400 | Paragraphs, chat, tables |
| Label caps | 11px | 700 | `RAG EVAL`, section labels — wide tracking (`0.14em–0.22em`) |
| Small / meta | 12px | 400–500 | Latency, sources, hints |

**RAG Eval** under the logo: mono, bold, uppercase, wide tracking, **teal accent** — must read as prominent secondary branding (not a footnote).

---

## Color system

### Design principles

- **Teal is the only accent** — links, active nav, primary buttons, chart highlight (`optimized` pipeline)
- **No purple / violet AI clichés**
- **Surfaces:** layered depth (bg → panel → elevated → chip), subtle borders — not flat white boxes with heavy shadows
- **Light mode:** soft cool gray base, not pure white `#FFFFFF` page fill; panels slightly elevated; borders visible but subtle
- **Dark mode reference:** keep existing values below as the `.dark` theme

### Dark theme tokens (existing — do not change)

| Token | Hex | Use |
|-------|-----|-----|
| `hf-bg` | `#0B0F14` | Page background |
| `hf-panel` | `#101419` | Cards, chat bubbles (assistant) |
| `hf-rail` | `#0C1016` | Sidebar |
| `hf-border` | `#1E2833` | Dividers, inputs, panels |
| `hf-elevated` | `#1A222C` | Hover states, user message bg |
| `hf-chip` | `#27313D` | Inactive pills, toggles off |
| `hf-text` | `#E8EEF5` | Primary text |
| `hf-muted` | `#8B9AAB` | Secondary text, placeholders |
| `hf-teal` | `#2DD4BF` | Primary accent |
| `hf-teal-bright` | `#57F1DB` | RAG Eval label, glows |
| `hf-teal-dim` | `#0A3D38` | Teal tint backgrounds |

**Background pattern (dark):** 24×24px grid, lines `rgba(30,40,51,0.18)`.

### Light theme tokens (to design)

Provide exact hex values on a **Design tokens / Light theme** screen:

| Token | Target feel | Guidance |
|-------|-------------|----------|
| `hf-bg` | Cool off-white | e.g. `#F4F6F9` – `#F8FAFC` |
| `hf-panel` | White or near-white card | Slightly above bg |
| `hf-rail` | Sidebar — distinct from main | 1 step darker than bg or same with border |
| `hf-border` | Cool gray border | Visible on light bg, e.g. `#D8DEE6` – `#E2E8F0` |
| `hf-elevated` | Hover / selected row | Subtle gray, e.g. `#EEF2F6` |
| `hf-chip` | Pill / toggle track off | `#E2E8F0` range |
| `hf-text` | Near-black | e.g. `#0F172A` – `#1E293B` |
| `hf-muted` | Medium gray | e.g. `#64748B` – `#94A3B8` |
| `hf-teal` | **Same or slightly deeper** | Keep `#2DD4BF` or use `#0D9488` for AA on white |
| `hf-teal-bright` | RAG Eval, highlights | Can match dark `#57F1DB` or darken slightly for contrast |
| `hf-teal-dim` | Teal tint bg | Very light mint wash, e.g. `#CCFBF1` at 40% opacity |

**Background pattern (light):** Same 24px grid, lower contrast — e.g. `rgba(15,23,42,0.06)`.

**Charts (Compare page):** 3 series — `degraded` (gray), `baseline` (mid gray), `optimized` (teal). Must remain distinguishable on light bg.

---

## Layout shell (desktop 1440px)

```
┌─────────────────────────────────────────────────────────────┐
│ SIDEBAR 256px          │ HEADER (sticky, 56px)               │
│                        ├─────────────────────────────────────┤
│ [Wordmark]             │                                     │
│ RAG EVAL               │  MAIN CONTENT (scroll)              │
│                        │                                     │
│ ● Ask                  │                                     │
│   Runs                 │                                     │
│   Compare              │                                     │
│                        │                                     │
│ ─────────────────      │                                     │
│ footer meta            │                                     │
└─────────────────────────────────────────────────────────────┘
```

- **Sidebar:** fixed left, 256px (`w-64`), border-right, subtle backdrop blur
- **Header:** sticky, one line muted tagline; **add theme toggle** top-right (sun/moon)
- **Main:** max-width content ~768px (Ask) or ~1152px (Compare), padding 24px
- **Active nav:** teal tint bg + 2px left inset bar in teal (same pattern as dark)

Reference dark HTML: `design/stitch/new/html/ask.html`, `runs.html`, `compare.html`.

---

## Screens to generate (light theme)

Generate **desktop** screens that mirror dark layout 1:1. Name files clearly.

| # | Screen name | Based on (dark) | Priority |
|---|-------------|-----------------|----------|
| 1 | **Design tokens — Light** | — | P0 |
| 2 | **HelixForge Wordmark (Dark)** | inverse of white wordmark | P0 |
| 3 | **HelixForge Icon Mark (Light bg)** | existing icon on light | P1 |
| 4 | **Ask — Light** | `e1701ac91b444840a5c1775f1dee8424` | P0 |
| 5 | **Runs — Light** | `410822530f0b4858a40874c1d1c759d8` | P0 |
| 6 | **Compare — Light** | `d150c6243c154d958a7219c2790fd1ce` | P0 |
| 7 | **Theme toggle component** | — | P1 |

---

## Page specs

### 1. Ask (light)

**Purpose:** Chat with handbook; pick RAG pipeline; try example questions.

**Layout (top → bottom):**

1. **Title:** “Ask the employee handbook”
2. **Subtitle:** Plain language — search indexed docs, show sources
3. **Pipeline panel** (card):
   - Label: “Pipeline”
   - Row: document count + “Show sources” toggle
   - Pills: `baseline` · `degraded` · `optimized` (technical ids, not renamed)
   - One-line hint per selected pipeline
4. **Example questions** (empty state): 2-column grid of category cards (Quick facts, Time off, etc.)
5. **Chat area:** user bubbles (teal tint), assistant bubbles (panel + border), error (red border)
6. **Input bar:** sticky bottom — text field + teal “Ask” button

**Do not:** cram pipeline + examples + index health in one sidebar column (old layout). Main column only.

---

### 2. Runs (light)

**Purpose:** Table of eval campaigns.

**Content:**

- H1: “Runs” — subtitle mentions SQLite / test batches
- **Stat cards (3):** Total runs · Last avg Faithfulness (with ⓘ tooltip) · Latest run id
- **Table columns:** Run · Created · Questions · Status · Pipelines · Errors · Faith
- Sample data: run_id 3, 40 questions, baseline/degraded/optimized

---

### 3. Compare (light)

**Purpose:** Side-by-side pipeline metrics for one test batch.

**Content:**

- H1: “Compare” — subtitle mentions same test set, Ragas 0–100%
- **Batch selector:** dropdown `Batch #3`
- **Summary cards:** Best faithfulness · Questions tested
- **Metric legend row:** Faithfulness · Relevancy · Precision · Recall (each with ⓘ tooltip — names stay technical)
- **Charts (full width, stacked):**
  - Ragas averages — grouped horizontal bars (3 pipelines × 4 metrics)
  - Average latency — horizontal bars per pipeline
- **Pipeline detail cards (×3):** baseline / degraded / optimized — metric list + latency
- **Expandable:** Per-question faithfulness table

**Chart colors:** optimized = teal; baseline/degraded = two gray steps.

---

## Components checklist

Design these consistently across light screens:

| Component | Light notes |
|-----------|-------------|
| **Card / panel** | Rounded-xl (~12px), 1px border, no heavy drop shadow |
| **Primary button** | Teal fill, dark text on button for contrast |
| **Pipeline pills** | Selected = teal fill; unselected = border + elevated bg |
| **Toggle** | Teal when on; chip gray when off |
| **Nav item** | Active = teal tint + left accent bar |
| **Tooltip** | Dark tooltip on light UI is OK; or light popover with border |
| **Table** | Subtle row borders; mono for numeric columns |
| **Chat bubble** | User: teal 15% bg; Assistant: panel + border |
| **Theme toggle** | Header top-right; icon button, hover elevated |

---

## Content & terminology (keep exact strings)

| UI label | Notes |
|----------|--------|
| Nav | Ask · Runs · Compare |
| Pipelines | `baseline` · `degraded` · `optimized` |
| Metrics | Faithfulness · Relevancy · Precision · Recall |
| Product line | RAG Eval (under logo) |
| Pipeline hints | k=4 context-only / k=1 truncated / k=8 query expansion |

Do **not** rename metrics or pipelines to “friendly” names in the design — tooltips carry plain-language explanations.

---

## Motion & atmosphere (reference only — implemented in code)

- Subtle ambient **beams** or grid (lower opacity in light mode)
- Smooth scroll (Lenis), gentle chart enter animations
- Keep light theme **calm** — avoid flashy gradients

---

## Accessibility

- Body text contrast **≥ 4.5:1** on light backgrounds
- Teal on white: verify `#2DD4BF` meets AA for small text; darken if needed
- Focus rings: teal outline on inputs and buttons
- Tooltip targets: minimum 44×44px touch area for ⓘ icons

---

## Anti-patterns (avoid)

- Purple / indigo primary colors
- Generic “AI chat” bubble gradients
- Light mode = pure white `#FFFFFF` everywhere
- Replacing pipeline/metric names with marketing copy
- Cramped sidebar with pipeline + questions + stats stacked
- Wordmark too small; **RAG Eval** too faint under logo

---

## Deliverables checklist for Stitch export

After generation, export:

- [ ] PNG/SVG wordmark (dark, transparent background)
- [ ] PNG/SVG icon mark on light background
- [ ] HTML or screenshots for Ask, Runs, Compare (light)
- [ ] Token screen with hex table for all `hf-*` variables
- [ ] Note any new screen IDs in `design/stitch/light/README.md`

**Existing dark project ID:** `7329311300505357317`  
**Suggested light project title:** `HelixForge RAG Eval UI — Light`

---

## Reference files in repo

| Path | Description |
|------|-------------|
| `design/stitch/new/html/ask.html` | Dark Ask (canonical) |
| `design/stitch/new/html/runs.html` | Dark Runs |
| `design/stitch/new/html/compare.html` | Dark Compare |
| `design/stitch/light/` | **Light theme** exports (HTML + images + brand) |
| `design/stitch/brand/` | Dark wordmark + icon exports |
| `web/src/index.css` | Implemented dark tokens |

When light screens are ready, say: **“Apply the light Stitch theme”** with project + screen IDs.
