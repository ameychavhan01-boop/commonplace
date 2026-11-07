"""Drawing engine: paper style, typography, motion, chrome (title card / header / key-idea banner),
avatars, icons and chart primitives. Pure cairocffi, 1920x1080."""
import math, random, contextlib
import cairocffi as cairo

W, H, FPS = 1920, 1080, 30

def hexc(h):
    h = h.lstrip('#'); return tuple(int(h[i:i + 2], 16) / 255 for i in (0, 2, 4))

PAPER = hexc('#F5EFE4'); INK = hexc('#1D2731'); MUTED = hexc('#6E7781'); GREEN = hexc('#2E7D5B')
GOLD = hexc('#D99A2B'); RED = hexc('#C8553D'); BLUE = hexc('#36689E'); NAVY = hexc('#22344A')
CARD = hexc('#FFFDF9'); WHITE = (1, 1, 1)
LGOLD = hexc('#F6E7C8'); LGREEN = hexc('#DDEDE2'); LRED = hexc('#F5DED6'); LBLUE = hexc('#DDE7F2')
LINE = hexc('#D8CFC0'); GRID = hexc('#E9E1D3'); FAINT = hexc('#B9B0A2'); ORANGE = hexc('#E8892B')
SKIN = [hexc('#E9B98F'), hexc('#C98E63'), hexc('#8D5A3B'), hexc('#F2CDA8'), hexc('#B07A52')]
HAIR = [hexc('#2B2118'), hexc('#5A3A22'), hexc('#1A1A1A'), hexc('#8A8F96'), hexc('#B5651D')]

def mix(a, b, t): return tuple(a[i] + (b[i] - a[i]) * t for i in range(3))

# ------------------------------------------------------------------ easing / timing
def clamp(x, a=0.0, b=1.0): return a if x < a else b if x > b else x
def lin(t, t0, d): return clamp((t - t0) / d) if d > 0 else (1.0 if t >= t0 else 0.0)
def eo(x): return 1 - (1 - x) ** 3
def eio(x): return 4 * x ** 3 if x < .5 else 1 - (-2 * x + 2) ** 3 / 2
def back(x, s=1.9):
    x = clamp(x); return 1 + (s + 1) * (x - 1) ** 3 + s * (x - 1) ** 2
def P(t, t0, d=0.6, f=eo): return f(lin(t, t0, d))
def popv(t, t0, d=0.5): return back(lin(t, t0, d)) if t >= t0 else 0.0
def lerp(a, b, x): return a + (b - a) * x
def wave(t, f=1.0, ph=0.0): return math.sin(t * f * 2 * math.pi + ph)

# ------------------------------------------------------------------ fonts / text
FONTS = {'head': ('Inter Display ExtraBold', 0, 0), 'bold': ('Inter Display', 0, 1), 'semi': ('Inter SemiBold', 0, 0),
         'body': ('Inter', 0, 0), 'med': ('Inter Medium', 0, 0), 'serif': ('Bitstream Charter', 1, 0),
         'serifr': ('Bitstream Charter', 0, 0), 'serifb': ('Bitstream Charter', 1, 1), 'ibold': ('Inter', 0, 1)}

def setfont(c, font, size):
    f = FONTS[font]; c.select_font_face(f[0], f[1], f[2]); c.set_font_size(size)

def col(c, cl, a=1.0):
    if len(cl) == 4: c.set_source_rgba(cl[0], cl[1], cl[2], cl[3] * a)
    else: c.set_source_rgba(cl[0], cl[1], cl[2], a)

def tw(c, s, size, font='body', ls=0):
    setfont(c, font, size)
    if not ls: return c.text_extents(s)[4]
    return sum(c.text_extents(ch)[4] for ch in s) + ls * max(0, len(s) - 1)

def text(c, s, x, y, size, font='body', cl=INK, align='l', a=1.0, ls=0):
    """y is the baseline. align l/c/r. returns width."""
    if a <= 0.002 or not s: return 0
    w = tw(c, s, size, font, ls)
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    col(c, cl, a)
    if not ls:
        c.move_to(x, y); c.show_text(s)
    else:
        for ch in s:
            c.move_to(x, y); c.show_text(ch); x += c.text_extents(ch)[4] + ls
    return w

def wrap(c, s, size, font, maxw):
    words, lines, cur = s.split(), [], ''
    for w in words:
        trial = (cur + ' ' + w).strip()
        if tw(c, trial, size, font) <= maxw or not cur: cur = trial
        else: lines.append(cur); cur = w
    if cur: lines.append(cur)
    return lines

def para(c, s, x, y, size, font='body', cl=INK, maxw=600, lh=1.32, align='l', a=1.0):
    lines = wrap(c, s, size, font, maxw)
    for i, ln in enumerate(lines): text(c, ln, x, y + i * size * lh, size, font, cl, align, a)
    return len(lines) * size * lh

def fit_size(c, s, font, size, maxw):
    while size > 10 and tw(c, s, size, font) > maxw: size -= 1
    return size

# ------------------------------------------------------------------ shapes
def rrect(c, x, y, w, h, r):
    r = max(0, min(r, w / 2, h / 2))
    c.new_sub_path()
    c.arc(x + w - r, y + r, r, -math.pi / 2, 0); c.arc(x + w - r, y + h - r, r, 0, math.pi / 2)
    c.arc(x + r, y + h - r, r, math.pi / 2, math.pi); c.arc(x + r, y + r, r, math.pi, 1.5 * math.pi)
    c.close_path()

def shadow(c, x, y, w, h, r, a=1.0, depth=1.0):
    for i in range(7):
        sp = (i + 1) * 2.2 * depth
        rrect(c, x - sp * .5, y - sp * .2 + i * 1.6 * depth, w + sp, h + sp * .6, r + sp * .5)
        col(c, (0.18, 0.13, 0.06), 0.016 * a); c.fill()

def card(c, x, y, w, h, r=22, fill=CARD, a=1.0, sh=True, border=None, bw=2, depth=1.0):
    if a <= 0.002: return
    if sh: shadow(c, x, y, w, h, r, a, depth)
    rrect(c, x, y, w, h, r); col(c, fill, a); c.fill()
    if border is not None:
        rrect(c, x, y, w, h, r); col(c, border, a); c.set_line_width(bw); c.stroke()

def circle(c, x, y, r, cl, a=1.0):
    c.arc(x, y, max(0.01, r), 0, 2 * math.pi); col(c, cl, a); c.fill()

def ring(c, x, y, r, cl, lw=3, a=1.0, p=1.0, start=-math.pi / 2):
    if p <= 0: return
    c.new_path(); c.arc(x, y, max(0.01, r), start, start + 2 * math.pi * p); col(c, cl, a); c.set_line_width(lw); c.stroke()

def line(c, x1, y1, x2, y2, cl=INK, lw=3, a=1.0, dash=None, p=1.0, cap=cairo.LINE_CAP_ROUND):
    if p <= 0 or a <= 0: return
    c.new_path(); c.move_to(x1, y1); c.line_to(lerp(x1, x2, p), lerp(y1, y2, p))
    col(c, cl, a); c.set_line_width(lw); c.set_line_cap(cap)
    if dash: c.set_dash(dash)
    c.stroke(); c.set_dash([])

def polyline(c, pts, cl=INK, lw=3, a=1.0, p=1.0, dash=None, close=False, join=cairo.LINE_JOIN_ROUND):
    if p <= 0 or len(pts) < 2: return None
    seg = [math.dist(pts[i], pts[i + 1]) for i in range(len(pts) - 1)]
    tot = sum(seg); target = tot * clamp(p); acc = 0
    c.new_path(); c.move_to(*pts[0]); head = pts[0]
    for i, L in enumerate(seg):
        if acc + L >= target:
            f = (target - acc) / L if L else 1
            head = (lerp(pts[i][0], pts[i + 1][0], f), lerp(pts[i][1], pts[i + 1][1], f)); c.line_to(*head); break
        c.line_to(*pts[i + 1]); acc += L; head = pts[i + 1]
    if close and p >= 1: c.close_path()
    col(c, cl, a); c.set_line_width(lw); c.set_line_join(join); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if dash: c.set_dash(dash)
    c.stroke(); c.set_dash([])
    return head

def arrow(c, x1, y1, x2, y2, cl=INK, lw=4, a=1.0, p=1.0, head=16, dash=None):
    if p <= 0 or a <= 0: return
    ex, ey = lerp(x1, x2, p), lerp(y1, y2, p)
    ang = math.atan2(ey - y1, ex - x1)
    bx, by = ex - math.cos(ang) * head * .6, ey - math.sin(ang) * head * .6
    line(c, x1, y1, bx, by, cl, lw, a, dash)
    c.new_path(); c.move_to(ex, ey)
    c.line_to(ex - head * math.cos(ang - .45), ey - head * math.sin(ang - .45))
    c.line_to(ex - head * math.cos(ang + .45), ey - head * math.sin(ang + .45)); c.close_path()
    col(c, cl, a); c.fill()

def curved_arrow(c, x1, y1, x2, y2, bend=0.3, cl=INK, lw=4, a=1.0, p=1.0, head=16):
    mx, my = (x1 + x2) / 2, (y1 + y2) / 2
    nx, ny = -(y2 - y1) * bend, (x2 - x1) * bend
    pts = []
    for i in range(41):
        u = i / 40
        pts.append(((1 - u) ** 2 * x1 + 2 * (1 - u) * u * (mx + nx) + u * u * x2,
                    (1 - u) ** 2 * y1 + 2 * (1 - u) * u * (my + ny) + u * u * y2))
    k = max(2, int(41 * clamp(p)))
    if p <= 0: return
    polyline(c, pts[:k], cl, lw, a)
    (ax, ay), (bx, by) = pts[k - 2], pts[k - 1]
    ang = math.atan2(by - ay, bx - ax)
    c.new_path(); c.move_to(bx, by)
    c.line_to(bx - head * math.cos(ang - .45), by - head * math.sin(ang - .45))
    c.line_to(bx - head * math.cos(ang + .45), by - head * math.sin(ang + .45)); c.close_path(); col(c, cl, a); c.fill()

@contextlib.contextmanager
def alpha_group(c, a, box=None):
    """Draw children with a group alpha. box=(x,y,w,h) limits the offscreen size."""
    if a >= 0.999:
        yield; return
    c.save()
    if box: c.rectangle(*box); c.clip()
    c.push_group()
    try:
        yield
    finally:
        c.pop_group_to_source(); c.paint_with_alpha(max(0.0, a)); c.restore()

@contextlib.contextmanager
def xf(c, cx=0, cy=0, s=1.0, rot=0.0, dx=0, dy=0):
    c.save(); c.translate(cx + dx, cy + dy)
    if rot: c.rotate(rot)
    if s != 1.0: c.scale(max(s, 0.0001), max(s, 0.0001))
    c.translate(-cx, -cy)
    try:
        yield
    finally:
        c.restore()

@contextlib.contextmanager
def pop(c, t, t0, cx, cy, d=0.5, rise=0):
    """pop-in with overshoot around (cx,cy); yields alpha."""
    s = popv(t, t0, d); a = P(t, t0, d * .6)
    if a <= 0.001:
        yield 0.0; return
    with xf(c, cx, cy, s, dy=(1 - P(t, t0, d)) * rise):
        yield a

@contextlib.contextmanager
def rise(c, t, t0, d=0.6, dist=26):
    a = P(t, t0, d)
    with xf(c, 0, 0, 1.0, dy=(1 - a) * dist):
        yield a

def pill(c, x, y, s, size=22, bg=GOLD, fg=WHITE, a=1.0, font='semi', align='l', padx=18, ls=1.5, h=None, sh=False):
    w = tw(c, s, size, font, ls) + padx * 2; hh = h or size * 1.9
    if align == 'c': x -= w / 2
    elif align == 'r': x -= w
    if sh: shadow(c, x, y, w, hh, hh / 2, a * .7, .6)
    rrect(c, x, y, w, hh, hh / 2); col(c, bg, a); c.fill()
    text(c, s, x + padx, y + hh / 2 + size * .36, size, font, fg, 'l', a, ls)
    return w

def tag(c, x, y, s, bg=NAVY, fg=WHITE, size=24, a=1.0, align='c', font='semi', point=None):
    """label box centered at x (align c), y = top. point=(px,py) draws a small pointer."""
    w = tw(c, s, size, font) + 26; h = size * 1.75
    x0 = x - w / 2 if align == 'c' else (x - w if align == 'r' else x)
    if point:
        px, py = point
        c.new_path(); c.move_to(clamp(px, x0 + 14, x0 + w - 14) - 9, y + h / 2); c.line_to(px, py)
        c.line_to(clamp(px, x0 + 14, x0 + w - 14) + 9, y + h / 2); c.close_path(); col(c, bg, a); c.fill()
    shadow(c, x0, y, w, h, 10, a * .6, .5)
    rrect(c, x0, y, w, h, 10); col(c, bg, a); c.fill()
    text(c, s, x0 + w / 2, y + h / 2 + size * .35, size, font, fg, 'c', a)
    return w, h

def glow_dot(c, x, y, r, cl, t=0, a=1.0, pulse=True):
    if pulse:
        ph = (t * 1.2) % 1.0
        circle(c, x, y, r * (1 + ph * 2.2), cl, a * .35 * (1 - ph))
    circle(c, x, y, r * 1.6, WHITE, a); circle(c, x, y, r, cl, a)

def check(c, x, y, s, cl=GREEN, a=1.0, p=1.0, lw=None):
    polyline(c, [(x - 14 * s, y), (x - 4 * s, y + 10 * s), (x + 16 * s, y - 12 * s)], cl, lw or 6 * s, a, p)

def cross(c, x, y, s, cl=RED, a=1.0, p=1.0, lw=None):
    line(c, x - 12 * s, y - 12 * s, x + 12 * s, y + 12 * s, cl, lw or 6 * s, a, p=clamp(p * 2))
    line(c, x + 12 * s, y - 12 * s, x - 12 * s, y + 12 * s, cl, lw or 6 * s, a, p=clamp(p * 2 - 1))

def badge(c, x, y, r, kind, a=1.0, p=1.0):
    circle(c, x, y, r, GREEN if kind == 'ok' else RED if kind == 'no' else GOLD, a)
    if kind == 'ok': check(c, x, y + 1, r / 26, WHITE, a, p)
    elif kind == 'no': cross(c, x, y, r / 26, WHITE, a, p)
    else: text(c, '!', x, y + r * .42, r * 1.2, 'head', WHITE, 'c', a)

# ------------------------------------------------------------------ background
_BG = None
def background():
    global _BG
    if _BG is not None: return _BG
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H); c = cairo.Context(s)
    col(c, PAPER); c.paint()
    g = cairo.RadialGradient(W * .5, H * .42, 80, W * .5, H * .5, 1250)
    g.add_color_stop_rgba(0, 1, .992, .975, .75); g.add_color_stop_rgba(.55, 1, .99, .97, .18)
    g.add_color_stop_rgba(1, .86, .80, .70, .45)
    c.set_source(g); c.paint()
    for (x, y, r, cl, a) in [(1650, 180, 330, GOLD, .07), (240, 930, 420, NAVY, .045), (1500, 980, 160, GOLD, .06),
                             (300, 120, 110, NAVY, .05)]:
        ring(c, x, y, r, cl, 2, a)
    for x in range(30, W, 38):
        for y in range(30, H, 38):
            circle(c, x, y, 1.25, INK, .065)
    _BG = s; return s

def draw_bg(c, t):
    c.set_source_surface(background(), 0, 0); c.paint()
    for i, (x, y, r, cl) in enumerate([(1500, 260, 170, GOLD), (380, 820, 230, NAVY)]):
        ring(c, x + 30 * wave(t, .023, i), y + 20 * wave(t, .031, i + 1), r + 8 * wave(t, .05, i), cl, 1.5, .05)

# ------------------------------------------------------------------ chrome
def title_card(c, t, num, title, total, a=1.0, t0=0.0, label='CHAPTER'):
    if a <= 0.002: return
    cx = W / 2
    with alpha_group(c, a):
        k = P(t, t0 + .1, .7)
        text(c, label, cx, 300 - (1 - k) * 20, 34, 'semi', GOLD, 'c', k, ls=16)
        s = popv(t, t0 + .25, .7)
        with xf(c, cx, 470, s):
            text(c, str(num), cx, 560, 290, 'head', NAVY, 'c', P(t, t0 + .25, .4))
        lw = 360 * P(t, t0 + .55, .8, eio)
        line(c, cx - lw / 2, 615, cx + lw / 2, 615, GOLD, 5, 1)
        k2 = P(t, t0 + .75, .7)
        sz = fit_size(c, title, 'serif', 76, 1500)
        text(c, title, cx, 712 - (1 - k2) * 18, sz, 'serif', INK, 'c', k2)
        text(c, f'{num} of {total}', cx, 790, 28, 'med', MUTED, 'c', P(t, t0 + 1.0, .6), ls=3)

def progress_dots(c, n, idx, a=1.0, x_right=1800, y=86):
    gap = 26; x0 = x_right - (n - 1) * gap
    for i in range(n):
        x = x0 + i * gap
        if i < idx: circle(c, x, y, 7, NAVY, a)
        elif i == idx: circle(c, x, y, 11, GOLD, a * .25); circle(c, x, y, 8, GOLD, a)
        else: ring(c, x, y, 6.5, FAINT, 2, a)

def header(c, pill_text, title, n_dots=0, idx=0, a=1.0, sub=None):
    if a <= 0.002: return
    with alpha_group(c, a, (0, 0, W, 240)):
        pill(c, 120, 62, pill_text, 20, GOLD, WHITE, 1, 'semi', ls=2.2)
        sz = fit_size(c, title, 'head', 62, 1450 if not n_dots else 1340)
        text(c, title, 118, 178, sz, 'head', INK, 'l', 1)
        if sub: text(c, sub, 120, 218, 26, 'med', MUTED, 'l', 1)
        if n_dots: progress_dots(c, n_dots, idx, 1)

def banner(c, msg, p, label='KEY IDEA'):
    if p <= 0.002 or not msg: return
    y = 932 + (1 - p) * 40
    with alpha_group(c, p, (0, 880, W, 200)):
        x, w, h = 120, 1680, 104
        shadow(c, x, y, w, h, 20, 1.2, 1.2)
        rrect(c, x, y, w, h, 20); col(c, NAVY); c.fill()
        c.save(); rrect(c, x, y, w, h, 20); c.clip(); c.rectangle(x, y, 12, h); col(c, GOLD); c.fill(); c.restore()
        text(c, label, x + 52, y + 44, 19, 'semi', GOLD, 'l', 1, ls=4)
        lw = 52 + tw(c, label, 19, 'semi', 4)
        line(c, x + 52, y + 60, x + 52 + 60 * P(p, 0, 1), y + 60, GOLD, 3)
        sz = fit_size(c, msg, 'serif', 40, w - (lw + 120) - 60)
        text(c, msg, x + lw + 120 - 52 + 40, y + 66, sz, 'serif', WHITE, 'l', 1)

# ------------------------------------------------------------------ avatars
def avatar(c, x, y, s=1.0, skin=None, hair=None, shirt=BLUE, style='short', tie=None, glasses=False,
           cap=None, beard=None, mood='smile', t=0.0, seed=0, a=1.0, look=0.0, body=True):
    skin = skin or SKIN[0]; hair = hair or HAIR[0]
    with alpha_group(c, a, (x - 120 * s, y - 110 * s, 240 * s, 260 * s)):
        y = y + wave(t, .45, seed) * 2.2 * s
        dk = mix(skin, (0, 0, 0), .16)
        if style == 'long':
            rrect(c, x - 50 * s, y - 52 * s, 100 * s, 102 * s, 46 * s); col(c, hair); c.fill()
        if body:
            c.new_path(); c.move_to(x - 80 * s, y + 140 * s)
            c.curve_to(x - 80 * s, y + 78 * s, x - 64 * s, y + 52 * s, x - 22 * s, y + 49 * s)
            c.line_to(x + 22 * s, y + 49 * s)
            c.curve_to(x + 64 * s, y + 52 * s, x + 80 * s, y + 78 * s, x + 80 * s, y + 140 * s); c.close_path()
            col(c, shirt); c.fill()
            c.rectangle(x - 12 * s, y + 26 * s, 24 * s, 28 * s); col(c, dk); c.fill()
            c.new_path(); c.move_to(x - 22 * s, y + 49 * s); c.line_to(x, y + 70 * s); c.line_to(x + 22 * s, y + 49 * s)
            c.line_to(x + 12 * s, y + 47 * s); c.line_to(x, y + 56 * s); c.line_to(x - 12 * s, y + 47 * s); c.close_path()
            col(c, WHITE, .95); c.fill()
            if tie:
                c.new_path(); c.move_to(x - 6 * s, y + 55 * s); c.line_to(x + 6 * s, y + 55 * s); c.line_to(x + 4 * s, y + 63 * s)
                c.line_to(x + 9 * s, y + 104 * s); c.line_to(x, y + 114 * s); c.line_to(x - 9 * s, y + 104 * s)
                c.line_to(x - 4 * s, y + 63 * s); c.close_path(); col(c, tie); c.fill()
        circle(c, x - 41 * s, y + 4 * s, 8.5 * s, dk); circle(c, x + 41 * s, y + 4 * s, 8.5 * s, dk)
        c.save(); c.translate(x, y); c.scale(40 * s, 44 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); col(c, skin); c.fill()
        if beard:
            c.new_path(); c.move_to(x - 40 * s, y + 2 * s)
            c.curve_to(x - 40 * s, y + 52 * s, x - 18 * s, y + 66 * s, x, y + 66 * s)
            c.curve_to(x + 18 * s, y + 66 * s, x + 40 * s, y + 52 * s, x + 40 * s, y + 2 * s)
            c.curve_to(x + 30 * s, y + 30 * s, x + 14 * s, y + 24 * s, x, y + 26 * s)
            c.curve_to(x - 14 * s, y + 24 * s, x - 30 * s, y + 30 * s, x - 40 * s, y + 2 * s); c.close_path()
            col(c, beard); c.fill()
        if style in ('short', 'long', 'bun', 'side'):
            c.new_path(); c.move_to(x - 42 * s, y + 4 * s)
            c.curve_to(x - 48 * s, y - 40 * s, x - 18 * s, y - 58 * s, x + 4 * s, y - 55 * s)
            c.curve_to(x + 36 * s, y - 54 * s, x + 50 * s, y - 32 * s, x + 42 * s, y + 4 * s)
            if style == 'side':
                c.curve_to(x + 36 * s, y - 24 * s, x + 4 * s, y - 34 * s, x - 22 * s, y - 22 * s)
            else:
                c.curve_to(x + 36 * s, y - 22 * s, x + 12 * s, y - 30 * s, x - 6 * s, y - 28 * s)
            c.curve_to(x - 26 * s, y - 26 * s, x - 36 * s, y - 16 * s, x - 42 * s, y + 4 * s); c.close_path()
            col(c, hair); c.fill()
            if style == 'bun': circle(c, x + 6 * s, y - 60 * s, 16 * s, hair)
        elif style == 'curly':
            for i in range(9):
                ang = math.pi + i * math.pi / 8
                circle(c, x + math.cos(ang) * 38 * s, y - 6 * s + math.sin(ang) * 40 * s, 15 * s, hair)
        elif style == 'bald':
            for sx in (-1, 1):
                c.new_path(); c.move_to(x + sx * 41 * s, y + 4 * s)
                c.curve_to(x + sx * 44 * s, y - 18 * s, x + sx * 36 * s, y - 28 * s, x + sx * 28 * s, y - 30 * s)
                c.line_to(x + sx * 34 * s, y - 8 * s); c.close_path(); col(c, hair); c.fill()
        if cap:
            c.new_path(); c.arc(x, y - 14 * s, 43 * s, math.pi, 2 * math.pi); c.close_path(); col(c, cap); c.fill()
            rrect(c, x - 10 * s, y - 20 * s, 66 * s, 10 * s, 5 * s); col(c, mix(cap, (0, 0, 0), .2)); c.fill()
            circle(c, x, y - 57 * s, 4 * s, mix(cap, (1, 1, 1), .3))
        ex = look * 4 * s
        bl = ((t + seed * 1.7) % 3.7) < 0.12
        for sx in (-1, 1):
            if bl: line(c, x + sx * 14 * s - 4 * s + ex, y + 4 * s, x + sx * 14 * s + 4 * s + ex, y + 4 * s, INK, 2.4 * s)
            else:
                c.save(); c.translate(x + sx * 14 * s + ex, y + 3 * s); c.scale(4.2 * s, 5.2 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); col(c, INK); c.fill()
            br = {'worried': (-5, 3), 'angry': (4, -3), 'happy': (-2, -2)}.get(mood, (0, 0))
            line(c, x + sx * 6 * s, y - 9 * s + br[0] * s * .6 * (1), x + sx * 21 * s, y - 10 * s + br[1] * s * .6, hair if not beard else beard, 3 * s)
        circle(c, x - 23 * s, y + 15 * s, 6.5 * s, (0.92, 0.45, 0.42), .22); circle(c, x + 23 * s, y + 15 * s, 6.5 * s, (0.92, 0.45, 0.42), .22)
        my = y + 22 * s
        if mood in ('smile', 'happy'):
            c.new_path(); c.arc(x, my - 6 * s, 11 * s, .25 * math.pi, .75 * math.pi); col(c, INK); c.set_line_width(3 * s); c.stroke()
            if mood == 'happy':
                c.new_path(); c.arc(x, my - 5 * s, 10 * s, 0, math.pi); col(c, (0.55, 0.15, 0.15)); c.fill()
        elif mood == 'worried':
            c.new_path(); c.arc(x, my + 9 * s, 10 * s, 1.2 * math.pi, 1.8 * math.pi); col(c, INK); c.set_line_width(3 * s); c.stroke()
        elif mood == 'shock':
            c.save(); c.translate(x, my + 2 * s); c.scale(6 * s, 8 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); col(c, (0.45, 0.12, 0.12)); c.fill()
        else:
            line(c, x - 9 * s, my, x + 9 * s, my, INK, 3 * s)
        if glasses:
            for sx in (-1, 1):
                rrect(c, x + sx * 14 * s - 11 * s, y - 4 * s, 22 * s, 16 * s, 5 * s); col(c, INK); c.set_line_width(2.4 * s); c.stroke()
            line(c, x - 3 * s, y + 2 * s, x + 3 * s, y + 2 * s, INK, 2.4 * s)

def bubble(c, x, y, w, h, msg, a=1.0, size=26, font='semi', fg=INK, bg=CARD, tail='bl', border=None):
    if a <= 0.002: return
    with alpha_group(c, a, (x - 40, y - 40, w + 80, h + 90)):
        shadow(c, x, y, w, h, 18, 1, .7)
        rrect(c, x, y, w, h, 18); col(c, bg); c.fill()
        tx = x + 40 if tail == 'bl' else x + w - 40 if tail == 'br' else x + w / 2
        c.new_path(); c.move_to(tx - 12, y + h - 1); c.line_to(tx + (-14 if tail == 'bl' else 14 if tail == 'br' else 0), y + h + 22); c.line_to(tx + 12, y + h - 1); c.close_path(); col(c, bg); c.fill()
        if border: rrect(c, x, y, w, h, 18); col(c, border); c.set_line_width(2.5); c.stroke()
        lines = wrap(c, msg, size, font, w - 36)
        y0 = y + h / 2 - (len(lines) - 1) * size * 1.25 / 2 + size * .35
        for i, ln in enumerate(lines): text(c, ln, x + w / 2, y0 + i * size * 1.25, size, font, fg, 'c')

# ------------------------------------------------------------------ icons
def coin(c, x, y, r, sym='$', cl=GOLD, a=1.0, spin=0.0):
    sx = abs(math.cos(spin)) if spin else 1.0
    with xf(c, x, y):
        c.save(); c.translate(x, y); c.scale(max(sx, .08), 1)
        c.arc(0, 4, r, 0, 2 * math.pi); col(c, mix(cl, (0, 0, 0), .25), a); c.fill()
        c.arc(0, 0, r, 0, 2 * math.pi); col(c, cl, a); c.fill()
        c.arc(0, 0, r * .78, 0, 2 * math.pi); col(c, mix(cl, (1, 1, 1), .25), a); c.set_line_width(max(1, r * .08)); c.stroke()
        if sym == 'B':
            setfont(c, 'head', r * 1.15); w = c.text_extents('B')[4]
            for dx in (-0.16, 0.12):
                c.rectangle(dx * r - r * .04, -r * .78, r * .09, r * 1.56); col(c, WHITE, a); c.fill()
            text(c, 'B', -w / 2 + r * .02, r * .40, r * 1.15, 'head', WHITE, 'l', a)
        else:
            text(c, sym, 0, r * .38, r * 1.05, 'head', WHITE, 'c', a)
        c.restore()

def btc(c, x, y, r, a=1.0, spin=0.0): coin(c, x, y, r, 'B', ORANGE, a, spin)

def newspaper(c, x, y, w, h, headline, a=1.0, sub=None, accent=RED, tilt=0.0):
    with xf(c, x + w / 2, y + h / 2, rot=tilt):
        card(c, x, y, w, h, 10, CARD, a)
        text(c, 'THE DAILY NEWS', x + 24, y + 38, 18, 'semi', MUTED, 'l', a, ls=3)
        line(c, x + 24, y + 52, x + w - 24, y + 52, INK, 2, a * .5)
        sz = fit_size(c, headline, 'head', 40, w - 48)
        text(c, headline, x + 24, y + 100, sz, 'head', accent, 'l', a)
        if sub: text(c, sub, x + 24, y + 136, 22, 'med', INK, 'l', a)
        for i in range(3):
            yy = y + (160 if sub else 132) + i * 20
            if yy < y + h - 14: line(c, x + 24, yy, x + w - 24 - (60 if i == 2 else 0), yy, LINE, 6, a)

def clock(c, x, y, r, t=0.0, a=1.0, speed=1.0, cl=NAVY):
    circle(c, x, y + 3, r, (0, 0, 0), .06 * a); circle(c, x, y, r, CARD, a); ring(c, x, y, r, cl, r * .1, a)
    for i in range(12):
        ang = i * math.pi / 6
        line(c, x + math.cos(ang) * r * .72, y + math.sin(ang) * r * .72, x + math.cos(ang) * r * .84, y + math.sin(ang) * r * .84, cl, r * .05, a)
    m = t * speed * 2 * math.pi / 6; hh = m / 12
    line(c, x, y, x + math.sin(hh) * r * .45, y - math.cos(hh) * r * .45, INK, r * .09, a)
    line(c, x, y, x + math.sin(m) * r * .68, y - math.cos(m) * r * .68, GOLD, r * .06, a)
    circle(c, x, y, r * .07, INK, a)

def hourglass(c, x, y, s, t=0.0, a=1.0):
    rrect(c, x - 40 * s, y - 66 * s, 80 * s, 12 * s, 4 * s); col(c, NAVY, a); c.fill()
    rrect(c, x - 40 * s, y + 54 * s, 80 * s, 12 * s, 4 * s); col(c, NAVY, a); c.fill()
    c.new_path(); c.move_to(x - 32 * s, y - 54 * s); c.line_to(x + 32 * s, y - 54 * s); c.line_to(x + 4 * s, y); c.line_to(x + 32 * s, y + 54 * s)
    c.line_to(x - 32 * s, y + 54 * s); c.line_to(x - 4 * s, y); c.close_path(); col(c, LBLUE, a); c.fill_preserve(); col(c, NAVY, a); c.set_line_width(3 * s); c.stroke()
    f = (t * .15) % 1
    c.new_path(); c.move_to(x - 26 * s * (1 - f), y - 6 * s - 40 * s * (1 - f)); c.line_to(x + 26 * s * (1 - f), y - 6 * s - 40 * s * (1 - f)); c.line_to(x, y - 4 * s); c.close_path(); col(c, GOLD, a); c.fill()
    c.new_path(); c.move_to(x - 28 * s, y + 52 * s); c.line_to(x + 28 * s, y + 52 * s); c.line_to(x, y + 52 * s - 36 * s * f); c.close_path(); col(c, GOLD, a); c.fill()
    line(c, x, y, x, y + 50 * s, GOLD, 2 * s, a)

def magnifier(c, x, y, r, a=1.0, cl=NAVY):
    circle(c, x, y, r, LBLUE, a * .55); ring(c, x, y, r, cl, r * .16, a)
    line(c, x + r * .72, y + r * .72, x + r * 1.55, y + r * 1.55, cl, r * .26, a)

def book3d(c, x, y, w, h, t=0.0, a=1.0, title='TECHNICAL ANALYSIS', sub='OF THE FINANCIAL MARKETS', author='JOHN J. MURPHY', fl=True):
    dy = wave(t, .25) * 8 if fl else 0
    rot = wave(t, .18, 1) * .02 if fl else 0
    with xf(c, x, y, rot=rot, dy=dy):
        x0, y0 = x - w / 2, y - h / 2
        shadow(c, x0, y0, w, h, 8, a * 1.4, 1.6)
        rrect(c, x0 + w - 8, y0 + 8, 14, h - 10, 4); col(c, (0.93, 0.9, 0.84), a); c.fill()
        rrect(c, x0, y0, w, h, 8); col(c, NAVY, a); c.fill()
        c.rectangle(x0, y0, w * .06, h); col(c, mix(NAVY, (0, 0, 0), .3), a); c.fill()
        c.rectangle(x0 + w * .12, y0 + h * .08, w * .78, 4); col(c, GOLD, a); c.fill()
        sz = fit_size(c, title, 'head', w * .12, w * .74)
        lines = title.split(' ')
        yy = y0 + h * .2
        for i, ln in enumerate(lines):
            text(c, ln, x0 + w * .13, yy + i * sz * 1.05, sz * 1.18 if len(lines) > 1 else sz, 'head', WHITE, 'l', a)
        if sub:
            ssz = fit_size(c, sub, 'semi', w * .052, w * .74)
            text(c, sub, x0 + w * .13, yy + len(lines) * sz * 1.05 + ssz * 1.4, ssz, 'semi', LGOLD, 'l', a)
        pts = []
        for i in range(9):
            pts.append((x0 + w * (.14 + i * .09), y0 + h * (.8 - .045 * i - (.06 if i % 2 else 0))))
        polyline(c, pts, GOLD, w * .016, a)
        text(c, author, x0 + w * .13, y0 + h * .93, w * .05, 'semi', WHITE, 'l', a, ls=2)

def factory(c, x, y, s, t=0.0, a=1.0, cl=NAVY):
    for i, (dx, hh) in enumerate([(-40, 70), (-12, 90)]):
        c.rectangle(x + dx * s, y - hh * s, 16 * s, hh * s); col(c, cl, a); c.fill()
        for k in range(3):
            ph = ((t * .5 + k / 3 + i * .17) % 1)
            circle(c, x + (dx + 8 + ph * 18) * s, y - (hh + 10 + ph * 50) * s, (7 + ph * 9) * s, FAINT, a * .5 * (1 - ph))
    c.new_path(); c.move_to(x - 60 * s, y + 40 * s); c.line_to(x - 60 * s, y - 20 * s); c.line_to(x - 30 * s, y - 2 * s); c.line_to(x - 30 * s, y - 20 * s)
    c.line_to(x, y - 2 * s); c.line_to(x, y - 20 * s); c.line_to(x + 30 * s, y - 2 * s); c.line_to(x + 30 * s, y - 20 * s); c.line_to(x + 60 * s, y - 2 * s)
    c.line_to(x + 60 * s, y + 40 * s); c.close_path(); col(c, cl, a); c.fill()
    for i in range(4): rrect(c, x + (-50 + i * 27) * s, y + 10 * s, 16 * s, 14 * s, 3 * s); col(c, GOLD, a); c.fill()

def train(c, x, y, s, t=0.0, a=1.0, cl=RED):
    rrect(c, x - 70 * s, y - 30 * s, 100 * s, 50 * s, 8 * s); col(c, cl, a); c.fill()
    rrect(c, x + 20 * s, y - 62 * s, 50 * s, 82 * s, 8 * s); col(c, mix(cl, (0, 0, 0), .2), a); c.fill()
    rrect(c, x + 30 * s, y - 52 * s, 30 * s, 24 * s, 4 * s); col(c, LBLUE, a); c.fill()
    c.rectangle(x - 50 * s, y - 56 * s, 16 * s, 26 * s); col(c, INK, a); c.fill()
    for k in range(3):
        ph = (t * .6 + k / 3) % 1
        circle(c, x - 42 * s - ph * 30 * s, y - 64 * s - ph * 40 * s, (6 + ph * 10) * s, FAINT, a * .5 * (1 - ph))
    c.new_path(); c.move_to(x + 70 * s, y + 20 * s); c.line_to(x + 92 * s, y + 20 * s); c.line_to(x + 70 * s, y - 6 * s); c.close_path(); col(c, INK, a); c.fill()
    for i, wx in enumerate((-50, -14, 22, 52)):
        circle(c, x + wx * s, y + 24 * s, 14 * s, INK, a); circle(c, x + wx * s, y + 24 * s, 5 * s, FAINT, a)
        ang = t * 4 + i
        line(c, x + wx * s, y + 24 * s, x + wx * s + math.cos(ang) * 12 * s, y + 24 * s + math.sin(ang) * 12 * s, FAINT, 2 * s, a)
    line(c, x - 80 * s, y + 40 * s, x + 100 * s, y + 40 * s, INK, 3 * s, a)

def bell(c, x, y, s, t=0.0, a=1.0, cl=GOLD, ringing=True):
    rot = wave(t, 1.6) * .25 * (1 if ringing else 0) * max(0, wave(t, .25))
    with xf(c, x, y - 40 * s, rot=rot):
        c.new_path(); c.move_to(x - 40 * s, y + 24 * s)
        c.curve_to(x - 34 * s, y + 6 * s, x - 34 * s, y - 40 * s, x, y - 44 * s)
        c.curve_to(x + 34 * s, y - 40 * s, x + 34 * s, y + 6 * s, x + 40 * s, y + 24 * s); c.close_path(); col(c, cl, a); c.fill()
        rrect(c, x - 46 * s, y + 20 * s, 92 * s, 12 * s, 6 * s); col(c, mix(cl, (0, 0, 0), .2), a); c.fill()
        circle(c, x, y + 38 * s, 9 * s, mix(cl, (0, 0, 0), .2), a); circle(c, x, y - 48 * s, 6 * s, mix(cl, (0, 0, 0), .2), a)

def bulb(c, x, y, s, a=1.0, on=1.0):
    if on > 0:
        for i in range(8):
            ang = i * math.pi / 4
            line(c, x + math.cos(ang) * 58 * s, y - 10 * s + math.sin(ang) * 58 * s, x + math.cos(ang) * 74 * s, y - 10 * s + math.sin(ang) * 74 * s, GOLD, 5 * s, a * on)
    circle(c, x, y - 10 * s, 40 * s, mix(LGOLD, GOLD, on * .7), a)
    rrect(c, x - 18 * s, y + 28 * s, 36 * s, 26 * s, 6 * s); col(c, NAVY, a); c.fill()
    line(c, x - 18 * s, y + 38 * s, x + 18 * s, y + 38 * s, FAINT, 3 * s, a)

def warn(c, x, y, s, a=1.0, cl=GOLD):
    c.new_path(); c.move_to(x, y - 44 * s); c.line_to(x + 50 * s, y + 40 * s); c.line_to(x - 50 * s, y + 40 * s); c.close_path()
    col(c, cl, a); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_width(10 * s); c.stroke_preserve(); c.fill()
    text(c, '!', x, y + 30 * s, 64 * s, 'head', WHITE, 'c', a)

def gavel(c, x, y, s, t=0.0, a=1.0, hit=0.0):
    """hit 0 = raised, 1 = striking the block."""
    rot = -0.75 * (1 - hit)
    px, py = x - 110 * s, y + 10 * s
    rrect(c, x - 40 * s, y + 52 * s, 130 * s, 26 * s, 8 * s); col(c, hexc('#6B4226'), a); c.fill()
    rrect(c, x - 54 * s, y + 74 * s, 158 * s, 14 * s, 6 * s); col(c, hexc('#4E3020'), a); c.fill()
    with xf(c, px, py, rot=rot):
        rrect(c, px, py - 8 * s, 150 * s, 16 * s, 6 * s); col(c, hexc('#8A5A33'), a); c.fill()
        rrect(c, x + 2 * s, py - 50 * s, 46 * s, 100 * s, 12 * s); col(c, hexc('#6B4226'), a); c.fill()
        rrect(c, x - 2 * s, py - 40 * s, 54 * s, 12 * s, 4 * s); col(c, GOLD, a); c.fill()
        rrect(c, x - 2 * s, py + 28 * s, 54 * s, 12 * s, 4 * s); col(c, GOLD, a); c.fill()

def scale_balance(c, x, y, s, tilt=0.0, a=1.0, left=None, right=None, cl=NAVY):
    rrect(c, x - 6 * s, y - 80 * s, 12 * s, 150 * s, 5 * s); col(c, cl, a); c.fill()
    rrect(c, x - 60 * s, y + 66 * s, 120 * s, 16 * s, 6 * s); col(c, cl, a); c.fill()
    circle(c, x, y - 84 * s, 12 * s, GOLD, a)
    ang = tilt * .32
    lx, ly = x - math.cos(ang) * 130 * s, y - 70 * s - math.sin(ang) * 130 * s
    rx, ry = x + math.cos(ang) * 130 * s, y - 70 * s + math.sin(ang) * 130 * s
    line(c, lx, ly, rx, ry, cl, 8 * s, a)
    for (px, py, lab) in ((lx, ly, left), (rx, ry, right)):
        line(c, px, py, px - 40 * s, py + 70 * s, FAINT, 2 * s, a); line(c, px, py, px + 40 * s, py + 70 * s, FAINT, 2 * s, a)
        c.new_path(); c.move_to(px - 56 * s, py + 70 * s); c.line_to(px + 56 * s, py + 70 * s); c.curve_to(px + 40 * s, py + 96 * s, px - 40 * s, py + 96 * s, px - 56 * s, py + 70 * s)
        col(c, GOLD, a); c.fill()
        if lab: text(c, lab, px, py + 124 * s, 26 * s, 'semi', INK, 'c', a)
    return (lx, ly), (rx, ry)

def funnel(c, x, y, s, a=1.0, cl=NAVY):
    c.new_path(); c.move_to(x - 120 * s, y - 70 * s); c.line_to(x + 120 * s, y - 70 * s); c.line_to(x + 24 * s, y + 30 * s)
    c.line_to(x + 24 * s, y + 90 * s); c.line_to(x - 24 * s, y + 90 * s); c.line_to(x - 24 * s, y + 30 * s); c.close_path()
    col(c, cl, a); c.fill()
    c.save(); c.translate(x, y - 70 * s); c.scale(120 * s, 18 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); col(c, mix(cl, (1, 1, 1), .25), a); c.fill()

def cloud(c, x, y, s, a=1.0, cl=FAINT):
    for dx, dy, r in ((-30, 6, 26), (0, -10, 34), (32, 4, 26), (-8, 14, 26), (16, 16, 24)):
        circle(c, x + dx * s, y + dy * s, r * s, cl, a)

def doc(c, x, y, s, a=1.0, cl=CARD, title=None, accent=BLUE):
    card(c, x - 50 * s, y - 64 * s, 100 * s, 128 * s, 10 * s, cl, a)
    if title: text(c, title, x, y - 34 * s, 18 * s, 'semi', accent, 'c', a)
    for i in range(5):
        line(c, x - 32 * s, y - 14 * s + i * 16 * s, x + (32 - (24 if i == 4 else 0)) * s, y - 14 * s + i * 16 * s, LINE, 5 * s, a)

def calendar(c, x, y, s, a=1.0, label=''):
    card(c, x - 60 * s, y - 56 * s, 120 * s, 120 * s, 14 * s, CARD, a)
    c.save(); rrect(c, x - 60 * s, y - 56 * s, 120 * s, 120 * s, 14 * s); c.clip(); c.rectangle(x - 60 * s, y - 56 * s, 120 * s, 34 * s); col(c, RED, a); c.fill(); c.restore()
    for i in range(3):
        for j in range(4):
            circle(c, x - 36 * s + j * 24 * s, y - 2 * s + i * 22 * s, 5 * s, FAINT, a)
    if label: text(c, label, x, y + 90 * s, 24 * s, 'semi', INK, 'c', a)

def shield(c, x, y, s, a=1.0, cl=BLUE):
    c.new_path(); c.move_to(x, y - 60 * s); c.curve_to(x + 30 * s, y - 44 * s, x + 50 * s, y - 44 * s, x + 54 * s, y - 44 * s)
    c.curve_to(x + 54 * s, y + 10 * s, x + 40 * s, y + 46 * s, x, y + 66 * s)
    c.curve_to(x - 40 * s, y + 46 * s, x - 54 * s, y + 10 * s, x - 54 * s, y - 44 * s)
    c.curve_to(x - 50 * s, y - 44 * s, x - 30 * s, y - 44 * s, x, y - 60 * s); c.close_path(); col(c, cl, a); c.fill()

def tv(c, x, y, s, a=1.0, t=0.0, label=''):
    rrect(c, x - 90 * s, y - 60 * s, 180 * s, 118 * s, 14 * s); col(c, NAVY, a); c.fill()
    rrect(c, x - 78 * s, y - 48 * s, 156 * s, 94 * s, 8 * s); col(c, LBLUE, a); c.fill()
    pts = [(x - 70 * s + i * 14 * s, y + 20 * s - 40 * s * (.3 + .3 * math.sin(i * .9 + t))) for i in range(11)]
    polyline(c, pts, GREEN, 4 * s, a)
    line(c, x - 30 * s, y + 80 * s, x + 30 * s, y + 80 * s, NAVY, 8 * s, a); line(c, x, y + 58 * s, x, y + 80 * s, NAVY, 8 * s, a)
    if label: text(c, label, x, y + 118 * s, 24 * s, 'semi', INK, 'c', a)

def chart_icon(c, x, y, s, a=1.0, up=True):
    card(c, x - 60 * s, y - 50 * s, 120 * s, 100 * s, 12 * s, CARD, a)
    pts = [(x - 44 * s, y + 26 * s), (x - 18 * s, y), (x + 4 * s, y + 12 * s), (x + 40 * s, y - 30 * s)] if up else \
          [(x - 44 * s, y - 26 * s), (x - 18 * s, y), (x + 4 * s, y - 10 * s), (x + 40 * s, y + 28 * s)]
    polyline(c, pts, GREEN if up else RED, 6 * s, a)

def megaphone(c, x, y, s, a=1.0, cl=RED):
    c.new_path(); c.move_to(x - 50 * s, y - 16 * s); c.line_to(x + 40 * s, y - 50 * s); c.line_to(x + 40 * s, y + 50 * s); c.line_to(x - 50 * s, y + 16 * s); c.close_path(); col(c, cl, a); c.fill()
    rrect(c, x - 66 * s, y - 18 * s, 22 * s, 36 * s, 6 * s); col(c, NAVY, a); c.fill()
    for i in range(3): ring(c, x + 40 * s, y, (30 + i * 18) * s, cl, 4 * s, a * (.6 - i * .15), .22, -.11 * 2 * math.pi)

def speedometer(c, x, y, r, v, a=1.0, label=''):
    c.new_path(); c.arc(x, y, r, math.pi, 2 * math.pi); col(c, NAVY, a); c.set_line_width(r * .16); c.stroke()
    for i, cl in enumerate((GREEN, GOLD, RED)):
        c.new_path(); c.arc(x, y, r * .8, math.pi + i * math.pi / 3, math.pi + (i + 1) * math.pi / 3); col(c, cl, a); c.set_line_width(r * .1); c.stroke()
    ang = math.pi + clamp(v) * math.pi
    line(c, x, y, x + math.cos(ang) * r * .75, y + math.sin(ang) * r * .75, INK, r * .07, a)
    circle(c, x, y, r * .1, INK, a)
    if label: text(c, label, x, y + r * .45, r * .26, 'semi', INK, 'c', a)

def handshake(c, x, y, s, a=1.0):
    rrect(c, x - 90 * s, y - 14 * s, 80 * s, 30 * s, 12 * s); col(c, GREEN, a); c.fill()
    rrect(c, x + 10 * s, y - 14 * s, 80 * s, 30 * s, 12 * s); col(c, RED, a); c.fill()
    c.save(); c.translate(x, y); c.scale(30 * s, 22 * s); c.arc(0, 0, 1, 0, 2 * math.pi); c.restore(); col(c, SKIN[0], a); c.fill()
    for i in range(3): line(c, x - 12 * s + i * 10 * s, y - 14 * s, x - 6 * s + i * 10 * s, y + 10 * s, mix(SKIN[0], (0, 0, 0), .2), 2 * s, a)

def ruler(c, x, y, w, ang=0.0, a=1.0):
    with xf(c, x, y, rot=ang):
        rrect(c, x - w / 2, y - 18, w, 36, 6); col(c, LGOLD, a); c.fill(); rrect(c, x - w / 2, y - 18, w, 36, 6); col(c, GOLD, a); c.set_line_width(2); c.stroke()
        for i in range(int(w / 16)):
            hh = 14 if i % 5 == 0 else 8
            line(c, x - w / 2 + 8 + i * 16, y - 18, x - w / 2 + 8 + i * 16, y - 18 + hh, GOLD, 2, a)

# ------------------------------------------------------------------ charts
class Frame:
    def __init__(self, x, y, w, h, x0, x1, y0, y1, log=False):
        self.x, self.y, self.w, self.h = x, y, w, h
        self.x0, self.x1, self.y0, self.y1, self.log = x0, x1, y0, y1, log
    def X(self, i): return self.x + (i - self.x0) / (self.x1 - self.x0) * self.w
    def Y(self, p):
        if self.log:
            l0, l1 = math.log(self.y0), math.log(self.y1)
            return self.y + self.h - (math.log(max(p, 1e-9)) - l0) / (l1 - l0) * self.h
        return self.y + self.h - (p - self.y0) / (self.y1 - self.y0) * self.h
    def P(self, i, p): return (self.X(i), self.Y(p))
    def bw(self): return self.w / (self.x1 - self.x0)

def chart_card(c, F, a=1.0, title=None, sub=None, src=None, pad=28):
    top = F.y - pad - (54 if title else 0); bot = F.y + F.h + 46 + (26 if src else 0)
    card(c, F.x - pad, top, F.w + pad * 2 + 70, bot - top, 22, CARD, a)
    if title: text(c, title, F.x, F.y - pad - 10, 26, 'semi', INK, 'l', a)
    if sub: text(c, sub, F.x + tw(c, title or '', 26, 'semi') + 16, F.y - pad - 10, 22, 'med', MUTED, 'l', a)
    if src: text(c, src, F.x + F.w + 70 + pad - 16, bot - 12, 16, 'med', FAINT, 'r', a)

def ygrid(c, F, ticks, fmt=lambda v: f'{v:,.0f}', a=1.0, side='r', size=18, lines=True):
    for v in ticks:
        y = F.Y(v)
        if y < F.y - 2 or y > F.y + F.h + 2: continue
        if lines: line(c, F.x, y, F.x + F.w, y, GRID, 1.5, a)
        if side == 'r': text(c, fmt(v), F.x + F.w + 12, y + size * .35, size, 'med', MUTED, 'l', a)
        else: text(c, fmt(v), F.x - 12, y + size * .35, size, 'med', MUTED, 'r', a)

def xlabels(c, F, items, a=1.0, size=18):
    for i, lab in items:
        x = F.X(i)
        if F.x - 5 <= x <= F.x + F.w + 5:
            line(c, x, F.y + F.h, x, F.y + F.h + 8, FAINT, 1.5, a)
            text(c, lab, x, F.y + F.h + 32, size, 'med', MUTED, 'c', a)

def candles(c, F, O, Hh, L, C, n, start=0, a=1.0, wfrac=.62, up=GREEN, dn=RED, hollow=False, grow=True, colors=None):
    """draw candles start..start+n (n may be fractional; last candle grows)."""
    bw = max(1.5, F.bw() * wfrac)
    end = min(len(C), start + int(math.ceil(n)))
    for i in range(start, end):
        f = 1.0
        if grow and i == start + int(math.ceil(n)) - 1 and n % 1: f = n % 1
        o, h, l, cl = O[i], Hh[i], L[i], C[i]
        x = F.X(i)
        k = colors[i] if colors else (up if cl >= o else dn)
        mid = (o + cl) / 2
        hh, ll = lerp(mid, h, f), lerp(mid, l, f)
        line(c, x, F.Y(hh), x, F.Y(ll), k, max(1.2, bw * .16), a, cap=cairo.LINE_CAP_BUTT)
        yt, yb = F.Y(lerp(mid, max(o, cl), f)), F.Y(lerp(mid, min(o, cl), f))
        c.rectangle(x - bw / 2, yt, bw, max(1.5, yb - yt)); col(c, k, a); c.fill()

def ohlc(c, F, O, Hh, L, C, n, start=0, a=1.0, cl=INK, lw=3, tick=None):
    tick = tick or F.bw() * .32
    for i in range(start, min(len(C), start + int(math.ceil(n)))):
        x = F.X(i)
        line(c, x, F.Y(Hh[i]), x, F.Y(L[i]), cl, lw, a, cap=cairo.LINE_CAP_BUTT)
        line(c, x - tick, F.Y(O[i]), x, F.Y(O[i]), cl, lw, a, cap=cairo.LINE_CAP_BUTT)
        line(c, x, F.Y(C[i]), x + tick, F.Y(C[i]), cl, lw, a, cap=cairo.LINE_CAP_BUTT)

def series(c, F, xs, ys, p=1.0, cl=NAVY, lw=3.5, a=1.0, fill=None, fill_a=.16, dash=None):
    pts = [F.P(x, y) for x, y in zip(xs, ys)]
    if p <= 0 or len(pts) < 2: return None
    k = (len(pts) - 1) * clamp(p); n = int(k)
    vis = pts[:n + 1]
    if n < len(pts) - 1:
        f = k - n; vis.append((lerp(pts[n][0], pts[n + 1][0], f), lerp(pts[n][1], pts[n + 1][1], f)))
    if fill is not None and len(vis) > 1:
        c.new_path(); c.move_to(vis[0][0], F.y + F.h)
        for q in vis: c.line_to(*q)
        c.line_to(vis[-1][0], F.y + F.h); c.close_path()
        g = cairo.LinearGradient(0, F.y, 0, F.y + F.h); g.add_color_stop_rgba(0, *fill, fill_a * a); g.add_color_stop_rgba(1, *fill, 0)
        c.set_source(g); c.fill()
    c.new_path(); c.move_to(*vis[0])
    for q in vis[1:]: c.line_to(*q)
    col(c, cl, a); c.set_line_width(lw); c.set_line_join(cairo.LINE_JOIN_ROUND); c.set_line_cap(cairo.LINE_CAP_ROUND)
    if dash: c.set_dash(dash)
    c.stroke(); c.set_dash([])
    return vis[-1]

def vbars(c, F, V, n, start=0, a=1.0, colors=None, cl=FAINT, wfrac=.62, vmax=None):
    vmax = vmax or max(V[start:start + max(1, int(n))] or [1])
    bw = max(1.5, F.bw() * wfrac)
    for i in range(start, min(len(V), start + int(math.ceil(n)))):
        h = V[i] / vmax * F.h
        c.rectangle(F.X(i) - bw / 2, F.y + F.h - h, bw, h); col(c, colors[i] if colors else cl, a); c.fill()

def hline(c, F, p, i0=None, i1=None, cl=GOLD, lw=3, a=1.0, prog=1.0, dash=None, label=None, lab_side='r', lab_bg=None, size=20):
    x0 = F.x if i0 is None else F.X(i0); x1 = F.x + F.w if i1 is None else F.X(i1)
    y = F.Y(p)
    line(c, x0, y, lerp(x0, x1, prog), y, cl, lw, a, dash)
    if label and prog > .6:
        la = a * clamp((prog - .6) / .4)
        if lab_side == 'r': tag(c, x1 + 8, y - size * .9, label, lab_bg or cl, WHITE, size, la, 'l')
        else: tag(c, x0 - 8, y - size * .9, label, lab_bg or cl, WHITE, size, la, 'r')
    return y

def seg(c, F, i1, p1, i2, p2, cl=BLUE, lw=3.5, a=1.0, prog=1.0, dash=None, ext=0.0):
    x1, y1 = F.P(i1, p1); x2, y2 = F.P(i2, p2)
    if ext:
        x2, y2 = x1 + (x2 - x1) * (1 + ext), y1 + (y2 - y1) * (1 + ext)
    line(c, x1, y1, x2, y2, cl, lw, a, dash, prog)

def zone(c, F, i0, i1, p0, p1, cl=GOLD, a=.15):
    x0, x1 = (F.x if i0 is None else F.X(i0)), (F.x + F.w if i1 is None else F.X(i1))
    y0, y1 = F.Y(max(p0, p1)), F.Y(min(p0, p1))
    c.rectangle(x0, y0, x1 - x0, y1 - y0); col(c, cl, a); c.fill()

def measure(c, x, y1, y2, cl=GOLD, a=1.0, p=1.0, label=None, side='r', lw=3.5, size=22):
    if p <= 0: return
    ym = lerp(y1, y2, p)
    arrow(c, x, y1, x, ym, cl, lw, a, 1, 13)
    line(c, x - 12, y1, x + 12, y1, cl, lw, a)
    if label and p > .7:
        la = a * clamp((p - .7) / .3)
        yy = (y1 + ym) / 2 - size * .9
        tag(c, x + (14 if side == 'r' else -14), yy, label, cl, WHITE, size, la, 'l' if side == 'r' else 'r')

def path_ohlc(keys, n, seed=1, noise=.012, wick=.010, span=None):
    """keys: [(u,price)] u in [0,1]. Returns O,H,L,C with closes following the piecewise-linear path."""
    rnd = random.Random(seed)
    span = span or (max(k[1] for k in keys) - min(k[1] for k in keys))
    def at(u):
        for j in range(len(keys) - 1):
            if keys[j][0] <= u <= keys[j + 1][0]:
                f = (u - keys[j][0]) / max(1e-9, keys[j + 1][0] - keys[j][0])
                return lerp(keys[j][1], keys[j + 1][1], f)
        return keys[-1][1]
    C = []
    for i in range(n):
        u = i / (n - 1); base = at(u)
        near_key = min(abs(u - k[0]) for k in keys) < .5 / n
        C.append(base + (0 if near_key else rnd.gauss(0, noise * span)))
    O = [C[0] - (C[1] - C[0]) * .5] + C[:-1]
    O = [o + rnd.gauss(0, noise * .4 * span) for o in O]
    Hh = [max(o, cl) + abs(rnd.gauss(0, wick * span)) + wick * .3 * span for o, cl in zip(O, C)]
    L = [min(o, cl) - abs(rnd.gauss(0, wick * span)) - wick * .3 * span for o, cl in zip(O, C)]
    return O, Hh, L, C

def path_line(keys, n):
    out = []
    for i in range(n):
        u = i / (n - 1)
        for j in range(len(keys) - 1):
            if keys[j][0] <= u <= keys[j + 1][0]:
                f = (u - keys[j][0]) / max(1e-9, keys[j + 1][0] - keys[j][0]); out.append(lerp(keys[j][1], keys[j + 1][1], f)); break
        else: out.append(keys[-1][1])
    return out

def fmt_k(v):
    return f'${v/1000:,.0f}k' if v >= 1000 else f'${v:,.0f}'

def nice_ticks(lo, hi, n=5):
    span = hi - lo; raw = span / n
    mag = 10 ** math.floor(math.log10(raw)); step = min((1, 2, 2.5, 5, 10), key=lambda m: abs(m * mag - raw)) * mag
    v = math.ceil(lo / step) * step; out = []
    while v <= hi + 1e-9: out.append(v); v += step
    return out

def log_ticks(lo, hi, steps=(1, 2, 5)):
    out = []; e = math.floor(math.log10(lo))
    while 10 ** e <= hi * 1.0001:
        for m in steps:
            v = m * 10 ** e
            if lo <= v <= hi: out.append(v)
        e += 1
    return out

def counter(c, t, t0, d, v0, v1, x, y, size, fmt=lambda v: f'{v:,.0f}', font='head', cl=INK, align='c', a=1.0):
    v = lerp(v0, v1, P(t, t0, d, eio))
    return text(c, fmt(v), x, y, size, font, cl, align, a)
