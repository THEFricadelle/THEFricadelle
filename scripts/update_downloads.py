"""Fetch Modrinth and CurseForge download counts and render the profile downloads card.

Author: THEFricadelle
"""

import json
import sys
import urllib.request
from pathlib import Path
from xml.sax.saxutils import escape

# Display name, Modrinth slug, CurseForge project ID.
MODS = [
    ("CustomPerm", "customperm", 1539594),
    ("Arcadia-Better-Creative", "arcadia-better-creative", 1617980),
]

OUTPUT = Path(__file__).resolve().parent.parent / "badges" / "downloads.svg"
USER_AGENT = "THEFricadelle/THEFricadelle profile downloads card"

BACKGROUND = "#0d1117"
ACCENT = "#ff4fa3"
MUTED = "#9e9e9e"
TEXT = "#c9d1d9"
FONT = "'Segoe UI', Ubuntu, 'Helvetica Neue', sans-serif"

WIDTH = 495
LEFT_COLUMN = 124
RIGHT_COLUMN = 371
ROW_CURSEFORGE = 30
ROW_NAME = WIDTH / 2
ROW_MODRINTH = WIDTH - 30
ROWS_TOP = 150
ROW_HEIGHT = 26


def fetch_json(url):
    request = urllib.request.Request(url, headers={"User-Agent": USER_AGENT})
    with urllib.request.urlopen(request, timeout=30) as response:
        if response.status != 200:
            raise RuntimeError(f"{url} returned HTTP {response.status}")
        return json.load(response)


def fetch_counts():
    counts = []
    for name, slug, project_id in MODS:
        modrinth = int(fetch_json(f"https://api.modrinth.com/v2/project/{slug}")["downloads"])
        curseforge = int(fetch_json(f"https://api.cfwidget.com/{project_id}")["downloads"]["total"])
        counts.append((name, modrinth, curseforge))
    return counts


def text(x, y, content, size, color, anchor="middle", weight=400):
    return (
        f'<text x="{x}" y="{y}" text-anchor="{anchor}" font-family="{FONT}" '
        f'font-size="{size}" font-weight="{weight}" fill="{color}">{escape(content)}</text>'
    )


def render(counts):
    total_modrinth = sum(row[1] for row in counts)
    total_curseforge = sum(row[2] for row in counts)
    height = ROWS_TOP + ROW_HEIGHT * len(counts) + 12

    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" width="{WIDTH}" height="{height}" '
        f'viewBox="0 0 {WIDTH} {height}" role="img" aria-label="Mod downloads">',
        f'<rect width="{WIDTH}" height="{height}" rx="6" fill="{BACKGROUND}"/>',
        text(LEFT_COLUMN, 58, f"{total_curseforge:,}", 30, ACCENT, weight=700),
        text(LEFT_COLUMN, 84, "CurseForge", 14, ACCENT),
        text(RIGHT_COLUMN, 58, f"{total_modrinth:,}", 30, ACCENT, weight=700),
        text(RIGHT_COLUMN, 84, "Modrinth", 14, ACCENT),
        f'<line x1="{WIDTH / 2}" y1="28" x2="{WIDTH / 2}" y2="92" stroke="{ACCENT}" stroke-width="1"/>',
        f'<line x1="25" y1="110" x2="{WIDTH - 25}" y2="110" stroke="{MUTED}" stroke-opacity="0.35" stroke-width="1"/>',
        text(ROW_CURSEFORGE, 132, "CURSEFORGE", 10, MUTED, anchor="start"),
        text(ROW_NAME, 132, "MOD", 10, MUTED),
        text(ROW_MODRINTH, 132, "MODRINTH", 10, MUTED, anchor="end"),
    ]
    for index, (name, modrinth, curseforge) in enumerate(counts):
        y = ROWS_TOP + ROW_HEIGHT * index + 8
        parts.append(text(ROW_CURSEFORGE, y, f"{curseforge:,}", 14, ACCENT, anchor="start", weight=600))
        parts.append(text(ROW_NAME, y, name, 14, TEXT))
        parts.append(text(ROW_MODRINTH, y, f"{modrinth:,}", 14, ACCENT, anchor="end", weight=600))
    parts.append("</svg>")
    return "\n".join(parts) + "\n"


def main():
    # Fetch everything before writing so a failed request never leaves a partial update.
    try:
        counts = fetch_counts()
    except Exception as error:
        print(f"Download fetch failed: {error}", file=sys.stderr)
        return 1

    OUTPUT.parent.mkdir(exist_ok=True)
    OUTPUT.write_text(render(counts), encoding="utf-8")
    for name, modrinth, curseforge in counts:
        print(f"{name}: modrinth={modrinth} curseforge={curseforge}")
    return 0


if __name__ == "__main__":
    sys.exit(main())
