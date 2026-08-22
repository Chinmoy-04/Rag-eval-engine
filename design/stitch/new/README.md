# HelixForge Stitch export (new project)

**Project ID:** `7329311300505357317`  
**Pulled:** 2026-08-21  
**This is the current design source** (supersedes the older export in `design/stitch/html/`).

## Screens (5/6 OK)

Brand assets: [`brand/`](brand/) (wordmark + icon mark).

| Role | Screen ID | HTML | Preview |
|------|-----------|------|---------|
| **Ask** | `e1701ac91b444840a5c1775f1dee8424` | [html/ask.html](html/ask.html) | [images/ask.png](images/ask.png) |
| **Runs** | `410822530f0b4858a40874c1d1c759d8` | [html/runs.html](html/runs.html) | [images/runs.png](images/runs.png) |
| **Compare** | `d150c6243c154d958a7219c2790fd1ce` | [html/compare.html](html/compare.html) | [images/compare.png](images/compare.png) |
| **Run detail** | `64b48ab7ab2f4f208aaec649d26e48ad` | [html/run_detail.html](html/run_detail.html) | [images/run_detail.png](images/run_detail.png) |
| **Ask (mobile layout)** | `b8f6ac5d78254834a79df1bf6e3aa680` | [html/ask_mobile.html](html/ask_mobile.html) | screenshot blank / incomplete |
| *(failed export)* | `060b15787a444ccdae35fd8dee01950a` | — | empty HTML URL from Stitch |

## Design notes (v2)

- Brand: **HelixForge** + **RAG EVAL**
- Fonts: **Space Grotesk** + **JetBrains Mono**
- Accent teal, border `#1E2833`, dark charcoal shell
- Nav: Ask / Runs / Compare
- Pipelines in Ask: Baseline RAG · Degraded Vectors · Optimized v2.4
- Runs table + Compare RAGAS bars + Run detail execution traces

## Next

Say **“restyle Streamlit from Stitch new”** to apply these screens to `src/dashboard/app.py`.
