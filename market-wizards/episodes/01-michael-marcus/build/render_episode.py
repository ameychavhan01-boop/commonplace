#!/usr/bin/env python3
"""
Market Wizards — Episode 01: Michael Marcus
Full-episode renderer. Reuses the house style and helpers from sample-01/render.py.

Inputs : build/timeline.json (from align.py), audio/chNN.mp3
Output : output/market-wizards-ep01-michael-marcus.mp4

    python3 build/render_episode.py            # full render
    python3 build/render_episode.py --stills   # one still per visual cue -> output/stills/
    python3 build/render_episode.py --range 300 360   # render a time window (preview)
"""
import json
import math
import os
import subprocess
import sys
import wave
from functools import lru_cache
from multiprocessing import Pool

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
SAMPLE = os.path.join(EP, "..", "..", "sample-01")
sys.path.insert(0, SAMPLE)
import render as R  # noqa: E402  (house style helpers)

W, H, FPS = R.W, R.H, R.FPS
OUT = os.path.join(EP, "output")
TL = json.load(open(os.path.join(HERE, "timeline.json")))
DUR = TL["duration"]
CARD = 5.0
GOLD, WHITE, MUTED, FAINT, RISK = R.GOLD, R.WHITE, R.MUTED, R.FAINT, R.RISK
PANEL, BORDER, GRID = R.PANEL, R.BORDER, R.GRID
LOSSBAR = R.LOSSBAR
AMBER = (214, 150, 70)

clamp, prog, ease_io, ease_out = R.clamp, R.prog, R.ease_io, R.ease_out


# ===================================================================== keys ==
SUBS = TL["subtitles"]


@lru_cache(maxsize=None)
def K(prefix, after=0.0):
    """Global time at which the subtitle starting with `prefix` begins."""
    for s in SUBS:
        if s["t0"] >= after - 0.01 and s["text"].startswith(prefix):
            return s["t0"]
    raise KeyError(prefix)


CHAPTERS = {c["id"]: c for c in TL["chapters"]}
CH_TITLES = {
    2: ("CHAPTER ONE", "The Scholar", "1969"),
    3: ("CHAPTER TWO", "The Blight", "1970 – 1971"),
    4: ("CHAPTER THREE", "Behind the Glass", "1971 – 1972"),
    5: ("CHAPTER FOUR", "The Ceiling That Broke", "1972"),
    6: ("CHAPTER FIVE", "The Same Mistake Twice", "1972"),
    7: ("CHAPTER SIX", "The Great Inflation", "1973"),
    8: ("CHAPTER SEVEN", "The Floor", "New York Cotton Exchange"),
    9: ("CHAPTER EIGHT", "“He Just Trades”", "Commodities Corporation · 1974 – 1984"),
    10: ("CHAPTER NINE", "The Night Shift", "1978 – 1984"),
    11: ("CHAPTER TEN", "Market Tone", "The method"),
    12: ("CHAPTER ELEVEN", "The Price of Success", "Life outside the markets"),
    13: ("CHAPTER TWELVE", "The Rules", "Advice to traders"),
    14: ("CHAPTER THIRTEEN", "Was He Right?", "Analysis"),
    15: ("EPILOGUE", "Every Failure, a Rule", "1988 – 2023"),
}


# ================================================================= helpers ==
def appear(lt, start, d=0.6):
    return ease_out(prog(lt, start, start + d))


def T(base, s, x, y, key, size, color, a=1.0, anchor="l", tr=0, shadow=False):
    return R.draw_text(base, s, x, y, key, size, color, a, anchor, tr, shadow)


def rect(base, box, color, a=1.0):
    R.rect(base, box, color, a)


def frame_box(base, x0, y0, x1, y1, a, stripe=None, fill=PANEL):
    rect(base, (x0, y0, x1, y1), fill, a)
    R.hline(base, x0, x1, y0, BORDER, a)
    R.hline(base, x0, x1, y1 - 1, BORDER, a)
    R.vline(base, x0, y0, y1, BORDER, a)
    R.vline(base, x1 - 1, y0, y1, BORDER, a)
    if stripe:
        rect(base, (x0, y0, x0 + 4, y1), stripe, a)


def aa_lines(base, polylines, a=1.0, S=2):
    """polylines: list of (points, color, width[, alpha]) drawn anti-aliased."""
    xs = [p[0] for pl in polylines for p in pl[0]]
    ys = [p[1] for pl in polylines for p in pl[0]]
    if not xs or a <= 0.003:
        return
    pad = 12
    x0, y0 = int(min(xs)) - pad, int(min(ys)) - pad
    x1, y1 = int(max(xs)) + pad, int(max(ys)) + pad
    w, h = max(2, x1 - x0), max(2, y1 - y0)
    layer = Image.new("RGBA", (w * S, h * S), (0, 0, 0, 0))
    d = ImageDraw.Draw(layer)
    for pl in polylines:
        pts, col, wd = pl[0], pl[1], pl[2]
        al = pl[3] if len(pl) > 3 else 1.0
        if len(pts) >= 2:
            d.line([((x - x0) * S, (y - y0) * S) for x, y in pts], fill=col + (int(255 * al),),
                   width=max(1, int(wd * S)), joint="curve")
    layer = layer.resize((w, h), Image.LANCZOS)
    R.blit(base, layer, x0, y0, a)


@lru_cache(maxsize=256)
def _disc(r, color, alpha255):
    S = 4
    im = Image.new("RGBA", (r * 2 * S + 2, r * 2 * S + 2), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((1, 1, r * 2 * S, r * 2 * S), fill=color + (alpha255,))
    return im.resize((r * 2 + 1, r * 2 + 1), Image.LANCZOS)


def dot(base, x, y, r, color, a=1.0):
    r = max(1, int(r))
    im = _disc(r, color, 255)
    R.blit(base, im, x - r, y - r, a)


@lru_cache(maxsize=64)
def _ring(r, width, color):
    S = 4
    im = Image.new("RGBA", (r * 2 * S + 4, r * 2 * S + 4), (0, 0, 0, 0))
    ImageDraw.Draw(im).ellipse((2, 2, r * 2 * S, r * 2 * S), outline=color + (255,), width=width * S)
    return im.resize((r * 2 + 1, r * 2 + 1), Image.LANCZOS)


def ring(base, x, y, r, color, a=1.0, width=2):
    im = _ring(int(r), width, color)
    R.blit(base, im, x - r, y - r, a)


def header(base, a, eyebrow, title, y=96):
    T(base, eyebrow, 150, y, "medium", 20, GOLD, a, "l", 6)
    T(base, title, 150, y + 34, "display_light", 50, WHITE, a)


def source(base, a, s, x=150, y=846):
    T(base, "SOURCE  ·  " + s, x, y, "mono", 16, FAINT, a, "l", 1)


def counter(v, fmt="${:,.0f}"):
    return fmt.format(v)


def series(seed, n, start, end, vol, shape=None):
    """Deterministic synthetic path from start to end (illustrative charts)."""
    rng = np.random.default_rng(seed)
    steps = rng.normal(0, vol, n)
    path = np.cumsum(steps)
    path = path - np.linspace(0, path[-1], n)
    base = np.linspace(start, end, n) if shape is None else shape
    return base + path


def chart_axes(base, a, x0, y0, x1, y1, vmin, vmax, ticks, fmt, xlabels=None):
    for v in ticks:
        y = y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)
        R.hline(base, x0, x1, y, GRID, a)
        T(base, fmt(v), x1 + 14, y - 12, "mono", 18, FAINT, a)
    if xlabels:
        for xx, lab in xlabels:
            T(base, lab, xx, y1 + 14, "mono", 18, FAINT, a, "m")


def lesson(base, a, lines, y=380, sub=None, eyebrow=None):
    if eyebrow:
        T(base, eyebrow, W / 2, y - 70, "medium", 22, GOLD, a, "m", 8)
    yy = y
    for ln in lines:
        T(base, ln, W / 2, yy, "display_light", 64, WHITE, a, "m")
        yy += 84
    R.hline(base, W / 2 - 150, W / 2 + 150, yy + 22, GOLD, a, 2)
    if sub:
        T(base, sub, W / 2, yy + 54, "regular", 30, MUTED, a, "m")


# ============================================================== backgrounds ==
def ambient(base, t, a=1.0):
    off = int((t * 18) % W)
    strip = R.WALK
    if off > 0:
        R.blit(base, strip.crop((off, 0, W, H)), 0, 40, a * 0.10)
        R.blit(base, strip.crop((0, 0, off, H)), W - off, 40, a * 0.10)


def chapter_card(base, t, c):
    lt = t - c["t0"]
    if lt < 0 or lt > CARD:
        return
    a = R.fade(lt, 0, CARD, 0.7, 0.6)
    num, title, years = CH_TITLES[c["id"]]
    bh = 250 * ease_out(prog(lt, 0.1, 1.0))
    rect(base, (300, 400, 303, 400 + bh), GOLD, a)
    T(base, num, 344, 418, "medium", 26, GOLD, a * appear(lt, 0.4), "l", 9)
    p2 = appear(lt, 0.7, 1.0)
    T(base, title, 340 + 30 * (1 - p2), 468, "display_light", 100, WHITE, a * p2)
    T(base, years, 344, 604, "regular", 28, MUTED, a * appear(lt, 1.4))


# ================================================================== scenes ==
# Every scene: f(base, t, lt, dur, a) — global time, local time, duration, alpha.

def s_board(base, t, lt, dur, a, freeze_at=None, unfreeze=False, dim=1.0):
    """Stylised quote board; CORN ticks down then locks limit-down."""
    if freeze_at is None:
        freeze_at = K("Then the board stops moving") - (t - lt)
    x0, x1 = 300, 1620
    T(base, "COMMODITY BOARD  ·  ILLUSTRATIVE", x0, 150, "medium", 18, FAINT, a * dim, "l", 6)
    rows = [("CORN", "DEC", 1.6200, -1), ("WHEAT", "DEC", 1.7150, 0), ("SOYBEANS", "NOV", 3.0850, 0),
            ("OATS", "DEC", 0.7425, 0), ("SOY MEAL", "DEC", 78.40, 0)]
    limit = 0.10
    for i, (name, mon, p0, trend) in enumerate(rows):
        y = 210 + i * 116
        frame_box(base, x0, y, x1, y + 96, a * dim * 0.9)
        T(base, name, x0 + 40, y + 28, "semibold", 34, WHITE, a * dim, "l", 3)
        T(base, mon, x0 + 290, y + 34, "mono", 26, MUTED, a * dim)
        if trend < 0:
            if unfreeze:
                tick = int(lt / 0.5)
                px = p0 - limit + 0.0025 * (math.sin(tick * 1.7) * 3 + tick * 0.4)
                locked = False
            else:
                steps = int(min(lt, freeze_at) / 0.55)
                px = max(p0 - limit, p0 - 0.0025 * steps * (1 + steps / 18))
                locked = lt >= freeze_at
            col = RISK
            chg = px - p0
        else:
            tick = int(lt / 0.8)
            px = p0 + 0.0025 * math.sin(tick * 1.3 + i) * (1 if p0 < 10 else 40)
            locked = False
            col = MUTED
            chg = px - p0
        fmt = "{:.2f}" if p0 > 10 else "{:.4f}"
        T(base, fmt.format(px), x0 + 480, y + 22, "mono_medium", 46, WHITE, a * dim)
        T(base, ("+" if chg >= 0 else "−") + fmt.format(abs(chg)), x0 + 760, y + 30, "mono", 30, col, a * dim)
        if locked:
            la = a * dim * appear(lt, freeze_at, 0.3)
            rect(base, (x0 + 1000, y + 18, x1 - 24, y + 78), RISK, la * 0.9)
            T(base, "LIMIT DOWN", (x0 + 1000 + x1 - 24) / 2, y + 30, "semibold", 26, (20, 10, 10), la, "m", 4)
    if not unfreeze and lt >= freeze_at:
        T(base, "TRADING HALTED — NO BUYERS AT THE LIMIT", W / 2, 820, "medium", 22, RISK,
          a * dim * appear(lt, freeze_at + 0.5), "m", 5)


def s_name(base, t, lt, dur, a):
    s_board(base, t, lt + 30, dur, a, freeze_at=0, dim=0.08)
    p = appear(lt, 0.3, 1.2)
    T(base, "MICHAEL MARCUS", W / 2, 330, "display_light", 120, WHITE, a * p, "m", 18)
    R.hline(base, W / 2 - 260 * p, W / 2 + 260 * p, 500, GOLD, a, 2)
    T(base, "Market Wizards (1989)  ·  Chapter One", W / 2, 532, "regular", 30, MUTED, a * appear(lt, 1.2), "m")
    k = K("According to Jack Schwager") - (t - lt)
    q = appear(lt, k, 0.8)
    T(base, "≈ 2,500×", W / 2, 610, "display_light", 96, GOLD, a * q, "m")
    T(base, "growth of his company account in ten years — as reported by Jack Schwager", W / 2, 726,
      "regular", 26, MUTED, a * q, "m")


def s_series_title(base, t, lt, dur, a):
    p = ease_out(prog(lt, 0, 3))
    T(base, "MARKET WIZARDS", W / 2, 380, "display_light", 130, WHITE, a * appear(lt, 0.2, 1.4), "m", int(14 + 14 * p))
    rw = 600 * ease_io(prog(lt, 1.0, 2.2))
    R.hline(base, W / 2 - rw / 2, W / 2 + rw / 2, 560, GOLD, a, 2)
    T(base, "EPISODE ONE  ·  MICHAEL MARCUS", W / 2, 600, "medium", 28, GOLD, a * appear(lt, 1.8), "m", 9)
    T(base, "The Trader Who Learned to Survive", W / 2, 660, "regular", 34, MUTED, a * appear(lt, 2.4), "m")


def s_ledger(base, t, lt, dur, a, title, eyebrow, rows, keys=None, x=300, y=300, step=120):
    header(base, a * appear(lt, 0.1), eyebrow, title)
    t0 = t - lt
    for i, row in enumerate(rows):
        st = (K(keys[i]) - t0) if keys and keys[i] else 0.5 + i * 1.6
        ra = a * appear(lt, st)
        yy = y + i * step + 20 * (1 - ra / max(a, 1e-6))
        lab, val = row[0], row[1]
        col = row[2] if len(row) > 2 else WHITE
        T(base, "%02d" % (i + 1), x, yy + 12, "mono", 20, GOLD, ra)
        T(base, lab, x + 60, yy, "medium", 22, MUTED, ra, "l", 4)
        T(base, val, x + 60, yy + 34, "display_light", 54, col, ra)


def s_futures(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "EXPLAINER", "What is a futures contract?")
    x0, y0 = 150, 260
    frame_box(base, x0, y0, x0 + 760, y0 + 470, a * appear(lt, 0.3), stripe=GOLD)
    fields = [("COMMODITY", "Corn"), ("QUANTITY", "5,000 bushels"), ("DELIVERY", "December"),
              ("PRICE", "$1.50 per bushel"), ("CONTRACT VALUE", "$7,500")]
    for i, (k, v) in enumerate(fields):
        fa = a * appear(lt, 0.6 + i * 0.7)
        T(base, k, x0 + 44, y0 + 40 + i * 84, "medium", 18, MUTED, fa, "l", 4)
        T(base, v, x0 + 44, y0 + 64 + i * 84, "semibold" if i == 4 else "regular", 34, GOLD if i == 4 else WHITE, fa)
    k = K("Traders don't pay the full value") - (t - lt)
    ma = a * appear(lt, k)
    bx = 1040
    T(base, "MARGIN — A SMALL DEPOSIT", bx, 260, "medium", 20, GOLD, ma, "l", 5)
    rect(base, (bx, 310, bx + 720, 360), LOSSBAR, ma)
    rect(base, (bx, 310, bx + 72, 360), GOLD, ma)
    T(base, "$750 deposit controls $7,500 of corn", bx, 376, "regular", 26, WHITE, ma)
    k2 = K("A small change in price") - (t - lt)
    la = a * appear(lt, k2)
    T(base, "PRICE  −5%", bx, 470, "mono_medium", 40, MUTED, la)
    rect(base, (bx, 530, bx + 720, 560), LOSSBAR, la)
    rect(base, (bx + 720 - 36 * ease_io(prog(lt, k2, k2 + 1)), 530, bx + 720, 560), MUTED, la)
    T(base, "ACCOUNT  −50%", bx, 600, "mono_medium", 40, RISK, la)
    rect(base, (bx, 660, bx + 720, 690), LOSSBAR, la)
    rect(base, (bx + 720 - 360 * ease_io(prog(lt, k2 + 0.5, k2 + 1.8)), 660, bx + 720, 690), RISK, la)
    T(base, "Hypothetical figures for illustration", bx, 720, "italic", 20, FAINT, la)


def s_spread(base, t, lt, dur, a, stamp=False):
    header(base, a * appear(lt, 0.1), "EXPLAINER", "The spread that couldn't lose")
    gx = 360
    base_y = 700
    hA, hF = 260, 410
    for i, (lab, h, col) in enumerate([("AUGUST", hA, MUTED), ("FEBRUARY", hF, WHITE)]):
        x = gx + i * 520
        ba = a * appear(lt, 0.4 + i * 0.5)
        hh = h * ease_io(prog(lt, 0.4 + i * 0.5, 1.4 + i * 0.5))
        rect(base, (x, base_y - hh, x + 220, base_y), col, ba * 0.85)
        T(base, lab, x + 110, base_y + 16, "semibold", 24, WHITE, ba, "m", 4)
        T(base, "PORK BELLIES", x + 110, base_y + 50, "medium", 16, MUTED, ba, "m", 4)
    sa = a * appear(lt, 2.2)
    bx = gx + 520 + 260
    R.vline(base, bx, base_y - hF, base_y - hA, GOLD, sa, 2)
    R.hline(base, bx - 10, bx + 10, base_y - hF, GOLD, sa, 2)
    R.hline(base, bx - 10, bx + 10, base_y - hA, GOLD, sa, 2)
    T(base, "SPREAD", bx + 24, base_y - (hF + hA) / 2 - 30, "semibold", 22, GOLD, sa, "l", 4)
    ca = a * appear(lt, 3.2)
    cx = bx + 230
    ch = 110
    R.vline(base, cx, base_y - hA - ch, base_y - hA, MUTED, ca, 2)
    R.hline(base, cx - 10, cx + 10, base_y - hA - ch, MUTED, ca, 2)
    R.hline(base, cx - 10, cx + 10, base_y - hA, MUTED, ca, 2)
    T(base, "CARRYING COST", cx + 24, base_y - hA - ch / 2 - 44, "semibold", 20, MUTED, ca, "l", 3)
    T(base, "storage · interest · insurance", cx + 24, base_y - hA - ch / 2 - 12, "regular", 20, MUTED, ca)
    T(base, "Spread > carrying cost  →  “riskless” profit?", gx, 800, "regular", 30, WHITE,
      a * appear(lt, 4.5))
    if stamp:
        rect(base, (0, 200, W, 880), (8, 8, 9), a * 0.6 * appear(lt, 0.2, 0.4))
        sp = appear(lt, 0.3, 0.5)
        sc = 1.25 - 0.25 * sp
        im = R.text_img("NOT DELIVERABLE", "display_semibold", int(96 * sc), RISK, 6)
        im = im.rotate(-8, expand=True, resample=Image.BICUBIC)
        R.blit(base, im, W / 2 - im.width / 2 + 80, 380 - im.height / 2, a * sp)
        T(base, "August bellies could not be delivered against the February contract", W / 2 + 80, 470,
          "regular", 26, WHITE, a * appear(lt, 1.0), "m")


def s_lesson_tally(base, t, lt, dur, a):
    k = K("Marcus fired his adviser") - (t - lt)
    la = a * (1 - ease_io(prog(lt, k - 0.4, k + 0.2)))
    lesson(base, la * appear(lt, 0.2), ["There is no such thing", "as a guaranteed profit."], y=340,
           sub="When a trade looks riskless, the risk is in the part you don't understand.", eyebrow="LESSON")
    ta = a * appear(lt, k + 0.2)
    if ta > 0:
        T(base, "HIS FIRST EIGHT TRADES", W / 2, 300, "medium", 22, GOLD, ta, "m", 8)
        names = ["SOY MEAL", "CORN", "WHEAT", "CORN", "BELLIES", "SILVER", "SILVER", "SILVER"]
        k8 = K("Eight trades") - (t - lt)
        for i, nm in enumerate(names):
            x = W / 2 - 4 * 190 + i * 190 + 15
            ia = ta * appear(lt, k + 0.6 + i * 0.35)
            frame_box(base, x, 380, x + 160, 540, ia)
            T(base, nm, x + 80, 400, "medium", 18, MUTED, ia, "m", 3)
            xa = ia * appear(lt, k + 0.9 + i * 0.35)
            aa_lines(base, [([(x + 50, 445), (x + 110, 505)], RISK, 5), ([(x + 110, 445), (x + 50, 505)], RISK, 5)], xa)
        T(base, "8 trades  ·  8 losses", W / 2, 620, "display_light", 64, WHITE, ta * appear(lt, k8), "m")


def s_keltner(base, t, lt, dur, a):
    s_ledger(base, t, lt, dur, a, "A second stake, a first lesson", "1970",
             [("STAKE", "$3,000 life insurance"), ("STUDY", "Chester Keltner's books & market letter"),
              ("FIRST WIN", "Wheat  +4¢ / bushel  ≈ $200", GOLD)],
             keys=[None, "He studied the books", "The first recommendation"])


def s_blight(base, t, lt, dur, a):
    t0 = t - lt
    # dot field: corn plants turning red
    rng = np.random.default_rng(4)
    pts = [(1060 + (i % 22) * 32, 250 + (i // 22) * 32) for i in range(22 * 15)]
    order = rng.permutation(len(pts))
    spread = ease_io(prog(lt, 1.0, 9.0)) * 0.15
    fa = a * appear(lt, 0.2)
    red = set(order[: int(len(pts) * spread)].tolist())
    for i, (x, y) in enumerate(pts):
        dot(base, x, y, 6, RISK if i in red else (70, 96, 60), fa * (0.95 if i in red else 0.7))
    T(base, "Each dot = a share of the US corn crop  ·  illustrative", 1060, 750, "regular", 20, FAINT, fa)
    T(base, "SOUTHERN CORN LEAF BLIGHT  ·  1970", 150, 250, "medium", 22, GOLD, a * appear(lt, 0.3), "l", 5)
    T(base, "≈15%", 150, 300, "display_light", 180, WHITE, a * appear(lt, 0.6))
    T(base, "of the US corn crop destroyed", 150, 520, "regular", 34, MUTED, a * appear(lt, 1.0))
    source(base, a * appear(lt, 1.2), "USDA / NASA Corn Blight Watch reports", y=580)
    k = K("Corn prices surged") - t0
    ca = a * appear(lt, k)
    v = 3000 + (30000 - 3000) * ease_io(prog(lt, k, k + 6))
    T(base, "HIS ACCOUNT  ·  SUMMER 1970", 150, 660, "medium", 20, GOLD, ca, "l", 4)
    T(base, counter(v), 150, 694, "mono_medium", 64, WHITE, ca)


def s_skill_luck(base, t, lt, dur, a):
    rect(base, (W / 2 - 1, 200, W / 2 + 1, 780), BORDER, a)
    T(base, "SKILL", W / 4, 240, "display_light", 90, WHITE, a * appear(lt, 0.2), "m", 10)
    T(base, "LUCK", 3 * W / 4, 240, "display_light", 90, GOLD, a * appear(lt, 0.5), "m", 10)
    # coin flip
    ph = lt * 5.0
    sx = abs(math.cos(ph))
    r = 90
    cx, cy = W / 2, 560
    w = max(4, int(2 * r * sx))
    coin = Image.new("RGBA", (2 * r + 4, 2 * r + 4), (0, 0, 0, 0))
    ImageDraw.Draw(coin).ellipse((2, 2, 2 * r + 2, 2 * r + 2), fill=GOLD + (255,) if math.cos(ph) > 0 else (150, 120, 60, 255))
    coin = coin.resize((w, 2 * r + 4), Image.LANCZOS)
    R.blit(base, coin, cx - w / 2, cy - r, a * appear(lt, 0.8))
    T(base, "Which part of the win was which?", W / 2, 720, "regular", 32, MUTED, a * appear(lt, 1.5), "m")


def s_headline(base, t, lt, dur, a):
    t0 = t - lt
    x0, y0, x1, y1 = 360, 190, 1560, 560
    ha = a * appear(lt, 0.2)
    rect(base, (x0, y0, x1, y1), (232, 226, 210), ha * 0.92)
    T(base, "THE GRAIN TRADE GAZETTE  ·  SPRING 1971", (x0 + x1) / 2, y0 + 30, "semibold", 20, (60, 55, 45), ha, "m", 5)
    R.hline(base, x0 + 40, x1 - 40, y0 + 70, (60, 55, 45), ha, 2)
    T(base, "Will the Blight Return?", (x0 + x1) / 2, y0 + 110, "display_semibold", 92, (25, 22, 18), ha, "m")
    T(base, "Traders bet the fungus survived the winter", (x0 + x1) / 2, y0 + 240, "italic", 32, (70, 64, 52), ha, "m")
    T(base, "Stylised headline — not a reproduction", x1, y1 + 12, "italic", 18, FAINT, ha, "r")
    k = K("He borrowed twenty thousand dollars") - t0
    ba = a * appear(lt, k)
    T(base, "CAPITAL COMMITTED TO ONE IDEA", 360, 640, "medium", 20, GOLD, ba, "l", 5)
    p = ease_io(prog(lt, k, k + 2.0))
    rect(base, (360, 680, 360 + 1200 * p, 730), RISK, ba)
    rect(base, (360 + 1200 * 0.6, 680, 360 + 1200 * 0.6 + 2, 730), (20, 20, 20), ba * (p > 0.6))
    T(base, "$30,000 his own", 370, 740, "regular", 24, WHITE, ba * (p > 0.3))
    T(base, "$20,000 borrowed", 360 + 1200 * 0.6 + 10, 740, "regular", 24, WHITE, ba * (p > 0.8))
    T(base, "100%", 1580, 688, "mono_medium", 34, RISK, ba * (p > 0.95))


def s_limit(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "Locked limit-down")
    x0, x1, y0, y1 = 150, 1100, 260, 760
    lim_y = 640
    ca = a * appear(lt, 0.3)
    R.hline(base, x0, x1, lim_y, RISK, ca, 2, dash=(16, 10))
    T(base, "DAILY LIMIT", x0, lim_y + 10, "semibold", 18, RISK, ca, "l", 4)
    T(base, "Where buyers & sellers would really meet", x0, 728, "italic", 20, FAINT, ca)
    R.hline(base, x0, x1, 724, FAINT, ca * 0.6, 1, dash=(6, 8))
    n = 60
    path = series(9, n, 330, 640, 7)
    path = np.minimum(path, lim_y)
    p = ease_io(prog(lt, 0.5, 6.0))
    m = max(2, int(n * p))
    pts = [(x0 + i / (n - 1) * (x1 - x0), path[i]) for i in range(m)]
    if p > 0.95:
        pts.append((x1, lim_y))
    aa_lines(base, [(pts, WHITE, 3)], ca)
    # order book
    bx = 1260
    T(base, "SELL ORDERS", bx, 260, "semibold", 20, RISK, ca, "l", 4)
    T(base, "BUY ORDERS", bx + 300, 260, "semibold", 20, GOLD, ca, "l", 4)
    nsell = int(14 * ease_io(prog(lt, 3.0, 12.0)))
    for i in range(nsell):
        rect(base, (bx, 720 - i * 30, bx + 220, 720 - i * 30 + 24), RISK, ca * 0.85)
    for i in range(max(0, 3 - int(lt / 3))):
        rect(base, (bx + 300, 720 - i * 30, bx + 520, 720 - i * 30 + 24), GOLD, ca * 0.8)
    T(base, "no buyers at the limit", bx + 300, 760, "italic", 20, MUTED, ca * appear(lt, 9))
    k = K("The next morning") - t0
    la = a * appear(lt, k)
    frame_box(base, 1240, 790, 1770, 860, la, stripe=RISK)
    T(base, "Next morning  ·  −$42,000", 1270, 806, "semibold", 30, WHITE, la)


def s_ruin(base, t, lt, dur, a):
    lesson(base, a * appear(lt, 0.2), ["Risk of ruin"], y=330, eyebrow="LESSON")
    ba = a * appear(lt, 1.2)
    T(base, "ONE POSITION  =  100% OF CAPITAL", W / 2, 520, "medium", 22, RISK, ba, "m", 6)
    rect(base, (360, 570, 1560, 640), RISK, ba)
    T(base, "Lost: $30,000 of his own + $12,000 of his mother's", W / 2, 670, "regular", 30, WHITE, ba, "m")


def s_glass(base, t, lt, dur, a):
    t0 = t - lt
    fa = a * appear(lt, 0.2)
    # left: research desk
    frame_box(base, 150, 220, 880, 760, fa)
    T(base, "RESEARCH REPORT", 190, 250, "medium", 20, GOLD, fa, "l", 5)
    for i in range(9):
        w = 560 - (i * 47) % 200
        rect(base, (190, 310 + i * 44, 190 + w, 322 + i * 44), LOSSBAR, fa)
    T(base, "Reynolds Securities  ·  analysts may not trade", 190, 712, "regular", 22, MUTED, fa)
    # glass
    rect(base, (930, 200, 936, 780), (90, 100, 110), fa * 0.6)
    rect(base, (936, 200, 1000, 780), (120, 130, 140), fa * 0.05)
    # right: blurred board
    tick = int(lt / 0.7)
    for i in range(6):
        y = 250 + i * 86
        v = 1.5 + 0.01 * math.sin(tick * 0.9 + i * 2)
        T(base, ["CORN", "WHEAT", "SOYBEANS", "SILVER", "COCOA", "PLYWOOD"][i], 1060, y, "semibold", 28, MUTED, fa * 0.55)
        T(base, "{:.4f}".format(v * (1 + i * 0.4)), 1460, y, "mono_medium", 30, WHITE, fa * 0.45)
    k = K("He borrowed from his mother, his brother") - t0
    ba = a * appear(lt, k)
    T(base, "Borrowed from: mother · brother · girlfriend", 1060, 770, "regular", 24, GOLD, ba)


def s_code(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "TRADING IN SECRET", "A code with his broker")
    for i, (phrase, meaning) in enumerate([("“The sun is out.”", "= one instruction"),
                                           ("“The weather is cloudy.”", "= another")]):
        ia = a * appear(lt, 0.5 + i * 1.2)
        x = 260 + i * 720
        flip = abs(math.cos(min(1.0, prog(lt, 0.5 + i * 1.2, 1.3 + i * 1.2)) * math.pi / 2 + math.pi / 2))
        frame_box(base, x, 320, x + 640, 620, ia, stripe=GOLD)
        T(base, phrase, x + 320, 410, "display_light", 48, WHITE, ia * flip, "m")
        T(base, meaning, x + 320, 500, "regular", 30, MUTED, ia * flip, "m")
    T(base, "He kept losing.", W / 2, 720, "display_light", 54, RISK,
      a * appear(lt, K("He kept losing", after=t - lt) - (t - lt)), "m")


def s_person(base, t, lt, dur, a, name, line1, line2, src, extra=None):
    ra = a * appear(lt, 0.2)
    ring(base, 430, 470, 170, GOLD, ra, 2)
    initials = "".join(w[0] for w in name.split()[:2])
    T(base, initials, 430, 400, "display_light", 120, WHITE, ra, "m")
    T(base, name, 700, 360, "display_light", 96, WHITE, a * appear(lt, 0.5), "l", 6)
    R.hline(base, 704, 704 + 420 * appear(lt, 0.8), 490, GOLD, a, 2)
    T(base, line1, 704, 520, "medium", 30, GOLD, a * appear(lt, 1.0), "l", 3)
    T(base, line2, 704, 572, "regular", 30, MUTED, a * appear(lt, 1.4))
    if extra:
        T(base, extra, 704, 640, "regular", 28, WHITE, a * appear(lt, 2.2))
    source(base, a * appear(lt, 1.6), src, x=704, y=720)


def s_trend(base, t, lt, dur, a):
    t0 = t - lt
    a_full = a
    k3 = K("Marcus remembered one example") - t0
    a = a * (1 - appear(lt, k3 - 0.2))
    header(base, a * appear(lt, 0.1), "EXPLAINER", "Trend following")
    k2 = K("The idea is simple to state") - t0
    phase2 = appear(lt, k2 + 0.2)
    a1 = a * (1 - phase2 * 0.85)
    x0, x1, y0, y1 = 150, 1300, 240, 780
    n = 120
    shape = np.concatenate([np.linspace(620, 600, 40), np.linspace(600, 330, 60), np.linspace(330, 420, 20)])
    path = series(21, n, 0, 0, 6, shape=shape)
    p = ease_io(prog(lt, 0.4, 8.0))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    pts = [(xs(i), path[i]) for i in range(m)]
    # trailing stop
    stop = []
    lo = 9e9
    for i in range(m):
        lo = min(path[max(0, i - 12):i + 1].max() + 0, 9e9)
        stop.append((xs(i), path[max(0, i - 15):i + 1].max() + 40))
    aa_lines(base, [(pts, WHITE, 3), (stop[40:], GOLD, 2, 0.8)] if m > 41 else [(pts, WHITE, 3)], a1)
    if m > 42:
        dot(base, xs(42), path[42], 9, GOLD, a1)
        T(base, "ENTRY: breakout", xs(42) - 20, path[42] + 24, "semibold", 20, GOLD, a1, "r", 2)
    if m > 112:
        T(base, "EXIT: trend reverses", xs(112), path[112] - 60, "semibold", 20, WHITE, a1, "m", 2)
    T(base, "trailing exit", x1 - 10, (stop[-1][1] if stop else 600) + 12, "italic", 18, GOLD, a1 * (m > 60), "r")
    # phase 2: many small losses, few big wins
    if phase2 > 0:
        pa = a * phase2
        vals = [-1, -1, 4.5, -1, -0.8, -1, -1, 7.0, -1, -0.6, -1, -1, -1, 3.2, -1, -0.9]
        bx0, by = 200, 560
        for i, v in enumerate(vals):
            x = bx0 + i * 64
            ia = pa * appear(lt, k2 + 0.4 + i * 0.12)
            if v > 0:
                rect(base, (x, by - v * 50, x + 44, by), GOLD, ia)
            else:
                rect(base, (x, by, x + 44, by - v * 50), RISK, ia)
        R.hline(base, bx0 - 20, bx0 + len(vals) * 64, by, BORDER, pa)
        cum = np.cumsum(vals)
        cx0 = 1320
        cpts = [(cx0 + i * 30, 560 - c * 22) for i, c in enumerate(cum)]
        aa_lines(base, [(cpts, WHITE, 3)], pa * appear(lt, k2 + 2.4))
        T(base, "CUMULATIVE", cx0, 300, "medium", 18, MUTED, pa * appear(lt, k2 + 2.4), "l", 4)
        T(base, "12 small losses  ·  3 large wins  ·  still profitable", W / 2, 800, "regular", 30, WHITE,
          pa * appear(lt, k2 + 3.0), "m")
        T(base, "Hypothetical", W / 2, 846, "italic", 18, FAINT, pa * appear(lt, k2 + 3.0), "m")
    k4 = K("A second mentor appeared") - t0
    a = a_full
    if lt > k3:
        q = a * appear(lt, k3) * (1 - appear(lt, k4))
        T(base, "“The trend is down — stay short until it changes.”", W / 2, 420, "display_light", 54, WHITE, q, "m")
        T(base, "Ed Seykota, as Marcus recalled him  ·  short silver", W / 2, 510, "regular", 28, MUTED, q, "m")
    if lt > k4:
        q = a * appear(lt, k4)
        T(base, "TWO MENTORS, ONE MESSAGE", W / 2, 300, "medium", 22, GOLD, q, "m", 8)
        T(base, "Ed Seykota  ·  Amos Hostetter", W / 2, 360, "display_light", 60, WHITE, q, "m")
        for i, s in enumerate(["Cut losses", "Ride winners", "Be patient"]):
            T(base, s, W / 2 - 480 + i * 480, 520, "display_light", 56, GOLD, q * appear(lt, k4 + 1 + i * 0.6), "m")


def s_controls(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "HISTORY", "Nixon's price controls")
    items = [("15 AUG 1971", "Wage-price freeze  (Phase I)"), ("NOV 1971 – JAN 1973", "Phase II price controls"),
             ("JAN 1973", "Phase III — controls loosen"), ("JUL 1973", "Phase IV")]
    x0, x1, y = 200, 1720, 380
    p = ease_io(prog(lt, 0.3, 2.5))
    R.hline(base, x0, x0 + (x1 - x0) * p, y, GOLD, a, 2)
    for i, (d, s) in enumerate(items):
        x = x0 + i * (x1 - x0) / 3
        ia = a * appear(lt, 0.6 + i * 0.6)
        dot(base, x, y, 9, GOLD, ia)
        T(base, d, x, y + 30, "mono_medium", 22, WHITE, ia, "m")
        T(base, s, x, y + 66, "regular", 22, MUTED, ia, "m")
    source(base, a * appear(lt, 2.0), "American Presidency Project; Economic Stabilization Act", y=520)
    k = K("Marcus was earning") - t0
    ka = a * appear(lt, k)
    T(base, "JOINT ACCOUNT  ·  JULY 1972", 200, 620, "medium", 20, GOLD, ka, "l", 5)
    T(base, "$700  +  $700", 200, 660, "display_light", 80, WHITE, ka)
    T(base, "his savings  ·  a friend's", 200, 760, "regular", 24, MUTED, ka)


def s_supply(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "What price ceilings do")
    x0, y0, x1, y1 = 260, 240, 1000, 800
    ca = a * appear(lt, 0.3)
    R.vline(base, x0, y0, y1, BORDER, ca, 2)
    R.hline(base, x0, x1, y1, BORDER, ca, 2)
    T(base, "PRICE", x0 - 20, y0, "medium", 18, MUTED, ca, "r", 3)
    T(base, "QUANTITY", x1, y1 + 14, "medium", 18, MUTED, ca, "r", 3)
    pd = ease_io(prog(lt, 0.6, 2.0))
    aa_lines(base, [([(x0 + 40, y0 + 40), (x0 + 40 + (x1 - x0 - 80) * pd, y0 + 40 + (y1 - y0 - 80) * pd)], WHITE, 3),
                    ([(x0 + 40, y1 - 40), (x0 + 40 + (x1 - x0 - 80) * pd, y1 - 40 - (y1 - y0 - 80) * pd)], GOLD, 3)], ca)
    T(base, "DEMAND", x1 - 10, y1 - 70, "semibold", 18, WHITE, ca * (pd > 0.9), "r", 3)
    T(base, "SUPPLY", x1 - 10, y0 + 20, "semibold", 18, GOLD, ca * (pd > 0.9), "r", 3)
    eq_y = (y0 + y1) / 2
    cy = eq_y + 130
    k = K("Economics offers a clear prediction") - t0
    ka = a * appear(lt, k)
    R.hline(base, x0, x1, cy, RISK, ka, 3)
    T(base, "CEILING  $110", x0 + 10, cy + 10, "semibold", 20, RISK, ka, "l", 3)
    # shortage gap
    dx = (cy - (y0 + 40)) / (y1 - y0 - 80) * (x1 - x0 - 80)
    xs_s = x0 + 40 + (y1 - 40 - cy) / (y1 - y0 - 80) * (x1 - x0 - 80)
    xd = x0 + 40 + dx
    sa = a * appear(lt, k + 1.0)
    rect(base, (xs_s, cy - 18, xd, cy - 2), RISK, sa * 0.5)
    T(base, "SHORTAGE", (xs_s + xd) / 2, cy - 54, "semibold", 22, RISK, sa, "m", 4)
    T(base, "EQUILIBRIUM", x0 + (x1 - x0) / 2 + 20, eq_y - 40, "medium", 16, MUTED, ca * (pd > 0.9), "l", 3)
    k2 = K("Then Marcus watched the futures price") - t0
    fa = a * appear(lt, k2)
    T(base, "FUTURES PRICE", 1160, 300, "medium", 20, GOLD, fa, "l", 5)
    tick = max(0, int((lt - k2) / 1.2))
    vals = [110.00, 110.10, 110.20, 110.20, 110.80]
    v = vals[min(tick, len(vals) - 1)]
    T(base, "${:.2f}".format(v), 1160, 340, "mono_medium", 96, WHITE if v <= 110 else GOLD, fa)
    T(base, "above the ceiling?", 1160, 470, "italic", 28, MUTED, fa * (v > 110))
    k3 = K("He bought one contract") - t0
    T(base, "BUY 1 CONTRACT", 1160, 560, "semibold", 40, GOLD, a * appear(lt, k3), "l", 4)


def s_plywood(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "PLYWOOD FUTURES  ·  1972", "Through the ceiling — and pyramiding")
    x0, x1, y0, y1 = 150, 1120, 260, 780
    vmin, vmax = 100, 210
    ca = a * appear(lt, 0.3)
    chart_axes(base, ca, x0, y0, x1, y1, vmin, vmax, [110, 140, 170, 200], lambda v: "$%d" % v)
    yv = lambda v: y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)
    R.hline(base, x0, x1, yv(110), RISK, ca, 2, dash=(14, 8))
    T(base, "CONTROL PRICE $110 (his recollection)", x1 - 6, yv(110) + 10, "semibold", 18, RISK, ca, "r", 2)
    n = 90
    shape = np.concatenate([np.linspace(104, 110.8, 15), np.linspace(110.8, 200, 75)])
    path = series(31, n, 0, 0, 1.5, shape=shape)
    p = ease_io(prog(lt, 0.8, 14.0))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    pts = [(xs(i), yv(path[i])) for i in range(m)]
    aa_lines(base, [(pts, GOLD, 3)], ca)
    # pyramid blocks
    adds = [15, 35, 55, 72]
    sizes = [4, 3, 2, 1]
    for j, (i, sz) in enumerate(zip(adds, sizes)):
        if m > i:
            ba = ca * appear(lt, 0.8 + i / n * 13.2)
            dot(base, xs(i), yv(path[i]), 8, WHITE, ba)
            bx = 1300
            bw = 80 * sz
            yy = 720 - j * 74
            rect(base, (bx + (320 - bw) / 2, yy, bx + (320 - bw) / 2 + bw, yy + 60), GOLD, ba * (0.9 - j * 0.12))
    T(base, "POSITION ADDS", 1300 + 160, 300, "medium", 18, MUTED, ca, "m", 4)
    T(base, "smaller each time", 1300 + 160, 330, "italic", 20, FAINT, ca, "m")
    k = K("In a few months") - t0
    ka = a * appear(lt, k)
    v = 700 + (12000 - 700) * ease_io(prog(lt, k, k + 3.0))
    T(base, counter(v), 1460, 400, "mono_medium", 60, WHITE, ka, "m")
    T(base, "his account (his account of it)", 1460, 476, "regular", 20, MUTED, ka, "m")


def s_two_tier(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "INTERPRETATION", "A two-tier market")
    for i, (title, lines, col) in enumerate([
            ("REGULATED CASH MARKET", ["Price capped", "Shortages", "Long-standing customers first"], MUTED),
            ("FUTURES MARKET", ["Price free to rise", "Supplier of last resort", "Buyers pay more — but can buy"], GOLD)]):
        x = 200 + i * 800
        ia = a * appear(lt, 0.4 + i * 0.8)
        frame_box(base, x, 280, x + 700, 700, ia, stripe=col)
        T(base, title, x + 40, 310, "semibold", 24, col, ia, "l", 4)
        for j, ln in enumerate(lines):
            T(base, ln, x + 40, 400 + j * 80, "display_light", 44, WHITE, ia * appear(lt, 0.8 + i * 0.8 + j * 0.4))
    T(base, "→", W / 2, 440, "display_light", 90, GOLD, a * appear(lt, 2.0), "m")


def s_lumber_intro(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "THE SAME LOGIC", "Plywood worked. Why not lumber?")
    for i, (nm, res, col) in enumerate([("PLYWOOD", "through the ceiling  ✓", GOLD), ("LUMBER", "everything on it  ?", RISK)]):
        ia = a * appear(lt, 0.5 + i * 1.0)
        x = 260 + i * 720
        frame_box(base, x, 330, x + 640, 620, ia, stripe=col)
        T(base, nm, x + 320, 380, "display_light", 80, WHITE, ia, "m", 8)
        T(base, res, x + 320, 520, "regular", 34, col, ia, "m")


def s_leverage(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "Why a small move can destroy a big position")
    cols = [("PLYWOOD", "+82% price move", "small position", GOLD, 0.82, None),
            ("LUMBER", "−10% price move", "account: $12,000 → under $4,000", RISK, -0.10, -0.67)]
    for i, (nm, mv, note, col, pm, am) in enumerate(cols):
        x = 220 + i * 800
        ia = a * appear(lt, 0.4 + i * 0.8)
        T(base, nm, x, 260, "semibold", 30, WHITE, ia, "l", 6)
        T(base, mv, x, 310, "mono_medium", 40, col, ia)
        T(base, "PRICE", x, 400, "medium", 18, MUTED, ia, "l", 4)
        rect(base, (x, 430, x + 600, 470), LOSSBAR, ia)
        pw = 600 * min(1, abs(pm)) * ease_io(prog(lt, 1.0 + i, 2.0 + i))
        rect(base, (x, 430, x + pw, 470), col if pm > 0 else MUTED, ia)
        T(base, note, x, 500, "regular", 26, MUTED, ia)
        if am:
            k = K("Do the arithmetic") - t0
            ka = a * appear(lt, k)
            T(base, "ACCOUNT", x, 580, "medium", 18, MUTED, ka, "l", 4)
            rect(base, (x, 610, x + 600, 650), LOSSBAR, ka)
            aw = 600 * ease_io(prog(lt, k + 0.3, k + 1.8)) * 0.67
            rect(base, (x + 600 - aw, 610, x + 600, 650), RISK, ka)
            T(base, "−67%", x + 600, 660, "mono_medium", 40, RISK, ka, "r")
    k = K("That implies his market exposure") - t0
    ea = a * appear(lt, k)
    frame_box(base, 220, 740, 1700, 820, ea, stripe=GOLD)
    T(base, "−10% price  →  −67% equity  ⇒  exposure ≈ 6–7× capital   (our calculation)", 260, 762, "semibold", 28, WHITE, ea)


def s_survive(base, t, lt, dur, a):
    lesson(base, a * appear(lt, 0.2), ["Survive first.", "Profit second."], y=300,
           sub="After lumber, he never again bet everything on one trade.", eyebrow="LESSON")
    T(base, "Year-end 1972:  ≈ $24,000", W / 2, 720, "mono_medium", 40, GOLD, a * appear(lt, 1.5), "m")


def s_inflation(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "1973", "Controls loosen — prices explode")
    names = ["CORN", "WHEAT", "SOYBEANS", "SUGAR", "COTTON"]
    cols = [WHITE, MUTED, GOLD, (180, 170, 150), (150, 160, 170)]
    x0, x1, y0, y1 = 150, 1300, 260, 780
    n = 80
    p = ease_io(prog(lt, 0.4, 9.0))
    m = max(2, int(n * p))
    lines = []
    for i, nm in enumerate(names):
        g = 1.8 + i * 0.35
        path = series(40 + i, n, 0, 0, 0.03, shape=np.linspace(1, g, n) ** 1.6)
        top = 3.2 ** 1.6
        ys = [y1 - (path[j] - 0.8) / (top + 0.2 - 0.8) * (y1 - y0) for j in range(n)]
        pts = [(x0 + j / (n - 1) * (x1 - x0), ys[j]) for j in range(m)]
        lines.append((pts, cols[i], 2.5))
        if m > 5:
            T(base, nm, pts[-1][0] + 12, pts[-1][1] - 12, "semibold", 18, cols[i], a, "l", 3)
    aa_lines(base, lines, a * appear(lt, 0.3))
    T(base, "Illustrative — indexed price paths", x0, y1 + 14, "italic", 18, FAINT, a)
    k = K("In 1973, his account grew") - t0
    ka = a * appear(lt, k)
    v = 24000 + 40000 * ease_io(prog(lt, k, k + 3))
    T(base, counter(v), 1500, 400, "mono_medium", 64, WHITE, ka)
    T(base, "his account, 1973 (his figures)", 1500, 480, "regular", 22, MUTED, ka)
    k2 = K("He described himself at the time") - t0
    T(base, "“inflation alarmist”", 1500, 600, "display_light", 44, GOLD, a * appear(lt, k2))


def s_soy(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "SOYBEANS  ·  1972–1973", "The win he let go")
    x0, x1, y0, y1 = 150, 1260, 260, 780
    vmin, vmax = 2.5, 13.5
    ca = a * appear(lt, 0.3)
    chart_axes(base, ca, x0, y0, x1, y1, vmin, vmax, [3, 6, 9, 12], lambda v: "$%d" % v)
    yv = lambda v: y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)
    n = 100
    shape = np.concatenate([np.linspace(3.25, 5.0, 45), np.linspace(5.0, 12.9, 45) ** 1.0, np.linspace(12.9, 8.5, 10)])
    path = series(55, n, 0, 0, 0.12, shape=shape)
    path[89] = 12.9
    p = ease_io(prog(lt, 0.6, 12.0))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    aa_lines(base, [([(xs(i), yv(path[i])) for i in range(m)], WHITE, 3)], ca)
    if m > 50:
        ea = ca * appear(lt, 0.6 + 50 / n * 11.4)
        dot(base, xs(50), yv(path[50]), 9, GOLD, ea)
        T(base, "MARCUS EXITS", xs(50) + 16, yv(path[50]) + 28, "semibold", 20, GOLD, ea, "l", 3)
    if m > 89:
        pa = ca * appear(lt, 0.6 + 89 / n * 11.4)
        dot(base, xs(89), yv(12.9), 8, WHITE, pa)
        T(base, "≈ $12.90 record  ·  June 1973", xs(89) - 20, yv(12.9) - 8, "semibold", 20, WHITE, pa, "r")
    source(base, ca, "University of Illinois farmdoc; price path illustrative")
    k = K("Marcus watched soybeans go limit-up") - t0
    ka = a * appear(lt, k)
    T(base, "LIMIT-UP DAYS (his recollection)", 1380, 300, "medium", 18, GOLD, ka, "l", 4)
    nd = int(12 * ease_io(prog(lt, k, k + 4)))
    for i in range(nd):
        x = 1380 + (i % 4) * 100
        y = 350 + (i // 4) * 100
        rect(base, (x, y, x + 80, y + 80), GOLD, ka * 0.85)
        T(base, str(i + 1), x + 40, y + 18, "mono_medium", 30, (20, 18, 12), ka, "m")


def s_winners(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "Why big winners matter")
    vals = [-1, -1, 0.6, -1, -0.8, 6.0, -1, -1, 0.5, -1, -0.7, -1, 0.8, -1, -1, 5.0, -1, -0.9, 0.4, -1]
    big = {5, 15}
    by = 560
    k = K("Shortly afterwards") - t0
    rem = appear(lt, 6.0, 1.0)                    # remove the two big winners
    for i, v in enumerate(vals):
        x = 220 + i * 66
        ia = a * appear(lt, 0.4 + i * 0.08)
        if i in big:
            ia *= (1 - 0.85 * rem)
        if v > 0:
            rect(base, (x, by - v * 40, x + 46, by), GOLD, ia)
        else:
            rect(base, (x, by, x + 46, by - v * 40), RISK, ia)
    R.hline(base, 200, 220 + 20 * 66, by, BORDER, a)
    tot_all = sum(vals)
    tot_wo = sum(v for i, v in enumerate(vals) if i not in big)
    T(base, "TOTAL WITH THE 2 BIG WINNERS", 1620, 300, "medium", 18, MUTED, a * appear(lt, 2), "l", 3)
    T(base, "%+.1f" % tot_all, 1620, 330, "mono_medium", 54, GOLD, a * appear(lt, 2))
    T(base, "WITHOUT THEM", 1620, 460, "medium", 18, MUTED, a * appear(lt, 6.5), "l", 3)
    T(base, "%+.1f" % tot_wo, 1620, 490, "mono_medium", 54, RISK, a * appear(lt, 6.5))
    T(base, "20 hypothetical trades, in units of risk", W / 2, 760, "italic", 20, FAINT, a, "m")
    ca = a * appear(lt, k)
    if ca > 0:
        rect(base, (0, 0, W, H), (10, 10, 12), ca * 0.97)
        T(base, "COFFEE — THE REVERSE", W / 2, 300, "medium", 22, GOLD, ca, "m", 8)
        for i, (who, what, col) in enumerate([("MARCUS", "close stop  →  small loss", MUTED),
                                              ("SEYKOTA", "no stop  →  locked limit-down for days", RISK)]):
            x = 260 + i * 720
            frame_box(base, x, 380, x + 640, 620, ca * appear(lt, k + 0.4 + i * 0.6), stripe=col)
            T(base, who, x + 320, 420, "display_light", 64, WHITE, ca * appear(lt, k + 0.4 + i * 0.6), "m", 8)
            T(base, what, x + 320, 530, "regular", 28, col, ca * appear(lt, k + 0.4 + i * 0.6), "m")
        k2 = K("He decided the competitiveness") - t0
        T(base, "Next: the trading floor", W / 2, 700, "regular", 30, MUTED, ca * appear(lt, k2), "m")


def s_ring(base, t, lt, dur, a):
    t0 = t - lt
    cx, cy = 680, 520
    ra = a * appear(lt, 0.2)
    for i, r in enumerate([110, 170, 230, 290]):
        ring(base, cx, cy, r, BORDER if i else GOLD, ra, 2)
    rng = np.random.default_rng(8)
    for i in range(60):
        ang = rng.uniform(0, 2 * math.pi)
        rr = rng.choice([140, 200, 260])
        pulse = 0.5 + 0.5 * math.sin(lt * 3 + i)
        dot(base, cx + rr * math.cos(ang), cy + rr * math.sin(ang), 5, WHITE, ra * (0.35 + 0.5 * pulse))
    T(base, "THE RING", cx, cy - 18, "medium", 22, GOLD, ra, "m", 6)
    T(base, "NEW YORK COTTON EXCHANGE", 1120, 330, "medium", 22, GOLD, a * appear(lt, 0.6), "l", 5)
    T(base, "$100,000", 1120, 380, "display_light", 96, WHITE, a * appear(lt, 0.8))
    T(base, "net worth required to join", 1120, 500, "regular", 30, MUTED, a * appear(lt, 1.0))
    k = K("Too shy to make himself heard") - t0
    T(base, "Too shy to shout.", 1120, 600, "display_light", 52, RISK, a * appear(lt, k))


def s_sound(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "Reading the room")
    x0, x1 = 150, 1700
    n = 200
    xs = [x0 + i / (n - 1) * (x1 - x0) for i in range(n)]
    env = np.concatenate([np.linspace(0.8, 1.0, 70), np.linspace(1.0, 0.15, 30), np.linspace(0.15, 0.5, 40),
                          np.linspace(0.5, 1.0, 20), np.full(40, 1.0)])
    p = ease_io(prog(lt, 0.4, 8.0))
    m = max(2, int(n * p))
    for i in range(0, m, 2):
        h = env[i] * (40 + 30 * math.sin(i * 1.7) ** 2)
        rect(base, (xs[i], 700 - h, xs[i] + 4, 700 + h), MUTED, a * 0.7)
    price = np.concatenate([np.linspace(560, 330, 70), np.linspace(330, 320, 30), np.linspace(320, 380, 40),
                            np.linspace(380, 300, 20), np.linspace(300, 360, 40)])
    aa_lines(base, [([(xs[i], price[i]) for i in range(m)], WHITE, 3)], a)
    T(base, "PRICE", x0, 250, "medium", 18, WHITE, a, "l", 4)
    T(base, "NOISE IN THE RING", x0, 610, "medium", 18, MUTED, a, "l", 4)
    if m > 100:
        T(base, "loud → quiet: the move is exhausting", xs[85], 250, "semibold", 22, GOLD, a * appear(lt, 4.5), "m")
    if m > 160:
        T(base, "suddenly very loud: hitting opposing orders", xs[160], 220, "semibold", 22, RISK, a * appear(lt, 6.8), "m")


def s_surf(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "The surfing technique")
    x0, x1, y0, y1 = 150, 1150, 260, 780
    ca = a * appear(lt, 0.3)
    n = 120
    shape = np.concatenate([np.linspace(620, 470, 40), np.linspace(470, 560, 25), np.linspace(560, 472, 20),
                            np.linspace(472, 290, 35)])
    path = series(77, n, 0, 0, 4, shape=shape)
    p = ease_io(prog(lt, 0.4, 9.0))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    prior = min(path[:45])
    R.hline(base, x0, x1, prior, GOLD, ca, 2, dash=(12, 8))
    T(base, "EARLIER HIGH OF THE DAY", x0, prior - 34, "semibold", 18, GOLD, ca, "l", 3)
    aa_lines(base, [([(xs(i), path[i]) for i in range(m)], WHITE, 3)], ca)
    if m > 86:
        ea = ca * appear(lt, 0.4 + 86 / n * 8.6)
        dot(base, xs(86), prior, 9, GOLD, ea)
        R.hline(base, xs(86) - 60, xs(86) + 120, prior + 22, RISK, ea, 2)
        T(base, "stop · 10 pts", xs(86) + 130, prior + 10, "semibold", 18, RISK, ea)
        T(base, "20 contracts (vs 3–5)", xs(86) - 20, prior + 44, "semibold", 18, WHITE, ea, "r")
    k = K("Look at the mathematics") - t0
    ka = a * appear(lt, k)
    bx = 1300
    T(base, "RISK : REWARD", bx, 280, "medium", 20, GOLD, ka, "l", 5)
    rect(base, (bx, 330, bx + 14, 360), RISK, ka)
    T(base, "1R risked", bx + 30, 330, "regular", 24, WHITE, ka)
    rect(base, (bx, 380, bx + 420 * ease_io(prog(lt, k, k + 1.5)), 410), GOLD, ka)
    T(base, "30R target", bx, 420, "regular", 24, WHITE, ka)
    rows = [("1 win × 30R", "+30R", GOLD), ("9 losses × 1R", "−9R", RISK), ("NET", "+21R", WHITE)]
    for i, (l, v, c) in enumerate(rows):
        ra = a * appear(lt, k + 1.5 + i * 0.6)
        T(base, l, bx, 520 + i * 64, "regular", 28, MUTED, ra)
        T(base, v, bx + 420, 520 + i * 64, "mono_medium", 30, c, ra, "r")
    T(base, "Hypothetical", bx, 720, "italic", 20, FAINT, ka)
    k2 = K("But Marcus added a warning") - t0
    wa = a * appear(lt, k2)
    frame_box(base, 150, 800, 1150, 860, wa, stripe=RISK)
    T(base, "By 1988: breakouts more likely to snap back", 180, 812, "semibold", 26, WHITE, wa)


def s_cc(base, t, lt, dur, a):
    t0 = t - lt
    T(base, "COMMODITIES CORPORATION", 150, 220, "medium", 24, GOLD, a * appear(lt, 0.2), "l", 6)
    T(base, "Princeton, New Jersey", 150, 260, "display_light", 72, WHITE, a * appear(lt, 0.4))
    facts = [("FOUNDED", "1969  ·  Helmut Weymar"), ("BACKERS INCLUDED", "Paul Samuelson  ·  Amos Hostetter"),
             ("LATER", "Acquired by Goldman Sachs, 1997")]
    for i, (k_, v) in enumerate(facts):
        fa = a * appear(lt, 1.0 + i * 0.7)
        T(base, k_, 150, 400 + i * 100, "medium", 18, MUTED, fa, "l", 4)
        T(base, v, 150, 428 + i * 100, "regular", 36, WHITE, fa)
    source(base, a * appear(lt, 2), "Goldman Sachs corporate history", y=720)
    k = K("The punchline") - t0
    qa = a * appear(lt, k)
    frame_box(base, 1100, 380, 1760, 600, qa, stripe=GOLD)
    T(base, "“He just trades.”", 1430, 440, "display_light", 72, WHITE, qa, "m")
    T(base, "the board's punchline, as Marcus remembered it", 1430, 540, "regular", 22, MUTED, qa, "m")


def s_compound(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "EXPLAINER", "The power of compounding")
    x0, x1, y0, y1 = 150, 1150, 260, 780
    ca = a * appear(lt, 0.3)
    lo, hi = math.log10(10_000), math.log10(200_000_000)
    yv = lambda v: y1 - (math.log10(v) - lo) / (hi - lo) * (y1 - y0)
    for v, lab in [(30_000, "$30K"), (1_000_000, "$1M"), (10_000_000, "$10M"), (80_000_000, "$80M")]:
        R.hline(base, x0, x1, yv(v), GRID, ca)
        T(base, lab, x1 + 14, yv(v) - 12, "mono", 18, FAINT, ca)
    n = 121
    growth = (80e6 / 30e3) ** (1 / 120)
    vals = [30e3 * growth ** i * (1 + 0.15 * math.sin(i / 7)) for i in range(n)]
    vals[0], vals[-1] = 30e3, 80e6
    p = ease_io(prog(lt, 0.6, 10.0))
    m = max(2, int(n * p))
    aa_lines(base, [([(x0 + i / (n - 1) * (x1 - x0), yv(vals[i])) for i in range(m)], GOLD, 3)], ca)
    T(base, "AUG 1974", x0, y1 + 14, "mono", 18, FAINT, ca)
    T(base, "~1984", x1, y1 + 14, "mono", 18, FAINT, ca, "r")
    T(base, "log scale  ·  path illustrative", x0, y1 + 44, "italic", 18, FAINT, ca)
    k = K("Schwager describes it") - t0
    ka = a * appear(lt, k)
    T(base, "≈ 2,500×", 1300, 300, "display_light", 110, GOLD, ka)
    T(base, "in ten years (Schwager)", 1300, 430, "regular", 26, MUTED, ka)
    k2 = K("To put that in perspective") - t0
    k2a = a * appear(lt, k2)
    T(base, "≈ 119%", 1300, 520, "display_light", 110, WHITE, k2a)
    T(base, "per year, compounded (our calculation)", 1300, 650, "regular", 26, MUTED, k2a)
    T(base, "while the firm took ~30% a year", 1300, 700, "italic", 22, FAINT, a * appear(lt, 2))


def s_disclosure(base, t, lt, dur, a):
    t0 = t - lt
    k = K("For almost two years") - t0
    da = a * (1 - appear(lt, k - 0.3))
    frame_box(base, 360, 330, 1560, 640, da * appear(lt, 0.2), stripe=AMBER)
    T(base, "DISCLOSURE", 410, 370, "semibold", 24, AMBER, da, "l", 6)
    T(base, "Performance figures as reported by Marcus and Schwager.", 410, 430, "regular", 36, WHITE, da)
    T(base, "No independent audited record is publicly available.", 410, 490, "regular", 36, WHITE, da)
    T(base, "Commodities Corporation was later acquired by Goldman Sachs (1997).", 410, 570, "regular", 26, MUTED, da)
    ca = a * appear(lt, k)
    if ca > 0:
        T(base, "COCOA", W / 2, 300, "display_light", 160, (150, 110, 80), ca, "m", 30)
        T(base, "~2 years trading almost nothing else", W / 2, 520, "regular", 34, WHITE, ca, "m")
        T(base, "on Helmut Weymar's information and network", W / 2, 580, "regular", 30, MUTED, ca, "m")


def s_world(base, t, lt, dur, a):
    cities = [("SYDNEY", 0), ("HONG KONG", 1), ("ZURICH", 2), ("LONDON", 3), ("NEW YORK", 4)]
    T(base, "A MARKET THAT NEVER CLOSES", W / 2, 260, "medium", 24, GOLD, a * appear(lt, 0.2), "m", 8)
    for name, i in cities:
        x = 260 + i * 350
        on = appear(lt, 0.8 + i * 0.9)
        ring(base, x, 520, 90, GOLD if on > 0.5 else BORDER, a, 2)
        ang = lt * 0.6 + i
        aa_lines(base, [([(x, 520), (x + 60 * math.cos(ang), 520 + 60 * math.sin(ang))], WHITE, 2)], a * 0.8)
        dot(base, x, 520, 6, GOLD, a * on)
        T(base, name, x, 640, "semibold", 24, WHITE if on > 0.5 else MUTED, a, "m", 4)
    T(base, "From California, Marcus could trade Hong Kong while New York slept.", W / 2, 760, "regular", 30, MUTED,
      a * appear(lt, 5), "m")


def s_dollar(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "LATE 1978", "The dollar tips its hand")
    events = [("Dollar falling to new lows", MUTED), ("A sudden, unexplained rally", GOLD),
              ("Marcus & Kovner sell their long currencies", WHITE), ("Carter dollar-rescue program · 1 Nov 1978", RISK),
              ("Currency futures lock limit-down for days", RISK)]
    for i, (s, c) in enumerate(events):
        ia = a * appear(lt, 0.6 + i * 2.2)
        y = 270 + i * 110
        dot(base, 220, y + 20, 10, c, ia)
        if i:
            R.vline(base, 219, y - 80, y + 10, BORDER, ia, 2)
        T(base, s, 270, y, "display_light", 46, WHITE if i != 2 else GOLD, ia)
    source(base, a * appear(lt, 9), "American Presidency Project (1 Nov 1978)")


def s_factcheck(base, t, lt, dur, a):
    t0 = t - lt
    k = K("That principle") - t0
    fa = a * (1 - appear(lt, k - 0.2))
    T(base, "FACT CHECK", W / 2, 260, "semibold", 24, AMBER, fa, "m", 10)
    for i, (lab, val, col) in enumerate([("MARCUS RECALLED", "“that weekend”", MUTED),
                                         ("THE RECORD", "Wednesday, 1 November 1978", WHITE)]):
        x = 260 + i * 720
        ia = fa * appear(lt, 0.4 + i * 0.8)
        frame_box(base, x, 340, x + 640, 580, ia, stripe=AMBER if i else BORDER)
        T(base, lab, x + 40, 380, "medium", 20, MUTED, ia, "l", 5)
        T(base, val, x + 40, 440, "display_light", 44, col, ia)
    source(base, fa, "American Presidency Project", x=260, y=620)
    pa = a * appear(lt, k)
    if pa > 0:
        lesson(base, pa, ["Big players tip their hand."], y=360,
               sub="An unexplained move against you? Get out first — find the reason later.", eyebrow="PRINCIPLE")


def s_gold(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "GOLD  ·  1979 – 1980", "His best year")
    x0, x1, y0, y1 = 150, 1300, 260, 780
    vmin, vmax = 200, 900
    ca = a * appear(lt, 0.3)
    chart_axes(base, ca, x0, y0, x1, y1, vmin, vmax, [300, 500, 700, 850], lambda v: "$%d" % v)
    yv = lambda v: y1 - (v - vmin) / (vmax - vmin) * (y1 - y0)
    n = 110
    shape = np.concatenate([np.linspace(230, 420, 60), np.linspace(420, 850, 30), np.linspace(850, 560, 20)])
    path = series(91, n, 0, 0, 6, shape=shape)
    path[89] = 850
    p = ease_io(prog(lt, 0.5, 16.0))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    aa_lines(base, [([(xs(i), yv(path[i])) for i in range(m)], GOLD, 3)], ca)
    marks = [(68, "Afghanistan · 200,000 oz bought (his account)", WHITE, "Then came the Soviet invasion"),
             (84, "Marcus sells ≈ $750", WHITE, "He sold at around seven hundred"),
             (89, "Peak ≈ $850 · 21 Jan 1980", GOLD, "He sold at around seven hundred")]
    for i, lab, col, key in marks:
        if m > i:
            ka = ca * appear(lt, max(0.5 + i / n * 15.5, K(key) - t0))
            vy = 750 if i == 84 else path[i]
            dot(base, xs(i), yv(vy), 8, col, ka)
            T(base, lab, xs(i) - 16, yv(vy) - 10 - (0 if i != 68 else -40), "semibold", 20, col, ka, "r")
    source(base, ca, "Bloomberg; price path illustrative")
    T(base, "Marcus remembered the top as “nearly $900”", 1340, 300, "italic", 22, MUTED,
      a * appear(lt, K("Gold went on to about eight hundred") - t0), "l")


def s_limitrule(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "HIS RULE FOR WILD MARKETS", "Consecutive limit-up days")
    days = [("DAY 1", "", BORDER), ("DAY 2", "", BORDER), ("DAY 3", "Very cautious", AMBER),
            ("DAY 4", "Almost always out", (230, 120, 60)), ("DAY 5", "Mandatory exit", RISK)]
    for i, (d, s, c) in enumerate(days):
        x = 200 + i * 310
        ia = a * appear(lt, 0.5 + i * 1.6)
        frame_box(base, x, 320, x + 270, 600, ia, stripe=c if i >= 2 else None)
        T(base, d, x + 135, 360, "semibold", 28, WHITE, ia, "m", 4)
        T(base, "LIMIT UP", x + 135, 420, "mono_medium", 24, GOLD, ia, "m")
        T(base, s, x + 135, 520, "semibold", 24, c if i >= 2 else MUTED, ia, "m")
    T(base, "“Insane” volatility and momentum = the end of a move, not the beginning", W / 2, 700, "regular", 30,
      MUTED, a * appear(lt, 9), "m")


def s_dm(base, t, lt, dur, a):
    t0 = t - lt
    k = K("And size brought its own danger") - t0
    da = a * (1 - appear(lt, k - 0.3))
    T(base, "CURRENCY POSITIONS (HIS ACCOUNT)", 150, 240, "medium", 22, GOLD, da, "l", 5)
    T(base, "DM 600 million", 150, 280, "display_light", 110, WHITE, da * appear(lt, 0.4))
    T(base, "≈ $300 million  ·  own + company account", 150, 420, "regular", 32, MUTED, da * appear(lt, 0.8))
    # clock with wake-ups
    cx, cy = 1450, 520
    ring(base, cx, cy, 200, BORDER, da, 2)
    for h in range(12):
        ang = h / 12 * 2 * math.pi - math.pi / 2
        on = appear(lt, 1.5 + h * 0.5)
        dot(base, cx + 170 * math.cos(ang), cy + 170 * math.sin(ang), 9, GOLD if h % 2 == 0 else BORDER, da * on)
    T(base, "woke ~every 2 hours", cx, cy - 20, "regular", 26, WHITE, da * appear(lt, 2), "m")
    ba = a * appear(lt, k)
    if ba > 0:
        T(base, "THE BUNDESBANK INTERVENES", W / 2, 260, "medium", 24, RISK, ba, "m", 8)
        T(base, "−$2.5 million", W / 2, 320, "display_light", 120, RISK, ba, "m")
        T(base, "in about five minutes — he got out", W / 2, 470, "regular", 32, WHITE, ba, "m")
        k2 = K("Half an hour later") - t0
        T(base, "30 minutes later: the market had fully recovered", W / 2, 560, "regular", 30, MUTED, a * appear(lt, k2), "m")
        k3 = K("He still believed") - t0
        T(base, "A stop protects you from the disaster you can't foresee.", W / 2, 680, "display_light", 44, GOLD,
          a * appear(lt, k3), "m")


def s_tone_intro(base, t, lt, dur, a):
    lesson(base, a * appear(lt, 0.2), ["The best trades have", "three things going for them."], y=360,
           eyebrow="THE METHOD")


def s_pillars(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "THE THREE CONDITIONS", "When everything lines up")
    pillars = [("FUNDAMENTALS", "supply / demand imbalance", "First, fundamentals"),
               ("TECHNICALS", "chart already moving that way", "Second, technicals"),
               ("MARKET TONE", "reacts the right way to news", "Third, market tone")]
    lit = 0
    for i, (nm, d, key) in enumerate(pillars):
        k = K(key) - t0
        on = appear(lt, k)
        lit += on
        x = 330 + i * 450
        rect(base, (x, 420, x + 260, 720), GOLD if on > 0.5 else LOSSBAR, a * (0.35 + 0.55 * on))
        T(base, nm, x + 130, 740, "semibold", 24, WHITE, a, "m", 4)
        T(base, d, x + 130, 780, "regular", 20, MUTED, a * on, "m")
    cap = a * appear(lt, K("Restrict yourself to those trades") - t0)
    rect(base, (290, 360, 1630, 410), GOLD, cap)
    T(base, "A-GRADE TRADE", W / 2, 368, "semibold", 26, (20, 18, 12), cap, "m", 8)
    k5 = K("When a trade met all three criteria") - t0
    T(base, "5 – 6× normal size", W / 2, 260 + 0, "display_light", 0 + 54, GOLD, a * appear(lt, k5), "m")


def s_goodnews(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "WHEN GOOD NEWS FAILS", "Soybeans, late 1970s")
    x0, x1, y0, y1 = 150, 1250, 260, 780
    ca = a * appear(lt, 0.3)
    lim = 330
    R.hline(base, x0, x1, lim, GOLD, ca, 2, dash=(14, 8))
    T(base, "LIMIT UP", x1, lim - 32, "semibold", 18, GOLD, ca, "r", 3)
    k = K("Soybeans opened limit-up") - t0
    n = 100
    pre = np.linspace(620, 600, 30)
    gap = np.full(15, lim)
    slip = np.linspace(lim, 520, 30) + series(5, 30, 0, 0, 5)
    fall = np.linspace(520, 700, 25)
    path = np.concatenate([pre, gap, slip, fall])
    p = ease_io(prog(lt, 0.5, max(1.0, k))) * 0.3 + 0.7 * ease_io(prog(lt, k, k + 14))
    m = max(2, int(n * p))
    xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
    aa_lines(base, [([(xs(i), path[i]) for i in range(m)], WHITE, 3)], ca)
    T(base, "Spectacular export figures:", 1300, 290, "regular", 26, MUTED, a * appear(lt, 1.0))
    T(base, "expected limit-up for 3 days", 1300, 326, "regular", 26, MUTED, a * appear(lt, 1.0))
    if m > 48:
        sa = ca * appear(lt, k + 3)
        dot(base, xs(48), path[48], 9, RISK, sa)
        T(base, "can't hold the limit", xs(48) + 20, path[48] - 40, "semibold", 22, RISK, sa)
    k2 = K("He sold frantically") - t0
    oa = a * appear(lt, k2)
    T(base, "SELL, SELL, SELL", 1300, 420, "display_semibold", 64, RISK, oa)
    T(base, "accidentally ends up short", 1300, 510, "regular", 28, WHITE, oa)
    k3 = K("He bought it back") - t0
    T(base, "covered 40–50¢ lower", 1300, 580, "mono_medium", 34, GOLD, a * appear(lt, k3))


def s_rule_card(base, t, lt, dur, a, lines, sub=None, eyebrow="RULE"):
    lesson(base, a * appear(lt, 0.2), lines, y=360, sub=sub, eyebrow=eyebrow)


def s_chain(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "WHO IS LEFT TO BUY?", "How breakouts changed")
    nodes = ["Professionals", "Commercial users", "Brokerage clients", "Short covering", "“The dentists”"]
    T(base, "EARLY 1970s — A SLOW CHAIN OF BUYERS", 150, 260, "medium", 20, GOLD, a * appear(lt, 0.4), "l", 5)
    for i, nm in enumerate(nodes):
        x = 150 + i * 340
        ia = a * appear(lt, 0.8 + i * 0.9)
        frame_box(base, x, 310, x + 290, 400, ia)
        T(base, nm, x + 145, 336, "regular", 26, WHITE, ia, "m")
        if i:
            T(base, "→", x - 26, 330, "regular", 34, GOLD, ia, "m")
    k = K("By the late 1980s") - t0
    ka = a * appear(lt, k)
    T(base, "LATE 1980s — EVERYONE AT ONCE", 150, 480, "medium", 20, RISK, ka, "l", 5)
    rng = np.random.default_rng(3)
    for i in range(40):
        x = 160 + rng.uniform(0, 1500)
        dot(base, x, 560 + rng.uniform(-30, 30), 7, WHITE, ka * appear(lt, k + 0.3 + rng.uniform(0, 0.6)))
    T(base, "→ breakout, then snap-back", 150, 640, "regular", 30, MUTED, ka)
    k2 = K("So the trader must always ask") - t0
    T(base, "How many people are left to act on this idea?", W / 2, 740, "display_light", 48, GOLD,
      a * appear(lt, k2), "m")


def s_lifestyle(base, t, lt, dur, a):
    t0 = t - lt
    groups = [("~10", "houses"), ("1", "plane charter service"), ("60–70", "employees")]
    for i, (n_, lab) in enumerate(groups):
        x = 300 + i * 460
        ia = a * appear(lt, 0.4 + i * 0.8)
        T(base, n_, x + 150, 340, "display_light", 140, WHITE, ia, "m")
        T(base, lab, x + 150, 520, "regular", 30, MUTED, ia, "m")
    T(base, "LIFE OUTSIDE THE MARKETS", W / 2, 240, "medium", 22, GOLD, a * appear(lt, 0.2), "m", 8)


def s_dollar_split(base, t, lt, dur, a):
    t0 = t - lt
    header(base, a * appear(lt, 0.1), "WHERE EACH TRADING DOLLAR WENT", "His own estimate")
    parts = [(0.30, "Taxes", MUTED), (0.30, "Planes", RISK), (0.20, "Real estate", AMBER), (0.20, "Left", GOLD)]
    x = 200
    tot = 1520
    for i, (f, lab, c) in enumerate(parts):
        ia = a * appear(lt, 0.5 + i * 0.7)
        w = tot * f
        rect(base, (x + 3, 360, x + w - 3, 500), c, ia)
        T(base, "%d¢" % round(f * 100), x + w / 2, 390, "mono_medium", 48, (20, 18, 14), ia, "m")
        T(base, lab, x + w / 2, 520, "regular", 28, WHITE, ia, "m")
        x += w
    k = K("He said he probably lost more than half") - t0
    T(base, "Lost: more than half of everything he made (his estimate)", W / 2, 640, "regular", 32, RISK,
      a * appear(lt, k), "m")
    k2 = K("He took it, he said, as a life lesson") - t0
    T(base, "“I can stay at a hotel and walk on the beach.” — paraphrased", W / 2, 720, "italic", 28, MUTED,
      a * appear(lt, k2), "m")


def s_rules_list(base, t, lt, dur, a):
    header(base, a * appear(lt, 0.1), "ADVICE TO TRADERS", "Seven rules")
    rules = ["Risk < 5% per idea", "Always use stops", "In doubt? Get out", "Hold winners, cut losers",
             "Follow your own light", "Watch your equity curve", "Don't rely on experts"]
    for i, r in enumerate(rules):
        ia = a * appear(lt, 0.3 + i * 0.25)
        y = 270 + i * 76
        T(base, "%d" % (i + 1), 200, y, "display_light", 48, GOLD, ia, "m")
        T(base, r, 260, y + 6, "display_light", 44, WHITE, ia)


def s_five(base, t, lt, dur, a):
    t0 = t - lt
    keys = ["Rule two", "Rule three", "Rule four", "Rule five"]
    ks = [K(x) - t0 for x in keys]
    cards = [
        (["Always use stops."], "Decide your exit before you enter. A stop commits you."),
        (["When in doubt,", "get out."], "Out of the position, you can think clearly again."),
        (["Hold winners.", "Cut losers."], "“If you don't stay with your winners, you are not going to be able to pay for the losers.”"),
        (["Follow your own light."], "Someone else's idea gives you none of the conviction to hold it."),
    ]
    # phase 0: the 5% explainer
    pa = a * (1 - appear(lt, ks[0] - 0.4))
    if pa > 0:
        header(base, pa, "RULE ONE", "Risk less than 5% on any one idea")
        eq = 1.0
        n = int(20 * ease_io(prog(lt, 1.0, 9.0)))
        for i in range(20):
            x = 180 + i * 74
            h = 360 * (0.95 ** i)
            ia = pa * (1 if i <= n else 0.15)
            rect(base, (x, 700 - h, x + 52, 700), RISK if i == n else GOLD, ia * 0.85)
        T(base, "20 losses in a row at 5% each", 180, 730, "regular", 26, MUTED, pa)
        T(base, "≈ 36% of capital left  (0.95²⁰)", 1740, 730, "mono_medium", 30, WHITE, pa * appear(lt, 8), "r")
        k1 = K("And note his precise wording") - t0
        qa = pa * appear(lt, k1)
        frame_box(base, 1180, 250, 1760, 450, qa, stripe=GOLD)
        T(base, "CORN  +  WHEAT", 1470, 290, "semibold", 30, WHITE, qa, "m", 4)
        T(base, "= ONE IDEA", 1470, 350, "display_light", 54, GOLD, qa, "m")
    for i, (lines, sub) in enumerate(cards):
        st = ks[i]
        en = ks[i + 1] if i + 1 < len(ks) else dur + 1
        ca = a * appear(lt, st) * (1 - appear(lt, en - 0.4))
        if ca > 0:
            lesson(base, ca, lines, y=360, sub=sub, eyebrow="RULE %s" % ["TWO", "THREE", "FOUR", "FIVE"][i])


def s_equity(base, t, lt, dur, a):
    t0 = t - lt
    k7 = K("Rule seven") - t0
    kb = K("Beyond the rules") - t0
    ea = a * (1 - appear(lt, k7 - 0.4))
    if ea > 0:
        header(base, ea, "RULE SIX", "Watch your equity curve")
        x0, x1, y0, y1 = 150, 1700, 280, 620
        n = 100
        shape = np.concatenate([np.linspace(560, 330, 55), np.linspace(330, 470, 25), np.linspace(470, 430, 20)])
        path = series(15, n, 0, 0, 5, shape=shape)
        p = ease_io(prog(lt, 0.4, 8.0))
        m = max(2, int(n * p))
        xs = lambda i: x0 + i / (n - 1) * (x1 - x0)
        if m > 56:
            rect(base, (xs(55), y0, xs(min(m - 1, 80)), y1), RISK, ea * 0.08)
            T(base, "drawdown → cut size", xs(56) + 10, y0 + 10, "semibold", 20, RISK, ea)
        aa_lines(base, [([(xs(i), path[i]) for i in range(m)], GOLD, 3)], ea)
        for i in range(0, m, 5):
            sz = 1.0 if i < 55 else (0.4 if i < 80 else 0.7)
            if 66 < i < 80:
                sz = 0.0
            rect(base, (xs(i), 760 - 80 * sz, xs(i) + 40, 760), MUTED, ea * 0.7)
        T(base, "POSITION SIZE", x0, 780, "medium", 18, MUTED, ea, "l", 4)
        T(base, "pause 3–4 weeks", xs(70), 700, "italic", 20, FAINT, ea * (m > 75), "m")
    ra = a * appear(lt, k7) * (1 - appear(lt, kb - 0.4))
    if ra > 0:
        lesson(base, ra, ["Don't rely on experts."], y=360, eyebrow="RULE SEVEN",
               sub="Do your own homework. The market is bigger than anyone.")
    qa = a * appear(lt, kb)
    if qa > 0:
        T(base, "WHAT CAN'T BE WRITTEN DOWN", W / 2, 260, "medium", 22, GOLD, qa, "m", 8)
        for i, w_ in enumerate(["Gut feel", "Courage", "A gift — or a learnable skill"]):
            T(base, w_, W / 2, 340 + i * 110, "display_light", 64, WHITE, qa * appear(lt, kb + 0.5 + i * 1.2), "m")


def s_analysis_intro(base, t, lt, dur, a):
    T(base, "ANALYSIS  ·  OUR INTERPRETATION", W / 2, 260, "semibold", 24, AMBER, a * appear(lt, 0.2), "m", 8)
    T(base, "“The era of trend following is over.”", W / 2, 380, "display_light", 64, WHITE, a * appear(lt, 0.6), "m")
    T(base, "Marcus's view, May 1988 — except under major imbalances", W / 2, 480, "regular", 30, MUTED,
      a * appear(lt, 1.2), "m")


def s_dennis(base, t, lt, dur, a):
    t0 = t - lt
    for i, (eb, big, line, src, key) in enumerate([
            ("1987 – 1988", ">50%", "losses stopped several Richard Dennis public funds", "Wikipedia; Futures (1988)", None),
            ("SUMMER 1988", "−37%", "US corn output in the great drought", "Chicago Fed Letter, Oct 1988",
             "And within weeks of the interview")]):
        x = 150 + i * 860
        st = 0.3 if key is None else K(key) - t0
        ia = a * appear(lt, st)
        T(base, eb, x, 260, "medium", 22, GOLD, ia, "l", 5)
        T(base, big, x, 300, "display_light", 150, RISK if i == 0 else GOLD, ia)
        T(base, line, x, 490, "regular", 28, WHITE, ia)
        source(base, ia, src, x=x, y=540)
    k = K("Was the larger claim right") - t0
    ka = a * appear(lt, k)
    frame_box(base, 150, 640, 1770, 820, ka, stripe=AMBER)
    T(base, "INTERPRETATION", 190, 664, "semibold", 20, AMBER, ka, "l", 5)
    T(base, "Trend following survived — but crowded signals make simple breakouts less reliable.", 190, 712,
      "regular", 32, WHITE, ka)


def s_strengths(base, t, lt, dur, a):
    t0 = t - lt
    k = K("What remains relevant today") - t0
    sa = a * (1 - appear(lt, k - 0.4))
    cols = [("STRENGTHS", GOLD, ["Small, defined losses", "Large winners", "Size on the best setups", "Admits mistakes"], 0.4),
            ("WEAKNESSES", RISK, ["Impulsiveness", "Trading for entertainment", "A uniquely favourable 1970s",
                                  "Lifestyle leakage"], K("It also had weaknesses") - t0)]
    for i, (h, c, items, st) in enumerate(cols):
        x = 200 + i * 800
        ia = sa * appear(lt, st)
        frame_box(base, x, 230, x + 720, 720, ia, stripe=c)
        T(base, h, x + 40, 260, "semibold", 26, c, ia, "l", 6)
        for j, it in enumerate(items):
            T(base, it, x + 40, 340 + j * 88, "display_light", 44, WHITE, ia * appear(lt, st + 0.5 + j * 0.5))
    ra = a * appear(lt, k)
    if ra > 0:
        T(base, "STILL RELEVANT", W / 2, 240, "medium", 22, GOLD, ra, "m", 8)
        items = ["Position sizing", "Stops before entry", "Let winners run", "Watch the reaction to news",
                 "Ask who is left to buy"]
        for j, it in enumerate(items):
            T(base, it, W / 2, 310 + j * 82, "display_light", 54, WHITE, ra * appear(lt, k + 0.5 + j * 0.7), "m")
        kk = K("Trading, he said, is emotion") - t0
        T(base, "Trading is emotion — greed and fear — in every market.", W / 2, 760, "regular", 32, GOLD,
          a * appear(lt, kk), "m")


def s_epilogue(base, t, lt, dur, a):
    t0 = t - lt
    k = K("Michael Marcus died") - t0
    ba = a * (1 - appear(lt, k - 0.5))
    T(base, "BALANCE", W / 2, 300, "display_light", 120, WHITE, ba * appear(lt, 0.3), "m", 20)
    T(base, "Karate  ·  spiritual traditions  ·  “Is the universe friendly?”", W / 2, 470, "regular", 32, MUTED,
      ba * appear(lt, 1.5), "m")
    da = a * appear(lt, k)
    if da > 0:
        T(base, "MICHAEL MARCUS", W / 2, 330, "display_light", 110, WHITE, da, "m", 16)
        T(base, "1947 – 2023", W / 2, 480, "mono_medium", 44, GOLD, da, "m")
        T(base, "“One of the greatest traders I ever knew.” — Jack Schwager, 2023", W / 2, 580, "italic", 30, MUTED,
          a * appear(lt, K("When Jack Schwager learned") - t0), "m")
        source(base, da, "Wikipedia; Jack Schwager on X (June 2023)", x=W / 2 - 330, y=660)


def s_board_return(base, t, lt, dur, a):
    t0 = t - lt
    s_board(base, t, lt + 20, dur, a, freeze_at=0, unfreeze=lt > 2.5, dim=0.9)
    k = K("What made him a Market Wizard") - t0
    qa = a * appear(lt, k)
    if qa > 0:
        rect(base, (0, 0, W, H), (6, 6, 7), qa * 0.85)
        T(base, "Each failure became a rule.", W / 2, 440, "display_light", 72, WHITE, qa, "m")


def s_end(base, t, lt, dur, a):
    T(base, "MARKET WIZARDS", W / 2, 360, "display_light", 96, WHITE, a * appear(lt, 0.3), "m", 26)
    R.hline(base, W / 2 - 220, W / 2 + 220, 490, GOLD, a * appear(lt, 0.6), 2)
    T(base, "EPISODE ONE  ·  MICHAEL MARCUS", W / 2, 520, "medium", 24, GOLD, a * appear(lt, 0.8), "m", 8)
    T(base, "Next episode: coming soon", W / 2, 580, "regular", 28, MUTED, a * appear(lt, 1.2), "m")
    for i, ln in enumerate([
            "Educational content. Hypothetical examples are illustrative. Not investment advice.",
            "Trader statements are their own recollections as published in Market Wizards (1989), Jack D. Schwager.",
            "Narration: AI voice (ElevenLabs). Charts are original illustrations unless a source is shown."]):
        T(base, ln, W / 2, 860 + i * 30, "regular", 18, FAINT, a * appear(lt, 1.5), "m")


def s_lumber_note(base, t, lt, dur, a):
    s_lumber_intro(base, t, lt, dur, a)


SCENES = {
    "1.0": s_board, "1.1": s_name, "1.2": s_series_title,
    "2.0": lambda b, t, l, d, a: s_ledger(b, t, l, d, a, "A scholar meets the market", "1969",
                                          [("JOHNS HOPKINS", "Phi Beta Kappa, 1969"), ("NEXT", "PhD fellowship, psychology"),
                                           ("THE PROMISE", "“Double your money every two weeks”", GOLD)],
                                          keys=[None, "He had a doctoral fellowship", "Then, through a friend"]),
    "2.1": lambda b, t, l, d, a: s_ledger(b, t, l, d, a, "The first trading budget", "1969",
                                          [("ADVISER", "John · $30 a week (plus potato chips)"),
                                           ("CAPITAL", "≈ $1,000 of savings"),
                                           ("FIRST BROKER", "Reynolds Securities, Baltimore")],
                                          keys=[None, "He put up about a thousand", "Their first trip"]),
    "2.2": s_futures, "2.3": s_spread, "2.4": lambda b, t, l, d, a: s_spread(b, t, l + 6, d, a, stamp=True),
    "2.5": s_lesson_tally,
    "3.0": s_keltner, "3.1": s_blight, "3.2": s_skill_luck, "3.3": s_headline, "3.4": s_limit, "3.5": s_ruin,
    "4.0": s_glass, "4.1": s_code,
    "4.2": lambda b, t, l, d, a: s_person(b, t, l, d, a, "Ed Seykota", "MIT  ·  1969",
                                          "Early computer-tested trend-following systems", "Wikipedia — Ed Seykota"),
    "4.3": s_trend,
    "5.0": s_controls, "5.1": s_supply, "5.2": s_plywood, "5.3": s_two_tier,
    "6.0": s_lumber_intro, "6.1": s_leverage, "6.2": s_survive,
    "7.0": s_inflation, "7.1": s_soy, "7.2": s_winners,
    "8.0": s_ring, "8.1": s_sound, "8.2": s_surf,
    "9.0": s_cc, "9.1": s_compound, "9.2": s_disclosure,
    "10.0": s_world, "10.1": s_dollar, "10.2": s_factcheck, "10.3": s_gold, "10.4": s_limitrule, "10.5": s_dm,
    "11.0": s_tone_intro, "11.1": s_pillars, "11.2": s_goodnews,
    "11.3": lambda b, t, l, d, a: s_rule_card(b, t, l, d, a, ["When the news is wonderful", "and the market can't go up —"],
                                              sub="sell.", eyebrow="LESSON"),
    "11.4": s_chain,
    "12.0": s_lifestyle, "12.1": s_dollar_split,
    "13.0": s_rules_list, "13.1": s_five, "13.2": s_equity,
    "13.3": lambda b, t, l, d, a: s_person(b, t, l, d, a, "Bruce Kovner", "Founded Caxton Associates, 1983",
                                           "Marcus's protégé — prized for his objectivity",
                                           "Wikipedia — Caxton Associates", extra="“A good trader can't be rigid.”"),
    "14.0": s_analysis_intro, "14.1": s_dennis, "14.2": s_strengths,
    "15.0": s_epilogue, "15.1": s_board_return, "15.2": s_end,
}

# --------------------------------------------------------- scene schedule ----
SCHED = []
cues = sorted(TL["cues"], key=lambda c: (c["chapter"], c["idx"]))
for c in cues:
    key = "%d.%d" % (c["chapter"], c["idx"])
    if key == "0.0" or key not in SCENES:
        continue
    t0 = c["t0"]
    if c["chapter"] >= 2 and c["idx"] == 0:
        t0 = CHAPTERS[c["chapter"]]["t0"] + CARD - 0.3
    SCHED.append([t0, None, key])
SCHED.sort()
for i in range(len(SCHED)):
    nxt = SCHED[i + 1][0] if i + 1 < len(SCHED) else DUR
    # a chapter card interrupts the previous scene
    for c in TL["chapters"]:
        if c["id"] >= 2 and SCHED[i][0] < c["t0"] < nxt:
            nxt = c["t0"] + 0.2
    SCHED[i][1] = nxt


# =============================================================== compositor ==
def subtitles(base, t):
    for s in SUBS:
        if s["t0"] - 0.05 <= t <= s["t1"] + 0.12:
            a = R.fade(t, s["t0"] - 0.05, s["t1"] + 0.12, 0.12, 0.12)
            lines = R.wrap(s["text"], "medium", 36, 1640)
            if len(lines) > 2:
                lines = R.wrap(s["text"], "medium", 32, 1760)
            size = 36 if len(lines) <= 2 else 32
            lh = 50 if size == 36 else 44
            y = 1020 - len(lines) * lh
            for ln in lines:
                R.draw_text(base, ln, W / 2, y, "medium", size, WHITE, a, "m", 0, shadow=True)
                y += lh
            break


def frame(t):
    base = Image.new("RGBA", (W, H), (0, 0, 0, 255))
    va = prog(t, 2.2, 3.2) * (1 - prog(t, DUR - 1.0, DUR))
    if va > 0:
        R.blit(base, R.VIGNETTE, 0, 0, va)
        ambient(base, t, va)
    if t < 2.6:
        R.scene_sting(base, t)
    for c in TL["chapters"]:
        if c["id"] >= 2:
            chapter_card(base, t, c)
    for t0, t1, key in SCHED:
        if t0 - 0.01 <= t <= t1 + 0.6:
            a = R.fade(t, t0, t1 + 0.6, 0.7, 0.6) if key != "15.2" else R.fade(t, t0, DUR, 0.8, 1.0)
            if a > 0.003:
                SCENES[key](base, t, t - t0, t1 - t0, a)
    subtitles(base, t)
    return base.convert("RGB")


# ==================================================================== audio ==
def decode(path, sr):
    raw = subprocess.run(["ffmpeg", "-v", "error", "-i", path, "-f", "s16le", "-ac", "1", "-ar", str(sr), "-"],
                         capture_output=True).stdout
    return np.frombuffer(raw, dtype="<i2").astype(np.float32) / 32768.0


def make_audio(path, sr=44100):
    n = int((DUR + 0.5) * sr)
    voice = np.zeros(n, np.float32)
    cache = {}
    for seg in TL["audio"]:
        f = seg["file"]
        if f not in cache:
            cache[f] = decode(os.path.join(EP, "audio", f), sr)
        x = cache[f]
        a0, a1 = int(seg["a0"] * sr), int(seg["a1"] * sr)
        a0 = max(0, a0 - int(0.03 * sr))
        a1 = min(len(x), a1 + int(0.18 * sr))
        clip = x[a0:a1].copy()
        fade_n = int(0.02 * sr)
        clip[:fade_n] *= np.linspace(0, 1, fade_n)
        clip[-fade_n:] *= np.linspace(1, 0, fade_n)
        o = int(seg["t0"] * sr) - int(0.03 * sr)
        o = max(0, o)
        e = min(n, o + len(clip))
        voice[o:e] += clip[: e - o]
    # music bed: slow minor pad, ducked under the voice
    t = np.arange(n) / sr

    def hz(m):
        return 440.0 * 2 ** ((m - 69) / 12)

    chords = [[45, 52, 57, 60, 64], [41, 48, 53, 57, 64], [38, 45, 50, 53, 57], [40, 47, 52, 56, 59]]
    music = np.zeros(n, np.float32)
    seg = 12.0
    st = 2.0
    k = 0
    while st < DUR:
        notes = chords[k % 4]
        a0t, a1t = st - 4, st + seg + 4
        i0, i1 = max(0, int(a0t * sr)), min(n, int(a1t * sr))
        tt = t[i0:i1]
        env = np.sin(np.clip((tt - a0t) / 5, 0, 1) * np.pi / 2) ** 2 * np.sin(np.clip((a1t - tt) / 5, 0, 1) * np.pi / 2) ** 2
        for j, m in enumerate(notes):
            f = hz(m)
            amp = (0.9 if j == 0 else 0.45) / len(notes)
            ph = 2 * np.pi * f * tt
            music[i0:i1] += (amp * env * (np.sin(ph) + 0.15 * np.sin(2 * ph))).astype(np.float32)
        st += seg
        k += 1
    # ducking envelope from voice RMS
    hop = int(0.05 * sr)

    def movavg(x, k):
        c = np.cumsum(np.concatenate([[0.0], x.astype(np.float64)]))
        out = (c[k:] - c[:-k]) / k
        pad = len(x) - len(out)
        return np.concatenate([np.full(pad // 2, out[0]), out, np.full(pad - pad // 2, out[-1])]).astype(np.float32)

    rms = np.sqrt(np.maximum(movavg(voice ** 2, hop), 0))
    duck = 1.0 - 0.55 * np.clip(rms / 0.05, 0, 1)
    duck = movavg(duck, hop * 8)
    music *= 0.11 * duck
    master = np.clip((t - 2.0) / 3.0, 0, 1) * np.clip((DUR - t) / 3.0, 0, 1)
    music *= master
    # stings: logo hit + chime, and a soft hit at each chapter card
    rng = np.random.default_rng(5)

    def hit(t0, gain):
        i0 = int(t0 * sr)
        ln = int(2.2 * sr)
        tt = np.arange(ln) / sr
        f = 70 * np.exp(-tt * 0.9) + 38
        b = np.sin(2 * np.pi * np.cumsum(f) / sr) * np.exp(-tt * 2.2) * np.clip(tt / 0.03, 0, 1)
        e = min(n, i0 + ln)
        music[i0:e] += (b[: e - i0] * gain).astype(np.float32)

    def chime(t0, notes, gain):
        i0 = int(t0 * sr)
        ln = int(2.0 * sr)
        tt = np.arange(ln) / sr
        c = sum(np.sin(2 * np.pi * f * tt) for f in notes) * np.exp(-tt * 2.6) * np.clip(tt / 0.01, 0, 1)
        e = min(n, i0 + ln)
        music[i0:e] += (c[: e - i0] * gain).astype(np.float32)

    hit(0.08, 0.5)
    chime(0.5, (1318.5, 1760.0), 0.05)
    chime(1.05, (2637.0, 1975.5), 0.03)
    for c in TL["chapters"]:
        if c["id"] >= 2:
            hit(c["t0"] + 0.05, 0.22)
    mix = np.clip(voice * 0.92 + music, -1, 1)
    pcm = (np.stack([mix, mix], 1) * 32767).astype("<i2")
    with wave.open(path, "wb") as wf:
        wf.setnchannels(2)
        wf.setsampwidth(2)
        wf.setframerate(sr)
        wf.writeframes(pcm.tobytes())


# =================================================================== render ==
def render_chunk(args):
    idx, f0, f1 = args
    out = os.path.join(OUT, "chunk_%03d.mp4" % idx)
    if os.path.exists(out) and os.path.getsize(out) > 0 and os.path.exists(out + ".done"):
        return out
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24",
           "-s", "%dx%d" % (W, H), "-r", str(FPS), "-i", "-",
           "-c:v", "libx264", "-preset", "medium", "-crf", "20", "-pix_fmt", "yuv420p",
           "-x264-params", "aq-mode=3", out]
    proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    for fi in range(f0, f1):
        proc.stdin.write(frame(fi / FPS).tobytes())
    proc.stdin.close()
    proc.wait()
    open(out + ".done", "w").close()
    return out


def stills():
    d = os.path.join(OUT, "stills")
    os.makedirs(d, exist_ok=True)
    for t0, t1, key in SCHED:
        tt = min(t1 - 0.5, t0 + max(4.0, (t1 - t0) * 0.6))
        frame(tt).save(os.path.join(d, "%05.0f_%s.png" % (tt, key.replace(".", "_"))))
    for c in TL["chapters"]:
        if c["id"] >= 2:
            frame(c["t0"] + 2.5).save(os.path.join(d, "%05.0f_card%02d.png" % (c["t0"] + 2.5, c["id"])))
    print("stills ->", d)


def main():
    os.makedirs(OUT, exist_ok=True)
    if "--stills" in sys.argv:
        stills()
        return
    if "--range" in sys.argv:
        i = sys.argv.index("--range")
        a0, a1 = float(sys.argv[i + 1]), float(sys.argv[i + 2])
        out = os.path.join(OUT, "preview_%d_%d.mp4" % (a0, a1))
        wav = os.path.join(OUT, "preview.wav")
        make_audio(wav)
        cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", "%dx%d" % (W, H),
               "-r", str(FPS), "-i", "-", "-ss", str(a0), "-t", str(a1 - a0), "-i", wav,
               "-c:v", "libx264", "-preset", "veryfast", "-crf", "22", "-pix_fmt", "yuv420p",
               "-c:a", "aac", "-shortest", out]
        proc = subprocess.Popen(cmd, stdin=subprocess.PIPE)
        for fi in range(int(a0 * FPS), int(a1 * FPS)):
            proc.stdin.write(frame(fi / FPS).tobytes())
        proc.stdin.close()
        proc.wait()
        os.remove(wav)
        print("preview ->", out)
        return
    total = int(DUR * FPS)
    chunk = FPS * 30
    jobs = [(i, f, min(total, f + chunk)) for i, f in enumerate(range(0, total, chunk))]
    workers = os.cpu_count() or 4
    with Pool(workers) as pool:
        chunks = []
        for k, c in enumerate(pool.imap(render_chunk, jobs)):
            chunks.append(c)
            if k % 10 == 0:
                print("chunk %d/%d" % (k + 1, len(jobs)), flush=True)
    lst = os.path.join(OUT, "chunks.txt")
    with open(lst, "w") as f:
        for c in chunks:
            f.write("file '%s'\n" % c)
    wav = os.path.join(OUT, "mix.wav")
    make_audio(wav)
    final = os.path.join(OUT, "market-wizards-ep01-michael-marcus.mp4")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", lst, "-i", wav,
                    "-c:v", "copy", "-af", "loudnorm=I=-16:TP=-1.5:LRA=11", "-ar", "48000", "-c:a", "aac", "-b:a", "192k",
                    "-shortest", "-movflags", "+faststart", final],
                   check=True)
    print("done ->", final)


if __name__ == "__main__":
    main()
