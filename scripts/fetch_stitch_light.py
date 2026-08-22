"""Download Stitch light-theme exports into design/stitch/light/."""
from __future__ import annotations

import json
import re
import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
LIGHT = ROOT / "design" / "stitch" / "light"
PUBLIC_BRAND = ROOT / "web" / "public" / "brand"

IMAGES = {
    "images/compare.png": "https://lh3.googleusercontent.com/aida/AEtjO1V50kgGyRDJxP4DwhV6Exqc_xQFrLDTCMMw8cHCdVP6yqt7818I5qJ6LYPAAhwqN8g3zVh0uh0IUHZsYP-Cswe9__vCrHOkW4MwLprSr2DYJWL8PkBdoEQOkaujkPYdqm7ePQ3dc_dJozKjKGf4MqJQPV9ReOzwi0RYjiGp_b5P0VM24AdeM6UiLvCMsWqTAC9MNrvnBLHUlhHmsEmNYfWzY3aP-CGSv04b-sz70Y_pDDIcV7foNvYik1E",
    "images/runs.png": "https://lh3.googleusercontent.com/aida/AEtjO1VDmJA5Aobhnktt2h5vU5oTBTDQWrDvZINAMnvmozjsrbQdW-hbSNqbfg-z95FEY0T3--xzu_EaTUNbNLOccdAfG0-_2rEezDGtHqTG5b470hP0loDqVRUINgXfa0OxLs7clduMI--4iTeIk7l3VFSakg2RDo7ktOODHb9_t4LUjzgCmG-B9qAlfnZ_JmI-xqg4soUqaLYXBzbA9WtXSOW_jpUr74YOxSgH5CflP3A1rjxqI0KOTMUUIlo",
    "images/ask.png": "https://lh3.googleusercontent.com/aida/AEtjO1UW_JOf2Uh4-RTO_VVwbEmdCmPvD4KMGzDb--8fPnc0OBdTGIJxIUxgqqh6AyeUNcxta1v7krfTEdAkDtXiLPJh2a5BNgGuop3SdLbULMKT9QU8e-Res3yoJWv4Qzm6juklb_QPziq7O6YAhyZRbiR3q3LsDj_ilva8n3lIgLL-4VdxsUwNpjaAL4bYB1zko7jy1kntPpspUtOq1X0nXfFAXusyrsfmT6XctXzGpMD5eTEdyadHIesl52M",
    "brand/helixforge-icon-mark-light.png": "https://lh3.googleusercontent.com/aida/AEtjO1XTBAnAzQdELUoebABxyvTmrcYyxjYLkKzFml35SAl7HNVpIX4JIK_VLDdv6_nIqt6_KZUE9JAzqgokEKKVoKndKhX8gseN6x-A5FI89PwR9c0WR1_tPxnK46x65jlCqaIOM4qMi2Uzf-akRXGd7UBgIaA-FXRqg_XitFOYm4azhkx6Gxymn1HLgIzo8Gxx9dwYvVYlaVB3wRPyIun_ObmdtHj7lXmQRCnn5L8b4ESk1OQ6Pv_2E4q9ow",
    "brand/helixforge-wordmark-dark.png": "https://lh3.googleusercontent.com/aida/AEtjO1W74pCzicQTLkOsFo_nPGYp3i76fmroCkhIMAh5wvApMXIceXwfJn3U5a7BT09Lg1Pvz51A-MI8MBw0TekbOO5mVk_Kji_wnd_5JFiRrX9TCu0yh5JEDJw4vLCumUaPJ-DlwZoAUCxrSdjr0mTFNb-uA2wsvBuwkOz2Qb2NzY8aUozxvlYaDkfIeT1HFdZHn25ZbZ7MZOuRGWfjTy_6pg9qMYLdtXvRCRq6LsW9F29xlZQrcIGPqs2s7ek",
}

HTML = {
    "html/compare.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OTllNjZhNjBiNTEwMzU2ZWNhNGYyMmQzNmUyEgsSBxDOo6_imAUYAZIBIwoKcHJvamVjdF9pZBIVQhM3MzI5MzExMzAwNTA1MzU3MzE3&filename=&opi=89354086",
    "html/runs.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OTllNjVkODNlOWMwNDRmNTdhMDVlMzc4Mzg3EgsSBxDOo6_imAUYAZIBIwoKcHJvamVjdF9pZBIVQhM3MzI5MzExMzAwNTA1MzU3MzE3&filename=&opi=89354086",
    "html/ask.html": "https://contribution.usercontent.google.com/download?c=CgthaWRhX2NvZGVmeBJ7Eh1hcHBfY29tcGFuaW9uX2dlbmVyYXRlZF9maWxlcxpaCiVodG1sXzAwMDY1OTllNjZiODA0YjkwMzU2ZWRmM2UxMDQ2ODMyEgsSBxDOo6_imAUYAZIBIwoKcHJvamVjdF9pZBIVQhM3MzI5MzExMzAwNTA1MzU3MzE3&filename=&opi=89354086",
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    print(f"  saved {dest.relative_to(ROOT)} ({dest.stat().st_size:,} bytes)")


def extract_tokens(html_path: Path) -> dict[str, str]:
    text = html_path.read_text(encoding="utf-8")
    m = re.search(r'"colors":(\{[^}]+\})', text)
    if not m:
        return {}
    raw = m.group(1)
    pairs = re.findall(r'"([^"]+)":"([^"]+)"', raw)
    hf = {k: v for k, v in pairs if k.startswith("hf-") or k in {"primary", "background", "grid-line"}}
    return hf


def make_transparent(src: Path, dest: Path, bg_rgb: tuple[int, int, int], tolerance: int = 18) -> None:
    try:
        from PIL import Image
    except ImportError:
        print(f"  skip transparent {dest.name} (Pillow not installed)")
        shutil.copy2(src, dest)
        return

    img = Image.open(src).convert("RGBA")
    data = img.getdata()
    r0, g0, b0 = bg_rgb
    new = []
    for r, g, b, a in data:
        if abs(r - r0) <= tolerance and abs(g - g0) <= tolerance and abs(b - b0) <= tolerance:
            new.append((r, g, b, 0))
        else:
            new.append((r, g, b, a))
    img.putdata(new)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    dest.parent.mkdir(parents=True, exist_ok=True)
    img.save(dest, "PNG")
    print(f"  saved {dest.relative_to(ROOT)} (transparent)")


def main() -> None:
    print("Downloading Stitch light exports…")
    for rel, url in {**IMAGES, **HTML}.items():
        download(url, LIGHT / rel)

    tokens = extract_tokens(LIGHT / "html" / "ask.html")
    (LIGHT / "tokens.json").write_text(json.dumps(tokens, indent=2), encoding="utf-8")
    print(f"  saved design/stitch/light/tokens.json ({len(tokens)} tokens)")

    PUBLIC_BRAND.mkdir(parents=True, exist_ok=True)
    make_transparent(
        LIGHT / "brand" / "helixforge-wordmark-dark.png",
        LIGHT / "brand" / "helixforge-wordmark-dark-transparent.png",
        bg_rgb=(255, 255, 255),
    )
    make_transparent(
        LIGHT / "brand" / "helixforge-icon-mark-light.png",
        LIGHT / "brand" / "helixforge-icon-mark-light-transparent.png",
        bg_rgb=(248, 250, 252),  # #F8FAFC light bg
    )
    shutil.copy2(
        LIGHT / "brand" / "helixforge-wordmark-dark-transparent.png",
        PUBLIC_BRAND / "helixforge-wordmark-dark-transparent.png",
    )
    shutil.copy2(
        LIGHT / "brand" / "helixforge-icon-mark-light-transparent.png",
        PUBLIC_BRAND / "helixforge-icon-light-transparent.png",
    )
    print("Done.")


if __name__ == "__main__":
    main()
