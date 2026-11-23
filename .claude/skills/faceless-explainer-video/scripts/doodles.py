"""Code-drawn cartoon 'doodle' building blocks (people, phones, laptops, clocks, server racks,
skylines, factories, money, screens...). Per-video scenes live in the project's doodle_scenes.py,
which defines DOODLES = {"img01": fn(f, t, fi), ...}, NIGHT = {...} and optional DOODLE_KW.

Code-drawn cartoon 'doodle' illustrations, used for any illustration that has no
ElevenLabs image yet. Same palette + boiling hand-drawn lines as the motion graphics,
so the whole video stays one consistent world. Every drawing is original (no logos)."""
import math
import numpy as np
import cv2
from gfx import *

SKIN = (236, 190, 150)
SKIN2 = (196, 140, 100)
CY = 470   # vertical centre of the drawing (bottom area is kept for captions)

# ------------------------------------------------------------------ building blocks
def person(f, x, y, s=1.0, shirt=TEAL, mood="neutral", fi=0, seed=0, skin=SKIN, arms="down", t=0.0):
    """Simple rounded character. y = feet position."""
    bw, bh = 110 * s, 150 * s
    box(f, x - bw / 2, y - bh, x + bw / 2, y, shirt, INK, max(3, int(5 * s)), fi, r=40 * s, seed=seed, shadow=False)
    hr = 58 * s; hy = y - bh - hr * 0.8
    poly(f, circle_pts(x, hy, hr, 36), INK, fill=skin, thick=max(3, int(5 * s)), fi=fi, wob=1.2, seed=seed + 1)
    ey = hy - 6 * s
    if mood == "shock":
        for dx in (-20, 20): cv2.circle(f, (int(x + dx * s), int(ey)), int(8 * s), INK, -1, cv2.LINE_AA)
        poly(f, circle_pts(x, hy + 26 * s, 13 * s, 16), INK, fill=(90, 30, 40), thick=3, fi=fi, wob=0.6, seed=seed + 2)
    elif mood == "sad":
        for dx in (-20, 20): cv2.circle(f, (int(x + dx * s), int(ey)), int(6 * s), INK, -1, cv2.LINE_AA)
        poly(f, [(x - 18 * s, hy + 32 * s), (x, hy + 24 * s), (x + 18 * s, hy + 32 * s)], INK, None, 4, fi, 0.6, seed + 3, closed=False)
    elif mood == "happy":
        for dx in (-20, 20): cv2.circle(f, (int(x + dx * s), int(ey)), int(6 * s), INK, -1, cv2.LINE_AA)
        poly(f, [(x - 20 * s, hy + 20 * s), (x, hy + 32 * s), (x + 20 * s, hy + 20 * s)], INK, None, 4, fi, 0.6, seed + 3, closed=False)
    else:
        for dx in (-20, 20): cv2.circle(f, (int(x + dx * s), int(ey)), int(6 * s), INK, -1, cv2.LINE_AA)
        poly(f, [(x - 14 * s, hy + 26 * s), (x + 14 * s, hy + 26 * s)], INK, None, 4, fi, 0.6, seed + 3, closed=False)
    if arms == "up":
        wave = math.sin(t * 8) * 8 * s
        for side in (-1, 1):
            poly(f, [(x + side * bw / 2.2, y - bh * 0.8), (x + side * (bw / 2 + 40 * s), y - bh * 1.35 + wave)], INK, None, int(9 * s), fi, 1, seed + 5 + side, closed=False)
    return hy

def phone(f, x, y, s=1.0, screen="spinner", fi=0, t=0.0, seed=0):
    w, h = 230 * s, 420 * s
    box(f, x - w / 2, y - h / 2, x + w / 2, y + h / 2, DARK2, INK, 7, fi, r=34 * s, seed=seed)
    sx0, sy0, sx1, sy1 = x - w / 2 + 16 * s, y - h / 2 + 40 * s, x + w / 2 - 16 * s, y + h / 2 - 40 * s
    cv2.rectangle(f, (int(sx0), int(sy0)), (int(sx1), int(sy1)), (238, 240, 245) if screen != "dark" else (25, 28, 36), -1)
    cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    if screen == "spinner":
        for k in range(8):
            a = 2 * math.pi * k / 8 + t * 4
            c = int(120 + 120 * ((k + int(t * 8)) % 8) / 8)
            cv2.circle(f, (int(cx + 40 * s * math.cos(a)), int(cy + 40 * s * math.sin(a))), int(9 * s), (c, c, c), -1, cv2.LINE_AA)
    elif screen == "redchart":
        pts = [(sx0 + 10, sy0 + 60 * s), (sx0 + 60 * s, sy0 + 80 * s), (cx, sy0 + 70 * s), (cx + 20 * s, cy + 40 * s), (sx1 - 10, sy1 - 30 * s)]
        poly(f, pts, RED, None, int(8 * s), fi, 1, seed + 3, closed=False)
        arrow(f, cx + 30 * s, cy + 10 * s, sx1 - 14, sy1 - 20 * s, RED, int(8 * s), 26 * s, fi, seed + 4)
    elif screen == "pie":
        poly(f, circle_pts(cx, cy, 70 * s, 40), INK, fill=(150, 180, 220), thick=4, fi=fi, wob=0.8, seed=seed + 5)
        poly(f, [(cx, cy)] + circle_pts(cx, cy, 70 * s, 8, -90, -72), INK, fill=(238, 240, 245), thick=4, fi=fi, wob=0.8, seed=seed + 6)
    elif screen == "game":
        for k in range(6):
            col = [LIME, YELLOW, ORANGE, TEAL, RED, BLUE][k]
            yy = sy0 + 30 * s + k * 50 * s + (t * 60 * s) % (50 * s)
            if yy < sy1 - 20: cv2.rectangle(f, (int(cx - 50 * s + (k % 3) * 30 * s), int(yy)), (int(cx - 20 * s + (k % 3) * 30 * s), int(yy + 30 * s)), col, -1)
    elif screen == "alert":
        put_text(f, "!", cx, cy, "anton", int(160 * s), RED)

def laptop(f, x, y, s=1.0, screen="spinner", fi=0, t=0.0, seed=0, glow_col=None):
    w, h = 520 * s, 320 * s
    box(f, x - w / 2, y - h, x + w / 2, y, DARK2, INK, 7, fi, r=18 * s, seed=seed)
    sx0, sy0, sx1, sy1 = x - w / 2 + 20 * s, y - h + 20 * s, x + w / 2 - 20 * s, y - 20 * s
    cv2.rectangle(f, (int(sx0), int(sy0)), (int(sx1), int(sy1)), (238, 240, 245) if screen != "dark" else (25, 28, 36), -1)
    poly(f, [(x - w / 2 - 60 * s, y), (x + w / 2 + 60 * s, y), (x + w / 2 + 30 * s, y + 30 * s), (x - w / 2 - 30 * s, y + 30 * s)], INK, fill=(170, 175, 190), thick=6, fi=fi, wob=1, seed=seed + 1)
    cx, cy = (sx0 + sx1) / 2, (sy0 + sy1) / 2
    if screen == "spinner":
        for k in range(8):
            a = 2 * math.pi * k / 8 + t * 4; c = int(120 + 120 * ((k + int(t * 8)) % 8) / 8)
            cv2.circle(f, (int(cx + 40 * s * math.cos(a)), int(cy + 40 * s * math.sin(a))), int(9 * s), (c, c, c), -1, cv2.LINE_AA)
    elif screen == "glitch":
        r = np.random.default_rng(fi // 3)
        for k in range(14):
            yy = int(r.uniform(sy0, sy1 - 10)); xx = int(r.uniform(sx0, sx1 - 80))
            cv2.rectangle(f, (xx, yy), (xx + int(r.uniform(30, 160)), yy + int(r.uniform(6, 22))), [RED, LIME, BLUE, YELLOW][k % 4], -1)
    elif screen == "code":
        for k in range(7):
            ww = (0.3 + 0.6 * ((k * 37) % 10) / 10) * (sx1 - sx0 - 40)
            cv2.rectangle(f, (int(sx0 + 20 + (k % 3) * 20), int(sy0 + 20 + k * 30 * s)), (int(sx0 + 20 + ww), int(sy0 + 34 + k * 30 * s)),
                          [LIME, BLUE, ORANGE][k % 3], -1)
    elif screen == "chip":
        chip(f, cx, cy, 70 * s, fi, 1.0, seed=seed + 9)
    elif screen == "blank":
        pass

def clock(f, x, y, r, hh, mm, fi=0, t=0.0, night=False, seed=0):
    poly(f, circle_pts(x, y, r, 60), INK, fill=(250, 246, 235) if not night else (215, 220, 235), thick=9, fi=fi, wob=1.4, seed=seed)
    for k in range(12):
        a = math.radians(k * 30 - 90)
        cv2.line(f, (int(x + r * 0.82 * math.cos(a)), int(y + r * 0.82 * math.sin(a))),
                 (int(x + r * 0.92 * math.cos(a)), int(y + r * 0.92 * math.sin(a))), INK, 6, cv2.LINE_AA)
    am = math.radians(mm * 6 - 90 + t * 6); ah = math.radians((hh % 12) * 30 + mm * 0.5 - 90)
    poly(f, [(x, y), (x + r * 0.5 * math.cos(ah), y + r * 0.5 * math.sin(ah))], INK, None, 14, fi, 0.6, seed + 1, closed=False)
    poly(f, [(x, y), (x + r * 0.78 * math.cos(am), y + r * 0.78 * math.sin(am))], RED, None, 9, fi, 0.6, seed + 2, closed=False)
    cv2.circle(f, (int(x), int(y)), 14, INK, -1, cv2.LINE_AA)

def rack(f, x, y, w, h, lit=1.0, fi=0, seed=0, col=LIME):
    box(f, x, y, x + w, y + h, (52, 58, 76), INK, 5, fi, r=10, seed=seed, shadow=False)
    rows = int(h / 34)
    for k in range(rows):
        yy = y + 14 + k * 34
        cv2.rectangle(f, (int(x + 10), int(yy)), (int(x + w - 10), int(yy + 22)), (70, 78, 98), -1)
        for j in range(3):
            on = lit > ((k * 7 + j * 3 + seed) % 10) / 10
            blink = (fi // 6 + k + j) % 3 != 0
            c = col if (on and blink) else (40, 44, 56)
            cv2.circle(f, (int(x + w - 26 - j * 18), int(yy + 11)), 5, c, -1, cv2.LINE_AA)

def racks_scene(f, t, fi, lit_fn, title_dark=False):
    for i in range(6):
        x = 230 + i * 250
        rack(f, x, 220, 190, 470, lit_fn(i, t), fi, seed=i * 5)

def building(f, x, base, w, h, color, fi, seed, windows=True, lit=0.6, win_col=(255, 225, 130)):
    box(f, x, base - h, x + w, base, color, INK, 5, fi, r=6, seed=seed, shadow=False)
    if windows:
        for r_ in range(int((h - 40) / 46)):
            for c in range(int((w - 20) / 40)):
                on = ((r_ * 13 + c * 7 + seed) % 10) / 10 < lit
                cv2.rectangle(f, (int(x + 16 + c * 40), int(base - h + 24 + r_ * 46)),
                              (int(x + 40 + c * 40), int(base - h + 50 + r_ * 46)), win_col if on else (70, 76, 96), -1)

def skyline(f, fi, lit=0.6, base=760, palette=None, seed=0, skip=None):
    palette = palette or [(120, 140, 170), (150, 120, 110), (110, 150, 140), (170, 150, 120), (120, 120, 160)]
    xs = [60, 260, 430, 1150, 1330, 1540, 1720]; hs = [300, 420, 250, 380, 280, 460, 320]
    for i, (x, h) in enumerate(zip(xs, hs)):
        if skip and skip(i): continue
        building(f, x, base, 170, h, palette[i % len(palette)], fi, seed + i, lit=lit)
    cv2.line(f, (0, base), (W, base), INK, 6, cv2.LINE_AA)

def sun(f, x, y, r, fi, t=0.0):
    glow(f, x, y, r * 3, YELLOW, 0.5)
    for k in range(12):
        a = math.radians(k * 30 + t * 10)
        poly(f, [(x + r * 1.25 * math.cos(a), y + r * 1.25 * math.sin(a)), (x + r * 1.6 * math.cos(a), y + r * 1.6 * math.sin(a))], ORANGE, None, 7, fi, 1, k, closed=False)
    poly(f, circle_pts(x, y, r, 40), INK, fill=YELLOW, thick=5, fi=fi, wob=1, seed=99)

def moon(f, x, y, r, fi):
    glow(f, x, y, r * 3, (180, 190, 255), 0.35)
    poly(f, circle_pts(x, y, r, 40), INK, fill=(245, 240, 215), thick=5, fi=fi, wob=1, seed=98)

def factory(f, x, base, s, fi, t, seed=0, running=True, color=(170, 120, 100)):
    box(f, x, base - 260 * s, x + 520 * s, base, color, INK, 6, fi, r=8, seed=seed, shadow=False)
    for k in range(3):   # saw-tooth roof
        x0 = x + k * 173 * s
        poly(f, [(x0, base - 260 * s), (x0 + 173 * s, base - 340 * s), (x0 + 173 * s, base - 260 * s)], INK, fill=(150, 100, 85), thick=6, fi=fi, wob=1, seed=seed + k)
    box(f, x + 400 * s, base - 470 * s, x + 470 * s, base - 260 * s, (120, 90, 80), INK, 6, fi, r=4, seed=seed + 7, shadow=False)
    if running:
        for k in range(4):   # smoke puffs
            ph = (t * 0.6 + k / 4) % 1
            poly(f, circle_pts(x + 435 * s + ph * 80 * s, base - 500 * s - ph * 200 * s, (20 + 40 * ph) * s, 20), (180, 180, 185),
                 fill=(220, 220, 225), thick=3, fi=fi, wob=1, seed=seed + 20 + k)
    # conveyor with chips
    cv2.rectangle(f, (int(x - 80 * s), int(base - 40 * s)), (int(x + 600 * s), int(base - 10 * s)), (90, 95, 110), -1)
    if running:
        for k in range(6):
            cxp = x - 60 * s + ((t * 120 * s + k * 120 * s) % (660 * s))
            chip(f, cxp, base - 75 * s, 24 * s, fi, 1.0, seed=seed + 30 + k)

def money(f, x, y, s, fi, seed, ang=0, alpha=1.0):
    pts = [(-90, -45), (90, -45), (90, 45), (-90, 45)]
    ca, sa = math.cos(ang), math.sin(ang)
    P = [(x + s * (px * ca - py * sa), y + s * (px * sa + py * ca)) for px, py in pts]
    poly(f, P, INK, fill=(150, 200, 120), thick=4, fi=fi, wob=0.8, seed=seed)
    poly(f, circle_pts(x, y, 26 * s, 16), (60, 110, 60), fill=(120, 170, 100), thick=3, fi=fi, wob=0.5, seed=seed + 1)

def question(f, x, y, size, fi, t, k=0, color=YELLOW):
    put_text(f, "?", x, y + math.sin(t * 3 + k) * 12, "anton", size, color, stroke=6, stroke_fill=INK)

def screen_box(f, x, y, w, h, fi, seed, content="blank", t=0.0):
    box(f, x - w / 2, y - h / 2, x + w / 2, y + h / 2, DARK2, INK, 7, fi, r=14, seed=seed)
    sx0, sy0, sx1, sy1 = x - w / 2 + 16, y - h / 2 + 16, x + w / 2 - 16, y + h / 2 - 16
    dark = content in ("blank_dark", "dark")
    cv2.rectangle(f, (int(sx0), int(sy0)), (int(sx1), int(sy1)), (28, 30, 40) if dark else (225, 228, 235), -1)
    if content == "molecule":
        pts = [(x - 80, y - 30), (x, y - 70), (x + 80, y - 20), (x + 30, y + 60), (x - 60, y + 50)]
        for a, b in zip(pts, pts[1:] + pts[:1]): cv2.line(f, tuple(map(int, a)), tuple(map(int, b)), INK, 5, cv2.LINE_AA)
        for i, p in enumerate(pts): cv2.circle(f, tuple(map(int, p)), 22, [RED, BLUE, LIME, YELLOW, ORANGE][i], -1, cv2.LINE_AA)
    elif content == "cross":
        cv2.rectangle(f, (int(x - 22), int(y - 70)), (int(x + 22), int(y + 70)), (220, 225, 232), -1)
    elif content == "weather":
        poly(f, circle_pts(x - 20, y, 40, 20) , (200, 205, 215), fill=(200, 205, 215), thick=0, fi=fi, wob=0.5, seed=seed + 4)
    elif content == "redchart":
        poly(f, [(sx0 + 20, sy0 + 30), (x - 40, y - 10), (x + 20, y - 20), (sx1 - 20, sy1 - 20)], RED, None, 8, fi, 1, seed + 2, closed=False)

# ------------------------------------------------------------------ dispatch
def render_doodle(img_id, t, fi):
    import doodle_scenes   # per-video file in the project folder
    night = getattr(doodle_scenes, "NIGHT", set())
    f = dark_bg() if img_id in night else paper_bg(PAPER, 5)
    f = f.copy()
    fn = doodle_scenes.DOODLES.get(img_id)
    if fn is None:
        put_text(f, img_id.upper(), W / 2, H / 2, "anton", 120, GREY)   # missing drawing: obvious in QC
    else:
        fn(f, t, fi)
    return f
