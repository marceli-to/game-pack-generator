"""Generate library/palette.png from style.json (pure Python, no Pillow).

    python -m server.palette
"""
from __future__ import annotations

import struct
import zlib
from pathlib import Path

from .paths import REPO
from .style import load_style


def hex_to_rgb(h: str) -> tuple[int, int, int]:
    h = h.lstrip("#")
    return int(h[0:2], 16), int(h[2:4], 16), int(h[4:6], 16)


def palette_pixels(style: dict) -> list[list[tuple[int, int, int]]]:
    pal = style["palette"]
    size, grid, cell = pal["size"], pal["grid"], pal["cell"]
    assert grid * cell == size, "palette size must equal grid * cell"
    colors = [hex_to_rgb(c) for c in pal["colors"]]
    assert len(colors) == grid * grid, f"palette needs {grid * grid} colours, has {len(colors)}"
    # Row 0 of the palette is the TOP row of the image (index = row * grid + col).
    rows = []
    for y in range(size):
        r = y // cell
        rows.append([colors[r * grid + (x // cell)] for x in range(size)])
    return rows


def write_png(path: Path, rows: list[list[tuple[int, int, int]]]) -> None:
    h, w = len(rows), len(rows[0])
    raw = b"".join(b"\x00" + bytes(c for px in row for c in px) for row in rows)

    def chunk(tag: bytes, data: bytes) -> bytes:
        return struct.pack(">I", len(data)) + tag + data + struct.pack(">I", zlib.crc32(tag + data) & 0xFFFFFFFF)

    png = b"\x89PNG\r\n\x1a\n"
    png += chunk(b"IHDR", struct.pack(">IIBBBBB", w, h, 8, 2, 0, 0, 0))
    png += chunk(b"IDAT", zlib.compress(raw, 9))
    png += chunk(b"IEND", b"")
    path.write_bytes(png)


def make_palette(out: Path | None = None) -> Path:
    style = load_style()
    out = out or REPO / style["palette"]["file"]
    out.parent.mkdir(parents=True, exist_ok=True)
    write_png(out, palette_pixels(style))
    return out


if __name__ == "__main__":
    print(make_palette())
