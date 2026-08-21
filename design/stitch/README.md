# HelixForge Stitch export

> **Current design:** use **[`new/`](new/)** (project `7329311300505357317`).  
> Everything below is the older export kept for reference.

**Project ID:** `13430568311430680757`  
**Pulled:** 2026-08-21  


## Primary screens (use these for Streamlit restyle)

| Role | Screen ID | HTML |
|------|-----------|------|
| **Ask (desktop)** | `5fc3fb1d32e0453d861a7f1177a4df50` | [html/ask_desktop.html](html/ask_desktop.html) |
| **Ask (alt / empty+chat)** | `f348b97cf82b4d76a209a5914d2288ba` | [html/ask_v2.html](html/ask_v2.html) |
| **Ask (mobile-ish)** | `7054094544d54e8985a0f52d08cd26c6` | [html/ask_compact.html](html/ask_compact.html) |
| **Runs** | `5324dcb9eb5c42a98833ffc16135a835` | [html/runs.html](html/runs.html) |
| **Runs (alt)** | `ef7c345a5fd64f1bbf73bc0085ed0cdb` | [html/runs_alt.html](html/runs_alt.html) |
| **Compare** | `288c5b76ec204c62b91952b548b37657` | [html/compare.html](html/compare.html) |
| **Compare (alt)** | `52b093ba999b4843b5b639cb179c0317` | [html/compare_alt.html](html/compare_alt.html) |
| **Run detail** | `1ec0ba2f0443482293403c3c1f8f956a` | [html/run_detail.html](html/run_detail.html) |

## Design tokens (from Stitch HTML)

- Background: dark charcoal (`bg-background` / `#0B0F14`-class)
- Accent teal: `#2DD4BF`
- Font: **Geist** (+ JetBrains Mono for data in some variants)
- Shell: fixed left nav — Ask / Runs / Compare
- Ask: chat thread + retrieved-context accordion + source chips + composer

## Also downloaded (raw IDs)

See `html/` for all pulled files. Screenshots in `images/` when download succeeded.

## Failed to export (6 screens)

Stitch returned empty/invalid HTML for these IDs (often drafts):

- `11ece934a46c477ea00e9a0459674dc8`
- `10aff66e1b8d4c1ea07f81f8de3049fe`
- `afa8ae1747c744f7a2a1fbe33d0c6043`
- `c2b6b428d36040df84ed816456030b7a`
- `f67a9c10197e49c59ccd6ae91dbc7213`
- `e4844d75a23743c586b4ff67f012db04`

## Next

Say **“restyle Streamlit from Stitch”** to apply Ask/Runs/Compare look to `src/dashboard/app.py`.
