#!/usr/bin/env python3
"""Generate the Easy Prompting toolbar icons.

A rounded chat bubble (the "prompt") with a pencil/caret, on a calm dark
background. Deliberately NOT a clock, so Chrome Web Store does not read the
two extensions as duplicates. Replace with final artwork before publishing if
you want something fancier; this is clean and recognisable as-is.
"""
from PIL import Image, ImageDraw

BG = (28, 30, 38, 255)        # calm dark slate
BUBBLE = (255, 255, 255, 255)  # white bubble
ACCENT = (94, 169, 255, 255)   # friendly blue caret


def rounded(draw, box, r, fill):
    draw.rounded_rectangle(box, radius=r, fill=fill)


def make(size):
    # Work at 4x for crisp downscaling.
    s = size * 4
    img = Image.new("RGBA", (s, s), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)

    # Background tile (rounded square).
    rounded(d, [0, 0, s - 1, s - 1], r=int(s * 0.22), fill=BG)

    # Chat bubble body.
    pad = int(s * 0.16)
    bx0, by0 = pad, int(s * 0.18)
    bx1, by1 = s - pad, int(s * 0.66)
    rounded(d, [bx0, by0, bx1, by1], r=int(s * 0.12), fill=BUBBLE)

    # Little tail at the bottom-left of the bubble.
    tail = [
        (int(s * 0.30), by1 - int(s * 0.02)),
        (int(s * 0.30), by1 + int(s * 0.14)),
        (int(s * 0.46), by1 - int(s * 0.02)),
    ]
    d.polygon(tail, fill=BUBBLE)

    # Blinking-caret style accent line + caret to suggest "typing a prompt".
    line_y = int((by0 + by1) / 2)
    lx0 = bx0 + int(s * 0.10)
    lx1 = bx1 - int(s * 0.20)
    lw = max(2, int(s * 0.045))
    d.line([(lx0, line_y), (lx1, line_y)], fill=(150, 158, 175, 255), width=lw)

    # Caret block at the end of the line.
    cw = int(s * 0.055)
    d.rectangle([lx1 + int(s * 0.04), line_y - int(s * 0.14),
                 lx1 + int(s * 0.04) + cw, line_y + int(s * 0.14)], fill=ACCENT)

    return img.resize((size, size), Image.LANCZOS)


for sz in (16, 48, 128):
    make(sz).save(f"icon/ep_icon{sz}x{sz}.png")
    print(f"wrote icon/ep_icon{sz}x{sz}.png")
