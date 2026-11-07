from engine import *
from . import scene
from .common import *

# ------------------------------------------------------------ 6.1 symmetrical triangle
ST_KEYS = [(0, 22), (.28, 70), (.36, 49.5), (.46, 66), (.54, 53.6), (.58, 63.2), (.62, 55.6), (.645, 62.2), (.72, 72), (1, 90)]
ST_N = 76
ST = path_ohlc(ST_KEYS, ST_N, 21, .008, .008)
up_l = lambda u: 70 - 22.2 * (u - .28)
lo_l = lambda u: 50 + 22.2 * (u - .36)

@scene('c6s1')
def c6s1(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        with pop(c, t, b[1], 960, 560) as a:
            card(c, 260, 360, 1400, 380, 26, CARD, a * a1)
            polyline(c, [(340, 680), (700, 480)], GREEN, 10, a * a1, P(t, b[1] + .2, .6))
            for q in range(5): line(c, 760 + q * 70, 470 + (q % 2) * 50, 820 + q * 70, 520 - (q % 2) * 50, NAVY, 6, a * a1 * P(t, b[1] + .7 + q * .1, .3))
            arrow(c, 1140, 470, 1560, 400, GREEN, 10, a * a1, P(t, b[1] + 1.3, .6), 30)
            text(c, 'trend', 520, 650, 28, 'semi', GREEN, 'c', a * a1); text(c, 'pause', 930, 640, 28, 'semi', NAVY, 'c', a * a1); text(c, 'trend resumes', 1360, 560, 28, 'semi', GREEN, 'c', a * a1)
    a2 = stage(t, b, 2, 3)
    if a2 > 0:
        for i, (lab, kind) in enumerate([('Symmetrical', 'sym'), ('Ascending', 'asc'), ('Descending', 'des')]):
            x = 230 + i * 520
            with pop(c, t, b[2] + .3 + i * .3, x + 230, 560) as a:
                card(c, x, 360, 460, 380, 24, CARD, a * a2, border=GOLD if i == 0 else None, bw=3)
                X0, Y0, Wd, Hh_ = x + 60, 430, 340, 220
                tops = {'sym': (Y0, Y0 + Hh_ / 2), 'asc': (Y0, Y0), 'des': (Y0, Y0 + Hh_ / 2)}[kind]
                bots = {'sym': (Y0 + Hh_, Y0 + Hh_ / 2), 'asc': (Y0 + Hh_, Y0 + 40), 'des': (Y0 + Hh_, Y0 + Hh_)}[kind]
                if kind == 'des': tops = (Y0, Y0 + Hh_ - 40)
                line(c, X0, tops[0], X0 + Wd, tops[1], RED, 5, a * a2); line(c, X0, bots[0], X0 + Wd, bots[1], GREEN, 5, a * a2)
                text(c, lab, x + 230, 710, 30, 'bold', NAVY, 'c', a * a2)
    aM = P(t, b[3] - .2, .5)
    if aM > 0:
        O, Hh, L, C = ST; n = ST_N
        F = Frame(230, 330, 1220, 400, -1, n, 15, 95); Vf = Frame(230, 760, 1220, 90, -1, n, 0, 1)
        card(c, 180, 300, 1320, 580, 24, CARD, aM)
        ib = int(.645 * (n - 1))
        kk = ib * P(t, b[3], 2.4) if t < b[6] + b.d[6] * .9 else ib + (n - ib) * P(t, b[6] + b.d[6] * .9, 1.4)
        if t > b[7] + b.d[7] * .4: kk = max(kk, n)
        candles(c, F, O, Hh, L, C, kk, a=aM)
        la = P(t, b[3] + 1.2, .6) * aM
        seg(c, F, .28 * (n - 1), up_l(.28), .771 * (n - 1), up_l(.771), RED, 4, la, P(t, b[3] + 1.2, .8))
        seg(c, F, .36 * (n - 1), lo_l(.36), .771 * (n - 1), lo_l(.771), GREEN, 4, la, P(t, b[3] + 1.4, .8))
        for q, (u, v) in enumerate(((.28, 70), (.36, 49.5), (.46, 66), (.54, 53.6))):
            pa = P(t, b[3] + 1.8 + q * .3, .3) * aM
            circle(c, F.X(u * (n - 1)), F.Y(v), 16, NAVY, pa); text(c, str(q + 1), F.X(u * (n - 1)), F.Y(v) + 7, 18, 'head', WHITE, 'c', pa)
        apx = P(t, b[5] - .3, .5) * aM
        glow_dot(c, F.X(.771 * (n - 1)), F.Y(59.1), 8, GOLD, t, apx)
        text(c, 'APEX', F.X(.771 * (n - 1)) + 16, F.Y(59.1) + 6, 20, 'head', GOLD, 'l', apx)
        ra = P(t, b[5], .5) * aM * (1 - P(t, b[7] - .3, .4))
        if ra > 0:
            x0, x1 = F.X(.28 * (n - 1)), F.X(.771 * (n - 1))
            y = F.y + F.h + 20
            line(c, x0, y, x1, y, NAVY, 3, ra)
            for f, lab in ((0, 'start'), (2 / 3, '2/3'), (3 / 4, '3/4'), (1, 'apex')):
                xx = lerp(x0, x1, f); line(c, xx, y - 8, xx, y + 8, NAVY, 3, ra); text(c, lab, xx, y + 32, 18, 'semi', MUTED, 'c', ra)
            c.rectangle(lerp(x0, x1, 2 / 3), F.y, lerp(x0, x1, 3 / 4) - lerp(x0, x1, 2 / 3), F.h); col(c, GOLD, .18 * ra); c.fill()
            tag(c, lerp(x0, x1, .7), F.y + 10, 'Breakout zone', GOLD, WHITE, 20, ra, 'c')
        da = P(t, b[6], .5) * aM * (1 - P(t, b[6] + b.d[6] * .85, .4))
        if da > 0:
            pts = [F.P(u * (n - 1), 59 + 2 * math.sin(u * 90)) for u in [x / 100 for x in range(62, 90)]]
            polyline(c, pts, FAINT, 4, da, P(t, b[6] + .2, 1.5), [8, 8])
            tag(c, F.X(.83 * (n - 1)), F.Y(59) - 70, 'Drifts to the apex: loses power', MUTED, WHITE, 20, da, 'c')
        va = P(t, b[7], .5) * aM
        if va > 0:
            V = []
            for i in range(n):
                u = i / (n - 1)
                V.append((1.3 if u < .28 else 1.2 - (u - .28) * 2.2 if u < .64 else 2.2 if u < .7 else 1.3) + .1 * math.sin(i * 1.3))
            vbars(c, Vf, V, kk, 0, va, [GREEN if C[i] >= O[i] else RED for i in range(n)], vmax=2.4)
            text(c, 'volume shrinks, then expands on the breakout', F.X(.46 * (n - 1)), 750, 20, 'semi', MUTED, 'c', va)
        ma = P(t, b[8], .5) * aM
        if ma > 0:
            measure(c, F.X(.28 * (n - 1)), F.Y(70), F.Y(48.2), BLUE, ma, P(t, b[8], .6), 'height', 'r')
            measure(c, F.X(.66 * (n - 1)), F.Y(62), F.Y(83.8), BLUE, ma, P(t, b[8] + .7, .8), 'same height', 'l')

# ------------------------------------------------------------ 6.2 ascending / descending
@scene('c6s2')
def c6s2(c, t, b):
    for i, (ttl, kind, t0, cl) in enumerate([('ASCENDING', 'asc', b[1], GREEN), ('DESCENDING', 'des', b[2], RED)]):
        x = 180 + i * 800
        with pop(c, t, t0, x + 380, 560) as a:
            a *= 1 - P(t, b[5] - .3, .4)
            if a <= 0: continue
            card(c, x, 300, 760, 580, 24, CARD, a)
            text(c, ttl + ' TRIANGLE', x + 380, 350, 28, 'head', cl, 'c', a, ls=3)
            F = Frame(x + 50, 380, 660, 330, 0, 10, 0, 130) if kind == 'asc' else Frame(x + 50, 380, 660, 330, 0, 10, -30, 100)
            if kind == 'asc':
                pts = [(0, 30), (2, 80), (3.4, 45), (5, 80), (6.2, 58), (7.4, 80), (8.2, 68), (9, 80), (10, 98)]
                flat, slope = ((1.6, 80), (9.2, 80)), ((3.4, 45), (8.4, 70))
            else:
                pts = [(0, 70), (2, 20), (3.4, 55), (5, 20), (6.2, 42), (7.4, 20), (8.2, 32), (9, 20), (10, 2)]
                flat, slope = ((1.6, 20), (9.2, 20)), ((3.4, 55), (8.4, 30))
            polyline(c, [F.P(*p_) for p_ in pts], NAVY, 5, a, P(t, t0 + .2, 2))
            seg(c, F, *flat[0], *flat[1], RED if kind == 'asc' else GREEN, 5, a * P(t, t0 + 1, .4))
            sl = slope; ext = (9.2 - sl[0][0]) / (sl[1][0] - sl[0][0]) - 1
            seg(c, F, *sl[0], *sl[1], GREEN if kind == 'asc' else RED, 5, a * P(t, t0 + 1.3, .4), ext=ext)
            la = P(t, t0 + 1.6, .4) * a
            if kind == 'asc':
                tag(c, F.X(5), F.Y(80) - 60, 'Sellers at the same price', RED, WHITE, 20, la, 'c')
                tag(c, F.X(5.2), F.Y(52) + 50, 'Buyers step in higher', GREEN, WHITE, 20, la, 'c')
            else:
                tag(c, F.X(5), F.Y(20) + 30, 'Buyers defend one level', GREEN, WHITE, 20, la, 'c')
                tag(c, F.X(5.2), F.Y(48) - 70, 'Sellers come in lower', RED, WHITE, 20, la, 'c')
            ma = P(t, b[3] + i * .4, .5) * a
            if ma > 0:
                if kind == 'asc':
                    measure(c, F.X(2.6), F.Y(80), F.Y(36), BLUE, ma, P(t, b[3] + i * .4, .6), 'height', 'r')
                    measure(c, F.X(9.6), F.Y(80), F.Y(124), BLUE, ma, P(t, b[3] + .6 + i * .4, .6), 'same', 'l')
                else:
                    measure(c, F.X(2.6), F.Y(20), F.Y(64), BLUE, ma, P(t, b[3] + i * .4, .6), 'height', 'r')
                    measure(c, F.X(9.6), F.Y(20), F.Y(-24), BLUE, ma, P(t, b[3] + 1 + i * .4, .6), 'same', 'l')
            va = P(t, b[4] + i * .3, .5) * a
            if va > 0:
                V = [1, .9, .8, .7, .62, .55, .5, .45, .42, 1.6, 1.3]
                for q, v in enumerate(V):
                    c.rectangle(x + 70 + q * 58, 850 - v * 80, 40, v * 80); col(c, cl if q >= 9 else FAINT, va); c.fill()
    a5 = P(t, b[5], .5) * (1 - P(t, b[6] - .3, .4))
    if a5 > 0:
        card(c, 560, 380, 800, 360, 26, NAVY, a5)
        text(c, 'Usually continuation patterns...', 960, 470, 34, 'serif', WHITE, 'c', a5)
        text(c, 'Ascending can form at a BOTTOM', 960, 560, 30, 'bold', GREEN, 'c', P(t, b[5] + 1, .4) * a5)
        text(c, 'Descending can form at a TOP', 960, 620, 30, 'bold', LRED, 'c', P(t, b[5] + 1.6, .4) * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        card(c, 460, 400, 1000, 300, 26, NAVY, a6)
        text(c, 'Flat side: who is defending', 960, 520, 40, 'serif', WHITE, 'c', a6)
        text(c, 'Sloping side: who is attacking', 960, 600, 40, 'serif', LGOLD, 'c', P(t, b[6] + .6, .5) * a6)

# ------------------------------------------------------------ 6.3 broadening formation
@scene('c6s3')
def c6s3(c, t, b):
    aM = P(t, .3, .5)
    F = Frame(230, 340, 1000, 420, 0, 10, 0, 100)
    card(c, 180, 300, 1100, 580, 24, CARD, aM)
    pts = [(0, 52), (1.2, 60), (2.2, 44), (3.6, 70), (5, 34), (6.6, 82), (8.2, 18), (9, 40), (10, 6)]
    polyline(c, [F.P(*p_) for p_ in pts], NAVY, 5, aM, P(t, .5, max(1.5, b[1] + 1)))
    la = P(t, b[1], .5) * aM
    seg(c, F, 1.2, 60, 6.6, 82, RED, 4, la, P(t, b[1], .8), ext=.3)
    seg(c, F, 2.2, 44, 8.2, 18, GREEN, 4, la, P(t, b[1] + .2, .8), ext=.15)
    with pop(c, t, b[1] + .6, 1500, 450) as a:
        megaphone(c, 1500, 450, 1.6, a)
    text(c, 'Like a megaphone', 1500, 580, 28, 'serif', MUTED, 'c', P(t, b[1] + 1, .5))
    ra = P(t, b[2], .5)
    if ra > 0:
        pill(c, 1500, 640, 'Relatively rare', 22, NAVY, WHITE, ra, 'semi', 'c', ls=1)
        pill(c, 1500, 700, 'Usually at major tops', 22, NAVY, WHITE, P(t, b[2] + .4, .4), 'semi', 'c', ls=1)
        pill(c, 1500, 760, 'Usually bearish', 22, RED, WHITE, P(t, b[2] + .8, .4), 'semi', 'c', ls=1)
    va = P(t, b[3], .5) * aM
    if va > 0:
        for q in range(9):
            v = .3 + q * .12
            c.rectangle(F.X(q + .5) - 18, 860 - v * 80, 36, v * 80); col(c, BLUE, va * P(t, b[3] + q * .08, .3)); c.fill()
        text(c, 'volume expands with the swings', F.X(5), 770, 20, 'semi', BLUE, 'c', va)
    ca = P(t, b[4], .5) * (1 - P(t, b[6] - .3, .4))
    if ca > 0:
        crowd(c, t, 1380, 860, 3, .45, ['shock', 'happy', 'worried'], ca, 120)
    wa = P(t, b[6], .5)
    if wa > 0:
        card(c, 1330, 640, 420, 230, 22, LRED, wa, border=RED)
        warn(c, 1400, 710, .5, wa, RED)
        text(c, 'Wilder swings', 1460, 705, 26, 'bold', INK, 'l', wa)
        text(c, 'near a top =', 1460, 740, 26, 'bold', INK, 'l', wa)
        text(c, 'a warning, not an invitation', 1540, 810, 22, 'semi', RED, 'c', wa)

# ------------------------------------------------------------ 6.4 flags & pennants
FL_KEYS = [(0, 22), (.12, 26), (.36, 62), (.42, 58), (.45, 60.5), (.5, 55.5), (.53, 58), (.58, 53.5), (.62, 57), (.86, 92), (1, 95)]
FL = path_ohlc(FL_KEYS, 60, 31, .006, .006)

@scene('c6s4')
def c6s4(c, t, b):
    O, Hh, L, C = FL; n = 60
    aM = 1 - P(t, b[3] - .3, .4) + P(t, b[4], .5) * (t > b[4])
    aM = clamp(aM)
    if aM > 0:
        F = Frame(230, 330, 1180, 450, -1, n, 15, 100)
        card(c, 180, 300, 1280, 580, 24, CARD, aM)
        kk = n * (.38 * P(t, .3, max(1, b[1] + 1.5)) if t < b[2] else .38 + .26 * P(t, b[2], 1.6) if t < b[5] else .64 + .36 * P(t, b[5] + .5, 1.6))
        if t >= b[4] and t < b[5]: kk = n * .64
        candles(c, F, O, Hh, L, C, kk, a=aM)
        pa = P(t, b[1] + 1, .5) * aM
        zone(c, F, .12 * 59, .36 * 59, 24, 64, GOLD, .14 * pa)
        text(c, 'FLAGPOLE', F.X(.24 * 59), F.Y(64) - 14, 22, 'head', GOLD, 'c', pa, ls=2)
        fa = P(t, b[2] + .8, .5) * aM
        seg(c, F, .36 * 59, 62.5, .62 * 59, 58, NAVY, 3, fa, P(t, b[2] + .8, .6))
        seg(c, F, .42 * 59, 57.5, .62 * 59, 52.5, NAVY, 3, fa, P(t, b[2] + 1, .6))
        tag(c, F.X(.5 * 59), F.Y(64) - 60, 'FLAG: slopes against the trend', NAVY, WHITE, 20, fa, 'c')
        wa = P(t, b[4] + .6, .5) * aM
        tag(c, 1630, 420, 'Lasts 1 to 3 weeks', NAVY, WHITE, 22, wa, 'c')
        tag(c, 1630, 470, 'Volume dries up', NAVY, WHITE, 22, P(t, b[4] + 1.2, .4) * aM, 'c')
        ha = P(t, b[5] + .5, .5) * aM * (1 - P(t, b[7] - .3, .4))
        if ha > 0:
            x = 1630; line(c, x, 820, x, 560, INK, 6, ha)
            fy = lerp(560, 690, P(t, b[5] + .5, 1.2, eio))
            c.new_path(); c.move_to(x + 3, fy); c.line_to(x + 90, fy + 20); c.line_to(x + 3, fy + 40); c.close_path(); col(c, RED, ha); c.fill()
            text(c, 'HALF-MAST', x, 860, 24, 'head', RED, 'c', ha, ls=2)
        ma = P(t, b[6], .5) * aM
        if ma > 0:
            measure(c, F.X(.36 * 59) - 60, F.Y(26), F.Y(62), BLUE, ma, P(t, b[6] + .2, .6), 'pole', 'l')
            measure(c, F.X(.66 * 59) + 70, F.Y(57), F.Y(93), BLUE, ma, P(t, b[6] + 1, .8), 'same distance', 'r')
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        F = Frame(330, 360, 1000, 420, 0, 10, 0, 100)
        card(c, 270, 320, 1120, 520, 24, CARD, a3)
        text(c, 'PENNANT: a small symmetrical triangle', 830, 370, 26, 'head', NAVY, 'c', a3, ls=1)
        pts = [(0, 10), (3, 66), (3.6, 52), (4.2, 63), (4.8, 55), (5.3, 61), (5.7, 57), (6.1, 60), (10, 98)]
        polyline(c, [F.P(*p_) for p_ in pts], NAVY, 5, a3, P(t, b[3], 1.8))
        seg(c, F, 3, 67, 6.4, 59, RED, 3, a3 * P(t, b[3] + 1, .4)); seg(c, F, 3.6, 51, 6.4, 58, GREEN, 3, a3 * P(t, b[3] + 1, .4))
    a7 = P(t, b[7], .5)
    if a7 > 0:
        card(c, 1480, 560, 300, 270, 22, NAVY, a7)
        text(c, 'A resting point,', 1630, 640, 26, 'bold', WHITE, 'c', a7)
        text(c, 'not a reason', 1630, 680, 26, 'bold', WHITE, 'c', a7)
        text(c, 'to fear', 1630, 720, 26, 'bold', WHITE, 'c', a7)
        text(c, 'often a 2nd chance', 1630, 780, 22, 'semi', GOLD, 'c', a7)

# ------------------------------------------------------------ 6.5 wedges
@scene('c6s5')
def c6s5(c, t, b):
    aM = 1 - P(t, b[4] - .3, .4)
    for i, (ttl, sub, kind, t0, cl) in enumerate([('FALLING WEDGE', 'in an uptrend: bullish', 'fall', b[2], GREEN), ('RISING WEDGE', 'in a downtrend: bearish', 'rise', b[2] + b.d[2] * .45, RED)]):
        x = 180 + i * 800
        with pop(c, t, t0 if t0 > 0 else .3, x + 380, 560) as a:
            if a <= 0 or aM <= 0: continue
            card(c, x, 300, 760, 560, 24, CARD, a * aM)
            text(c, ttl, x + 380, 350, 30, 'head', cl, 'c', a * aM, ls=3)
            text(c, sub, x + 380, 390, 24, 'semi', MUTED, 'c', a * aM)
            F = Frame(x + 50, 420, 660, 400, 0, 10, 0, 100)
            if kind == 'fall':
                pts = [(0, 10), (2.5, 80), (3.4, 60), (4.4, 72), (5.4, 54), (6.3, 64), (7.2, 50), (7.8, 57), (10, 96)]
                up, dn = ((2.5, 80), (7.8, 59)), ((3.4, 60), (7.2, 50))
            else:
                pts = [(0, 90), (2.5, 20), (3.4, 40), (4.4, 28), (5.4, 46), (6.3, 36), (7.2, 50), (7.8, 43), (10, 4)]
                up, dn = ((3.4, 40), (7.2, 50)), ((2.5, 20), (7.8, 41))
            polyline(c, [F.P(*p_) for p_ in pts], NAVY, 5, a * aM, P(t, (t0 if t0 > 0 else .3) + .2, 2.2))
            seg(c, F, *up[0], *up[1], RED, 4, a * aM * P(t, b[1] + .5, .5))
            seg(c, F, *dn[0], *dn[1], GREEN, 4, a * aM * P(t, b[1] + .5, .5))
            sa = P(t, b[1] + 1, .5) * a * aM
            arrow(c, F.X(4), F.Y(66 if kind == 'fall' else 34) - 90 * (1 if kind == 'fall' else -1) * 0, F.X(7), F.Y(56 if kind == 'fall' else 46), GOLD, 5, sa, P(t, b[1] + 1, .5), 16)
            text(c, 'slant', F.X(5.5), F.Y(76 if kind == 'fall' else 24), 24, 'bold', GOLD, 'c', sa)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        with pop(c, t, b[4], 960, 560) as a:
            calendar(c, 760, 560, 1.6, a * a4)
            text(c, 'More than 1 month', 1150, 540, 40, 'head', NAVY, 'l', a * a4)
            text(c, 'but not more than 3', 1150, 600, 40, 'head', GOLD, 'l', a * a4)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        F = Frame(260, 350, 1100, 450, 0, 10, 0, 100)
        card(c, 210, 310, 1200, 560, 24, CARD, a5)
        text(c, 'RISING WEDGE AT A TOP', 810, 350, 26, 'head', RED, 'c', a5, ls=3)
        pts = [(0, 10), (2, 50), (3, 40), (4.6, 70), (5.4, 60), (6.6, 80), (7.2, 72), (8, 86), (8.6, 74), (10, 30)]
        polyline(c, [F.P(*p_) for p_ in pts], NAVY, 5, a5, P(t, b[5], 2.2))
        seg(c, F, 2, 50, 8, 86, RED, 3, a5 * P(t, b[5] + 1, .4)); seg(c, F, 3, 40, 8.6, 75, GREEN, 3, a5 * P(t, b[5] + 1, .4))
        for q, (x0, x1, v) in enumerate(((3, 4.6, '+30'), (5.4, 6.6, '+20'), (7.2, 8, '+14'))):
            tag(c, F.X((x0 + x1) / 2) - 40, F.Y(90 - q * 2) - 40 + q * 0, f'push {q+1}: {v}', [GREEN, GOLD, RED][q], WHITE, 18, P(t, b[5] + 1.6 + q * .4, .3) * a5, 'c')
        text(c, 'Each push gains less ground', 1580, 560, 28, 'serif', RED, 'c', P(t, b[5] + 3, .5) * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        card(c, 460, 420, 1000, 260, 26, NAVY, a6)
        text(c, 'Watch the slant:', 960, 520, 40, 'serif', WHITE, 'c', a6)
        text(c, 'a wedge usually breaks against it', 960, 600, 40, 'serif', LGOLD, 'c', a6)

# ------------------------------------------------------------ 6.6 rectangles & measured move
@scene('c6s6')
def c6s6(c, t, b):
    aR = stage(t, b, 0, 5)
    if aR > 0:
        F = Frame(230, 330, 1200, 380, -1, 50, 20, 95); Vf = Frame(230, 740, 1200, 110, -1, 50, 0, 1)
        card(c, 180, 300, 1320, 580, 24, CARD, aR)
        keys = [(0, 24), (.2, 60), (.27, 46), (.34, 60), (.41, 46.5), (.48, 60), (.55, 46), (.62, 60), (.69, 47), (.76, 60), (.82, 66), (1, 90)]
        O, Hh, L, C = path_ohlc(keys, 50, 41, .006, .006)
        kk = 50 * (.78 * P(t, .3, max(1, b[1] + 2)) if t < b[2] + b.d[2] * .6 else .78 + .22 * P(t, b[2] + b.d[2] * .6, 1.2))
        candles(c, F, O, Hh, L, C, kk, a=aR)
        ra = P(t, b[1], .5) * aR
        zone(c, F, 9.8, 38, 46, 60.5, GOLD, .12 * ra)
        hline(c, F, 60.5, 9.8, 38, RED, 3, ra, dash=[10, 6]); hline(c, F, 46, 9.8, 38, GREEN, 3, ra, dash=[10, 6])
        tag(c, F.X(24), F.Y(60.5) - 50, 'RECTANGLE: a trading range', NAVY, WHITE, 20, ra, 'c')
        va = P(t, b[3], .5) * aR
        if va > 0:
            V = [(1.4 if C[i] >= O[i] else .7) + .1 * math.sin(i) for i in range(50)]
            vbars(c, Vf, V, kk, 0, va, [GREEN if C[i] >= O[i] else RED for i in range(50)], vmax=1.6)
            tag(c, 1650, 600, 'Heavier volume on rallies', GREEN, WHITE, 22, va, 'c')
            tag(c, 1650, 650, '= buyers in control', GREEN, WHITE, 22, va, 'c')
        ta = P(t, b[4], .5) * aR
        if ta > 0:
            for q, (i, kind) in enumerate(((13, 'BUY'), (17, 'SELL'), (21, 'BUY'), (25, 'SELL'))):
                pill(c, F.X(i), F.Y(46) + 14 if kind == 'BUY' else F.Y(60.5) - 50, kind, 16, GREEN if kind == 'BUY' else RED, WHITE, P(t, b[4] + q * .3, .3) * ta, 'semi', 'c', ls=1)
        pa = P(t, b[2], .5) * aR * (1 - P(t, b[3] - .2, .4))
        tag(c, 1650, 450, 'Usually continues the trend', NAVY, WHITE, 22, pa, 'c')
        tag(c, 1650, 500, 'but can reverse: wait', GOLD, WHITE, 22, pa, 'c')
    aM = stage(t, b, 5, 8)
    if aM > 0:
        F = Frame(260, 340, 1100, 480, 0, 10, 0, 100)
        card(c, 210, 300, 1500, 580, 24, CARD, aM)
        text(c, 'MEASURED MOVE', 240, 345, 22, 'head', GOLD, 'l', aM, ls=3)
        A, B, C_, D = (0, 10), (3.6, 52), (5, 38), (8.6, 80)
        polyline(c, [F.P(*A), F.P(*B)], NAVY, 6, aM, P(t, b[6], .8))
        polyline(c, [F.P(*B), F.P(*C_)], NAVY, 6, aM, P(t, b[6] + .8, .6))
        polyline(c, [F.P(*C_), F.P(*D)], NAVY, 6, aM, P(t, b[7], .9))
        for lab, p_, t0 in (('A', A, b[6]), ('B', B, b[6] + .6), ('C', C_, b[6] + 1.2), ('D', D, b[7] + .8)):
            la = P(t, t0, .3) * aM
            circle(c, *F.P(*p_), 22, GOLD, la); text(c, lab, F.X(p_[0]), F.Y(p_[1]) + 9, 24, 'head', WHITE, 'c', la)
        m1 = P(t, b[6] + .6, .5) * aM
        measure(c, F.X(0) + 60, F.Y(10), F.Y(52), BLUE, m1, P(t, b[6] + .6, .6), 'leg 1', 'r')
        tag(c, F.X(4.8) + 120, F.Y(45), 'retraces 1/3 to 1/2', GOLD, WHITE, 20, P(t, b[6] + 1.6, .4) * aM, 'c')
        m2 = P(t, b[7] + .9, .5) * aM
        measure(c, F.X(10), F.Y(38), F.Y(80), BLUE, m2, P(t, b[7] + .9, .8), 'leg 2 = leg 1', 'l')
    a8 = stage(t, b, 8, 9)
    if a8 > 0:
        F = Frame(260, 360, 1100, 420, 0, 10, 0, 100)
        card(c, 210, 310, 1500, 560, 24, CARD, a8)
        text(c, 'CONTINUATION HEAD & SHOULDERS', 240, 355, 22, 'head', GOLD, 'l', a8, ls=3)
        pts = [(0, 10), (2, 60), (3, 48), (4, 60), (5, 36), (6, 60), (6.8, 50), (7.4, 60), (10, 96)]
        polyline(c, [F.P(*p_) for p_ in pts], NAVY, 6, a8, P(t, b[8] + .2, 2.2))
        line(c, F.X(1.8), F.Y(60), F.X(7.6), F.Y(60), GOLD, 4, a8 * P(t, b[8] + 1.6, .4))
        tag(c, F.X(5), F.Y(36) + 30, 'inverse H&S inside an uptrend', NAVY, WHITE, 20, P(t, b[8] + 1.8, .4) * a8, 'c')
    a9 = P(t, b[9], .5)
    if a9 > 0:
        with pop(c, t, b[9], 960, 560) as a:
            card(c, 400, 400, 1120, 300, 26, NAVY, a * a9)
            text(c, 'A pause is just a pause until it breaks.', 960, 520, 44, 'serif', WHITE, 'c', a * a9)
            text(c, 'Measure it. Respect it. Let the breakout decide.', 960, 600, 32, 'serif', LGOLD, 'c', a * a9)

# ------------------------------------------------------------ 6.7 confirmation & divergence
@scene('c6s7')
def c6s7(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        items = [('Price pattern', 'Triangle breakout', b[2]), ('Volume', 'Expands on the break', b[2] + b.d[2] * .35), ('Bigger trend', 'Up on the weekly chart', b[2] + b.d[2] * .65), ('Indicators', 'Coming in Part 2', b[1] + 1)]
        for i, (ttl, sub, t0) in enumerate(items):
            x = 190 + i * 390
            with pop(c, t, b[1] + .2 + i * .25, x + 175, 520) as a:
                card(c, x, 360, 350, 330, 24, CARD, a * a1)
                ok = P(t, t0, .4)
                circle(c, x + 175, 460, 56, mix(FAINT, GREEN, ok), a * a1)
                if ok > .5: check(c, x + 175, 462, 1.8, WHITE, a * a1, ok)
                text(c, ttl, x + 175, 580, 30, 'bold', INK, 'c', a * a1)
                text(c, sub, x + 175, 620, 22, 'semi', MUTED, 'c', a * a1)
        ca = P(t, b[2] + b.d[2] * .8, .5) * a1
        pill(c, 960, 760, 'THE EVIDENCE AGREES: CONFIRMATION', 28, GREEN, WHITE, ca, 'semi', 'c', ls=2)
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        P1 = Frame(260, 330, 900, 260, 0, 10, 0, 100); V1 = Frame(260, 640, 900, 200, 0, 10, 0, 100)
        card(c, 210, 300, 1000, 570, 24, CARD, a3)
        text(c, 'PRICE', 240, 345, 20, 'head', NAVY, 'l', a3, ls=3); text(c, 'VOLUME / INDICATOR', 240, 630, 20, 'head', NAVY, 'l', a3, ls=3)
        pp = [(0, 20), (2, 55), (3, 40), (5.5, 70), (6.5, 55), (9, 88), (10, 80)]
        vv = [(0, 25), (2, 80), (3, 50), (5.5, 70), (6.5, 45), (9, 55), (10, 40)]
        polyline(c, [P1.P(*p_) for p_ in pp], NAVY, 5, a3, P(t, b[3], 1.6))
        polyline(c, [V1.P(*p_) for p_ in vv], BLUE, 5, a3, P(t, b[3] + .3, 1.6))
        da = P(t, b[3] + 1.8, .5) * a3
        seg(c, P1, 5.5, 70, 9, 88, GREEN, 4, da); seg(c, V1, 5.5, 70, 9, 55, RED, 4, da)
        text(c, 'higher high', P1.X(9) + 10, P1.Y(88) - 20, 22, 'bold', GREEN, 'l', da)
        text(c, 'lower high', V1.X(9) + 10, V1.Y(55) - 20, 22, 'bold', RED, 'l', da)
        la = P(t, b[4], .5) * a3
        if la > 0:
            rrect(c, 1400, 360, 170, 420, 40); col(c, INK, la); c.fill()
            for q, cl in enumerate((RED, GOLD, GREEN)):
                on = q == 1
                circle(c, 1485, 440 + q * 130, 48, cl, la * (1 if on else .2))
                if on: circle(c, 1485, 440 + q * 130, 66, GOLD, la * .25 * (.6 + .4 * math.sin(t * 5)))
            text(c, 'Warning light,', 1690, 540, 26, 'bold', INK, 'l', la)
            text(c, 'not a sell signal', 1690, 576, 26, 'bold', INK, 'l', la)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        with pop(c, t, b[5], 960, 560) as a:
            factory(c, 700, 580, 1.4, t, a * a5); train(c, 1220, 560, 1.1, t, a * a5)
            text(c, "Dow's confirmation idea,", 960, 760, 34, 'serif', NAVY, 'c', a * a5)
            text(c, 'now applied to every tool', 960, 810, 34, 'serif', GOLD, 'c', a * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, lab in enumerate(['Signal 1', 'Signal 2', 'Signal 3']):
            with pop(c, t, b[6] + .2 + i * .3, 560 + i * 400, 520) as a:
                card(c, 420 + i * 400, 420, 280, 200, 22, CARD, a * a6)
                badge(c, 560 + i * 400, 490, 34, 'ok', a * a6)
                text(c, lab, 560 + i * 400, 580, 28, 'bold', INK, 'c', a * a6)
        pill(c, 960, 700, 'Independent signals agree = worth acting on', 28, NAVY, WHITE, P(t, b[6] + 1.4, .5), 'semi', 'c', ls=0)
