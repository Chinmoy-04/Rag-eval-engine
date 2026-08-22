# HelixForge Stitch export — Light theme

**Project ID:** `7329311300505357317`  
**Pulled:** 2026-08-22  
**Companion:** Dark export in [`../new/`](../new/) · Brief in [`../design.md`](../design.md)

## Screens

| Role | Screen ID | HTML | Preview |
|------|-----------|------|---------|
| **Ask — Light** | `1968b18cd393400d84767bbbcf8170dc` | [html/ask.html](html/ask.html) | [images/ask.png](images/ask.png) |
| **Runs — Light** | `79d5c84b6b9b492d852bcc81b3f3a256` | [html/runs.html](html/runs.html) | [images/runs.png](images/runs.png) |
| **Compare — Light** | `3ac312f4cdf24b10b77dcfee07937bcd` | [html/compare.html](html/compare.html) | [images/compare.png](images/compare.png) |
| **Icon Mark (Light BG)** | `c3eeb06d32024083860c3561eaa3b2cf` | — | [brand/helixforge-icon-mark-light.png](brand/helixforge-icon-mark-light.png) |
| **Wordmark (Dark)** | `a5067a0d7c8d44b7a5c2229affbe030b` | — | [brand/helixforge-wordmark-dark.png](brand/helixforge-wordmark-dark.png) |
| **Design System** | `asset-stub-assets_0039dd063bae41f29015d05858b0b766` | — | *(Stitch export failed — use tokens below)* |

## Brand assets (transparent)

| File | Use |
|------|-----|
| [brand/helixforge-wordmark-dark-transparent.png](brand/helixforge-wordmark-dark-transparent.png) | Light-mode sidebar wordmark |
| [brand/helixforge-icon-mark-light-transparent.png](brand/helixforge-icon-mark-light-transparent.png) | Light-mode icon |
| `web/public/brand/helixforge-wordmark-dark-transparent.png` | Copied for React app |
| `web/public/brand/helixforge-icon-light-transparent.png` | Copied for React app |

## Light theme tokens

Full token set extracted from Stitch HTML → [`tokens.json`](tokens.json):

| Token | Value | Notes |
|-------|-------|--------|
| `hf-bg` | `#F8FAFC` | Page background |
| `background` | `#FAF8FF` | Material surface tint |
| `hf-panel` | `#FFFFFF` | Cards, sidebar |
| `hf-border` / `hf-chip` | `#E2E8F0` | Borders, inactive pills |
| `hf-rail` / `hf-elevated` | `#F1F5F9` | Table header, elevated surfaces |
| `hf-teal-dim` | `rgba(13, 148, 136, 0.1)` | Active nav tint |
| `hf-text` | `#0F172A` | Primary text |
| `hf-muted` | `#64748B` | Secondary text |
| `primary` | `#00685F` | Teal accent |
| `grid-line` | `rgba(15, 23, 42, 0.06)` | 24×24px background grid |

Implement in `web/src/index.css` as `:root` (light) with existing `.dark` block unchanged.

## Re-fetch

```bash
uv run python scripts/fetch_stitch_light.py
```

## Stitch image source URLs

Screenshots downloaded via Stitch `get_screen_image`:

- Compare: `https://lh3.googleusercontent.com/aida/AEtjO1V50kgGyRDJxP4DwhV6Exqc_xQFrLDTCMMw8cHCdVP6yqt7818I5qJ6LYPAAhwqN8g3zVh0uh0IUHZsYP-Cswe9__vCrHOkW4MwLprSr2DYJWL8PkBdoEQOkaujkPYdqm7ePQ3dc_dJozKjKGf4MqJQPV9ReOzwi0RYjiGp_b5P0VM24AdeM6UiLvCMsWqTAC9MNrvnBLHUlhHmsEmNYfWzY3aP-CGSv04b-sz70Y_pDDIcV7foNvYik1E`
- Runs: `https://lh3.googleusercontent.com/aida/AEtjO1VDmJA5Aobhnktt2h5vU5oTBTDQWrDvZINAMnvmozjsrbQdW-hbSNqbfg-z95FEY0T3--xzu_EaTUNbNLOccdAfG0-_2rEezDGtHqTG5b470hP0loDqVRUINgXfa0OxLs7clduMI--4iTeIk7l3VFSakg2RDo7ktOODHb9_t4LUjzgCmG-B9qAlfnZ_JmI-xqg4soUqaLYXBzbA9WtXSOW_jpUr74YOxSgH5CflP3A1rjxqI0KOTMUUIlo`
- Ask: `https://lh3.googleusercontent.com/aida/AEtjO1UW_JOf2Uh4-RTO_VVwbEmdCmPvD4KMGzDb--8fPnc0OBdTGIJxIUxgqqh6AyeUNcxta1v7krfTEdAkDtXiLPJh2a5BNgGuop3SdLbULMKT9QU8e-Res3yoJWv4Qzm6juklb_QPziq7O6YAhyZRbiR3q3LsDj_ilva8n3lIgLL-4VdxsUwNpjaAL4bYB1zko7jy1kntPpspUtOq1X0nXfFAXusyrsfmT6XctXzGpMD5eTEdyadHIesl52M`
- Icon: `https://lh3.googleusercontent.com/aida/AEtjO1XTBAnAzQdELUoebABxyvTmrcYyxjYLkKzFml35SAl7HNVpIX4JIK_VLDdv6_nIqt6_KZUE9JAzqgokEKKVoKndKhX8gseN6x-A5FI89PwR9c0WR1_tPxnK46x65jlCqaIOM4qMi2Uzf-akRXGd7UBgIaA-FXRqg_XitFOYm4azhkx6Gxymn1HLgIzo8Gxx9dwYvVYlaVB3wRPyIun_ObmdtHj7lXmQRCnn5L8b4ESk1OQ6Pv_2E4q9ow`
- Wordmark: `https://lh3.googleusercontent.com/aida/AEtjO1W74pCzicQTLkOsFo_nPGYp3i76fmroCkhIMAh5wvApMXIceXwfJn3U5a7BT09Lg1Pvz51A-MI8MBw0TekbOO5mVk_Kji_wnd_5JFiRrX9TCu0yh5JEDJw4vLCumUaPJ-DlwZoAUCxrSdjr0mTFNb-uA2wsvBuwkOz2Qb2NzY8aUozxvlYaDkfIeT1HFdZHn25ZbZ7MZOuRGWfjTy_6pg9qMYLdtXvRCRq6LsW9F29xlZQrcIGPqs2s7ek`

## Applied in React

Light tokens are wired in `web/src/index.css` (`:root`) with dark in `.dark`. Theme toggle in the header; preference stored in `localStorage` (`hf-theme`) with system fallback.
