#!/usr/bin/env python3
"""Download section images (client hero + Pexels) and update content/*/_index.md."""
from __future__ import annotations

import re
import urllib.error
import urllib.request
from io import BytesIO
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
CONTENT = ROOT / "content"
IMAGES_DIR = ROOT / "static" / "images"

PEX = "https://images.pexels.com/photos/{id}/pexels-photo-{id}.jpeg?auto=compress&cs=tinysrgb&w=900"

PEXELS: dict[str, tuple[str, str]] = {
    "breakfast.webp": (PEX.format(id="2092900"), "Pexels #2092900"),
    "starters.webp": (PEX.format(id="247117"), "Pexels #247117"),
    "salads.webp": (PEX.format(id="1128678"), "Pexels #1128678"),
    "protein-add-ons.webp": (PEX.format(id="376464"), "Pexels #376464"),
    "plates.webp": (PEX.format(id="2233348"), "Pexels #2233348"),
    "kids-menu.webp": (PEX.format(id="1640774"), "Pexels #1640774"),
    "pastas.webp": (PEX.format(id="4518843"), "Pexels #4518843"),
    "cachapas.webp": (PEX.format(id="1435907"), "Pexels #1435907"),
    "menu-add-ons.webp": (PEX.format(id="410648"), "Pexels #410648"),
    "parrillas.webp": (PEX.format(id="2696037"), "Pexels #2696037"),
    "chicken-pork-specials.webp": (PEX.format(id="2092897"), "Pexels #2092897"),
    "main-course.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
    "sides.webp": (PEX.format(id="2284163"), "Pexels #2284163"),
    "fast-food.webp": (PEX.format(id="1639565"), "Pexels #1639565"),
    "virgin-drinks.webp": (PEX.format(id="1199957"), "Pexels #1199957"),
    "drinks.webp": (PEX.format(id="274192"), "Pexels #274192"),
    "slideshow-parrillas.webp": (PEX.format(id="2696037"), "Pexels #2696037"),
    "slideshow-breakfast.webp": (PEX.format(id="2092900"), "Pexels #2092900"),
    "slideshow-main-course.webp": (PEX.format(id="1279330"), "Pexels #1279330"),
}

SECTIONS: dict[str, str] = {
    "breakfast": "breakfast.webp",
    "starters": "starters.webp",
    "salads": "salads.webp",
    "protein-add-ons": "protein-add-ons.webp",
    "plates": "plates.webp",
    "kids-menu": "kids-menu.webp",
    "pastas": "pastas.webp",
    "cachapas": "cachapas.webp",
    "menu-add-ons": "menu-add-ons.webp",
    "parrillas": "parrillas.webp",
    "chicken-pork-specials": "chicken-pork-specials.webp",
    "main-course": "main-course.webp",
    "sides": "sides.webp",
    "fast-food": "fast-food.webp",
    "virgin-drinks": "virgin-drinks.webp",
    "drinks": "drinks.webp",
}


def img(name: str) -> str:
    return f"images/{name}"


def download_pexels(filename: str, url: str) -> bool:
    from PIL import Image

    webp = IMAGES_DIR / filename
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        with urllib.request.urlopen(req, timeout=30) as resp:
            data = resp.read()
    except urllib.error.HTTPError as e:
        print(f"SKIP {filename}: HTTP {e.code}")
        return webp.exists()
    Image.open(BytesIO(data)).save(webp, "WEBP", quality=85)
    print(f"OK {filename}")
    return True


def body_after_frontmatter(raw: str) -> str:
    if raw.count("---") < 2:
        return raw.strip()
    return raw.split("---", 2)[2].strip()


def update_section_index(section: str, image_file: str) -> None:
    path = CONTENT / section / "_index.md"
    if not path.exists():
        return
    raw = path.read_text(encoding="utf-8")
    title_m = re.search(r"^title:\s*(.+)$", raw, re.M)
    weight_m = re.search(r"^weight:\s*(.+)$", raw, re.M)
    title = title_m.group(1).strip().strip('"') if title_m else section.replace("-", " ").title()
    weight = weight_m.group(1).strip().strip('"') if weight_m else "1"
    body = body_after_frontmatter(raw)

    lines = [
        "---",
        f"title: {title}",
        f"weight: {weight}",
        f"icon: {img(image_file)}",
        "images:",
        f"    primary: {img(image_file)}",
        "---",
    ]
    if body:
        lines.extend(["", body])
    lines.append("")
    path.write_text("\n".join(lines), encoding="utf-8")


def update_home_index() -> None:
    path = CONTENT / "_index.md"
    body = body_after_frontmatter(path.read_text(encoding="utf-8"))
    if not body.strip():
        body = (
            "<p>Merengue Restaurant — authentic Venezuelan food. "
            "VAT and service charge may apply; see menu for details.</p>"
        )
    hero = "food.jpg" if (IMAGES_DIR / "food.jpg").exists() else "parrillas.webp"
    text = (
        "---\n"
        'title: "Merengue Restaurant"\n'
        f"image: {img(hero)}\n"
        "images:\n"
        f"    - image: {img(hero)}\n"
        f"    - image: {img('parrillas.webp')}\n"
        f"    - image: {img('breakfast.webp')}\n"
        f"    - image: {img('main-course.webp')}\n"
        "slideshow:\n"
        f"    - image: {img(hero)}\n"
        f"    - image: {img('slideshow-parrillas.webp')}\n"
        f"    - image: {img('slideshow-breakfast.webp')}\n"
        f"    - image: {img('slideshow-main-course.webp')}\n"
        f"    - image: {img('cachapas.webp')}\n"
        f"    - image: {img('starters.webp')}\n"
        "---"
    )
    text += f"\n\n{body}\n"
    path.write_text(text, encoding="utf-8")


def main() -> None:
    IMAGES_DIR.mkdir(parents=True, exist_ok=True)
    credits: list[str] = []

    if (IMAGES_DIR / "food.jpg").exists():
        credits.append("- food.jpg — Merengue Restaurant (client-owned)")

    for filename, (url, credit) in PEXELS.items():
        if download_pexels(filename, url):
            credits.append(f"- {filename} — {credit}")

    missing = [s for s, f in SECTIONS.items() if not (IMAGES_DIR / f).exists()]
    if missing:
        print("Missing:", ", ".join(missing))
        return

    for section, image_file in SECTIONS.items():
        update_section_index(section, image_file)

    update_home_index()

    (IMAGES_DIR / "IMAGE_CREDITS.txt").write_text(
        "Section photos:\n" + "\n".join(dict.fromkeys(credits)) + "\n",
        encoding="utf-8",
    )
    print("Section headers updated.")


if __name__ == "__main__":
    main()
