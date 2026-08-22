"""Download Stitch HelixForge favicon (dark) into design/ and web/public/."""
from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
FAVICON_DIR = ROOT / "design" / "stitch" / "brand" / "favicon"
PUBLIC = ROOT / "web" / "public"

SCREEN_ID = "39a59dd075e74819991991cccc3f1467"
URL = (
    "https://lh3.googleusercontent.com/aida/AEtjO1WpjMKsDr3FuRYqc_i2RYFrLAiUr7QwZB0oIPQP1eiDEK7mlMjWdxlJoBGRfoBm1cWv-yBdV9BLoGL20tAvHV3uMTdx1LT4KoY8p5mRzl2eGxb93dDHkKRdIIgGk42ZpN4xqL04q0etaWaVSZV7_b-aE1HUzP7-kGiZ_nNbjDxgdiysnw0sHMZtcZ-KDS_Bd5wkfoigtbk54iMpr_WBMXMihUAIVgE-xk3AJjUI3l186I9a-dqg60JVEyw"
)


def main() -> None:
    from PIL import Image

    FAVICON_DIR.mkdir(parents=True, exist_ok=True)
    raw = FAVICON_DIR / "helixforge-favicon-dark.png"
    req = urllib.request.Request(URL, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        raw.write_bytes(resp.read())
    print(f"saved {raw.relative_to(ROOT)}")

    im = Image.open(raw).convert("RGBA")
    PUBLIC.mkdir(parents=True, exist_ok=True)
    for size, name in [
        (32, "favicon.png"),
        (180, "apple-touch-icon.png"),
        (512, "favicon-512.png"),
    ]:
        im.resize((size, size), Image.Resampling.LANCZOS).save(PUBLIC / name, "PNG")
        print(f"saved web/public/{name} ({size}px)")


if __name__ == "__main__":
    main()
