"""Drawing primitives for the motion-graphics renderer (1920x1080, 30 fps).

Look: warm cream paper + dark navy ink, slightly "boiling" hand-drawn lines,
bold condensed numbers (Anton), clean labels (Poppins), handwritten notes
(Patrick Hand). All fonts are SIL Open Font Licence (commercial use OK).
"""
import functools, math
from pathlib import Path
import numpy as np
import cv2
from PIL import Image, ImageDraw, ImageFont

W, H, FPS = 1920, 1080, 30
SCRATCH = Path("/tmp/claude-0/-home-user-commonplace/b86ce5d7-0153-5b98-a71a-4c4535dda987/scratchpad")
FONTS = SCRATCH / "fonts"

# ------------------------------------------------------------------ palette (RGB)
PAPER = (244, 236, 222)
PAPER2 = (236, 225, 206)
INK = (30, 36, 51)
DARK = (21, 25, 37)
DARK2 = (34, 40, 58)
RED = (230, 57, 70)
YELLOW = (255, 200, 61)
LIME = (132, 204, 72)
TEAL = (42, 157, 143)
ORANGE = (244, 150, 80)
BLUE = (69, 123, 157)
WHITE = (255, 255, 255)
GREY = (140, 140, 150)
SAFFRON = (255, 153, 51)
INGREEN = (19, 136, 8)

# ------------------------------------------------------------------ easing
def clamp(x, a=0.0, b=1.0): return max(a, min(b, x))
def ease_out(x): x = clamp(x); return 1 - (1 - x) ** 3
def ease_in_out(x): x = clamp(x); return 3 * x * x - 2 * x * x * x
def ease_back(x, s=1.70158):
    x = clamp(x); x -= 1
    return x * x * ((s + 1) * x + s) + 1
def lerp(a, b, t): return a + (b - a) * t
def prog(t, start, dur): return clamp((t - start) / dur) if dur > 0 else float(t >= start)

# ------------------------------------------------------------------ fonts / text
@functools.lru_cache(None)
def font(name, size):
    files = {"anton": "Anton-Regular.ttf", "black": "Poppins-Black.ttf", "xbold": "Poppins-ExtraBold.ttf",
             "bold": "Poppins-Bold.ttf", "semi": "Poppins-SemiBold.ttf", "hand": "PatrickHand-Regular.ttf"}
    return ImageFont.truetype(str(FONTS / files[name]), size)

@functools.lru_cache(maxsize=4096)
def text_layer(text, fname="anton", size=120, fill=WHITE, stroke=0, stroke_fill=INK, shadow=0,
               spacing=0, align="center", line_gap=1.05):
    """Render text to an RGBA numpy array (premultiplied-free)."""
    f = font(fname, size)
    lines = text.split("\n")
    pad = stroke + shadow + 8
    widths, heights = [], []
    for ln in lines:
        bb = f.getbbox(ln or " ", stroke_width=stroke)
        widths.append(bb[2] - bb[0] + spacing * max(0, len(ln) - 1)); heights.append(size)
    lh = int(size * line_gap * (1.25 if fname in ("semi", "bold", "xbold", "black", "hand") else 1.0))
    w = max(widths) + pad * 2; h = lh * len(lines) + pad * 2 + int(size * 0.25)
    img = Image.new("RGBA", (w, h), (0, 0, 0, 0)); d = ImageDraw.Draw(img)
    for i, ln in enumerate(lines):
        x = pad + {"center": (max(widths) - widths[i]) // 2, "left": 0, "right": max(widths) - widths[i]}[align]
        y = pad + i * lh
        if shadow:
            d.text((x + shadow, y + shadow), ln, font=f, fill=(0, 0, 0, 110), stroke_width=stroke, stroke_fill=(0, 0, 0, 110))
        if spacing:
            cx = x
            for ch in ln:
                d.text((cx, y), ch, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
                cx += f.getlength(ch) + spacing
        else:
            d.text((x, y), ln, font=f, fill=fill + (255,), stroke_width=stroke, stroke_fill=stroke_fill + (255,))
    a = np.array(img)
    ys, xs = np.where(a[:, :, 3] > 0)
    if len(ys): a = a[max(0, ys.min() - 4):ys.max() + 5, max(0, xs.min() - 4):xs.max() + 5]
    return a

def text_size(text, fname, size, stroke=0):
    a = text_layer(text, fname, size, WHITE, stroke)
    return a.shape[1], a.shape[0]

# ------------------------------------------------------------------ compositing
def blit(frame, layer, cx, cy, scale=1.0, alpha=1.0, rot=0.0, anchor="center"):
    """Alpha-composite RGBA `layer` onto RGB uint8 `frame` centred at (cx, cy)."""
    if alpha <= 0.003 or scale <= 0.01: return
    L = layer
    if abs(scale - 1) > 1e-3 or abs(rot) > 1e-3:
        h, w = L.shape[:2]
        M = cv2.getRotationMatrix2D((w / 2, h / 2), rot, scale)
        cos, sin = abs(M[0, 0]), abs(M[0, 1])
        nw, nh = int(h * sin + w * cos) + 2, int(h * cos + w * sin) + 2
        M[0, 2] += nw / 2 - w / 2; M[1, 2] += nh / 2 - h / 2
        L = cv2.warpAffine(L, M, (nw, nh), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_CONSTANT, borderValue=(0, 0, 0, 0))
    h, w = L.shape[:2]
    if anchor == "center": x0, y0 = int(round(cx - w / 2)), int(round(cy - h / 2))
    elif anchor == "left": x0, y0 = int(round(cx)), int(round(cy - h / 2))
    elif anchor == "right": x0, y0 = int(round(cx - w)), int(round(cy - h / 2))
    else: x0, y0 = int(cx), int(cy)
    fx0, fy0, fx1, fy1 = max(0, x0), max(0, y0), min(W, x0 + w), min(H, y0 + h)
    if fx1 <= fx0 or fy1 <= fy0: return
    sub = L[fy0 - y0:fy1 - y0, fx0 - x0:fx1 - x0]
    a = sub[:, :, 3:4].astype(np.float32) / 255.0 * alpha
    dst = frame[fy0:fy1, fx0:fx1].astype(np.float32)
    frame[fy0:fy1, fx0:fx1] = (sub[:, :, :3] * a + dst * (1 - a)).astype(np.uint8)

def put_text(frame, text, cx, cy, fname="anton", size=120, fill=WHITE, stroke=0, stroke_fill=INK,
             shadow=0, scale=1.0, alpha=1.0, rot=0.0, anchor="center", spacing=0, align="center"):
    L = text_layer(text, fname, size, tuple(fill), stroke, tuple(stroke_fill), shadow, spacing, align)
    blit(frame, L, cx, cy, scale, alpha, rot, anchor)
    return L.shape[1] * scale, L.shape[0] * scale

def pop_scale(t, start, dur=0.35):
    p = prog(t, start, dur)
    return 0.0 if t < start else ease_back(p, 2.2)

# ------------------------------------------------------------------ backgrounds
@functools.lru_cache(None)
def _noise(seed, sigma, amp):
    r = np.random.default_rng(seed)
    n = r.standard_normal((H // 4, W // 4)).astype(np.float32)
    n = cv2.GaussianBlur(n, (0, 0), sigma)
    n = cv2.resize(n, (W, H), interpolation=cv2.INTER_CUBIC)
    return n / (np.abs(n).max() + 1e-6) * amp

@functools.lru_cache(None)
def vignette_mask(strength=0.35):
    y, x = np.mgrid[0:H, 0:W].astype(np.float32)
    d = np.sqrt(((x - W / 2) / (W / 2)) ** 2 + ((y - H / 2) / (H / 2)) ** 2)
    return (1 - strength * np.clip(d - 0.35, 0, 1) ** 1.6)[:, :, None]

@functools.lru_cache(None)
def paper_bg(color=PAPER, seed=1, vig=0.3):
    base = np.ones((H, W, 3), np.float32) * np.array(color, np.float32)
    base += _noise(seed, 6, 9)[:, :, None] + _noise(seed + 5, 1.2, 4)[:, :, None]
    base *= vignette_mask(vig)
    return np.clip(base, 0, 255).astype(np.uint8)

@functools.lru_cache(None)
def dark_bg(color=DARK, seed=3, vig=0.45):
    return paper_bg(color, seed, vig)

def bg(kind="paper"):
    return {"paper": paper_bg, "dark": dark_bg}[kind]().copy() if kind in ("paper", "dark") else \
        paper_bg(kind).copy()

@functools.lru_cache(None)
def grain(i):
    r = np.random.default_rng(100 + i)
    return (r.standard_normal((H, W, 1)) * 3.2).astype(np.float32)

def add_grain(frame, fi):
    return np.clip(frame.astype(np.float32) + grain(fi % 4), 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ hand-drawn shapes
def wobble(pts, fi, amp=1.6, seed=0):
    """Jitter points, re-seeded every 3 frames, for a 'boiling' hand-drawn line."""
    pts = np.asarray(pts, np.float32)
    r = np.random.default_rng(seed * 7919 + fi // 3)
    return pts + r.uniform(-amp, amp, pts.shape).astype(np.float32)

def poly(frame, pts, color, fill=None, thick=5, fi=0, wob=1.5, seed=0, closed=True):
    p = wobble(pts, fi, wob, seed) if wob else np.asarray(pts, np.float32)
    ip = np.round(p * 4).astype(np.int32)
    if fill is not None:
        cv2.fillPoly(frame, [ip], tuple(int(c) for c in fill), cv2.LINE_AA, shift=2)
    if thick:
        cv2.polylines(frame, [ip], closed, tuple(int(c) for c in color), thick, cv2.LINE_AA, shift=2)

def rect_pts(x0, y0, x1, y1, n=6):
    top = [(lerp(x0, x1, i / n), y0) for i in range(n)]
    right = [(x1, lerp(y0, y1, i / n)) for i in range(n)]
    bot = [(lerp(x1, x0, i / n), y1) for i in range(n)]
    left = [(x0, lerp(y1, y0, i / n)) for i in range(n)]
    return top + right + bot + left

def rrect_pts(x0, y0, x1, y1, r=24, n=6):
    pts = []
    for cx, cy, a0 in ((x1 - r, y0 + r, -90), (x1 - r, y1 - r, 0), (x0 + r, y1 - r, 90), (x0 + r, y0 + r, 180)):
        for k in range(n + 1):
            a = math.radians(a0 + 90 * k / n); pts.append((cx + r * math.cos(a), cy + r * math.sin(a)))
    return pts

def box(frame, x0, y0, x1, y1, fill, color=INK, thick=5, fi=0, r=22, seed=0, wob=1.4, shadow=True):
    if shadow:
        poly(frame, rrect_pts(x0 + 10, y0 + 12, x1 + 10, y1 + 12, r), None, fill=(0, 0, 0) if sum(fill) < 200 else
             tuple(int(c * 0.78) for c in PAPER), thick=0, fi=fi, wob=0, seed=seed)
    poly(frame, rrect_pts(x0, y0, x1, y1, r), color, fill=fill, thick=thick, fi=fi, wob=wob, seed=seed)

def circle_pts(cx, cy, r, n=48, a0=0, a1=360):
    return [(cx + r * math.cos(math.radians(lerp(a0, a1, i / n))), cy + r * math.sin(math.radians(lerp(a0, a1, i / n))))
            for i in range(n + 1)]

def arrow(frame, x0, y0, x1, y1, color=INK, thick=7, head=26, fi=0, seed=0, p=1.0):
    x1p, y1p = lerp(x0, x1, p), lerp(y0, y1, p)
    pts = [(lerp(x0, x1p, i / 10), lerp(y0, y1p, i / 10)) for i in range(11)]
    poly(frame, pts, color, None, thick, fi, 1.2, seed, closed=False)
    if p > 0.95:
        ang = math.atan2(y1 - y0, x1 - x0)
        a1 = (x1 - head * math.cos(ang - 0.45), y1 - head * math.sin(ang - 0.45))
        a2 = (x1 - head * math.cos(ang + 0.45), y1 - head * math.sin(ang + 0.45))
        poly(frame, [a1, (x1, y1), a2], color, None, thick, fi, 1.0, seed + 1, closed=False)

def glow(frame, cx, cy, r, color, strength=0.6):
    x0, y0, x1, y1 = int(max(0, cx - r)), int(max(0, cy - r)), int(min(W, cx + r)), int(min(H, cy + r))
    if x1 <= x0 or y1 <= y0: return
    y, x = np.mgrid[y0:y1, x0:x1].astype(np.float32)
    d = np.sqrt((x - cx) ** 2 + (y - cy) ** 2) / r
    a = (np.clip(1 - d, 0, 1) ** 2 * strength)[:, :, None]
    sub = frame[y0:y1, x0:x1].astype(np.float32)
    frame[y0:y1, x0:x1] = np.clip(sub + np.array(color, np.float32) * a, 0, 255).astype(np.uint8)

# ------------------------------------------------------------------ chip icon
def chip(frame, cx, cy, s, fi=0, lit=1.0, color=LIME, seed=0, label=None):
    """Stylised GPU chip (generic, no brand mark). s = half-size in px."""
    if lit > 0.02: glow(frame, cx, cy, s * 2.4, color, 0.55 * lit)
    pins = int(s / 9)
    for side in range(4):
        for k in range(pins):
            off = lerp(-s * 0.75, s * 0.75, k / max(1, pins - 1))
            if side == 0: p = [(cx + off, cy - s), (cx + off, cy - s * 1.25)]
            elif side == 1: p = [(cx + off, cy + s), (cx + off, cy + s * 1.25)]
            elif side == 2: p = [(cx - s, cy + off), (cx - s * 1.25, cy + off)]
            else: p = [(cx + s, cy + off), (cx + s * 1.25, cy + off)]
            poly(frame, p, (180, 180, 170) if lit < 0.5 else (210, 210, 200), None, max(2, int(s / 40)), fi, 0.8, seed + side * 50 + k, closed=False)
    body = tuple(int(lerp(c1, c2, lit)) for c1, c2 in zip((60, 62, 70), (45, 52, 66)))
    box(frame, cx - s, cy - s, cx + s, cy + s, body, INK, max(3, int(s / 22)), fi, r=s * 0.12, seed=seed, shadow=False)
    core = tuple(int(lerp(c1, c2, lit)) for c1, c2 in zip((80, 80, 85), color))
    box(frame, cx - s * 0.55, cy - s * 0.55, cx + s * 0.55, cy + s * 0.55, core, INK, max(3, int(s / 28)), fi, r=s * 0.06, seed=seed + 9, shadow=False)
    if label:
        put_text(frame, label, cx, cy, "anton", int(s * 0.42), DARK if lit > 0.5 else (200, 200, 200))

# ------------------------------------------------------------------ misc
def shake(t, start, dur=0.5, amp=14):
    p = prog(t, start, dur)
    if p <= 0 or p >= 1: return 0, 0
    k = (1 - p) * amp
    return int(math.sin(t * 90) * k), int(math.cos(t * 77) * k)

def fmt_num(v, decimals=0, commas=True):
    s = f"{v:,.{decimals}f}" if commas else f"{v:.{decimals}f}"
    return s
