#!/usr/bin/env python3
"""
Market Wizards — Style Sample 01
"Opening + concept lesson: The Arithmetic of Survival"

Renders a ~2-minute 1920x1080 / 30fps sample that demonstrates the series'
visual identity: JSR logo sting, cinematic cold open, series title, chapter
card, and an animated educational lesson on risk-per-trade and position sizing.

Every figure in the lesson is a HYPOTHETICAL example computed in this file.

Usage:
    python3 render.py                 # full render -> output/market-wizards-sample-01.mp4
    python3 render.py --stills        # only render preview stills -> output/stills/

Logo: if assets/jsr_logo.png exists it is used (fitted into a circle);
otherwise a placeholder round "JSR" monogram is drawn.
"""
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter, ImageFont

HERE = os.path.dirname(os.path.abspath(__file__))
OUT = os.path.join(HERE, "output")
W, H, FPS = 1920, 1080, 30
DURATION = 121.0

# ---------------------------------------------------------------- palette ---
BLACK = (0, 0, 0)
BG_C = (21, 22, 26)          # charcoal centre
BG_E = (7, 7, 8)             # vignette edge
PANEL = (18, 19, 22)
BORDER = (38, 39, 44)
GRID = (34, 35, 39)
WHITE = (242, 240, 235)
MUTED = (142, 140, 134)
FAINT = (96, 95, 92)
GOLD = (201, 165, 90)
RISK = (196, 106, 90)        # restrained red for losses / stops
LOSSBAR = (74, 74, 80)
CANDLE_UP = (216, 212, 202)
CANDLE_DN = (92, 90, 86)

FONTS = "/usr/share/fonts/opentype/inter/"
MONO = "/usr/share/fonts/truetype/jetbrains-mono/"
FONT_FILES = {
    "display_light": FONTS + "InterDisplay-Light.otf",
    "display_thin": FONTS + "InterDisplay-Thin.otf",
    "display_semibold": FONTS + "InterDisplay-SemiBold.otf",
    "regular": FONTS + "Inter-Regular.otf",
    "medium": FONTS + "Inter-Medium.otf",
    "semibold": FONTS + "Inter-SemiBold.otf",
    "italic": FONTS + "Inter-Italic.otf",
    "mono": MONO + "JetBrainsMono-Regular.ttf",
    "mono_medium": MONO + "JetBrainsMono-Medium.ttf",
}

# ------------------------------------------------------------- narration ---
# (start, end, text) — subtitles now; the same text is the voice-over script.
NARRATION = [
    (3.0, 7.6, "Every trader in this series has lost money. Some lost fortunes."),
    (7.8, 12.9, "What set them apart was not avoiding losses. It was surviving them."),
    (25.0, 29.6, "Imagine two hypothetical traders, each starting with one hundred thousand dollars."),
    (29.8, 35.6, "Trader A risks ten percent of the account per trade. Trader B risks one percent."),
    (35.8, 41.6, "Now give them both the same bad luck: ten losing trades in a row."),
    (41.8, 48.6, "Trader A is left with about thirty-five thousand dollars. Trader B still has about ninety."),
    (48.8, 55.3, "Same market. Same losing streak. The only difference was how much they risked."),
    (56.2, 60.6, "And losses are harder to recover from than they look."),
    (60.8, 68.4, "A ten percent loss needs an eleven percent gain to recover. A twenty-five percent loss needs thirty-three."),
    (68.6, 73.8, "Lose half, and you must double what remains just to break even."),
    (74.0, 80.6, "Trader A lost sixty-five percent. Recovering requires a gain of nearly one hundred and ninety percent."),
    (81.6, 86.4, "That is why position size is often set by risk, not by conviction."),
    (86.6, 92.8, "First, choose the most you will lose on one trade: one percent, or one thousand dollars."),
    (93.0, 99.2, "You buy at fifty dollars, with a stop at forty-eight. Each share risks two dollars."),
    (99.4, 105.0, "One thousand dollars, divided by two dollars per share: five hundred shares."),
    (105.2, 111.6, "If the stop is hit, the loss is planned, though gaps and slippage can make it larger."),
    (112.4, 117.0, "Every trader in this series found their own answer to this problem."),
]

# ------------------------------------------------------------ hypotheticals -
START = 100_000
RISK_A, RISK_B = 0.10, 0.01
STREAK = 10
EQ_A = [START * (1 - RISK_A) ** k for k in range(STREAK + 1)]
EQ_B = [START * (1 - RISK_B) ** k for k in range(STREAK + 1)]
LOSS_A = 1 - EQ_A[-1] / START                       # 0.6513
RECOVERY = [(0.10,), (0.25,), (0.50,), (LOSS_A,)]
RECOVERY = [(l, l / (1 - l)) for (l,) in RECOVERY]  # (loss, gain needed)
ENTRY, STOP, RISK_DOLLARS = 50.00, 48.00, START * 0.01
SHARES = int(RISK_DOLLARS / (ENTRY - STOP))         # 500


# ================================================================ helpers ===
def clamp(x, a=0.0, b=1.0):
    return max(a, min(b, x))


def prog(t, a, b):
    return clamp((t - a) / (b - a)) if b > a else float(t >= a)


def ease_out(x):
    return 1 - (1 - x) ** 3


def ease_io(x):
    return 4 * x ** 3 if x < 0.5 else 1 - (-2 * x + 2) ** 3 / 2


def fade(t, a, b, fin=0.6, fout=0.6):
    """Opacity envelope for an element visible between a and b."""
    if t < a or t > b:
        return 0.0
    return ease_io(prog(t, a, a + fin)) * (1 - ease_io(prog(t, b - fout, b)))


@lru_cache(maxsize=None)
def font(key, size):
    return ImageFont.truetype(FONT_FILES[key], size)


def with_alpha(img, alpha):
    if alpha >= 0.999:
        return img
    a = np.asarray(img.getchannel("A"), dtype=np.float32) * alpha
    out = img.copy()
    out.putalpha(Image.fromarray(a.astype(np.uint8)))
    return out


def blit(base, img, x, y, alpha=1.0):
    """Alpha-composite img onto base at integer (x, y), clipping at edges."""
    if alpha <= 0.003:
        return
    img = with_alpha(img, alpha)
    x, y = int(round(x)), int(round(y))
    sx, sy = max(0, -x), max(0, -y)
    dx, dy = max(0, x), max(0, y)
    w = min(img.width - sx, base.width - dx)
    h = min(img.height - sy, base.height - dy)
    if w <= 0 or h <= 0:
        return
    if (sx, sy, w, h) != (0, 0, img.width, img.height):
        img = img.crop((sx, sy, sx + w, sy + h))
    base.alpha_composite(img, dest=(dx, dy))


PAD = 8


@lru_cache(maxsize=4096)
def text_img(text, fkey, size, color, tracking=0, shadow=False):
    f = font(fkey, size)
    asc, desc = f.getmetrics()
    if tracking:
        widths = [f.getlength(c) for c in text]
        tw = sum(widths) + tracking * (len(text) - 1)
    else:
        tw = f.getlength(text)
    img = Image.new("RGBA", (int(math.ceil(tw)) + PAD * 2, asc + desc + PAD * 2), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    if tracking:
        x = PAD
        for c, cw in zip(text, widths):
            d.text((x, PAD), c, font=f, fill=color + (255,))
            x += cw + tracking
    else:
        d.text((PAD, PAD), text, font=f, fill=color + (255,))
    if shadow:
        sh = Image.new("RGBA", img.size, (0, 0, 0, 0))
        sh.putalpha(img.getchannel("A").filter(ImageFilter.GaussianBlur(5)).point(lambda v: min(255, int(v * 1.6))))
        out = Image.new("RGBA", img.size, (0, 0, 0, 0))
        out.alpha_composite(sh, dest=(0, 2))
        out.alpha_composite(img)
        img = out
    return img


def draw_text(base, text, x, y, fkey, size, color, alpha=1.0, anchor="l", tracking=0, shadow=False):
    """y = top of the text's ascent box. anchor: l / m / r on x."""
    if alpha <= 0.003:
        return 0
    img = text_img(text, fkey, size, color, tracking, shadow)
    w = img.width - PAD * 2
    if anchor == "m":
        x -= w / 2
    elif anchor == "r":
        x -= w
    blit(base, img, x - PAD, y - PAD, alpha)
    return w


def text_w(text, fkey, size, tracking=0):
    return text_img(text, fkey, size, WHITE, tracking).width - PAD * 2


def overlay():
    return Image.new("RGBA", (W, H), (0, 0, 0, 0))


def rect(base, box, color, alpha=1.0):
    if alpha <= 0.003:
        return
    x0, y0, x1, y1 = [int(round(v)) for v in box]
    if x1 <= x0 or y1 <= y0:
        return
    tile = Image.new("RGBA", (x1 - x0, y1 - y0), color + (int(255 * alpha),))
    blit(base, tile, x0, y0)


def hline(base, x0, x1, y, color, alpha=1.0, th=1, dash=None):
    if dash is None:
        rect(base, (x0, y, x1, y + th), color, alpha)
    else:
        on, off = dash
        x = x0
        while x < x1:
            rect(base, (x, y, min(x + on, x1), y + th), color, alpha)
            x += on + off


def vline(base, x, y0, y1, color, alpha=1.0, th=1):
    rect(base, (x, y0, x + th, y1), color, alpha)


def money(v):
    return "${:,.0f}".format(v)


# ============================================================ static art ===
def make_vignette():
    yy, xx = np.mgrid[0:H, 0:W].astype(np.float32)
    r = np.sqrt(((xx - W / 2) / (W * 0.62)) ** 2 + ((yy - H * 0.45) / (H * 0.70)) ** 2)
    k = np.clip(r, 0, 1) ** 1.6
    c0, c1 = np.array(BG_C, np.float32), np.array(BG_E, np.float32)
    img = c0[None, None] * (1 - k[..., None]) + c1[None, None] * k[..., None]
    rng = np.random.default_rng(3)
    img += rng.normal(0, 1.1, img.shape[:2])[..., None]  # dither against banding
    rgb = np.clip(img, 0, 255).astype(np.uint8)
    return Image.fromarray(rgb, "RGB").convert("RGBA")


def make_walk():
    """Faint background price path for the cold open (original, synthetic)."""
    rng = np.random.default_rng(7)
    n = 520
    steps = rng.normal(0, 1, n)
    path = np.cumsum(steps)
    path = path - np.linspace(0, path[-1], n) * 0.4
    path = (path - path.min()) / (path.max() - path.min())
    xs = np.linspace(-20, W + 20, n)
    ys = 760 - path * 420
    S = 2
    img = Image.new("RGBA", (W * S, H * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(img)
    pts = [(x * S, y * S) for x, y in zip(xs, ys)]
    d.line(pts, fill=GOLD + (120,), width=3 * S, joint="curve")
    img = img.resize((W, H), Image.LANCZOS)
    return img, xs, ys


LOGO_R = 190          # logo radius in px at 1080p
RING_GAP = 18         # gap between disc and gold ring


def make_logo():
    """Load the round JSR logo (assets/jsr_logo.png, prepared by prepare_logo.py).
    Falls back to a drawn placeholder if the asset is missing.
    Returns pieces used by the animated sting."""
    size = LOGO_R * 2
    path = os.path.join(HERE, "assets", "jsr_logo.png")
    if os.path.exists(path):
        src = Image.open(path).convert("RGBA").resize((size, size), Image.LANCZOS)
    else:
        src = Image.new("RGBA", (size, size), (0, 0, 0, 0))
        d = ImageDraw.Draw(src)
        d.ellipse((0, 0, size - 1, size - 1), fill=(0, 0, 0, 255))
        d.text((size / 2, size / 2), "JSR", font=font("display_semibold", 90), fill=WHITE + (255,), anchor="mm")
    disc_mask = src.getchannel("A")
    letters = np.asarray(src.convert("L"), np.float32) / 255.0 * (np.asarray(disc_mask, np.float32) / 255.0)

    # faint rim light on the disc edge so the black disc separates from the black screen
    S = 4
    rim = Image.new("L", (size * S, size * S), 0)
    ImageDraw.Draw(rim).ellipse((S, S, size * S - S - 1, size * S - S - 1), outline=255, width=int(1.5 * S))
    rim = np.asarray(rim.resize((size, size), Image.LANCZOS), np.float32) / 255.0

    # coordinates for the light sweep (diagonal, top-left to bottom-right)
    yy, xx = np.mgrid[0:size, 0:size].astype(np.float32) / size
    diag = (xx * 0.82 + yy * 0.57)

    glow_size = int(size * 2.4)
    glow = Image.new("RGBA", (glow_size, glow_size), (0, 0, 0, 0))
    gr = size * 0.62
    c = glow_size / 2
    ImageDraw.Draw(glow).ellipse((c - gr, c - gr, c + gr, c + gr), fill=GOLD + (95,))
    glow = glow.filter(ImageFilter.GaussianBlur(size * 0.26))
    return dict(size=size, disc=np.asarray(disc_mask, np.float32) / 255.0, letters=letters,
                rim=rim, diag=diag, glow=glow)


def logo_layer(L, ring_p, shine_pos):
    """Compose disc + letters + rim + gold ring + light sweep (RGBA, unscaled)."""
    size = L["size"]
    pad = RING_GAP + 12
    full = size + pad * 2
    # disc and letters
    band = np.exp(-((L["diag"] - shine_pos) / 0.075) ** 2) if shine_pos is not None else 0.0
    lum = np.clip(L["letters"] * (0.96 + 0.12 * band), 0, 1)                      # letters brighten as light passes
    sheen = L["disc"] * band * 0.10                                # glassy sweep across the black disc
    rim = L["rim"] * (0.16 + 0.35 * band)
    rgb = np.zeros((size, size, 3), np.float32)
    white = np.array(WHITE, np.float32) / 255.0
    gold = np.array(GOLD, np.float32) / 255.0
    rgb += lum[..., None] * white
    rgb += sheen[..., None] * (white * 0.6 + gold * 0.4)
    rgb += rim[..., None] * gold
    rgb = np.clip(rgb, 0, 1)
    disc = Image.fromarray((rgb * 255).astype(np.uint8), "RGB").convert("RGBA")
    disc.putalpha(Image.fromarray((L["disc"] * 255).astype(np.uint8)))
    layer = Image.new("RGBA", (full, full), (0, 0, 0, 0))
    layer.alpha_composite(disc, dest=(pad, pad))
    # gold ring drawn clockwise from 12 o'clock
    if ring_p > 0:
        S = 3
        ring = Image.new("RGBA", (full * S, full * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(ring)
        rr = (size / 2 + RING_GAP) * S
        c = full * S / 2
        box = (c - rr, c - rr, c + rr, c + rr)
        d.arc(box, -90, -90 + 360 * ring_p, fill=GOLD + (235,), width=int(2.2 * S))
        if ring_p < 1:
            ang = math.radians(-90 + 360 * ring_p)
            hx, hy = c + rr * math.cos(ang), c + rr * math.sin(ang)
            hr = 4 * S
            d.ellipse((hx - hr, hy - hr, hx + hr, hy + hr), fill=(255, 236, 190, 255))
        ring = ring.resize((full, full), Image.LANCZOS)
        layer.alpha_composite(ring)
    return layer


def make_candles():
    """Synthetic daily candles: trend, base above $48.3, breakout to $50."""
    rng = np.random.default_rng(11)
    closes = []
    p = 46.6
    for i in range(42):
        if i < 14:
            drift = 0.17
        elif i < 33:
            drift = (48.95 - p) * 0.35
        else:
            drift = (50.0 - p) * 0.38
        p = p + drift + rng.normal(0, 0.22 if 14 <= i < 33 else 0.16)
        if 14 <= i < 33:
            p = min(max(p, 48.55), 49.55)
        closes.append(p)
    closes[-1] = 50.0
    candles = []
    prev = 46.4
    for c in closes:
        o = prev + rng.normal(0, 0.12)
        hi = max(o, c) + abs(rng.normal(0.18, 0.1))
        lo = min(o, c) - abs(rng.normal(0.18, 0.1))
        candles.append((o, hi, lo, c))
        prev = c
    # keep the base clearly above the stop
    candles = [(o, h, max(l, 48.32) if i >= 14 else l, c) for i, (o, h, l, c) in enumerate(candles)]
    return candles


VIGNETTE = make_vignette()
WALK, WALK_X, WALK_Y = make_walk()
LOGO = make_logo()
GLOW = LOGO["glow"]
CANDLES = make_candles()


# ================================================================= scenes ===
def ease_out_expo(x):
    return 1.0 if x >= 1 else 1 - 2 ** (-10 * x)


def sting_state(t):
    """Logo animation (about 2.2 s): rise in, ring draws, light sweep, lift away."""
    p_in = ease_out_expo(prog(t, 0.10, 0.95))
    a_in = ease_io(prog(t, 0.10, 0.50))
    p_out = prog(t, 1.70, 2.25)
    e_out = p_out ** 2.2
    alpha = a_in * (1 - ease_io(p_out))
    y_off = (1 - p_in) * 170 - e_out * 80
    scale = (0.90 + 0.10 * p_in) * (1 + 0.035 * e_out)
    ring_p = ease_io(prog(t, 0.45, 1.30))
    shine = prog(t, 0.95, 1.65)
    shine_pos = -0.35 + 1.75 * ease_io(shine) if 0 < shine < 1 else None
    glow_a = ease_io(prog(t, 0.30, 1.10)) * (0.85 + 0.15 * math.sin(t * 5.0))
    return alpha, y_off, scale, ring_p, shine_pos, glow_a


def scene_sting(base, t):
    if t > 2.3:
        return
    # motion blur: average sub-frames while the logo is moving quickly
    moving = t < 0.95 or t > 1.70
    offs = (-0.375, -0.125, 0.125, 0.375) if moving else (0.0,)
    acc_p = None   # premultiplied colour sum
    acc_a = None   # alpha sum
    _, _, _, ring_p, shine_pos, glow_a = sting_state(t)   # ring + light sweep: no blur
    base_layer = logo_layer(LOGO, ring_p, shine_pos)
    for o in offs:
        tt = max(0.0, t + o / FPS)
        alpha, y_off, scale, _, _, _ = sting_state(tt)     # movement: blurred
        sub = Image.new("RGBA", (W, H), (0, 0, 0, 0))
        if alpha > 0.003:
            layer = base_layer
            sz = int(round(layer.width * scale))
            if sz != layer.width:
                layer = layer.resize((sz, sz), Image.LANCZOS)
            cx, cy = W / 2, H / 2 + y_off
            blit(sub, GLOW, cx - GLOW.width / 2, cy - GLOW.height / 2, alpha * glow_a)
            blit(sub, layer, cx - sz / 2, cy - sz / 2, alpha)
        arr = np.asarray(sub, np.float32)
        pm = arr[..., :3] * arr[..., 3:4] / 255.0
        acc_p = pm if acc_p is None else acc_p + pm
        acc_a = arr[..., 3:4] if acc_a is None else acc_a + arr[..., 3:4]
    rgb = acc_p * 255.0 / np.maximum(acc_a, 1e-3)
    out = np.concatenate([np.clip(rgb, 0, 255), acc_a / len(offs)], -1)
    base.alpha_composite(Image.fromarray(out.astype(np.uint8), "RGBA"))


def scene_cold_open(base, t):
    a = fade(t, 2.2, 13.4, 1.2, 0.8)
    if a <= 0:
        return
    # faint grid
    for gy in range(300, 820, 104):
        hline(base, 0, W, gy, GRID, a * 0.55)
    p = ease_io(prog(t, 2.4, 13.2))
    xr = int(p * W)
    if xr > 0:
        blit(base, WALK.crop((0, 0, xr, H)), 0, 0, a)
        i = int(p * (len(WALK_X) - 1))
        hx, hy = WALK_X[i], WALK_Y[i]
        blit(base, GLOW.resize((120, 120)), hx - 60, hy - 60, a * 0.8)
        dot = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
        ImageDraw.Draw(dot).ellipse((0, 0, 13, 13), fill=GOLD + (255,))
        blit(base, dot, hx - 7, hy - 7, a)


def scene_title(base, t):
    a = fade(t, 13.4, 19.4, 1.4, 0.7)
    if a <= 0:
        return
    p = ease_out(prog(t, 13.4, 19.4))
    tracking = int(16 + 14 * p)
    draw_text(base, "MARKET WIZARDS", W / 2, 440, "display_light", 120, WHITE, a, "m", tracking)
    rw = 560 * ease_io(prog(t, 14.4, 15.6))
    hline(base, W / 2 - rw / 2, W / 2 + rw / 2, 610, GOLD, a, 2)
    a2 = a * ease_io(prog(t, 15.2, 16.4))
    draw_text(base, "THE TRADERS  ·  THE METHODS  ·  THE LESSONS", W / 2, 650, "regular", 24, MUTED, a2, "m", 7)


def scene_chapter(base, t):
    a = fade(t, 19.4, 24.6, 0.8, 0.6)
    if a <= 0:
        return
    bh = 230 * ease_out(prog(t, 19.5, 20.4))
    rect(base, (300, 425, 303, 425 + bh), GOLD, a)
    a1 = a * ease_out(prog(t, 19.9, 20.7))
    draw_text(base, "CHAPTER ONE", 344, 440, "medium", 26, GOLD, a1, "l", 9)
    p2 = ease_out(prog(t, 20.3, 21.4))
    draw_text(base, "The Arithmetic of Survival", 340 + 30 * (1 - p2), 492, "display_light", 96, WHITE, a * p2)
    a3 = a * ease_out(prog(t, 21.2, 22.2))
    draw_text(base, "Why risk per trade decides who is still trading tomorrow", 344, 622, "regular", 28, MUTED, a3)


def header(base, a, title):
    draw_text(base, "THE ARITHMETIC OF SURVIVAL", 150, 104, "medium", 20, GOLD, a, "l", 6)
    draw_text(base, title, 150, 138, "display_light", 50, WHITE, a)


# --- Scene E: two traders, one losing streak --------------------------------
PX0, PX1, PY0, PY1 = 270, 1220, 270, 760


def ex(k):
    return PX0 + k / STREAK * (PX1 - PX0)


def ey(v):
    return PY1 - v / START * (PY1 - PY0)


def eq_at(r, p):
    return START * (1 - r) ** p


def scene_streak(base, t):
    a = fade(t, 24.6, 55.8, 0.8, 0.6)
    if a <= 0:
        return
    header(base, a * ease_out(prog(t, 24.8, 25.6)), "One losing streak. Two outcomes.")
    ga = a * ease_io(prog(t, 25.2, 26.4))
    for v in (0, 25_000, 50_000, 75_000, 100_000):
        hline(base, PX0, PX1, ey(v), GRID if v else BORDER, ga)
        draw_text(base, "$%dk" % (v // 1000), PX0 - 18, ey(v) - 14, "mono", 20, FAINT, ga, "r")
    for k in range(STREAK + 1):
        draw_text(base, str(k), ex(k), PY1 + 14, "mono", 20, FAINT, ga, "m")
    draw_text(base, "CONSECUTIVE LOSING TRADES", (PX0 + PX1) / 2, PY1 + 52, "medium", 16, FAINT, ga, "m", 5)

    p = STREAK * ease_io(prog(t, 36.2, 45.4))  # trades elapsed (continuous)

    # lines (2x supersampled for smooth diagonals)
    if p > 0:
        S = 2
        ox, oy = PX0 - 20, PY0 - 20
        lw, lh = PX1 - PX0 + 40, PY1 - PY0 + 40
        layer = Image.new("RGBA", (lw * S, lh * S), (0, 0, 0, 0))
        d = ImageDraw.Draw(layer)
        for r, col in ((RISK_A, RISK), (RISK_B, GOLD)):
            n = int(p)
            pts = [(ex(k), ey(eq_at(r, k))) for k in range(n + 1)]
            if p > n:
                pts.append((ex(p), ey(eq_at(r, p))))
            pts2 = [((x - ox) * S, (y - oy) * S) for x, y in pts]
            if len(pts2) > 1:
                d.line(pts2, fill=col + (255,), width=3 * S, joint="curve")
            for x, y in pts2[: n + 1]:
                d.ellipse((x - 5 * S, y - 5 * S, x + 5 * S, y + 5 * S), fill=col + (255,))
            hx, hy = pts2[-1]
            d.ellipse((hx - 7 * S, hy - 7 * S, hx + 7 * S, hy + 7 * S), fill=col + (255,))
        layer = layer.resize((lw, lh), Image.LANCZOS)
        blit(base, layer, ox, oy, a)
    else:
        for col in (RISK, GOLD):
            dot = Image.new("RGBA", (14, 14), (0, 0, 0, 0))
            ImageDraw.Draw(dot).ellipse((0, 0, 13, 13), fill=col + (255,))
            blit(base, dot, ex(0) - 7, ey(START) - 7, ga * ease_io(prog(t, 30.0, 33.0)))

    # end labels
    la = a * ease_out(prog(t, 45.4, 46.2))
    draw_text(base, money(EQ_B[-1]), PX1 - 14, ey(EQ_B[-1]) - 50, "mono_medium", 28, GOLD, la, "r")
    draw_text(base, money(EQ_A[-1]), PX1 - 14, ey(EQ_A[-1]) + 14, "mono_medium", 28, RISK, la, "r")

    # difference bracket
    ba = a * ease_out(prog(t, 49.0, 49.9))
    if ba > 0:
        x = PX1 + 18
        y0, y1 = ey(EQ_B[-1]), ey(EQ_A[-1])
        grow = ease_io(prog(t, 49.0, 49.9))
        vline(base, x, y0, y0 + (y1 - y0) * grow, WHITE, ba * 0.85, 2)
        hline(base, x - 8, x + 2, y0, WHITE, ba * 0.85, 2)
        hline(base, x - 8, x + 2, y0 + (y1 - y0) * grow, WHITE, ba * 0.85, 2)
        ym = (y0 + y1) / 2
        draw_text(base, money(EQ_B[-1] - EQ_A[-1]), x - 24, ym - 34, "mono_medium", 30, WHITE, ba, "r")
        draw_text(base, "DIFFERENCE", x - 24, ym + 6, "medium", 16, MUTED, ba, "r", 5)

    # trader cards
    for i, (name, r, col, t0) in enumerate((("TRADER A", RISK_A, RISK, 29.8), ("TRADER B", RISK_B, GOLD, 32.4))):
        ca = a * ease_out(prog(t, t0, t0 + 0.7))
        if ca <= 0:
            continue
        x0, y0 = 1330, 262 + i * 262 + 20 * (1 - ca)
        rect(base, (x0, y0, x0 + 440, y0 + 230), PANEL, ca)
        hline(base, x0, x0 + 440, y0, BORDER, ca)
        hline(base, x0, x0 + 440, y0 + 229, BORDER, ca)
        vline(base, x0 + 439, y0, y0 + 230, BORDER, ca)
        rect(base, (x0, y0, x0 + 4, y0 + 230), col, ca)
        draw_text(base, name, x0 + 32, y0 + 26, "semibold", 18, col, ca, "l", 6)
        draw_text(base, "Risks %d%% per trade" % round(r * 100), x0 + 32, y0 + 58, "regular", 28, WHITE, ca)
        n = STREAK if p >= STREAK - 1e-6 else int(p)  # completed trades only: every figure exact
        draw_text(base, money(eq_at(r, n)), x0 + 32, y0 + 112, "mono_medium", 54, WHITE, ca)
        draw_text(base, "after %d losing trade%s" % (n, "" if n == 1 else "s"), x0 + 32, y0 + 184,
                  "regular", 20, MUTED, ca)


# --- Scene F: recovery asymmetry --------------------------------------------
BX0, BPX = 430, 6.0  # bar origin, px per percent


def scene_recovery(base, t):
    a = fade(t, 55.8, 81.0, 0.8, 0.6)
    if a <= 0:
        return
    header(base, a * ease_out(prog(t, 56.0, 56.8)), "The gain required to break even")
    ga = a * ease_io(prog(t, 56.6, 57.6))
    for pct in (0, 50, 100, 150, 200):
        x = BX0 + pct * BPX
        vline(base, x, 290, 812, GRID if pct else BORDER, ga)
        draw_text(base, "%d%%" % pct, x, 826, "mono", 18, FAINT, ga, "m")
    # legend
    rect(base, (1360, 120, 1392, 132), LOSSBAR, ga)
    draw_text(base, "LOSS", 1404, 112, "medium", 16, MUTED, ga, "l", 4)
    rect(base, (1500, 120, 1532, 132), GOLD, ga)
    draw_text(base, "GAIN NEEDED TO RECOVER", 1544, 112, "medium", 16, MUTED, ga, "l", 4)

    starts = (61.0, 64.6, 68.8, 74.6)
    for i, ((loss, gain), t0) in enumerate(zip(RECOVERY, starts)):
        ra = a * ease_out(prog(t, t0, t0 + 0.5))
        if ra <= 0:
            continue
        y = 300 + i * 130
        lp = loss * 100
        label = "Lose %g%%" % round(lp, 1) if i < 3 else "Lose %.1f%%" % lp
        draw_text(base, label, 150, y + 8, "regular", 32, WHITE, ra)
        if i == 3:
            draw_text(base, "TRADER A", 152, y + 54, "semibold", 16, RISK, ra, "l", 5)
        lw = lp * BPX * ease_io(prog(t, t0, t0 + 0.8))
        gw = gain * 100 * BPX * ease_io(prog(t, t0 + 0.5, t0 + 1.6))
        rect(base, (BX0, y + 6, BX0 + lw, y + 26), LOSSBAR, ra)
        rect(base, (BX0, y + 38, BX0 + gw, y + 58), GOLD, ra)
        draw_text(base, "−%s%%" % ("%g" % round(lp, 1)), BX0 + lw + 14, y + 2, "mono", 22, MUTED,
                  ra * ease_out(prog(t, t0 + 0.6, t0 + 1.0)))
        gtxt = "+%g%%" % round(gain * 100, 1)
        draw_text(base, gtxt, BX0 + gw + 14, y + 33, "mono_medium", 24, GOLD,
                  ra * ease_out(prog(t, t0 + 1.4, t0 + 1.9)))


# --- Scene G: position sizing -----------------------------------------------
CX0, CX1, CY0, CY1 = 150, 1010, 270, 800
PMIN, PMAX = 46.0, 52.0


def cy(price):
    return CY1 - (price - PMIN) / (PMAX - PMIN) * (CY1 - CY0)


def scene_sizing(base, t):
    a = fade(t, 81.0, 112.0, 0.8, 0.6)
    if a <= 0:
        return
    header(base, a * ease_out(prog(t, 81.2, 82.0)), "Sizing a position from risk")
    ga = a * ease_io(prog(t, 81.4, 82.4))
    for pr in range(46, 53):
        hline(base, CX0, CX1, cy(pr), GRID, ga)
        draw_text(base, "%.2f" % pr, CX1 + 14, cy(pr) - 13, "mono", 18, FAINT, ga)
    draw_text(base, "HYPOTHETICAL STOCK  ·  DAILY", CX0, CY1 + 16, "medium", 16, FAINT, ga, "l", 5)

    step = (CX1 - CX0 - 300) / len(CANDLES)
    for i, (o, hi, lo, c) in enumerate(CANDLES):
        ta = ga * ease_out(prog(t, 81.6 + i * 0.065, 81.9 + i * 0.065))
        if ta <= 0:
            continue
        xc = CX0 + 20 + i * step + step / 2
        col = CANDLE_UP if c >= o else CANDLE_DN
        vline(base, xc - 1, cy(hi), cy(lo), col, ta, 2)
        top, bot = cy(max(o, c)), cy(min(o, c))
        rect(base, (xc - 6, top, xc + 6, max(bot, top + 2)), col, ta)

    xe = CX0 + 20 + (len(CANDLES) - 1) * step + step / 2
    # risk zone
    za = a * ease_out(prog(t, 95.2, 96.0))
    rect(base, (xe + 30, cy(ENTRY), CX1, cy(STOP)), RISK, za * 0.13)
    zx = (xe + 30 + CX1) / 2
    draw_text(base, "$2.00 RISK", zx, (cy(ENTRY) + cy(STOP)) / 2 - 26, "semibold", 18, RISK, za, "m", 4)
    draw_text(base, "PER SHARE", zx, (cy(ENTRY) + cy(STOP)) / 2 + 2, "semibold", 18, RISK, za, "m", 4)
    # entry and stop lines
    pe = ease_io(prog(t, 93.2, 93.9))
    hline(base, CX0, CX0 + (CX1 - CX0) * pe, cy(ENTRY), WHITE, a * 0.9 * min(1, pe * 4), 2)
    draw_text(base, "ENTRY  50.00", CX1 - 6, cy(ENTRY) - 34, "semibold", 17, WHITE,
              a * ease_out(prog(t, 93.6, 94.1)), "r", 3)
    ps = ease_io(prog(t, 94.6, 95.3))
    hline(base, CX0, CX0 + (CX1 - CX0) * ps, cy(STOP), RISK, a * min(1, ps * 4), 2, dash=(14, 8))
    draw_text(base, "STOP  48.00", CX1 - 6, cy(STOP) + 12, "semibold", 17, RISK,
              a * ease_out(prog(t, 95.0, 95.5)), "r", 3)

    # calculation panel
    PXL = 1170
    vline(base, PXL, 270, 270 + 580 * ease_out(prog(t, 81.8, 83.0)), GOLD, a * 0.8, 2)
    rows = [
        (82.2, "ACCOUNT", money(START), "mono_medium", 40, WHITE),
        (87.2, "RISK PER TRADE  ·  1%", money(RISK_DOLLARS), "mono_medium", 40, WHITE),
        (94.8, "RISK PER SHARE", "$50.00 − $48.00 = $2.00", "mono", 32, WHITE),
        (99.8, "POSITION SIZE", "$1,000 ÷ $2.00", "mono", 32, WHITE),
        (105.6, "MAXIMUM PLANNED LOSS", "$1,000  (1% of account)", "mono", 32, WHITE),
    ]
    ys = [270, 380, 490, 590, 750]
    for n, ((t0, lab, val, fk, fs, col), y) in enumerate(zip(rows, ys)):
        ra = a * ease_out(prog(t, t0, t0 + 0.6))
        if ra <= 0:
            continue
        dx = 16 * (1 - ra / max(a, 1e-6))
        draw_text(base, "%02d" % (n + 1), PXL + 30 + dx, y + 2, "mono", 16, GOLD, ra)
        draw_text(base, lab, PXL + 66 + dx, y, "medium", 18, MUTED, ra, "l", 4)
        draw_text(base, val, PXL + 30 + dx, y + 34, fk, fs, col, ra)
    big = a * ease_out(prog(t, 100.8, 101.6))
    draw_text(base, "= %d shares" % SHARES, PXL + 30, 668, "display_semibold", 52, GOLD, big)
    draw_text(base, "Gaps and slippage can make a loss larger than planned.", PXL + 30, 838,
              "italic", 20, MUTED, a * ease_out(prog(t, 107.6, 108.4)))


def scene_outro(base, t):
    a = fade(t, 112.0, 117.2, 1.0, 0.8)
    if a > 0:
        p = ease_io(prog(t, 112.0, 117.2))
        xr = int(p * W)
        if xr > 0:
            blit(base, WALK.crop((0, 0, xr, H)), 0, 0, a * 0.7)
    e = fade(t, 117.2, 121.2, 1.0, 0.9)
    if e > 0:
        draw_text(base, "MARKET WIZARDS", W / 2, 440, "display_light", 84, WHITE, e, "m", 26)
        hline(base, W / 2 - 200, W / 2 + 200, 560, GOLD, e, 2)
        draw_text(base, "EPISODE ONE  ·  COMING SOON", W / 2, 594, "regular", 22, MUTED, e, "m", 7)
        draw_text(base, "All figures shown are hypothetical and for educational purposes only. Not investment advice.",
                  W / 2, 990, "regular", 18, FAINT, e, "m")


# ------------------------------------------------------------- subtitles ---
def wrap(text, fkey, size, maxw):
    words, lines, cur = text.split(), [], ""
    for wd in words:
        trial = (cur + " " + wd).strip()
        if text_w(trial, fkey, size) <= maxw or not cur:
            cur = trial
        else:
            lines.append(cur)
            cur = wd
    if cur:
        lines.append(cur)
    if len(lines) == 2 and len(lines[1].split()) < 4:
        ws = text.split()
        best = min(range(1, len(ws)), key=lambda i: abs(text_w(" ".join(ws[:i]), fkey, size)
                                                       - text_w(" ".join(ws[i:]), fkey, size)))
        lines = [" ".join(ws[:best]), " ".join(ws[best:])]
    return lines


def subtitles(base, t):
    for s, e, txt in NARRATION:
        if s - 0.01 <= t <= e:
            a = fade(t, s, e, 0.18, 0.18)
            lines = wrap(txt, "medium", 38, 1640)
            lh = 52
            y = 1012 - len(lines) * lh
            for ln in lines:
                draw_text(base, ln, W / 2, y, "medium", 38, WHITE, a, "m", 0, shadow=True)
                y += lh


# ================================================================ compose ===
def frame(t):
    base = Image.new("RGBA", (W, H), BLACK + (255,))
    va = prog(t, 2.1, 3.4) * (1 - prog(t, 120.2, 121.0))
    if va > 0:
        blit(base, VIGNETTE, 0, 0, va)
    scene_sting(base, t)
    scene_cold_open(base, t)
    scene_title(base, t)
    scene_chapter(base, t)
    scene_streak(base, t)
    scene_recovery(base, t)
    scene_sizing(base, t)
    scene_outro(base, t)
    subtitles(base, t)
    return base.convert("RGB")


# ================================================================== audio ===
def make_audio(path, sr=44100):
    """Original synthesized ambient pad + logo hit (placeholder for licensed score)."""
    n = int(DURATION * sr)
    t = np.arange(n) / sr
    L = np.zeros(n, np.float64)
    R = np.zeros(n, np.float64)

    def hz(m):
        return 440.0 * 2 ** ((m - 69) / 12)

    # A minor — F major7 — D minor9 — E sus, slow and low
    chords = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 64], [38, 45, 50, 53, 57, 64], [40, 47, 52, 57, 59]]
    seg = 10.0
    start = 2.0
    k = 0
    while start < DURATION:
        notes = chords[k % len(chords)]
        a0, a1 = start - 3.0, start + seg + 3.0
        i0, i1 = max(0, int(a0 * sr)), min(n, int(a1 * sr))
        tt = t[i0:i1]
        env = np.clip((tt - a0) / 4.0, 0, 1) * np.clip((a1 - tt) / 4.0, 0, 1)
        env = np.sin(env * np.pi / 2) ** 2
        for j, m in enumerate(notes):
            f = hz(m)
            amp = (0.9 if j == 0 else 0.5) / len(notes)
            for det, side in ((-0.18, 0), (0.18, 1)):
                ph = 2 * np.pi * (f + det) * tt
                w = np.sin(ph) + 0.18 * np.sin(2 * ph) + 0.05 * np.sin(3 * ph)
                trem = 1 + 0.08 * np.sin(2 * np.pi * 0.11 * tt + j)
                (L if side == 0 else R)[i0:i1] += amp * env * trem * w
        start += seg
        k += 1
    mix = np.stack([L, R], 1)
    mix *= 0.16
    master = np.clip((t - 2.0) / 4.0, 0, 1) * np.clip((DURATION - t) / 3.0, 0, 1)
    mix *= master[:, None]

    # logo hit: low swell + soft air
    rng = np.random.default_rng(5)
    for t0, gain in ((0.08, 0.55), (19.5, 0.25)):
        i0 = int(t0 * sr)
        ln = int(2.4 * sr)
        tt = np.arange(ln) / sr
        f = 70 * np.exp(-tt * 0.9) + 38
        boom = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 2.2) * np.clip(tt / 0.03, 0, 1)
        air = rng.normal(0, 1, ln)
        air = np.convolve(air, np.ones(60) / 60, mode="same") * np.exp(-((tt - 0.25) ** 2) / 0.05) * 0.6
        hit = (boom + air) * gain
        e = min(n, i0 + ln)
        mix[i0:e, 0] += hit[: e - i0]
        mix[i0:e, 1] += hit[: e - i0]

    # soft chime as the gold ring draws and the light sweeps across the logo
    for t0, notes, gain in ((0.50, (1318.5, 1760.0), 0.05), (1.05, (2637.0, 1975.5), 0.03)):
        i0 = int(t0 * sr)
        ln = int(2.0 * sr)
        tt = np.arange(ln) / sr
        ch = sum(np.sin(2 * np.pi * f * tt) for f in notes) * np.exp(-tt * 2.6) * np.clip(tt / 0.01, 0, 1)
        e = min(n, i0 + ln)
        mix[i0:e, 0] += ch[: e - i0] * gain
        mix[i0:e, 1] += ch[: e - i0] * gain * 0.85
    mix = np.clip(mix, -1, 1)
    pcm = (mix * 32767).astype("<i2")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# ================================================================ render ===
def render_chunk(args):
    idx, f0, f1 = args
    out = os.path.join(OUT, "chunk_%02d.mp4" % idx)
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "18", "-pix_fmt", "yuv420p",
           "-x264-params", "aq-mode=3", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        proc.stdin.write(frame(fi / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    return out


def stills():
    d = os.path.join(OUT, "stills")
    os.makedirs(d, exist_ok=True)
    times = [1.0, 9.0, 17.5, 22.5, 52.0, 79.0, 108.0, 119.0]
    imgs = []
    for tt in times:
        im = frame(tt)
        im.save(os.path.join(d, "t%05.1f.png" % tt))
        imgs.append(im)
    sheet = Image.new("RGB", (960 * 2 + 30, 540 * 4 + 50), (30, 30, 30))
    for i, im in enumerate(imgs):
        sheet.paste(im.resize((960, 540), Image.LANCZOS), (10 + (i % 2) * 970, 10 + (i // 2) * 550))
    sheet.save(os.path.join(d, "contact-sheet.png"))
    print("stills ->", d)


def render_intro():
    """Standalone JSR logo intro (logo sting only) for reuse on any video."""
    dur = 2.6
    wav = os.path.join(OUT, "intro.wav")
    make_audio(wav)
    out = os.path.join(OUT, "jsr-intro.mp4")
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-", "-t", str(dur), "-i", wav,
           "-c:v", "libx264", "-preset", "medium", "-crf", "16", "-pix_fmt", "yuv420p",
           "-af", "afade=t=out:st=%.2f:d=0.4" % (dur - 0.4), "-c:a", "aac", "-b:a", "192k",
           "-shortest", "-movflags", "+faststart", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(int(dur * FPS)):
        im = Image.new("RGBA", (W, H), BLACK + (255,))
        scene_sting(im, fi / FPS)
        proc.stdin.write(im.convert("RGB").tobytes())
    proc.stdin.close()
    proc.wait()
    os.remove(wav)
    print("done ->", out)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--stills" in sys.argv:
        stills()
        return
    if "--intro" in sys.argv:
        render_intro()
        return
    total = int(DURATION * FPS)
    workers = os.cpu_count() or 4
    bounds = np.linspace(0, total, workers * 2 + 1).astype(int)
    jobs = [(i, bounds[i], bounds[i + 1]) for i in range(len(bounds) - 1)]
    with Pool(workers) as pool:
        chunks = pool.map(render_chunk, jobs)
    lst = os.path.join(OUT, "chunks.txt")
    with open(lst, "w") as f:
        for c in chunks:
            f.write("file '%s'\n" % c)
    wav = os.path.join(OUT, "music.wav")
    make_audio(wav)
    final = os.path.join(OUT, "market-wizards-sample-01.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst,
                    "-i", wav, "-c:v", "copy", "-c:a", "aac", "-b:a", "192k", "-shortest",
                    "-movflags", "+faststart", final], check=True)
    for c in chunks:
        os.remove(c)
    os.remove(lst)
    os.remove(wav)
    print("done ->", final)


if __name__ == "__main__":
    main()
