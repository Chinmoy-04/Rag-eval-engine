"""Download Stitch mono wordmark screens into design/stitch/brand/mono/."""
from __future__ import annotations

import shutil
import urllib.request
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MONO = ROOT / "design" / "stitch" / "brand" / "mono"
PUBLIC = ROOT / "web" / "public" / "brand"

SCREENS = {
    "helixforge-wordmark-mono-light.png": (
        "56b5e8e1a178433c94e26653f3888632",
        "https://lh3.googleusercontent.com/aida/AEtjO1VBjrrOJHdFvvzllrwOlI9jGNnhP-PNIuV6ei2st34ciQHz0kOKrmqLuf4eoUKArj1zY1zmbash4kNUaT-_J0SfZBaD8-UzPJxLnDNpKBQ-LHaQ-Htz87CTbxLPQR5C7AOETI76PE2qqz_YpdB_F19x6A_5grnsCNbqG2jipsYzGNcFm8nHqeVPgS1Fm6gojNugiHoDYu4QSDcvWe76D58pqBXlcNkUSrD8TgXHGafbrQTAu4jJR2E8TsY",
    ),
    "helixforge-wordmark-mono-dark.png": (
        "8248f46ebace40f5991ee02b866de3b0",
        "https://lh3.googleusercontent.com/aida/AEtjO1VQOjC7kDnX7gaBVkBksbi7_twvf2TFqA4PfYj1H4BC4zz49cFZ6LG-DuIXcCujlcYFS4n0HV2UciGFDYn_MMPvkTAhQt_mUeW1u-BmOq6uJulHpVT7RoI3whzc8UBpDv6xBoYcFueF3ROC9ewlLGeW2QMzJmYJ22BQVy-JyWUF2mU0kI6wwyxX3ksm_qnDZ7eUixw2su1qHGqH2LdDunMDUMHwoWlZ7DKeW86gWMfb0E-dWQ85sEEzgx8",
    ),
}


def download(url: str, dest: Path) -> None:
    dest.parent.mkdir(parents=True, exist_ok=True)
    req = urllib.request.Request(url, headers={"User-Agent": "curl/8.0"})
    with urllib.request.urlopen(req, timeout=120) as resp:
        dest.write_bytes(resp.read())
    print(f"  saved {dest.relative_to(ROOT)} ({dest.stat().st_size:,} bytes)")


def make_transparent(
    src: Path,
    dest: Path,
    bg_rgb: tuple[int, int, int],
    tolerance: int = 30,
) -> None:
    from PIL import Image

    img = Image.open(src).convert("RGBA")
    px = img.load()
    w, h = img.size
    r0, g0, b0 = bg_rgb
    for y in range(h):
        for x in range(w):
            r, g, b, a = px[x, y]
            if (
                abs(r - r0) <= tolerance
                and abs(g - g0) <= tolerance
                and abs(b - b0) <= tolerance
            ):
                px[x, y] = (r, g, b, 0)
            else:
                px[x, y] = (r, g, b, 255)
    bbox = img.getbbox()
    if bbox:
        img = img.crop(bbox)
    img.save(dest, "PNG")
    print(f"  saved {dest.relative_to(ROOT)} {img.size} (transparent)")


def main() -> None:
    print("Downloading Stitch mono wordmarks…")
    for filename, (_screen_id, url) in SCREENS.items():
        download(url, MONO / filename)

    make_transparent(
        MONO / "helixforge-wordmark-mono-light.png",
        MONO / "helixforge-wordmark-mono-light-transparent.png",
        bg_rgb=(255, 255, 255),
    )
    make_transparent(
        MONO / "helixforge-wordmark-mono-dark.png",
        MONO / "helixforge-wordmark-mono-dark-transparent.png",
        bg_rgb=(0, 0, 0),
    )

    PUBLIC.mkdir(parents=True, exist_ok=True)
    for name in (
        "helixforge-wordmark-mono-light-transparent.png",
        "helixforge-wordmark-mono-dark-transparent.png",
    ):
        shutil.copy2(MONO / name, PUBLIC / name)

    print("Done.")


if __name__ == "__main__":
    main()
