"""Shared scene helpers: pivots, mini pattern sketches, temple pillars, crowds, step indicators."""
from engine import *

def pivots(H_, L_, pct=0.08):
    """zigzag swing points on highs/lows: list of (i, price, 'H'|'L')."""
    out = []; mode = None
    hi_i = lo_i = 0; hi, lo = H_[0], L_[0]
    for i in range(1, len(H_)):
        if mode is None:
            if H_[i] > hi: hi_i, hi = i, H_[i]
            if L_[i] < lo: lo_i, lo = i, L_[i]
            if hi > lo * (1 + pct):
                if lo_i < hi_i: out.append((lo_i, lo, 'L')); mode = 'up'
                else: out.append((hi_i, hi, 'H')); mode = 'down'
        elif mode == 'up':
            if H_[i] > hi: hi_i, hi = i, H_[i]
            elif L_[i] < hi * (1 - pct): out.append((hi_i, hi, 'H')); mode = 'down'; lo_i, lo = i, L_[i]
        else:
            if L_[i] < lo: lo_i, lo = i, L_[i]
            elif H_[i] > lo * (1 + pct): out.append((lo_i, lo, 'L')); mode = 'up'; hi_i, hi = i, H_[i]
    return out

PATTERNS = {
    'hs': [(0, .25), (.15, .62), (.25, .45), (.42, .9), (.58, .45), (.72, .66), (.85, .38), (1, .12)],
    'ihs': [(0, .75), (.15, .38), (.25, .55), (.42, .1), (.58, .55), (.72, .34), (.85, .62), (1, .88)],
    'dtop': [(0, .2), (.25, .85), (.5, .45), (.75, .85), (1, .15)],
    'dbot': [(0, .8), (.25, .15), (.5, .55), (.75, .15), (1, .85)],
    'ttop': [(0, .2), (.18, .85), (.34, .45), (.5, .85), (.66, .45), (.82, .85), (1, .12)],
    'tri': [(0, .1), (.2, .9), (.4, .25), (.58, .75), (.74, .4), (.86, .6), (1, .95)],
    'flag': [(0, .05), (.4, .85), (.52, .72), (.6, .8), (.72, .66), (.8, .74), (1, 1)],
    'up': [(0, .1), (.2, .45), (.32, .3), (.55, .7), (.67, .55), (.9, .95), (1, .85)],
    'down': [(0, .9), (.2, .55), (.32, .7), (.55, .3), (.67, .45), (.9, .05), (1, .15)],
    'side': [(0, .5), (.15, .8), (.3, .25), (.48, .78), (.64, .22), (.82, .8), (1, .5)],
    'vbot': [(0, .9), (.45, .08), (1, .9)],
    'saucer': None,
    'wedge': [(0, .2), (.15, .55), (.3, .4), (.45, .7), (.6, .58), (.75, .8), (.88, .74), (1, .3)],
    'bcast': [(0, .5), (.15, .62), (.3, .4), (.48, .75), (.64, .25), (.82, .9), (1, .1)],
}

def pattern_pts(kind, x, y, w, h):
    if kind == 'saucer':
        return [(x + w * u / 30, y + h * (.15 + .7 * math.sin(math.pi * u / 30))) for u in range(31)]
    return [(x + u * w, y + (1 - v) * h) for u, v in PATTERNS[kind]]

def mini_pattern(c, kind, x, y, w, h, cl=NAVY, p=1.0, a=1.0, lw=5):
    return polyline(c, pattern_pts(kind, x, y, w, h), cl, lw, a, p)

def temple(c, t, x, y, w, labels, starts, roof_t, a=1.0, roof_label='TECHNICAL ANALYSIS'):
    """three pillars that rise at starts[i]; roof drops at roof_t."""
    n = len(labels); colw = w / n
    base_y = y + 420
    rrect(c, x - 30, base_y, w + 60, 26, 6); col(c, NAVY, a * P(t, starts[0] - .4, .5)); c.fill()
    rrect(c, x - 10, base_y - 14, w + 20, 18, 5); col(c, mix(NAVY, WHITE, .2), a * P(t, starts[0] - .4, .5)); c.fill()
    for i, lab in enumerate(labels):
        k = P(t, starts[i], .8, eo)
        cx = x + colw * (i + .5)
        hh = 300 * k
        pw = 170
        c.rectangle(cx - pw / 2, base_y - 14 - hh, pw, hh); col(c, CARD, a); c.fill()
        for f in range(-3, 4): line(c, cx + f * 22, base_y - 14 - hh + 10, cx + f * 22, base_y - 24, GRID, 4, a * k)
        c.rectangle(cx - pw / 2, base_y - 14 - hh, pw, hh); col(c, mix(LINE, NAVY, .25), a * k); c.set_line_width(2); c.stroke()
        rrect(c, cx - pw / 2 - 16, base_y - 14 - hh - 22, pw + 32, 24, 5); col(c, GOLD, a * k); c.fill()
        circle(c, cx, base_y - 14 - hh + 62, 36, NAVY, a * k)
        text(c, str(i + 1), cx, base_y - 14 - hh + 77, 40, 'head', WHITE, 'c', a * k)
        la = P(t, starts[i] + .3, .5) * a * k
        lines = lab.split('\n')
        bw_ = max(tw(c, ln, 24, 'semi') for ln in lines) + 36
        card(c, cx - bw_ / 2, base_y - 14 - hh + 118, bw_, 30 * len(lines) + 30, 12, CARD, la)
        for j, ln in enumerate(lines):
            text(c, ln, cx, base_y - 14 - hh + 150 + j * 30, 24, 'semi', INK, 'c', la)
    r = P(t, roof_t, .7, eo)
    if r > 0:
        ry = y - 40 - (1 - r) * 60
        c.new_path(); c.move_to(x - 40, ry + 100); c.line_to(x + w / 2, ry); c.line_to(x + w + 40, ry + 100); c.close_path()
        col(c, NAVY, a * r); c.fill()
        text(c, roof_label, x + w / 2, ry + 82, 26, 'semi', LGOLD, 'c', a * r, ls=4)

def crowd(c, t, x, y, n, s=.6, moods=None, a=1.0, gap=110, seed=0):
    shirts = [BLUE, GREEN, RED, GOLD, NAVY, hexc('#7A8794')]
    styles = ['short', 'long', 'curly', 'side', 'bun', 'bald']
    for i in range(n):
        m = moods[i] if moods else 'smile'
        avatar(c, x + i * gap, y + (i % 2) * 18 * s, s, SKIN[(i + seed) % len(SKIN)], HAIR[(i * 2 + seed) % len(HAIR)],
               shirts[(i + seed) % len(shirts)], styles[(i + seed) % len(styles)], mood=m, t=t, seed=i + seed, a=a)

def steps(c, labels, cur, x=1800, y=290, a=1.0):
    """small numbered step indicator, right aligned."""
    n = len(labels)
    for i in range(n):
        xx = x - (n - 1 - i) * 54
        on = i <= cur
        circle(c, xx, y, 20, GOLD if i == cur else (NAVY if on else CARD), a)
        if not on: ring(c, xx, y, 20, FAINT, 2, a)
        text(c, str(i + 1), xx, y + 8, 22, 'head', WHITE if on else MUTED, 'c', a)

def stage(t, b, i0, i1=None, fin=.5, fout=.4):
    """alpha for content shown from beat i0 until beat i1."""
    a = P(t, b[i0], fin)
    if i1 is not None: a *= 1 - P(t, b[i1] - .25, fout)
    return a

def label_card(c, x, y, w, h, title, body=None, a=1.0, accent=GOLD, size=30, bsize=24, fill=CARD, border=None):
    card(c, x, y, w, h, 20, fill, a, border=border)
    c.save(); rrect(c, x, y, w, h, 20); c.clip(); c.rectangle(x, y, 8, h); col(c, accent, a); c.fill(); c.restore()
    text(c, title, x + 32, y + 22 + size, size, 'bold', INK, 'l', a)
    if body: para(c, body, x + 32, y + 30 + size + bsize * 1.4, bsize, 'med', MUTED, w - 60, 1.3, 'l', a)

def mini_chart_card(c, x, y, w, h, kind, a=1.0, cl=NAVY, title=None, p=1.0, border=None):
    card(c, x, y, w, h, 18, CARD, a, border=border)
    if title: text(c, title, x + w / 2, y + h - 22, 22, 'semi', INK, 'c', a)
    mini_pattern(c, kind, x + 26, y + 26, w - 52, h - (80 if title else 52), cl, p, a, 4)
