#!/usr/bin/env python3
"""Generate Chrome Web Store promo assets for Easy Prompting.

Pure-PIL, rendered at 2x then downscaled for crisp anti-aliased output at the
exact CWS dimensions:
  - screenshot_1_1280x800.png   (main screenshot)
  - screenshot_2_1280x800.png   (features / shortcuts)
  - small_promo_440x280.png     (small promo tile)
  - marquee_1400x560.png        (marquee promo tile)
"""
import os
from PIL import Image, ImageDraw, ImageFont, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = HERE
ICON = os.path.join(HERE, "..", "easyprompting", "icon", "ep_icon128x128.png")
FONT_DIR = "/mnt/chromeos/fonts/roboto"

S = 2  # supersample factor

# Palette
BG = (28, 30, 38)
SURFACE = (38, 41, 52)
SURFACE2 = (47, 51, 64)
TEXT = (232, 234, 240)
MUTED = (154, 160, 176)
ACCENT = (94, 169, 255)
ACCENT_TEXT = (8, 32, 58)
BORDER = (58, 63, 77)
MONO = (150, 158, 175)

_font_cache = {}


def font(size, weight="Regular"):
    key = (size, weight)
    if key not in _font_cache:
        _font_cache[key] = ImageFont.truetype(
            os.path.join(FONT_DIR, f"Roboto-{weight}.ttf"), int(size * S))
    return _font_cache[key]


def new_canvas(w, h):
    """Dark gradient canvas with a soft blue glow, at 2x."""
    W, H = w * S, h * S
    img = Image.new("RGB", (W, H))
    top = (23, 26, 34)
    bot = (20, 22, 29)
    px = img.load()
    for y in range(H):
        t = y / H
        r = int(top[0] + (bot[0] - top[0]) * t)
        g = int(top[1] + (bot[1] - top[1]) * t)
        b = int(top[2] + (bot[2] - top[2]) * t)
        for x in range(0, W, 1):
            px[x, y] = (r, g, b)
    # Blue glow top-right.
    glow = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    gd = ImageDraw.Draw(glow)
    gx, gy = int(W * 0.82), int(H * -0.05)
    rad = int(W * 0.42)
    gd.ellipse([gx - rad, gy - rad, gx + rad, gy + rad], fill=ACCENT + (70,))
    glow = glow.filter(ImageFilter.GaussianBlur(int(120 * S)))
    img = Image.alpha_composite(img.convert("RGBA"), glow).convert("RGB")
    return img, ImageDraw.Draw(img)


def text(d, xy, s, size, color, weight="Regular", anchor="la", spacing=4):
    d.multiline_text((xy[0] * S, xy[1] * S), s, font=font(size, weight),
                     fill=color, anchor=anchor, spacing=int(spacing * S))


def text_w(s, size, weight="Regular"):
    return font(size, weight).getlength(s) / S


def rrect(d, box, radius, fill=None, outline=None, width=1):
    b = [int(v * S) for v in box]
    d.rounded_rectangle(b, radius=int(radius * S), fill=fill,
                        outline=outline, width=int(width * S))


def paste_shadow(img, box, radius, blur, alpha):
    """Soft drop shadow behind a rounded rect."""
    W, H = img.size
    sh = Image.new("RGBA", (W, H), (0, 0, 0, 0))
    sd = ImageDraw.Draw(sh)
    b = [int(v * S) for v in box]
    sd.rounded_rectangle(b, radius=int(radius * S), fill=(0, 0, 0, alpha))
    sh = sh.filter(ImageFilter.GaussianBlur(int(blur * S)))
    img.paste(Image.alpha_composite(img.convert("RGBA"), sh).convert("RGB"), (0, 0))


# ---------- App window mockup ----------
def draw_app(img, d, x, y, w, h, tabs, active, pad_text, counter,
             show_clear=True, show_size=True):
    paste_shadow(img, [x + 6, y + 14, x + w + 6, y + h + 14], 16, 22, 150)
    d = ImageDraw.Draw(img)

    rrect(d, [x, y, x + w, y + h], 14, fill=BG, outline=BORDER, width=1)

    # Titlebar
    tb = 34
    rrect(d, [x, y, x + w, y + tb + 14], 14, fill=(20, 22, 29))
    d.rectangle([int((x) * S), int((y + 14) * S), int((x + w) * S), int((y + tb) * S)], fill=(20, 22, 29))
    dots = [(255, 95, 87), (254, 188, 46), (40, 200, 64)]
    for i, c in enumerate(dots):
        cx = x + 16 + i * 18
        cy = y + tb / 2
        d.ellipse([int((cx - 5.5) * S), int((cy - 5.5) * S),
                   int((cx + 5.5) * S), int((cy + 5.5) * S)], fill=c)
    text(d, (x + 16 + 3 * 18 + 10, y + tb / 2), "Easy Prompting", 12.5, MUTED, anchor="lm")

    # Tabs bar
    ty = y + tb
    th = 46
    d.rectangle([int(x * S), int(ty * S), int((x + w) * S), int((ty + th) * S)], fill=SURFACE)
    d.line([int(x * S), int((ty + th) * S), int((x + w) * S), int((ty + th) * S)], fill=BORDER, width=S)
    tx = x + 12
    for i, name in enumerate(tabs):
        tw = text_w(name, 14, "Regular") + 34
        cy = ty + th / 2
        is_active = (i == active)
        rrect(d, [tx, cy - 15, tx + tw, cy + 15], 8,
              fill=(BG if is_active else SURFACE2),
              outline=(ACCENT if is_active else None),
              width=1 if is_active else 1)
        text(d, (tx + 12, cy), name, 14, TEXT if is_active else MUTED, anchor="lm")
        text(d, (tx + tw - 14, cy), "×", 14, MUTED, anchor="mm")
        tx += tw + 6
    # + button
    bs = 32
    rrect(d, [x + w - 12 - bs, ty + th / 2 - bs / 2, x + w - 12, ty + th / 2 + bs / 2],
          8, fill=SURFACE2, outline=BORDER, width=1)
    text(d, (x + w - 12 - bs / 2, ty + th / 2 - 1), "+", 22, TEXT, anchor="mm")

    # Pad area
    py = ty + th
    bar_h = 52
    text(d, (x + 18, py + 16), pad_text, 15.5, TEXT, spacing=7)
    # caret after last line
    last = pad_text.split("\n")[-1]
    lines = pad_text.split("\n")
    cx = x + 18 + text_w(last, 15.5)
    cy0 = py + 16 + (len(lines) - 1) * (15.5 * 1.0 + 7) * 1.0
    # approximate line height
    lh = (font(15.5).getbbox("Ag")[3] / S) + 7
    cy0 = py + 16 + (len(lines) - 1) * lh
    d.rectangle([int((cx + 2) * S), int(cy0 * S), int((cx + 5) * S), int((cy0 + 19) * S)], fill=ACCENT)

    # Bottom bar
    by = y + h - bar_h
    d.rectangle([int(x * S), int(by * S), int((x + w) * S), int((y + h) * S)], fill=SURFACE)
    d.line([int(x * S), int(by * S), int((x + w) * S), int(by * S)], fill=BORDER, width=S)
    bcy = by + bar_h / 2
    # Copy primary
    cw = text_w("Copy", 14, "Bold") + 32
    rrect(d, [x + 10, bcy - 16, x + 10 + cw, bcy + 16], 8, fill=ACCENT)
    text(d, (x + 10 + cw / 2, bcy - 1), "Copy", 14, ACCENT_TEXT, weight="Bold", anchor="mm")
    nx = x + 10 + cw + 8
    if show_clear:
        clw = text_w("Clear", 14) + 28
        rrect(d, [nx, bcy - 16, nx + clw, bcy + 16], 8, fill=SURFACE2, outline=BORDER, width=1)
        text(d, (nx + clw / 2, bcy - 1), "Clear", 14, TEXT, anchor="mm")
        nx += clw + 12
    text(d, (nx, bcy), counter, 13, MUTED, anchor="lm")
    # right side buttons
    rx = x + w - 10
    btns = (["A−", "A+", "?"] if show_size else ["?"])
    for label in reversed(btns):
        bw = text_w(label, 14) + 22
        rrect(d, [rx - bw, bcy - 16, rx, bcy + 16], 8, fill=SURFACE2, outline=BORDER, width=1)
        text(d, (rx - bw / 2, bcy - 1), label, 14, TEXT, anchor="mm")
        rx -= bw + 8


# ---------- Feature icons (minimal line glyphs) ----------
def icon_tile(d, x, y, size=30):
    rrect(d, [x, y, x + size, y + size], 9, fill=(36, 58, 92))


def ic_enter(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    cx, cy = x + sz / 2, y + sz / 2
    a = ACCENT
    # down-then-left arrow
    d.line([int((cx + 6) * S), int((cy - 7) * S), int((cx + 6) * S), int((cy + 3) * S)], fill=a, width=int(2 * S))
    d.line([int((cx + 6) * S), int((cy + 3) * S), int((cx - 6) * S), int((cy + 3) * S)], fill=a, width=int(2 * S))
    d.line([int((cx - 6) * S), int((cy + 3) * S), int((cx - 2) * S), int((cy - 1) * S)], fill=a, width=int(2 * S))
    d.line([int((cx - 6) * S), int((cy + 3) * S), int((cx - 2) * S), int((cy + 7) * S)], fill=a, width=int(2 * S))


def ic_save(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    cx, cy = x + sz / 2, y + sz / 2
    rrect(d, [cx - 7, cy - 7, cx + 7, cy + 7], 2, outline=ACCENT, width=2)
    d.rectangle([int((cx - 3) * S), int((cy - 7) * S), int((cx + 3) * S), int((cy - 2) * S)], fill=ACCENT)
    d.rectangle([int((cx - 4) * S), int((cy + 1) * S), int((cx + 4) * S), int((cy + 6) * S)], outline=ACCENT, width=S)


def ic_copy(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    cx, cy = x + sz / 2, y + sz / 2
    rrect(d, [cx - 7, cy - 5, cx + 3, cy + 8], 2, fill=(36, 58, 92), outline=ACCENT, width=2)
    rrect(d, [cx - 3, cy - 8, cx + 7, cy + 5], 2, outline=ACCENT, width=2)


def ic_swap(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    cx, cy = x + sz / 2, y + sz / 2
    a = ACCENT
    d.line([int((cx - 7) * S), int((cy - 3) * S), int((cx + 7) * S), int((cy - 3) * S)], fill=a, width=int(2 * S))
    d.line([int((cx + 7) * S), int((cy - 3) * S), int((cx + 3) * S), int((cy - 7) * S)], fill=a, width=int(2 * S))
    d.line([int((cx + 7) * S), int((cy + 3) * S), int((cx - 7) * S), int((cy + 3) * S)], fill=a, width=int(2 * S))
    d.line([int((cx - 7) * S), int((cy + 3) * S), int((cx - 3) * S), int((cy + 7) * S)], fill=a, width=int(2 * S))


def ic_lock(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    cx, cy = x + sz / 2, y + sz / 2
    rrect(d, [cx - 6, cy - 1, cx + 6, cy + 8], 2, fill=ACCENT)
    d.arc([int((cx - 5) * S), int((cy - 9) * S), int((cx + 5) * S), int((cy + 1) * S)],
          180, 360, fill=ACCENT, width=int(2 * S))


def ic_num(d, x, y, sz=30):
    icon_tile(d, x, y, sz)
    text(d, (x + sz / 2, y + sz / 2 - 1), "1", 16, ACCENT, weight="Bold", anchor="mm")


def feature(d, x, y, icon, title, desc, w=380):
    icon(d, x, y)
    text(d, (x + 44, y - 1), title, 16.5, TEXT, weight="Medium")
    text(d, (x + 44, y + 22), desc, 14, MUTED, spacing=3)


def brand(d, img, x, y, size=52, name_size=26):
    ic = Image.open(ICON).convert("RGBA").resize((size * S, size * S), Image.LANCZOS)
    img.paste(ic, (int(x * S), int(y * S)), ic)
    text(d, (x + size + 14, y + size / 2 - 1), "Easy Prompting", name_size, TEXT,
         weight="Bold", anchor="lm")


def finish(img, w, h, name):
    out = img.resize((w, h), Image.LANCZOS)
    path = os.path.join(OUT, name)
    out.save(path)
    print("wrote", path)


# ============ Screenshot 1 — hero ============
def shot1():
    W, H = 1280, 800
    img, d = new_canvas(W, H)
    brand(d, img, 80, 96, 54, 26)
    text(d, (80, 180), "Never lose a", 52, TEXT, weight="Black")
    text(d, (80, 240), "prompt", 52, ACCENT, weight="Black")
    pw = text_w("prompt", 52, "Black")
    text(d, (80 + pw + 18, 240), "again.", 52, TEXT, weight="Black")
    text(d, (80, 320), "A safe scratchpad for your AI chat prompts.\nWrite here first — then copy it over when it's ready.",
         19, MUTED, spacing=6)
    feature(d, 82, 400, ic_enter, "Enter never sends",
            "No stray keystroke or Ctrl+C can wipe or fire your draft.")
    feature(d, 82, 458, ic_save, "Autosaves every keystroke",
            "Close the window, come back — your prompt is still here.")
    feature(d, 82, 516, ic_copy, "One-click copy",
            "Ready? Copy the whole prompt and paste it into any chat.")

    pad = ("You are a senior code reviewer. Refactor the\n"
           "function below for readability and add tests.\n\n"
           "Constraints:\n"
           "- keep the public API unchanged\n"
           "- explain each change in one line\n\n"
           "```js\n"
           "function f(a){return a.map(x=>x*2)}\n"
           "```")
    draw_app(img, d, 600, 120, 600, 560,
             ["Refactor request", "System prompt", "Snippets"], 0,
             pad, "38 words · 247 chars")
    finish(img, W, H, "screenshot_1_1280x800.png")


# ============ Screenshot 2 — tabs & shortcuts ============
def shot2():
    W, H = 1280, 800
    img, d = new_canvas(W, H)
    # pill
    pill = "Stays open beside your chat"
    pwid = text_w(pill, 14, "Medium") + 28
    rrect(d, [(W - pwid) / 2, 60, (W + pwid) / 2, 94], 17,
          fill=(24, 44, 74), outline=ACCENT, width=1)
    text(d, (W / 2, 77), pill, 14, ACCENT, weight="Medium", anchor="mm")

    text(d, (W / 2, 130), "Juggle several prompts at once", 40, TEXT,
         weight="Black", anchor="ma")
    text(d, (W / 2, 192),
         "Keep a system prompt, a working draft and reusable snippets in\n"
         "separate tabs — switch between them with the keyboard.",
         19, MUTED, anchor="ma", spacing=6)

    pad = ("You are a meticulous translator (EN -> NL).\n"
           "Keep tone friendly and concise.\n"
           "Never invent facts. Ask if unsure.")
    draw_app(img, d, 90, 300, 560, 430,
             ["Draft", "System prompt", "Snippets"], 1,
             pad, "17 words · 112 chars", show_size=False)

    fx = 710
    feature(d, fx, 320, ic_swap, "Switch tabs while typing", "Alt + E / R  —  previous / next")
    feature(d, fx, 392, ic_num, "Jump straight to a tab", "Alt + 1 … 9")
    feature(d, fx, 464, ic_save, "Live word & character count", "Know your prompt's size at a glance.")
    feature(d, fx, 536, ic_lock, "100% local & private", "Nothing ever leaves your device.")
    finish(img, W, H, "screenshot_2_1280x800.png")


# ============ Small promo tile 440x280 ============
def small():
    W, H = 440, 280
    img, d = new_canvas(W, H)
    brand(d, img, 34, 56, 46, 28)
    text(d, (34, 130), "A safe scratchpad", 23, TEXT, weight="Black")
    text(d, (34, 162), "for AI prompts", 23, ACCENT, weight="Black")
    text(d, (34, 205), "Draft your prompt, never lose it to a\nstray Enter, then copy it in.",
         14.5, MUTED, spacing=5)
    finish(img, W, H, "small_promo_440x280.png")


# ============ Marquee 1400x560 ============
def marquee():
    W, H = 1400, 560
    img, d = new_canvas(W, H)
    brand(d, img, 90, 90, 56, 30)
    text(d, (90, 190), "Never lose a", 52, TEXT, weight="Black")
    text(d, (90, 250), "prompt", 52, ACCENT, weight="Black")
    pw = text_w("prompt", 52, "Black")
    text(d, (90 + pw + 18, 250), "again.", 52, TEXT, weight="Black")
    text(d, (90, 340),
         "A safe scratchpad for AI chat prompts. Enter just makes a new\n"
         "line, autosave keeps it safe — then copy it in with one click.",
         20, MUTED, spacing=6)

    pad = ("You are a senior code reviewer. Refactor the\n"
           "function below for readability and add tests.\n\n"
           "Keep the public API unchanged.")
    draw_app(img, d, 770, 100, 540, 380,
             ["Refactor request", "System prompt", "Snippets"], 0,
             pad, "38 words · 247 chars", show_size=False)
    finish(img, W, H, "marquee_1400x560.png")


if __name__ == "__main__":
    shot1()
    shot2()
    small()
    marquee()
