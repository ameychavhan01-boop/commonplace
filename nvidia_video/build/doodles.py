"""Code-drawn cartoon 'doodle' illustrations, used for any illustration that has no
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

# ------------------------------------------------------------------ the 51 scenes
def d_bedroom(f, t, fi):
    sun(f, 1560, 260, 80, fi, t)
    box(f, 220, 560, 1050, 760, (150, 120, 200), INK, 7, fi, r=30, seed=1)          # bed
    box(f, 200, 470, 300, 760, (120, 90, 160), INK, 7, fi, r=20, seed=2)            # headboard
    person(f, 520, 590, 1.1, (240, 200, 120), "neutral", fi, 3, arms="down")
    box(f, 1120, 600, 1330, 760, (190, 140, 100), INK, 6, fi, r=10, seed=4)          # nightstand
    phone(f, 1230, 540, 0.25, "spinner", fi, t, 5)
    clock(f, 1420, 520, 90, 7, 0, fi, t, seed=6)

def d_phone(screen, mood="neutral"):
    def fn(f, t, fi):
        phone(f, 960, CY, 1.25, screen, fi, t, 1)
        if mood != "none":
            person(f, 560, 780, 1.3, TEAL, mood, fi, 4)
    return fn

def d_laptop(screen, mood="neutral", shirt=ORANGE):
    def fn(f, t, fi):
        person(f, 520, 760, 1.2, shirt, mood, fi, 3)
        laptop(f, 1180, 700, 1.25, screen, fi, t, 6)
    return fn

def d_vanish_tower(f, t, fi):
    sun(f, 300, 220, 60, fi, t)
    skyline(f, fi, 0.5, seed=2, skip=lambda i: i == 3)
    k = clamp(t / 4.0)
    cx, base = 960, 760
    # chip tower dissolving upward into pixels
    r = np.random.default_rng(4)
    for j in range(260):
        x = cx + r.uniform(-120, 120); y = base - r.uniform(0, 560)
        rise = k * r.uniform(150, 600); dx = k * r.uniform(-200, 200)
        if r.random() > k * 1.2 or y - rise > 60:
            s_ = int(r.uniform(10, 26))
            cv2.rectangle(f, (int(x + dx), int(y - rise)), (int(x + dx) + s_, int(y - rise) + s_), LIME if j % 3 else YELLOW, -1)
    glow(f, cx, base - 300, 400, LIME, 0.25 * (1 - k))
    for i in range(4): person(f, 700 + i * 170, 900, 0.55, [TEAL, ORANGE, BLUE, RED][i], "shock", fi, 10 + i)

def d_title_bg(f, t, fi):
    glow(f, 960, 540, 800, RED, 0.25)
    chip(f, 960, 540, 260, fi, 1.0, seed=3)
    r = np.random.default_rng(7)
    for k in range(9):
        x, y = 960, 540; a = r.uniform(0, 2 * math.pi); pts = [(x, y)]
        for s_ in range(7): a += r.uniform(-0.5, 0.5); x += math.cos(a) * 55; y += math.sin(a) * 55; pts.append((x, y))
        poly(f, pts, (255, 235, 190), None, 7, fi, 0.6, k, closed=False)

def d_chef(f, t, fi):
    box(f, 600, 560, 1320, 760, (200, 170, 140), INK, 7, fi, r=12, seed=1)          # counter
    person(f, 960, 560, 1.2, WHITE, "happy", fi, 2)
    poly(f, [(915, 330), (1005, 330), (1020, 250), (960, 220), (900, 250)], INK, fill=WHITE, thick=5, fi=fi, wob=1, seed=3)  # chef hat
    poly(f, circle_pts(1180, 540, 60, 30, 0, 180), INK, fill=(90, 95, 110), thick=6, fi=fi, wob=1, seed=4)   # pan
    for k in range(3):
        ph = (t * 0.7 + k / 3) % 1
        poly(f, [(1150 + k * 30, 470 - ph * 120), (1160 + k * 30, 440 - ph * 120)], (180, 180, 185), None, 5, fi, 1, 10 + k, closed=False)

def d_cooks(f, t, fi):
    for r_ in range(4):
        for c in range(11):
            x = 180 + c * 156; y = 330 + r_ * 135
            bob = math.sin(t * 10 + r_ + c * 0.7) * 6
            person(f, x, y + bob, 0.42, [TEAL, ORANGE, BLUE, RED][(r_ + c) % 4], "happy", fi, r_ * 20 + c)

def d_racks_lit(f, t, fi):
    racks_scene(f, t, fi, lambda i, t: 1.0)

def d_racks_dark(f, t, fi):
    racks_scene(f, t, fi, lambda i, t: clamp(1 - (t * 0.7 - (5 - i) * 0.18)))
    person(f, 960, 900, 0.7, ORANGE, "shock", fi, 40)

def d_racks_back(f, t, fi):
    racks_scene(f, t, fi, lambda i, t: clamp(t * 0.4 - i * 0.05))

def d_globe_links(f, t, fi):
    chip(f, 960, CY, 120, fi, 1.0, seed=2)
    for k in range(10):
        a = 2 * math.pi * k / 10 + t * 0.2
        x, y = 960 + 520 * math.cos(a), CY + 300 * math.sin(a)
        cv2.line(f, (int(x), int(y)), (960, CY), (120, 180, 120), 3, cv2.LINE_AA)
        laptop(f, x, y + 50, 0.28, "code", fi, t, 10 + k)

def d_dc_building(f, t, fi):
    moon(f, 1600, 200, 60, fi)
    box(f, 380, 380, 1540, 760, (90, 100, 125), INK, 7, fi, r=10, seed=1)
    for k in range(10):
        cv2.rectangle(f, (430 + k * 108, 440), (500 + k * 108, 470), LIME if (fi // 8 + k) % 3 else (60, 70, 60), -1)
    for k in range(3):
        box(f, 470 + k * 360, 300, 600 + k * 360, 380, (130, 140, 160), INK, 5, fi, r=6, seed=10 + k, shadow=False)
    cv2.line(f, (0, 760), (W, 760), INK, 6, cv2.LINE_AA)

def d_midnight(f, t, fi):
    moon(f, 1600, 220, 80, fi)
    skyline(f, fi, 0.25, seed=5)
    box(f, 860, 300, 1060, 760, (120, 110, 140), INK, 7, fi, r=6, seed=9)
    clock(f, 960, 400, 80, 12, 0, fi, 0, night=True, seed=7)

def d_people_spinner(f, t, fi):
    for i, sh in enumerate([TEAL, ORANGE, BLUE, RED]):
        x = 330 + i * 420
        person(f, x, 780, 0.9, sh, "neutral", fi, i * 7)
        phone(f, x + 80, 560, 0.3, "spinner", fi, t + i, i)
        question(f, x - 60, 300, 110, fi, t, i)

def d_speaker(f, t, fi):
    box(f, 380, 640, 1540, 760, (200, 170, 140), INK, 7, fi, r=10, seed=1)
    box(f, 1000, 420, 1160, 640, (60, 64, 80), INK, 7, fi, r=40, seed=2)
    cv2.ellipse(f, (1080, 430), (70, 16), 0, 0, 360, (40, 44, 56), 6, cv2.LINE_AA)
    person(f, 700, 640, 1.0, ORANGE, "neutral", fi, 3)
    for k in range(3): question(f, 900 + k * 70, 330 - k * 30, 70, fi, t, k)

def d_one_lit(f, t, fi):
    moon(f, 300, 200, 50, fi)
    for i in range(6):
        x = 120 + i * 300; lit = i == 5
        box(f, x, 520, x + 240, 760, (150, 120, 200) if lit else (70, 74, 90), INK, 6, fi, r=8, seed=i, shadow=False)
        if lit: glow(f, x + 120, 620, 300, (150, 200, 255), 0.5)
    cv2.line(f, (0, 760), (W, 760), INK, 6, cv2.LINE_AA)

def d_screen_person(content, mood="neutral", shirt=WHITE):
    def fn(f, t, fi):
        screen_box(f, 1180, CY - 20, 640, 420, fi, 2, content, t)
        person(f, 560, 800, 1.2, shirt, mood, fi, 5)
        question(f, 560, 250, 120, fi, t)
    return fn

def d_bank(f, t, fi):
    for r_ in range(2):
        for c in range(4):
            screen_box(f, 420 + c * 360, 300 + r_ * 260, 320, 210, fi, r_ * 4 + c, "blank_dark")
    for i in range(3): person(f, 620 + i * 340, 900, 0.65, [BLUE, TEAL, ORANGE][i], "shock", fi, 30 + i)

def d_trading(f, t, fi):
    box(f, 260, 140, 1660, 470, (30, 34, 46), INK, 7, fi, r=10, seed=1)
    for k in range(5):
        x = 400 + k * 280
        arrow(f, x, 220, x + 60, 400, RED, 12, 34, fi, 10 + k)
    for i in range(6):
        person(f, 260 + i * 280, 900 + (i % 2) * 20, 0.75, [BLUE, TEAL, ORANGE, RED, YELLOW, LIME][i], "shock", fi, 40 + i, arms="up", t=t + i)

def d_money_fly(f, t, fi):
    skyline(f, fi, 0.3, seed=8)
    r = np.random.default_rng(11)
    for k in range(18):
        x0, y0 = r.uniform(200, 1700), r.uniform(450, 750)
        ph = (t * 0.25 + k / 18) % 1
        money(f, x0 + ph * 500, y0 - ph * 650, 0.8, fi, k, ang=ph * 4 + k, alpha=1 - ph)

def d_dominoes(f, t, fi):
    cv2.line(f, (0, 780), (W, 780), INK, 6, cv2.LINE_AA)
    for k in range(11):
        x = 120 + k * 165
        fall = clamp(t * 2.2 - k * 0.35)
        ang = fall * 1.25
        w_, h_ = 60, 300
        pts = [(0, 0), (w_, 0), (w_, -h_), (0, -h_)]
        ca, sa = math.cos(ang), math.sin(ang)
        P = [(x + px * ca - py * sa, 780 + px * sa + py * ca) for px, py in pts]
        poly(f, P, INK, fill=[(240, 235, 220), (220, 200, 180)][k % 2], thick=6, fi=fi, wob=1, seed=k)

def d_crowd_q(f, t, fi, panic=False):
    box(f, 360, 120, 1560, 430, (40, 44, 58), INK, 7, fi, r=10, seed=2)
    for k in range(6): question(f, 480 + k * 190, 270, 150, fi, t, k)
    for i in range(7):
        person(f, 240 + i * 240, 930, 0.7, [BLUE, TEAL, ORANGE, RED, YELLOW, LIME, BLUE][i], "shock" if panic else "neutral", fi, 50 + i)

def d_boardroom(f, t, fi):
    box(f, 360, 600, 1560, 700, (150, 110, 80), INK, 7, fi, r=20, seed=1)
    for i in range(5):
        person(f, 520 + i * 220, 620, 0.8, [DARK2, BLUE, DARK2, TEAL, DARK2][i], "shock", fi, 60 + i, arms="up" if i % 2 else "down", t=t + i)
    for k in range(4):
        x = 700 + k * 200 + math.sin(t * 3 + k) * 20; y = 260 + (t * 120 + k * 60) % 200
        cv2.rectangle(f, (int(x), int(y)), (int(x + 70), int(y + 90)), WHITE, -1); cv2.rectangle(f, (int(x), int(y)), (int(x + 70), int(y + 90)), INK, 3)

def d_dock(f, t, fi):
    box(f, 200, 160, 1720, 760, (150, 140, 130), INK, 7, fi, r=6, seed=1)
    for k in range(3):
        box(f, 300 + k * 480, 260, 680 + k * 480, 760, (40, 42, 52), INK, 6, fi, r=4, seed=2 + k, shadow=False)
    cv2.rectangle(f, (200, 700), (1720, 740), (90, 95, 110), -1)
    person(f, 1500, 900, 0.8, ORANGE, "sad", fi, 9)

def d_factory_trucks(f, t, fi):
    factory(f, 300, 760, 1.4, fi, t, 1)
    for k in range(4):
        x = 1260 + k * 150
        box(f, x, 640, x + 130, 740, (200, 120, 90), INK, 5, fi, r=10, seed=20 + k, shadow=False)
        for wx in (x + 28, x + 100): cv2.circle(f, (wx, 750), 18, INK, -1, cv2.LINE_AA)
    box(f, 1300, 200, 1700, 480, WHITE, INK, 6, fi, r=10, seed=30)   # booked calendar
    for r_ in range(4):
        for c in range(6):
            cv2.line(f, (1330 + c * 62, 250 + r_ * 55), (1370 + c * 62, 290 + r_ * 55), RED, 6, cv2.LINE_AA)
            cv2.line(f, (1370 + c * 62, 250 + r_ * 55), (1330 + c * 62, 290 + r_ * 55), RED, 6, cv2.LINE_AA)

def d_library(f, t, fi):
    for c in range(7):
        x = 150 + c * 240
        box(f, x, 120, x + 200, 760, (150, 100, 70), INK, 6, fi, r=4, seed=c, shadow=False)
        for r_ in range(6):
            for b in range(5):
                cv2.rectangle(f, (x + 12 + b * 36, 140 + r_ * 100), (x + 40 + b * 36, 220 + r_ * 100),
                              [RED, TEAL, YELLOW, BLUE, ORANGE][(b + r_ + c) % 5], -1)
    box(f, 760, 700, 1160, 780, (200, 160, 110), INK, 6, fi, r=6, seed=40)
    person(f, 960, 720, 0.8, BLUE, "sad", fi, 41)

def d_puzzle(f, t, fi):
    pieces = [(700, 300), (860, 300), (1020, 300), (1180, 300), (700, 460), (1180, 460), (860, 620), (1020, 620)]
    for i, (x, y) in enumerate(pieces):
        box(f, x - 75, y - 75, x + 75, y + 75, [LIME, BLUE, ORANGE, TEAL][i % 4], INK, 6, fi, r=14, seed=i)
    for (x, y) in [(860, 460), (1020, 460), (700, 620), (1180, 620)]:
        poly(f, rect_pts(x - 75, y - 75, x + 75, y + 75), (160, 150, 140), None, 4, fi, 2, int(x + y))
    for i, x in enumerate((260, 1660)): person(f, x, 860, 0.9, [RED, BLUE][i], "neutral", fi, 70 + i)

def d_auction(f, t, fi):
    box(f, 860, 560, 1060, 760, (150, 40, 60), INK, 6, fi, r=10, seed=1)
    chip(f, 960, 470, 80, fi, 1.0, seed=2)
    for i in range(6):
        x = 260 + i * 280 if i < 3 else 1100 + (i - 3) * 230
        person(f, x, 960, 0.7, [DARK2, BLUE, DARK2, TEAL, DARK2, ORANGE][i], "shock", fi, 80 + i, arms="up", t=t + i * 0.7)
    arrow(f, 1350, 520, 1450, 160, RED, 14, 40, fi, 90)

def d_office_chips(f, t, fi):
    moon(f, 1650, 160, 50, fi)
    for i in range(3):
        x = 420 + i * 540
        laptop(f, x, 640, 0.7, "chip", fi, t, i)
        person(f, x - 150, 860, 0.7, [TEAL, ORANGE, BLUE][i], "happy", fi, 20 + i)

def d_engineer_shock(f, t, fi):
    sun(f, 1600, 230, 60, fi, t)
    person(f, 760, 860, 1.4, (120, 160, 200), "shock", fi, 3, skin=SKIN2)
    phone(f, 1200, 520, 0.8, "alert", fi, t, 5)

def d_startup_dark(f, t, fi):
    rack(f, 1380, 260, 220, 520, 0.0, fi, 3)
    box(f, 300, 640, 1150, 720, (190, 150, 110), INK, 6, fi, r=10, seed=1)
    for i in range(3): person(f, 470 + i * 260, 660, 0.8, [ORANGE, TEAL, RED][i], "sad", fi, 10 + i, skin=SKIN2)

def d_construction(f, t, fi):
    sun(f, 300, 200, 60, fi, t)
    cv2.line(f, (0, 780), (W, 780), INK, 6, cv2.LINE_AA)
    for k in range(4):   # building frame
        for j in range(3):
            poly(f, rect_pts(700 + k * 160, 780 - (j + 1) * 140, 860 + k * 160, 780 - j * 140, 3), INK, None, 5, fi, 1, k * 10 + j)
    for c, x in enumerate((420, 1500)):   # cranes
        poly(f, [(x, 780), (x, 220)], (220, 170, 40), None, 16, fi, 1, 50 + c, closed=False)
        poly(f, [(x - 120, 240), (x + 380 * (1 if c == 0 else -1), 240)], (220, 170, 40), None, 12, fi, 1, 60 + c, closed=False)

def d_it_pause(f, t, fi):
    screen_box(f, 1250, 420, 640, 400, fi, 2, "blank")
    poly(f, circle_pts(1250, 420, 110, 36), INK, fill=YELLOW, thick=6, fi=fi, wob=1, seed=9)
    for dx in (-30, 30): cv2.rectangle(f, (1250 + dx - 14, 360), (1250 + dx + 14, 480), INK, -1)
    for i in range(3): person(f, 300 + i * 220, 900, 0.75, [TEAL, ORANGE, BLUE][i], "neutral", fi, 10 + i, skin=SKIN2)

def d_train_gamer(f, t, fi):
    box(f, 100, 200, 1820, 820, (120, 160, 170), INK, 8, fi, r=30, seed=1)
    for k in range(4): box(f, 200 + k * 420, 270, 520 + k * 420, 480, (210, 235, 245), INK, 6, fi, r=10, seed=2 + k, shadow=False)
    person(f, 780, 900, 1.1, SAFFRON, "happy", fi, 7, skin=SKIN2)
    phone(f, 1100, 640, 0.55, "game", fi, t, 8)

def d_gpu_price(f, t, fi):
    box(f, 1000, 380, 1600, 640, (60, 64, 80), INK, 7, fi, r=16, seed=1)
    for k in range(2): poly(f, circle_pts(1160 + k * 260, 510, 90, 30), INK, fill=(40, 44, 56), thick=5, fi=fi, wob=1, seed=2 + k)
    box(f, 1420, 160, 1720, 330, WHITE, INK, 6, fi, r=10, seed=5)
    put_text(f, "$$$$", 1570, 245, "anton", 90, RED)
    person(f, 520, 880, 1.2, (60, 60, 70), "shock", fi, 8)

def d_market_tv(f, t, fi):
    screen_box(f, 960, 360, 560, 360, fi, 2, "redchart")
    for i in range(5): person(f, 360 + i * 300, 960, 0.75, [SAFFRON, TEAL, ORANGE, BLUE, RED][i], "sad", fi, 10 + i, skin=SKIN2)

def d_sunrise_coders(f, t, fi):
    sun(f, 1650, 220, 90, fi, t)
    for i in range(3):
        x = 420 + i * 520
        laptop(f, x, 650, 0.7, "code", fi, t, i)
        person(f, x - 150, 870, 0.7, [SAFFRON, TEAL, ORANGE][i], "happy", fi, 20 + i, skin=SKIN2)

def d_rebuild_sky(f, t, fi):
    sun(f, 960, 640, 120, fi, t)
    skyline(f, fi, 0.8, seed=12)
    for x in (520, 1400):
        poly(f, [(x, 760), (x, 300)], (220, 170, 40), None, 14, fi, 1, x, closed=False)
        poly(f, [(x - 100, 320), (x + 260, 320)], (220, 170, 40), None, 10, fi, 1, x + 1, closed=False)

def d_two_factories(f, t, fi):
    factory(f, 140, 760, 1.2, fi, t, 1, color=(190, 120, 100))
    factory(f, 1060, 760, 1.2, fi, t + 0.5, 2, color=(110, 140, 180))

def d_watering(f, t, fi):
    factory(f, 700, 820, 1.0, fi, t, 1)
    box(f, 520, 120, 860, 300, (130, 160, 190), INK, 7, fi, r=40, seed=3)
    poly(f, [(860, 200), (1060, 150), (1060, 190), (860, 260)], INK, fill=(130, 160, 190), thick=6, fi=fi, wob=1, seed=4)
    for k in range(10):
        ph = (t * 0.8 + k / 10) % 1
        x = 1060 + (k % 3) * 20 - 30; y = 190 + ph * 330
        poly(f, circle_pts(x, y, 16, 14), INK, fill=YELLOW, thick=3, fi=fi, wob=0.5, seed=20 + k)

def d_talent_moves(f, t, fi):
    box(f, 80, 260, 520, 780, (110, 110, 120), INK, 7, fi, r=6, seed=1)
    for i, (x, c) in enumerate(((1200, (110, 140, 180)), (1450, (190, 120, 100)), (1700, (110, 160, 120)))):
        building(f, x - 100, 780, 200, 420 - i * 40, c, fi, 10 + i, lit=0.8)
    for k in range(4):
        ph = clamp(t * 0.25 - k * 0.12)
        person(f, lerp(560, 1150 + (k % 3) * 250, ph), 880, 0.55, [TEAL, ORANGE, BLUE, RED][k], "happy", fi, 30 + k)
    cv2.line(f, (0, 780), (W, 780), INK, 6, cv2.LINE_AA)

def d_six_towers(f, t, fi):
    sun(f, 300, 200, 60, fi, t)
    cols = [LIME, BLUE, ORANGE, TEAL, YELLOW, RED]
    for i in range(6):
        x = 260 + i * 240
        building(f, x, 780, 180, 380 + (i % 3) * 40, cols[i], fi, i, lit=0.7, win_col=WHITE)
        if i < 5: cv2.line(f, (x + 180, 600), (x + 240, 600), INK, 8, cv2.LINE_AA)
    cv2.line(f, (0, 780), (W, 780), INK, 6, cv2.LINE_AA)

def d_bridge(f, t, fi):
    cv2.rectangle(f, (0, 640), (W, H), (120, 170, 200), -1)
    skyline(f, fi, 0.6, base=640, seed=20, skip=lambda i: i < 3)
    box(f, 0, 560, 420, 700, (150, 170, 120), INK, 6, fi, r=6, seed=1, shadow=False)
    poly(f, [(420, 600), (1150, 600)], INK, None, 14, fi, 1, 2, closed=False)
    for k in range(5): poly(f, [(500 + k * 150, 600), (500 + k * 150, 700)], INK, None, 10, fi, 1, 3 + k, closed=False)
    for k in range(7):
        x = 440 + ((t * 80 + k * 100) % 700)
        box(f, x, 560, x + 70, 598, [RED, YELLOW, BLUE, LIME][k % 4], INK, 3, fi, r=8, seed=20 + k, shadow=False)
    crack = clamp(t * 0.4)
    if crack > 0.1:
        poly(f, [(790, 590), (800, 610), (785, 630), (805, 660)][:max(2, int(4 * crack))], RED, None, 7, fi, 1, 40, closed=False)

def d_blueprint(f, t, fi):
    box(f, 420, 200, 1500, 760, (40, 90, 150), INK, 8, fi, r=8, seed=1)
    for k in range(8):
        cv2.line(f, (440, 220 + k * 70), (1480, 220 + k * 70), (70, 120, 180), 2)
    chip(f, 960, 480, 160, fi, 0.4, color=(150, 200, 255), seed=2)
    person(f, 1680, 900, 0.9, ORANGE, "happy", fi, 3)

def d_fab_sea(f, t, fi):
    cv2.rectangle(f, (0, 700), (W, H), (90, 150, 190), -1)
    factory(f, 900, 700, 1.3, fi, t, 1, color=(170, 170, 180))
    for k in range(2):
        x = 200 + ((t * 60 + k * 500) % 900)
        poly(f, [(x, 800), (x + 260, 800), (x + 220, 860), (x + 40, 860)], INK, fill=(180, 60, 50), thick=5, fi=fi, wob=1, seed=10 + k)
        for c in range(3): box(f, x + 40 + c * 60, 750, x + 90 + c * 60, 800, [YELLOW, LIME, ORANGE][c], INK, 3, fi, r=4, seed=20 + c, shadow=False)

def d_globe_q(f, t, fi):
    poly(f, circle_pts(1100, CY, 230, 60), INK, fill=(110, 160, 200), thick=7, fi=fi, wob=1.2, seed=1)
    poly(f, [(1000, 330), (1080, 300), (1140, 380), (1060, 450), (990, 420)], INK, fill=(140, 190, 110), thick=4, fi=fi, wob=1, seed=2)
    poly(f, [(1130, 520), (1220, 500), (1250, 600), (1150, 640)], INK, fill=(140, 190, 110), thick=4, fi=fi, wob=1, seed=3)
    for k in range(6):
        a = t * 0.6 + k * math.pi / 3
        building(f, 1100 + 330 * math.cos(a) - 30, CY + 200 * math.sin(a) + 40, 60, 90, [RED, YELLOW, LIME, ORANGE, BLUE, TEAL][k], fi, k, windows=False)
    person(f, 520, 860, 1.2, TEAL, "neutral", fi, 9)
    question(f, 520, 240, 160, fi, t)

def d_desk(f, t, fi):
    glow(f, 960, 400, 500, YELLOW, 0.2)
    box(f, 360, 820, 1560, 900, (150, 110, 80), INK, 7, fi, r=10, seed=1)
    poly(f, circle_pts(1300, 740, 70, 40), INK, fill=(110, 160, 200), thick=5, fi=fi, wob=1, seed=2)

DOODLES = {
    "img01": d_bedroom, "img02": d_phone("spinner", "none"), "img03": d_laptop("spinner", "neutral"),
    "img04": d_phone("redchart", "shock"), "img05": d_vanish_tower, "img06": d_title_bg, "img07": d_chef,
    "img08": d_cooks, "img09": d_racks_lit, "img10": d_globe_links, "img11": d_dc_building, "img12": d_midnight,
    "img13": d_racks_dark, "img14": d_people_spinner, "img15": d_laptop("glitch", "shock", BLUE), "img16": d_speaker,
    "img17": d_one_lit, "img18": d_screen_person("cross", "neutral", WHITE), "img19": d_bank, "img20": d_screen_person("blank", "neutral", BLUE),
    "img21": d_screen_person("molecule", "neutral", WHITE), "img22": d_trading, "img23": d_phone("pie", "shock"),
    "img24": d_money_fly, "img25": d_dominoes, "img26": lambda f, t, fi: d_crowd_q(f, t, fi, False),
    "img27": d_boardroom, "img28": d_dock, "img29": d_factory_trucks, "img30": d_library, "img31": d_puzzle,
    "img32": d_auction, "img33": d_office_chips, "img34": d_engineer_shock, "img35": d_startup_dark,
    "img36": d_construction, "img37": d_it_pause, "img38": d_train_gamer, "img39": d_gpu_price, "img40": d_market_tv,
    "img41": d_sunrise_coders, "img42": d_rebuild_sky, "img43": d_two_factories, "img44": d_watering,
    "img45": d_talent_moves, "img46": d_six_towers, "img47": d_bridge, "img48": d_blueprint, "img49": d_fab_sea,
    "img50": d_globe_q, "img51": d_desk,
}
NIGHT = {"img06", "img11", "img12", "img13", "img17", "img19", "img33", "img35", "img51", "img09", "img10"}

def render_doodle(img_id, t, fi):
    f = dark_bg() if img_id in NIGHT else paper_bg(PAPER, 5)
    f = f.copy()
    DOODLES[img_id](f, t, fi)
    return f
