from engine import *
from . import scene
from .common import *
from .data import nifty_d20, idx

def key_index(keys, u, n): return int(round(u * (n - 1)))

HS_KEYS = [(0, 30), (.05, 36), (.13, 62), (.22, 48), (.38, 82), (.5, 48.5), (.63, 64), (.74, 49), (.79, 40), (.86, 48), (1, 24)]
HS_N = 64
HS = path_ohlc(HS_KEYS, HS_N, 7, .012, .012)
NECK = lambda i: 48.2 + (48.8 - 48.2) * (i - 14) / 33

def hs_frame(): return Frame(230, 330, 1240, 400, -1, HS_N, 18, 90)

def draw_volume(c, V, n, F, a, cols=None):
    vbars(c, F, V, n, 0, a, cols or [FAINT] * len(V), vmax=max(V))

# ------------------------------------------------------------ 5.1 overview & rules
@scene('c5s1')
def c5s1(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        for i, (ttl, sub, kind, cl) in enumerate([('REVERSAL', 'The trend is turning', 'rev', RED), ('CONTINUATION', 'A pause, then the trend resumes', 'cont', GREEN)]):
            x = 220 + i * 760
            with pop(c, t, b[1] + i * b.d[1] * .45, x + 350, 560) as a:
                card(c, x, 340, 700, 440, 26, CARD, a * a1)
                text(c, ttl, x + 350, 410, 40, 'head', cl, 'c', a * a1, ls=4)
                text(c, sub, x + 350, 455, 26, 'semi', MUTED, 'c', a * a1)
                if kind == 'rev': polyline(c, [(x + 100, 720), (x + 260, 560), (x + 350, 520), (x + 440, 560), (x + 600, 720)], NAVY, 7, a * a1, P(t, b[1] + .3 + i, 1))
                else: polyline(c, [(x + 90, 730), (x + 260, 580), (x + 300, 610), (x + 340, 580), (x + 380, 610), (x + 420, 580), (x + 610, 500)], NAVY, 7, a * a1, P(t, b[1] + .3 + i * b.d[1] * .45, 1))
    a2 = stage(t, b, 2, 3)
    if a2 > 0:
        kinds = [('hs', 'Head & shoulders'), ('ttop', 'Triple top'), ('dtop', 'Double top'), ('vbot', 'Spike (V)'), ('saucer', 'Rounding (saucer)')]
        for i, (k, lab) in enumerate(kinds):
            x = 150 + i * 330
            with pop(c, t, b[2] + .2 + i * .35, x + 150, 560) as a:
                mini_chart_card(c, x, 400, 300, 300, k, a * a2, NAVY, lab, P(t, b[2] + .4 + i * .35, 1))
        text(c, 'Five major reversal patterns', 960, 790, 32, 'serif', MUTED, 'c', P(t, b[2] + 2, .5) * a2)
    aR = P(t, b[3], .5)
    if aR > 0:
        rules = [('There must be a prior trend', b[4]), ('First signal: an important trendline breaks', b[5]), ('The bigger the pattern, the bigger the move', b[6]),
                 ('Tops: shorter and more volatile', b[7]), ('Bottoms: smaller ranges, take longer', b[7] + b.d[7] * .5), ('Volume matters more on the upside', b[8])]
        cur = max([i for i, (_, t0) in enumerate(rules) if t >= t0 - .1] or [-1])
        for i, (txt, t0) in enumerate(rules):
            y = 300 + i * 98
            with rise(c, t, t0) as a:
                on = i == cur
                card(c, 150, y, 860, 82, 18, NAVY if on else CARD, a * aR)
                circle(c, 196, y + 41, 24, GOLD, a * aR)
                text(c, str(i + 1), 196, y + 50, 26, 'head', WHITE, 'c', a * aR)
                text(c, txt, 236, y + 52, 27, 'semi', WHITE if on else INK, 'l', a * aR)
        pa = aR * P(t, b[4] - .2, .4)
        card(c, 1060, 300, 700, 570, 26, CARD, pa)
        X0, Y0 = 1100, 340
        ill = cur
        k = P(t, rules[max(cur, 0)][1], .9)
        if ill == 0:
            polyline(c, [(X0 + 20, Y0 + 460), (X0 + 260, Y0 + 220), (X0 + 330, Y0 + 260), (X0 + 400, Y0 + 160), (X0 + 470, Y0 + 270), (X0 + 620, Y0 + 420)], NAVY, 6, pa, k)
            tag(c, X0 + 150, Y0 + 260, 'prior uptrend', GREEN, WHITE, 22, pa * k, 'c')
        elif ill == 1:
            polyline(c, [(X0 + 20, Y0 + 460), (X0 + 160, Y0 + 300), (X0 + 210, Y0 + 350), (X0 + 360, Y0 + 180), (X0 + 420, Y0 + 260), (X0 + 500, Y0 + 230), (X0 + 620, Y0 + 400)], NAVY, 6, pa)
            line(c, X0 + 20, Y0 + 470, X0 + 620, Y0 + 150, GREEN, 5, pa, p=k)
            badge(c, X0 + 545, Y0 + 205, 22, 'no', pa * P(t, rules[1][1] + .8, .4))
        elif ill == 2:
            mini_pattern(c, 'hs', X0 + 20, Y0 + 40, 340, 230, NAVY, 1, pa, 5)
            arrow(c, X0 + 360, Y0 + 230, X0 + 360, Y0 + 480, RED, 7, pa, k, 22)
            mini_pattern(c, 'hs', X0 + 430, Y0 + 210, 160, 90, NAVY, 1, pa, 4)
            arrow(c, X0 + 600, Y0 + 300, X0 + 600, Y0 + 370, RED, 5, pa, k, 16)
        elif ill in (3, 4):
            polyline(c, [(X0 + 20, Y0 + 300), (X0 + 120, Y0 + 60), (X0 + 160, Y0 + 200), (X0 + 210, Y0 + 40), (X0 + 260, Y0 + 290)], RED, 6, pa)
            text(c, 'TOP: fast, volatile', X0 + 140, Y0 + 350, 24, 'bold', RED, 'c', pa)
            pts = [(X0 + 330 + u * 3, Y0 + 260 + 120 * math.sin(math.pi * u / 90) + 8 * math.sin(u * .4)) for u in range(91)]
            polyline(c, pts, GREEN, 6, pa * (P(t, rules[4][1], .5) if ill == 4 else .25))
            text(c, 'BOTTOM: wide, slow', X0 + 470, Y0 + 460, 24, 'bold', GREEN, 'c', pa * (P(t, rules[4][1], .5) if ill == 4 else .25))
        elif ill == 5:
            pts = [(X0 + 30 + u * 5, Y0 + 230 + 70 * math.sin(math.pi * u / 80)) for u in range(81)] + [(X0 + 460, Y0 + 120), (X0 + 600, Y0 + 40)]
            polyline(c, pts, NAVY, 6, pa)
            V = [3, 3, 2.5, 2, 2, 1.8, 2, 2.5, 3, 7, 9]
            for q, v in enumerate(V):
                c.rectangle(X0 + 40 + q * 52, Y0 + 520 - v * 18, 36, v * 18); col(c, GREEN if q >= 9 else FAINT, pa * P(t, rules[5][1] + q * .08, .3)); c.fill()
            tag(c, X0 + 540, Y0 + 300, 'Breakout volume', GREEN, WHITE, 22, pa * P(t, rules[5][1] + 1.2, .4), 'c')

# ------------------------------------------------------------ 5.2 head & shoulders top
def hs_upto(t, b):
    marks = [(0, 0), (b[1], .2), (b[2], .52), (b[3], .72), (b[6], .82), (b[7], .9), (b[8], 1.0)]
    u = 0
    for (t0, u0), (t1, u1) in zip(marks, marks[1:]):
        if t >= t0: u = lerp(u0, u1, P(t, t0, min(2.5, max(.5, (t1 - t0) * .7))))
    return u * HS_N

@scene('c5s2')
def c5s2(c, t, b):
    O, Hh, L, C = HS
    F = hs_frame(); Vf = Frame(230, 760, 1240, 90, -1, HS_N, 0, 1)
    a = P(t, .3, .5)
    card(c, 180, 300, 1340, 580, 24, CARD, a)
    k = hs_upto(t, b)
    candles(c, F, O, Hh, L, C, k, a=a)
    ils, ih, irs = key_index(HS_KEYS, .13, HS_N), key_index(HS_KEYS, .38, HS_N), key_index(HS_KEYS, .63, HS_N)
    for lab, i, t0, cl in (('LEFT SHOULDER', ils, b[1] + .5, NAVY), ('HEAD', ih, b[2] + .8, NAVY), ('RIGHT SHOULDER', irs, b[3] + .8, RED)):
        la = P(t, t0, .4) * a
        tag(c, F.X(i), F.Y(Hh[i]) - 58, lab, cl, WHITE, 20, la, 'c', point=(F.X(i), F.Y(Hh[i]) - 8))
    na = P(t, b[4], .5) * a
    seg(c, F, 10, NECK(10), 58, NECK(58), GOLD, 4, na, P(t, b[4], 1.0))
    text(c, 'NECKLINE', F.X(10), F.Y(NECK(10)) + 34, 22, 'head', GOLD, 'l', na, ls=2)
    va = P(t, b[5], .5) * a
    if va > 0:
        V = [1.0 + .3 * math.sin(i) for i in range(HS_N)]
        for i in range(HS_N):
            u = i / (HS_N - 1)
            V[i] = (1.6 if u < .14 else 1.1 if u < .4 else .8 if u < .65 else .55 if u < .74 else 1.8 if u < .8 else 1.0) + .15 * math.sin(i * 1.7)
        cols = [GREEN if C[i] >= O[i] else RED for i in range(HS_N)]
        vbars(c, Vf, V, min(k, HS_N), 0, va, cols, vmax=2.1)
        text(c, 'VOLUME', 236, 754, 16, 'semi', MUTED, 'l', va, ls=3)
        for q, (u, lab) in enumerate(((.1, 'heavy'), (.38, 'lighter'), (.63, 'lighter still'))):
            text(c, lab, F.X(u * (HS_N - 1)), 740, 20, 'semi', [GREEN, GOLD, RED][q], 'c', P(t, b[5] + .6 + q * .5, .4) * a)
    ca = P(t, b[6] + 1.0, .5) * a
    ib = key_index(HS_KEYS, .79, HS_N)
    if ca > 0:
        glow_dot(c, F.X(ib - 1), F.Y(C[ib - 1]), 9, RED, t, ca)
        tag(c, 1650, 470, 'Close below neckline', RED, WHITE, 24, ca, 'c')
        tag(c, 1650, 520, '= pattern complete', RED, WHITE, 24, ca, 'c')
    pre = P(t, b[6] - .3, .4) * (1 - P(t, b[6] + .8, .4)) * a
    tag(c, 1650, 470, 'Before the break:', MUTED, WHITE, 24, pre, 'c'); tag(c, 1650, 520, 'just a possibility', MUTED, WHITE, 24, pre, 'c')
    ra = P(t, b[7] + .8, .5) * a
    ir = key_index(HS_KEYS, .86, HS_N)
    if ra > 0:
        curved_arrow(c, F.X(ib) + 10, F.Y(L[ib]) + 30, F.X(ir), F.Y(Hh[ir]) + 14, -.3, GOLD, 4, ra, P(t, b[7] + .8, .6))
        tag(c, 1650, 600, 'Return move:', GOLD, WHITE, 24, ra, 'c'); tag(c, 1650, 650, 'neckline = resistance', GOLD, WHITE, 24, ra, 'c')
    sa = P(t, b[8] + .6, .5) * a
    if sa > 0:
        for lab, i, p_, cl in (('Higher high', ih, Hh[ih], GREEN), ('Lower high', irs, Hh[irs], RED)):
            text(c, lab, F.X(i) + 90, F.Y(p_) + 4, 22, 'bold', cl, 'l', sa)
        text(c, 'Lower low', F.X(HS_N - 3), F.Y(L[HS_N - 3]) + 40, 22, 'bold', RED, 'c', sa)

# ------------------------------------------------------------ 5.3 measuring
MS_KEYS = [(0, 92), (.12, 108), (.22, 100), (.38, 120), (.5, 100), (.63, 110), (.74, 100.3), (.8, 96), (.86, 100), (1, 76)]
MS = path_ohlc(MS_KEYS, 56, 3, .010, .008)

@scene('c5s3')
def c5s3(c, t, b):
    O, Hh, L, C = MS; n = 56
    aM = 1 - P(t, b[5] - .3, .4)
    if aM > 0:
        F = Frame(250, 330, 1200, 520, -1, n, 70, 126)
        card(c, 190, 300, 1330, 580, 24, CARD, aM)
        ygrid(c, F, [80, 90, 100, 110, 120], fmt=lambda v: f'{v:.0f}', a=aM)
        kk = n * min(1, .82 + .18 * P(t, b[4], 1.5)) if t > b[4] else n * .82 * P(t, .3, 1.2)
        if t > b[6] - .3 and t < b[7] + 2: kk = n * .82
        candles(c, F, O, Hh, L, C, kk, a=aM)
        hline(c, F, 100, 8, n - 1, GOLD, 4, aM)
        text(c, 'NECKLINE', F.X(9), F.Y(100) + 30, 20, 'head', GOLD, 'l', aM, ls=2)
        ih = key_index(MS_KEYS, .38, n); ib = key_index(MS_KEYS, .75, n)
        m1 = P(t, b[1], .8) * aM
        measure(c, F.X(ih), F.Y(120), F.Y(100), RED, m1, P(t, b[1], .8), 'height 20', 'r')
        m2 = P(t, b[2], .8) * aM
        line(c, F.X(ih) + 14, F.Y(120), F.X(ib), F.Y(120), RED, 1.5, m2 * .5, [4, 6])
        measure(c, F.X(ib), F.Y(100), F.Y(80), RED, m2, P(t, b[2] + .2, 1.0), '-20', 'r')
        ta = P(t, b[2] + 1.2, .5) * aM
        hline(c, F, 80, ib - 2, n - 1, RED, 4, ta, dash=[12, 8], label='Target 80')
        nums = P(t, b[3], .5) * aM
        if nums > 0:
            card(c, 1580, 360, 200, 300, 22, NAVY, nums)
            for q, (lab, v, cl) in enumerate((('Head', '120', WHITE), ('Neckline', '100', LGOLD), ('Height', '20', WHITE), ('Target', '80', GOLD))):
                ya = P(t, b[3] + q * .5, .4) * nums
                text(c, lab, 1604, 410 + q * 66, 22, 'semi', LGOLD, 'l', ya)
                text(c, v, 1750, 412 + q * 66, 32, 'head', cl, 'r', ya)
        mi = P(t, b[4], .5) * aM
        if mi > 0:
            with pop(c, t, b[4], 1670, 760) as aa:
                rrect(c, 1580, 710, 200, 90, 14); col(c, RED, aa * mi); c.set_line_width(5); c.stroke()
                text(c, 'MINIMUM', 1680, 770, 32, 'head', RED, 'c', aa * mi, ls=2)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        for i, (ttl, sub, sl, cl) in enumerate([('Up-sloping neckline', 'common', -1, NAVY), ('Down-sloping neckline', 'even weaker', 1, RED)]):
            x = 220 + i * 760
            with pop(c, t, b[5] + i * b.d[5] * .4, x + 350, 560) as aa:
                card(c, x, 330, 700, 480, 24, CARD, aa * a5, border=cl if i else None, bw=3)
                text(c, ttl, x + 350, 390, 32, 'bold', cl, 'c', aa * a5)
                text(c, sub, x + 350, 430, 24, 'semi', MUTED, 'c', aa * a5)
                ny = lambda xx: 640 + sl * (xx - (x + 400)) * .14
                pts = [(x + 60, 740), (x + 150, ny(x + 150) - 90), (x + 220, ny(x + 220)), (x + 320, ny(x + 320) - 170), (x + 410, ny(x + 410)), (x + 500, ny(x + 500) - 80), (x + 600, ny(x + 600) + 50), (x + 640, ny(x + 640) + 100)]
                polyline(c, pts, NAVY, 5, aa * a5)
                line(c, x + 140, ny(x + 140), x + 660, ny(x + 660), GOLD, 4, aa * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        F = Frame(250, 330, 1200, 520, -1, n, 70, 126)
        card(c, 190, 300, 1330, 580, 24, CARD, a6)
        hline(c, F, 100, 8, n - 1, GOLD, 4, a6)
        k0 = int(n * .82)
        Cf = C[:k0] + [100 + q * 2.4 for q in range(n - k0)]
        Of = O[:k0] + [Cf[k0 - 1 + q] for q in range(n - k0)]
        Hf = Hh[:k0] + [max(Of[k0 + q], Cf[k0 + q]) + 1 for q in range(n - k0)]
        Lf = L[:k0] + [min(Of[k0 + q], Cf[k0 + q]) - 1 for q in range(n - k0)]
        candles(c, F, Of, Hf, Lf, Cf, k0 + (n - k0) * P(t, b[6] + .5, 1.6), a=a6)
        fa = P(t, b[6] + 1.6, .5) * a6
        tag(c, 1650, 470, 'Back above the neckline', GREEN, WHITE, 24, fa, 'c')
        tag(c, 1650, 520, '= failed pattern', GREEN, WHITE, 24, fa, 'c')
        arrow(c, F.X(n - 6), F.Y(104), F.X(n - 1), F.Y(118), GREEN, 6, fa, 1, 20)
        text(c, 'A failure is information too', 1650, 640, 26, 'serif', NAVY, 'c', P(t, b[7], .5))

# ------------------------------------------------------------ 5.4 inverse H&S
IH_KEYS = [(0, 80), (.13, 50), (.24, 62), (.38, 30), (.52, 62.5), (.64, 47), (.76, 63), (.84, 72), (.9, 66), (1, 92)]
IH = path_ohlc(IH_KEYS, 60, 9, .012, .012)

@scene('c5s4')
def c5s4(c, t, b):
    O, Hh, L, C = IH; n = 60
    aM = 1 - P(t, b[6] - .3, .4)
    if aM > 0:
        F = Frame(230, 330, 1240, 400, -1, n, 22, 100); Vf = Frame(230, 760, 1240, 90, -1, n, 0, 1)
        card(c, 180, 300, 1340, 580, 24, CARD, aM)
        kk = n * (.7 * P(t, .3, max(1, b[1] + 3)) if t < b[2] else .7 + .3 * P(t, b[3], 2))
        candles(c, F, O, Hh, L, C, kk, a=aM)
        for lab, u in (('LEFT SHOULDER', .13), ('HEAD', .38), ('RIGHT SHOULDER', .64)):
            i = key_index(IH_KEYS, u, n); la = P(t, b[1] + (u - .1) * 4, .4) * aM
            tag(c, F.X(i), F.Y(L[i]) + 26, lab, NAVY, WHITE, 20, la, 'c')
        na = P(t, b[2], .5) * aM
        seg(c, F, 10, 62.2, 52, 62.8, GOLD, 4, na, P(t, b[2], 1), ext=.15)
        text(c, 'NECKLINE', F.X(12), F.Y(62.2) - 14, 22, 'head', GOLD, 'l', na, ls=2)
        ma = P(t, b[3] + .8, .5) * aM
        ih = key_index(IH_KEYS, .38, n); ib = key_index(IH_KEYS, .77, n)
        measure(c, F.X(ih), F.Y(30), F.Y(62.5), GREEN, ma, P(t, b[3] + .8, .6), 'height', 'r')
        measure(c, F.X(ib), F.Y(63), F.Y(95.5), GREEN, ma, P(t, b[3] + 1.4, .8), 'same height up', 'r')
        va = P(t, b[4], .5) * aM
        if va > 0:
            V = []
            for i in range(n):
                u = i / (n - 1)
                V.append((1.2 if u < .14 else .8 if u < .4 else 1.0 if u < .52 else .6 if u < .66 else 1.2 if u < .74 else 2.4 if u < .82 else 1.4) + .1 * math.sin(i * 1.9))
            cols = [GREEN if C[i] >= O[i] else RED for i in range(n)]
            vbars(c, Vf, V, kk, 0, va, cols, vmax=2.6)
            text(c, 'VOLUME', 236, 754, 16, 'semi', MUTED, 'l', va, ls=3)
            tag(c, Vf.X(ib + 1), Vf.y - 26, 'Volume expands on the breakout', GREEN, WHITE, 20, P(t, b[4] + 1.2, .4) * aM, 'c')
        wa = P(t, b[5], .5) * aM
        if wa > 0:
            card(c, 1560, 420, 240, 260, 20, LGOLD, wa, border=GOLD)
            warn(c, 1680, 490, .5, wa, GOLD)
            text(c, 'No volume?', 1680, 590, 26, 'bold', INK, 'c', wa)
            text(c, 'Much less', 1680, 625, 22, 'semi', MUTED, 'c', wa)
            text(c, 'trustworthy', 1680, 652, 22, 'semi', MUTED, 'c', wa)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        keys = [(0, 30), (.08, 58), (.14, 46), (.22, 60), (.3, 47), (.45, 85), (.6, 47), (.7, 60), (.78, 46), (.86, 58), (.92, 44), (1, 20)]
        F = Frame(260, 340, 1100, 420, 0, 1, 10, 95)
        card(c, 210, 300, 1200, 540, 24, CARD, a6)
        text(c, 'COMPLEX HEAD & SHOULDERS', 240, 345, 22, 'head', GOLD, 'l', a6, ls=3)
        polyline(c, [F.P(u, v) for u, v in keys], NAVY, 6, a6, P(t, b[6] + .2, 1.8))
        for q, (u, v) in enumerate(((.08, 58), (.22, 60))): pill(c, F.X(u), F.Y(v) - 46, 'LS', 18, BLUE, WHITE, P(t, b[6] + .8 + q * .2, .3) * a6, 'semi', 'c', ls=1)
        pill(c, F.X(.45), F.Y(85) - 46, 'HEAD', 18, NAVY, WHITE, P(t, b[6] + 1.3, .3) * a6, 'semi', 'c', ls=1)
        for q, (u, v) in enumerate(((.7, 60), (.86, 58))): pill(c, F.X(u), F.Y(v) - 46, 'RS', 18, BLUE, WHITE, P(t, b[6] + 1.6 + q * .2, .3) * a6, 'semi', 'c', ls=1)
        line(c, F.X(.12), F.Y(46.5), F.X(.94), F.Y(45.5), GOLD, 4, a6 * P(t, b[6] + 2, .4))
        ta = P(t, b[6] + b.d[6] * .6, .5)
        card(c, 1450, 420, 320, 260, 22, NAVY, ta)
        text(c, 'Two left', 1610, 500, 30, 'bold', WHITE, 'c', ta)
        text(c, 'shoulders?', 1610, 540, 30, 'bold', WHITE, 'c', ta)
        text(c, 'Expect two', 1610, 600, 30, 'bold', GOLD, 'c', ta)
        text(c, 'right ones', 1610, 640, 30, 'bold', GOLD, 'c', ta)

# ------------------------------------------------------------ 5.5 double & triple
DT_KEYS = [(0, 40), (.25, 85), (.42, 62), (.62, 84), (.78, 61.5), (.84, 55), (1, 36)]
DT = path_ohlc(DT_KEYS, 50, 4, .012, .012)

@scene('c5s5')
def c5s5(c, t, b):
    O, Hh, L, C = DT; n = 50
    aM = 1 - P(t, b[3] - .3, .4)
    if aM > 0:
        F = Frame(240, 330, 1160, 500, -1, n, 28, 92)
        card(c, 190, 300, 1290, 580, 24, CARD, aM)
        kk = n * (.7 * P(t, .3, max(1, b[1] + 2)) if t < b[2] else .7 + .3 * P(t, b[2] + .3, 1.6))
        candles(c, F, O, Hh, L, C, kk, a=aM)
        i1, i2, im = key_index(DT_KEYS, .25, n), key_index(DT_KEYS, .62, n), key_index(DT_KEYS, .42, n)
        la = P(t, b[1] + 1, .5) * aM
        tag(c, F.X(i1), F.Y(Hh[i1]) - 56, 'Peak 1', NAVY, WHITE, 20, la, 'c'); tag(c, F.X(i2), F.Y(Hh[i2]) - 56, 'Peak 2: fails', RED, WHITE, 20, la, 'c')
        text(c, 'M', 1640, 560, 160, 'head', GOLD, 'c', la * .9)
        ta = P(t, b[2], .5) * aM
        hline(c, F, 62, im, n - 1, GOLD, 4, ta, P(t, b[2], .8), label='Middle trough')
        ca = P(t, b[2] + 1.6, .4) * aM
        tag(c, 1640, 720, 'Close below = complete', RED, WHITE, 24, ca, 'c')
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        with pop(c, t, b[3], 560, 580) as aa:
            card(c, 220, 330, 680, 500, 24, CARD, aa * a3)
            text(c, 'DOUBLE BOTTOM', 560, 390, 30, 'head', GREEN, 'c', aa * a3, ls=3)
            mini_pattern(c, 'dbot', 290, 430, 540, 300, NAVY, P(t, b[3] + .3, 1.2), aa * a3, 6)
            line(c, 290 + 540 * .5 - 60, 430 + 300 * .45, 290 + 540, 430 + 300 * .45, GOLD, 4, aa * a3 * P(t, b[3] + 1.4, .4), [10, 8])
            text(c, 'W', 560, 800, 60, 'head', GOLD, 'c', aa * a3)
        ma = P(t, b[4], .5) * a3
        if ma > 0:
            card(c, 1000, 330, 700, 500, 24, CARD, ma)
            text(c, 'MEASURING', 1350, 390, 30, 'head', NAVY, 'c', ma, ls=3)
            mini_pattern(c, 'dtop', 1060, 440, 420, 260, NAVY, 1, ma, 5)
            measure(c, 1060 + 420 * .25, 440 + 260 * .15, 440 + 260 * .55, RED, ma, P(t, b[4] + .4, .6), 'height', 'r')
            measure(c, 1560, 440 + 260 * .55, 440 + 260 * .95, RED, ma, P(t, b[4] + 1.0, .8), 'same', 'l')
    a5 = stage(t, b, 5, 7)
    if a5 > 0:
        for i, (ttl, keys) in enumerate([('Second peak a little lower', [(0, 30), (.25, 85), (.5, 55), (.72, 80), (1, 25)]),
                                          ('Second peak pokes above, then fails', [(0, 30), (.25, 80), (.5, 55), (.72, 86), (1, 25)])]):
            x = 220 + i * 760
            with pop(c, t, b[5] + i * .5, x + 350, 560) as aa:
                card(c, x, 330, 700, 460, 24, CARD, aa * a5)
                text(c, ttl, x + 350, 390, 28, 'bold', NAVY, 'c', aa * a5)
                F = Frame(x + 60, 420, 580, 250, 0, 1, 20, 92)
                polyline(c, [F.P(u, v) for u, v in keys], NAVY, 5, aa * a5)
                line(c, F.X(.15), F.Y(80 if i else 85), F.X(.85), F.Y(80 if i else 85), FAINT, 2, aa * a5, [6, 6])
                if a5 and t > b[6]:
                    V = [6, 5, 4, 3.5, 2.5, 3, 2, 1.6, 4]
                    for q, v in enumerate(V):
                        c.rectangle(x + 80 + q * 62, 760 - v * 12, 40, v * 12); col(c, FAINT if q < 8 else RED, aa * a5 * P(t, b[6] + q * .06, .3)); c.fill()
        text(c, "Don't demand textbook symmetry", 960, 860, 30, 'serif', MUTED, 'c', P(t, b[5] + 1.4, .5) * a5 * (1 - P(t, b[6] - .2, .3)))
        tag(c, 960, 820, 'Volume: lighter on the second peak', NAVY, WHITE, 24, P(t, b[6] + .6, .5) * a5, 'c')
    a7 = P(t, b[7], .5)
    if a7 > 0:
        F = Frame(260, 350, 1100, 440, 0, 1, 10, 95)
        card(c, 210, 310, 1200, 540, 24, CARD, a7)
        text(c, 'TRIPLE TOP', 810, 350, 26, 'head', RED, 'c', a7, ls=3)
        keys = PATTERNS['ttop']
        polyline(c, [F.P(u, 10 + v * 85) for u, v in keys], NAVY, 6, a7, P(t, b[7] + .2, 1.6))
        line(c, F.X(.2), F.Y(10 + .45 * 85), F.X(1), F.Y(10 + .45 * 85), GOLD, 4, a7 * P(t, b[7] + 1.6, .4), [10, 8])
        tag(c, F.X(.86), F.Y(10 + .45 * 85) + 30, 'Breaks both troughs', RED, WHITE, 22, P(t, b[7] + 2, .4) * a7, 'c')
        ka = P(t, b[8], .5)
        card(c, 1450, 400, 320, 300, 22, NAVY, ka)
        text(c, 'Wait for', 1610, 500, 34, 'bold', WHITE, 'c', ka)
        text(c, 'the break', 1610, 545, 34, 'bold', GOLD, 'c', ka)
        text(c, 'that confirms', 1610, 600, 26, 'semi', LGOLD, 'c', ka)

# ------------------------------------------------------------ 5.6 saucers & V
@scene('c5s6')
def c5s6(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        F = Frame(280, 340, 1000, 330, 0, 60, 0, 100)
        card(c, 220, 300, 1120, 580, 24, CARD, a1)
        text(c, 'SAUCER  /  ROUNDING BOTTOM', 780, 345, 22, 'head', NAVY, 'c', a1, ls=3)
        ys = [70 - 55 * math.sin(math.pi * x / 60) + 2 * math.sin(x * 1.3) for x in range(61)]
        series(c, F, range(61), ys, P(t, b[1], 2.5), NAVY, 6, a1)
        V = [1.6 - 1.2 * math.sin(math.pi * x / 60) + .1 * math.sin(x) for x in range(61)]
        Vf = Frame(280, 700, 1000, 150, -.5, 60.5, 0, 1)
        vbars(c, Vf, V, 61 * P(t, b[1] + .4, 2.5), 0, a1, [BLUE] * 61, vmax=1.8)
        text(c, 'volume traces a saucer too', 1300, 780, 22, 'semi', BLUE, 'l', P(t, b[1] + 2.5, .4) * a1)
        pa = P(t, b[2], .5) * a1
        hourglass(c, 1560, 520, 1.1, t, pa)
        text(c, 'Slow. Hard to time.', 1560, 640, 26, 'bold', INK, 'c', pa)
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        card(c, 220, 300, 1120, 580, 24, CARD, a3)
        text(c, 'SPIKE  /  V-REVERSAL', 780, 345, 22, 'head', RED, 'c', a3, ls=3)
        F = Frame(280, 380, 1000, 440, 0, 40, 0, 100)
        ys = [92 - x * 4.4 if x < 20 else 4 + (x - 20) * 4.2 for x in range(41)]
        series(c, F, range(41), ys, P(t, b[3], 1.6), NAVY, 7, a3)
        ta = P(t, b[4] + .6, .5) * a3
        glow_dot(c, F.X(20), F.Y(4), 11, GOLD, t, ta)
        tag(c, F.X(20), F.Y(4) - 70, 'Often a reversal day', GOLD, WHITE, 22, ta, 'c')
        wa = P(t, b[4], .5) * a3
        card(c, 1400, 420, 340, 280, 22, LRED, wa, border=RED)
        warn(c, 1570, 490, .55, wa, RED)
        text(c, 'Hardest to trade:', 1570, 590, 26, 'bold', INK, 'c', wa)
        text(c, 'little or no warning', 1570, 628, 24, 'semi', MUTED, 'c', wa)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        d = nifty_d20(); s0, s1 = idx(d, '2020-02-17'), idx(d, '2020-04-30')
        O, Hh, L, C = d['o'], d['h'], d['l'], d['c']
        F = Frame(220, 340, 1280, 470, s0 - 1, s1 + 1, 7000, 12500)
        chart_card(c, F, a5, 'NIFTY 50', 'daily, Feb to Apr 2020', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [8000, 9000, 10000, 11000, 12000], a=a5)
        candles(c, F, O, Hh, L, C, (s1 - s0 + 1) * P(t, b[5] + .2, 1.6), start=s0, a=a5)
        i23, i24 = idx(d, '2020-03-23'), idx(d, '2020-03-24')
        ra = P(t, b[5] + 1.8, .5) * a5
        hline(c, F, C[i23], i23 - 3, i24 + 4, MUTED, 2, ra, dash=[6, 6])
        ring(c, F.X(i24), F.Y((Hh[i24] + L[i24]) / 2), 40, GOLD, 4, ra)
        tag(c, F.X(i24) + 210, F.Y(L[i24]) + 10, '24 Mar: new low 7,511', RED, WHITE, 20, ra, 'c')
        tag(c, F.X(i24) + 210, F.Y(L[i24]) - 40, 'closes 7,801 > prior 7,610', GREEN, WHITE, 20, P(t, b[5] + 2.4, .5) * a5, 'c')
        card(c, 1560, 430, 220, 200, 20, NAVY, P(t, b[5] + 3, .5))
        text(c, 'BOTTOM', 1670, 510, 26, 'head', GOLD, 'c', P(t, b[5] + 3, .5), ls=2)
        text(c, 'REVERSAL', 1670, 545, 26, 'head', GOLD, 'c', P(t, b[5] + 3, .5), ls=2)
        text(c, 'DAY', 1670, 580, 26, 'head', GOLD, 'c', P(t, b[5] + 3, .5), ls=2)
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        d = nifty_d20(); C = d['c']; n = len(C)
        F = Frame(220, 340, 1280, 470, 0, n - 1, 6500, 16500)
        chart_card(c, F, a6, 'NIFTY 50', 'daily close, 2020 to Feb 2021', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [8000, 10000, 12000, 14000, 16000], a=a6)
        series(c, F, range(n), C, P(t, b[6] + .2, 2.2), NAVY, 4, a6, BLUE, .15)
        tag(c, F.X(idx(d, '2020-03-23')) + 30, F.Y(7300), 'Just a V', RED, WHITE, 24, P(t, b[6] + 1.2, .5) * a6, 'l')
        ma = P(t, b[6] + 2.4, .5) * a6
        measure(c, F.X(n - 1) + 40, F.Y(7610), F.Y(15315), GREEN, ma, P(t, b[6] + 2.4, .8), 'x2 in < 1 year', 'l')
    a7 = P(t, b[7], .5)
    if a7 > 0:
        with pop(c, t, b[7], 960, 580) as aa:
            card(c, 300, 400, 1320, 340, 26, NAVY, aa * a7)
            text(c, 'Patterns are tools, not guarantees.', 960, 520, 50, 'serif', WHITE, 'c', aa * a7)
            text(c, 'Recognise the new trend quickly. Do not argue with it.', 960, 600, 34, 'serif', LGOLD, 'c', aa * a7)
