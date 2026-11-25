#!/usr/bin/env python3
"""Tile a folder of screenshots into contact sheets (JPEG pages) with file-name captions.

Usage: contact_sheet.sh <screenshots_dir> <out_dir> [per_page=12]
Writes sheet-1.jpg, sheet-2.jpg, ... Needs Pillow (contact_sheet.sh sets up a private venv).
"""
import os, sys
from PIL import Image, ImageDraw, ImageFont

COLS, CELL_W, PAD, CAP_H = 3, 620, 16, 44


def font(size):
    for p in ["/System/Library/Fonts/Supplemental/Arial.ttf", "/System/Library/Fonts/Helvetica.ttc",
              "/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf"]:
        if os.path.exists(p):
            return ImageFont.truetype(p, size)
    return ImageFont.load_default()


def main():
    src, out = sys.argv[1], sys.argv[2]
    per = int(sys.argv[3]) if len(sys.argv) > 3 else 12
    files = sorted(f for f in os.listdir(src) if f.lower().endswith((".png", ".jpg", ".jpeg")))
    os.makedirs(out, exist_ok=True)
    f_cap, written = font(15), []
    for page, i in enumerate(range(0, len(files), per), 1):
        chunk, thumbs = files[i:i + per], []
        for name in chunk:
            im = Image.open(os.path.join(src, name)).convert("RGB")
            im.thumbnail((CELL_W, CELL_W))
            thumbs.append((name, im))
        rows = [thumbs[r:r + COLS] for r in range(0, len(thumbs), COLS)]
        row_h = [max(t[1].height for t in row) + CAP_H for row in rows]
        W = COLS * CELL_W + (COLS + 1) * PAD
        H = sum(row_h) + (len(rows) + 1) * PAD
        sheet = Image.new("RGB", (W, H), "white")
        d = ImageDraw.Draw(sheet)
        y = PAD
        for row, h in zip(rows, row_h):
            x = PAD
            for name, im in row:
                sheet.paste(im, (x, y))
                warn = "WARN" in name or "FAIL" in name
                d.text((x, y + im.height + 6), name[:78], fill=(200, 0, 0) if warn else (30, 30, 30), font=f_cap)
                x += CELL_W + PAD
            y += h + PAD
        p = os.path.join(out, f"sheet-{page}.jpg")
        sheet.save(p, "JPEG", quality=82, optimize=True)
        written.append(p)
    print("\n".join(written))


if __name__ == "__main__":
    main()
