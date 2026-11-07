from engine import *
from . import scene
from .common import *
from .data import nifty_w, idx

TENETS = ['The averages discount everything', 'The market has three trends', 'Major trends have three phases',
          'The averages must confirm', 'Volume must confirm the trend', 'A trend persists until it reverses']

def swing_chart(c, F, pts, p, cl=NAVY, lw=5, a=1.0):
    return polyline(c, [F.P(i, v) for i, v in pts], cl, lw, a, p)

# ------------------------------------------------------------ 2.1 Charles Dow
@scene('c2s1')
def c2s1(c, t, b):
    aT = stage(t, b, 1, 5)
    if aT > 0:
        with pop(c, t, b[1], 300, 420) as a:
            avatar(c, 300, 390, 1.2, SKIN[3], HAIR[3], NAVY, 'bald', tie=INK, beard=HAIR[3], mood='neutral', t=t, a=a * aT)
            text(c, 'Charles Dow', 300, 590, 32, 'bold', INK, 'c', a * aT)
            text(c, 'journalist', 300, 626, 24, 'serif', MUTED, 'c', a * aT)
        x0, x1, ty = 560, 1740, 720
        line(c, x0, ty, x1, ty, LINE, 6, aT, p=P(t, b[1] + .3, 1.2, eio))
        nodes = [(620, '1882', 'Dow Jones & Co. founded', b[1] + b.d[1] * .5), (930, '1884', 'First average: 11 stocks', b[2]),
                 (1260, '1902', 'Dow dies', b[3] + b.d[3] * .55), (1600, 'Later', 'Hamilton & Rhea', b[4])]
        for x, yr, lab, t0 in nodes:
            na = P(t, t0, .5) * aT
            glow_dot(c, x, ty, 12, GOLD, t, na, False)
            text(c, yr, x, ty + 56, 32, 'head', NAVY, 'c', na)
            text(c, lab, x, ty + 92, 22, 'semi', MUTED, 'c', na)
        # 1884 average: 9 rails + 2 industrials
        ga = P(t, b[2] + .3, .4) * aT * (1 - P(t, b[2] + b.d[2] * .55, .4))
        for k in range(11):
            r, cc = divmod(k, 6)
            x, y = 700 + cc * 95, 440 + r * 105
            with pop(c, t, b[2] + .3 + k * .08, x, y) as a:
                if k < 9: train(c, x, y, .42, t, a * ga, RED)
                else: factory(c, x, y + 8, .45, t, a * ga, NAVY)
        text(c, '9 railroads + 2 others', 930, 640, 24, 'semi', INK, 'c', ga)
        sa = P(t, b[2] + b.d[2] * .55, .5) * aT * (1 - P(t, b[3] - .2, .4))
        if sa > 0:
            card(c, 640, 400, 300, 220, 22, CARD, sa); factory(c, 790, 520, .8, t, sa); text(c, 'Industrials', 790, 600, 26, 'bold', NAVY, 'c', sa)
            card(c, 980, 400, 300, 220, 22, CARD, sa); train(c, 1130, 500, .7, t, sa); text(c, 'Rails', 1130, 600, 26, 'bold', RED, 'c', sa)
        ea = P(t, b[3], .5) * aT * (1 - P(t, b[4] - .2, .4))
        if ea > 0:
            with pop(c, t, b[3], 980, 500) as a:
                newspaper(c, 760, 380, 460, 220, 'DOW ON THE MARKET', a * ea, 'Editorials, Wall Street Journal', NAVY, -.02)
            pill(c, 1350, 440, 'Never wrote a book', 26, RED, WHITE, P(t, b[3] + .8, .4) * ea, 'semi', ls=1)
        ha = P(t, b[4], .5) * aT
        if ha > 0:
            for k, (nm, yr) in enumerate([('W. P. Hamilton', '1922'), ('Robert Rhea', '1932')]):
                x = 820 + k * 330
                with pop(c, t, b[4] + k * .4, x, 470) as a:
                    avatar(c, x, 440, .85, SKIN[k * 3], HAIR[k + 1], [BLUE, GREEN][k], 'side', tie=GOLD, glasses=k == 1, t=t, seed=k, a=a * ha)
                    text(c, nm, x, 600, 24, 'bold', INK, 'c', a * ha)
            with pop(c, t, b[4] + 1.0, 1500, 480) as a:
                book3d(c, 1500, 480, 150, 200, t, a * ha, 'DOW THEORY', '', '', False)
    aR = stage(t, b, 5, 6)
    if aR > 0:
        with pop(c, t, b[5], 960, 790) as a:
            card(c, 700, 740, 520, 110, 24, NAVY, a * aR)
            text(c, 'DOW THEORY', 960, 808, 40, 'head', WHITE, 'c', a * aR, ls=6)
        branches = ['Trends', 'Support & resistance', 'Volume', 'Confirmation']
        for i, lab in enumerate(branches):
            ex = 330 + i * 420
            k = P(t, b[5] + .4 + i * .3, .7)
            pts = []
            for q in range(31):
                u = q / 30
                pts.append((lerp(960, ex, eio(u)), lerp(740, 560, u)))
            polyline(c, pts, GOLD, 5, aR, k)
            with pop(c, t, b[5] + .9 + i * .3, ex, 500) as a:
                card(c, ex - 180, 440, 360, 120, 22, CARD, a * aR, border=GOLD)
                text(c, lab, ex, 512, 30, 'bold', INK, 'c', a * aR)
        text(c, 'The roots of modern technical analysis', 960, 360, 34, 'serif', MUTED, 'c', P(t, b[5] + 1.5, .5) * aR)
    aS = P(t, b[6], .5)
    if aS > 0:
        for i, ttl in enumerate(TENETS):
            r, cc = divmod(i, 3)
            x, y = 170 + cc * 540, 300 + r * 270
            with pop(c, t, b[6] + .2 + i * .25, x + 250, y + 110) as a:
                card(c, x, y, 500, 220, 22, CARD, a * aS)
                circle(c, x + 70, y + 80, 40, GOLD, a * aS)
                text(c, str(i + 1), x + 70, y + 96, 44, 'head', WHITE, 'c', a * aS)
                text(c, 'TENET', x + 130, y + 72, 20, 'semi', GOLD, 'l', a * aS, ls=4)
                para(c, ttl, x + 40, y + 160, 28, 'bold', INK, 430, 1.2, 'l', a * aS)

# ------------------------------------------------------------ 2.2 three trends
def sea(c, t, x, y, w, h, layers, a=1.0):
    """layers: (tide, waves, ripples) visibility 0..1"""
    tide, waves, rip = layers
    pts = []
    for k in range(0, 241):
        u = k / 240; xx = x + u * w
        yy = y + h * .55 - tide * (h * .18) * (.5 + .5 * math.sin(t * .35)) \
             - waves * 34 * math.sin(u * 9 - t * 1.6) - rip * 7 * math.sin(u * 70 - t * 5)
        pts.append((xx, yy))
    c.new_path(); c.move_to(x, y + h)
    for p_ in pts: c.line_to(*p_)
    c.line_to(x + w, y + h); c.close_path()
    g = cairo.LinearGradient(0, y + h * .3, 0, y + h)
    g.add_color_stop_rgba(0, *mix(BLUE, WHITE, .25), .9 * a); g.add_color_stop_rgba(1, *NAVY, .95 * a)
    c.set_source(g); c.fill()
    polyline(c, pts, mix(BLUE, WHITE, .6), 3, a)
    return pts

@scene('c2s2')
def c2s2(c, t, b):
    a0 = stage(t, b, 0, 1)
    if a0 > 0:
        with pop(c, t, .3, 960, 560) as a:
            label_card(c, 360, 400, 1200, 260, 'Tenet 1: The averages discount everything', 'Premise 1 of technical analysis, applied to the market averages', a * a0, GOLD, 44, 30)
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        F = Frame(260, 330, 1400, 460, 0, 8, 0, 100)
        pts = [(0, 15), (1, 40), (2, 28), (3, 60), (4, 46), (5, 78), (6, 64), (7, 92), (8, 84)]
        swing_chart(c, F, pts, P(t, b[1] + .2, 2), NAVY, 6, a1)
        for j, (i, v) in enumerate(pts[1:], 1):
            pa = P(t, b[1] + .3 + j * .25, .4) * a1
            pk = j % 2 == 1
            glow_dot(c, *F.P(i, v), 9, GREEN if pk else BLUE, t, pa, False)
            text(c, 'Higher high' if pk else 'Higher low', F.X(i), F.Y(v) + (-24 if pk else 46), 22, 'semi', GREEN if pk else BLUE, 'c', pa)
    aS = stage(t, b, 2, 5)
    if aS > 0:
        lay = (P(t, b[2], .8), P(t, b[3], .8), P(t, b[4], .8))
        card(c, 170, 290, 1580, 600, 26, CARD, aS)
        c.save(); rrect(c, 170, 290, 1580, 600, 26); c.clip()
        rrect(c, 300, 360, 22, 520, 6); col(c, hexc('#8A5A33'), aS); c.fill()
        for k in range(12):
            line(c, 322, 400 + k * 40, 342 if k % 2 else 352, 400 + k * 40, hexc('#8A5A33'), 3, aS)
        pts = sea(c, t, 170, 380, 1580, 510, lay, aS)
        bx, by = pts[60]
        with xf(c, bx, by, rot=math.atan2(pts[62][1] - pts[58][1], pts[62][0] - pts[58][0])):
            c.new_path(); c.move_to(bx - 50, by - 8); c.line_to(bx + 50, by - 8); c.line_to(bx + 34, by + 14); c.line_to(bx - 34, by + 14); c.close_path(); col(c, RED, aS); c.fill()
            line(c, bx, by - 8, bx, by - 70, INK, 4, aS)
            c.new_path(); c.move_to(bx + 3, by - 68); c.line_to(bx + 40, by - 20); c.line_to(bx + 3, by - 20); c.close_path(); col(c, CARD, aS); c.fill()
        c.restore()
        for i, (lab, sub, t0, yy) in enumerate([('TIDE', 'Primary trend', b[2], 400), ('WAVES', 'Secondary trend', b[3], 480), ('RIPPLES', 'Minor trend', b[4], 560)]):
            la = P(t, t0 + .3, .5) * aS
            card(c, 1360, 316 + i * 82, 360, 70, 16, [NAVY, BLUE, GOLD][i], la)
            text(c, lab, 1390, 360 + i * 82, 26, 'head', WHITE, 'l', la, ls=2)
            text(c, sub, 1690, 360 + i * 82, 22, 'semi', WHITE, 'r', la)
    aL = stage(t, b, 5, 8)
    if aL > 0:
        n = 120
        prim = [20 + i * .55 for i in range(n)]
        sec = [9 * math.sin(i / n * 2 * math.pi * 3.2) for i in range(n)]
        rnd = random.Random(2); mn = [rnd.gauss(0, 1.4) for i in range(n)]
        F = Frame(200, 330, 900, 480, 0, n - 1, 0, 100)
        card(c, 160, 300, 980, 560, 24, CARD, aL)
        series(c, F, range(n), prim, P(t, b[5], 1.0), NAVY, 7, aL)
        series(c, F, range(n), [p + s for p, s in zip(prim, sec)], P(t, b[6], 1.4), BLUE, 4, aL)
        series(c, F, range(n), [p + s + m for p, s, m in zip(prim, sec, mn)], P(t, b[7], 1.4), GOLD, 2, aL)
        cards = [('PRIMARY', 'More than a year, often several', NAVY, b[5]), ('SECONDARY', '3 weeks to 3 months; retraces 1/3 to 2/3, often 1/2', BLUE, b[6]),
                 ('MINOR', 'Less than 3 weeks', GOLD, b[7])]
        for i, (ttl, sub, cl, t0) in enumerate(cards):
            with pop(c, t, t0 + .2, 1450, 380 + i * 170) as a:
                card(c, 1190, 310 + i * 175, 560, 150, 20, CARD, a * aL)
                c.save(); rrect(c, 1190, 310 + i * 175, 560, 150, 20); c.clip(); c.rectangle(1190, 310 + i * 175, 10, 150); col(c, cl, a * aL); c.fill(); c.restore()
                text(c, ttl, 1225, 360 + i * 175, 28, 'head', cl, 'l', a * aL, ls=2)
                para(c, sub, 1225, 400 + i * 175, 23, 'med', INK, 500, 1.25, 'l', a * aL)
    aN = stage(t, b, 8)
    if aN > 0:
        d = nifty_w(); C = d['c']; n = len(C)
        F = Frame(200, 330, 1420, 470, 0, n - 1, 7000, 27500)
        chart_card(c, F, aN, 'NIFTY 50', 'weekly close, 2020 to 2024', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [10000, 15000, 20000, 25000], a=aN)
        xlabels(c, F, [(idx(d, f'{y}-01-01'), str(y)) for y in (2021, 2022, 2023, 2024)], aN)
        series(c, F, range(n), C, P(t, b[8] + .2, 1.6), mix(NAVY, WHITE, .35), 2.5, aN)
        k = 18; tide = []
        for i in range(n):
            lo_, hi_ = max(0, i - k), min(n, i + k + 1); tide.append(sum(C[lo_:hi_]) / (hi_ - lo_))
        series(c, F, range(n), tide, P(t, b[8] + 1.4, 1.6), NAVY, 9, aN * .85)
        tag(c, F.X(n - 30), F.Y(tide[n - 30]) + 60, 'The tide: rising', NAVY, WHITE, 22, P(t, b[8] + 2.8, .5) * aN, 'c')
        pv = pivots(d['h'], d['l'], .07)
        for j in range(len(pv) - 1):
            (i1, p1, k1), (i2, p2, k2) = pv[j], pv[j + 1]
            if k1 == 'H':
                za = P(t, b[8] + 3.2 + j * .1, .4) * aN
                zone(c, F, i1, i2, p2, p1, RED, .2 * za)
        tag(c, F.X(100), F.Y(15000) + 40, 'Waves: the corrections', RED, WHITE, 22, P(t, b[8] + 3.6, .5) * aN, 'c')

# ------------------------------------------------------------ 2.3 three phases
@scene('c2s3')
def c2s3(c, t, b):
    F = Frame(180, 320, 1560, 310, 0, 100, 0, 100)
    xs = list(range(101))
    ys = [10 + 3 * math.sin(x * .5) if x < 30 else (10 + (x - 30) * 1.75 + 2 * math.sin(x * .6) if x < 70 else 80 - (x - 82) ** 2 * .03 + 2 * math.sin(x * .7)) for x in xs]
    am = P(t, b[1] - .2, .5) * (1 - P(t, b[4] - .3, .4))
    if am > 0:
        zones = [(0, 30, GOLD, 'ACCUMULATION', b[1]), (30, 70, GREEN, 'PUBLIC PARTICIPATION', b[2]), (70, 100, RED, 'DISTRIBUTION', b[3])]
        for i0, i1, cl, lab, t0 in zones:
            za = P(t, t0, .5) * am
            zone(c, F, i0, i1, 0, 100, cl, .09 * za)
            text(c, lab, (F.X(i0) + F.X(i1)) / 2, F.y - 6, 24, 'head', cl, 'c', za, ls=2)
        k = 30 if t < b[2] else 70 if t < b[3] else 100
        k0 = 0 if t < b[2] else 30 if t < b[3] else 70
        t0 = b[1] if t < b[2] else b[2] if t < b[3] else b[3]
        prog = lerp(k0, k, P(t, t0, 2.2, eio)) / 100
        series(c, F, xs, ys, prog, NAVY, 6, am)
        # actors
        sm = P(t, b[1] + .6, .5) * am
        avatar(c, 330, 715, .7, SKIN[0], HAIR[3], NAVY, 'side', tie=GOLD, glasses=True, mood='smile', t=t, a=sm)
        text(c, 'Informed investors buy', 330, 845, 22, 'semi', INK, 'c', sm)
        for q in range(3):
            ph = (t * .6 + q / 3) % 1
            coin(c, lerp(470, 360, ph), 690 - 40 * math.sin(ph * math.pi), 14, '$', GOLD, sm * (1 - ph))
        text(c, 'News: bad · Mood: fear', 330, 880, 20, 'med', RED, 'c', sm)
        pa = P(t, b[2] + 1, .5) * am
        crowd(c, t, 790, 730, 3, .5, ['smile', 'happy', 'smile'], pa, 120)
        text(c, 'Trend-followers join', 910, 845, 22, 'semi', INK, 'c', pa)
        text(c, 'News improves · Mood: optimism', 910, 880, 20, 'med', GREEN, 'c', pa)
        da = P(t, b[3] + 1, .5) * am
        crowd(c, t, 1330, 735, 4, .45, ['happy'] * 4, da, 95, seed=2)
        avatar(c, 1700, 725, .6, SKIN[0], HAIR[3], NAVY, 'side', tie=GOLD, glasses=True, mood='smile', t=t, a=da)
        for q in range(3):
            ph = (t * .6 + q / 3) % 1
            coin(c, lerp(1580, 1690, ph), 690 - 40 * math.sin(ph * math.pi), 14, '$', GOLD, da * (1 - ph))
        text(c, 'Public buys · insiders sell', 1500, 845, 22, 'semi', INK, 'c', da)
        text(c, 'News: wonderful · Mood: euphoria', 1500, 880, 20, 'med', RED, 'c', da)
    aX = stage(t, b, 4, 6)
    if aX > 0:
        G = Frame(300, 340, 1320, 430, 0, 100, 0, 100)
        card(c, 240, 300, 1440, 540, 24, CARD, aX)
        series(c, G, xs, [90 - x * .8 for x in xs], P(t, b[4] + .2, 1.6), GREEN, 7, aX)
        series(c, G, xs, [10 + x * .8 for x in xs], P(t, b[4] + .6, 1.6), RED, 7, aX)
        text(c, 'Opportunity', G.X(4), G.Y(96), 30, 'bold', GREEN, 'l', P(t, b[4] + .5, .5) * aX)
        text(c, 'Confidence', G.X(4), G.Y(2), 30, 'bold', RED, 'l', P(t, b[4] + .9, .5) * aX)
        text(c, 'Fear peaks here', G.X(2), G.y + G.h + 50, 24, 'semi', MUTED, 'l', P(t, b[4] + 1.6, .5) * aX)
        text(c, 'Euphoria peaks here', G.X(98), G.y + G.h + 50, 24, 'semi', MUTED, 'r', P(t, b[4] + 1.9, .5) * aX)
        ma = P(t, b[5], .5) * aX
        for i, m in enumerate(['Stocks', 'Commodities', 'Crypto']):
            pill(c, 760 + i * 200, 860, m, 24, NAVY, WHITE, P(t, b[5] + i * .2, .4) * aX, 'semi', 'c', ls=1)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        crowd(c, t, 360, 600, 5, .8, ['happy'] * 5, a6, 150)
        bubble(c, 250, 380, 620, 100, '"It can only go up!"', a6, 38, 'serif', INK, CARD, 'bl')
        with pop(c, t, b[6] + 1.2, 1400, 520) as a:
            avatar(c, 1400, 600, 1.1, SKIN[1], HAIR[0], GOLD, 'short', glasses=True, mood='neutral', t=t, a=a * a6)
            bubble(c, 1130, 380, 560, 100, 'Which phase am I in?', a * a6, 38, 'bold', NAVY, LGOLD, 'br', GOLD)

# ------------------------------------------------------------ 2.4 averages must confirm
@scene('c2s4')
def c2s4(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        with pop(c, t, b[1], 420, 560) as a:
            factory(c, 420, 580, 2.0, t, a * a1)
            text(c, 'Industrials make goods', 420, 760, 30, 'bold', NAVY, 'c', a * a1)
        u = (t * .25) % 1
        for q in range(3):
            uu = (u + q / 3) % 1
            rrect(c, lerp(640, 1200, uu) - 22, 560, 44, 40, 6); col(c, GOLD, a1 * P(t, b[1] + .6, .4)); c.fill()
        arrow(c, 620, 640, 1240, 640, GOLD, 5, a1, P(t, b[1] + .6, .8))
        with pop(c, t, b[1] + b.d[1] * .4, 1480, 560) as a:
            train(c, 1480, 590, 1.6, t, a * a1)
            text(c, 'Rails ship them', 1480, 760, 30, 'bold', RED, 'c', a * a1)
    def two_charts(aa, diverge, t0):
        for k, (lab, cl) in enumerate([('INDUSTRIALS', NAVY), ('RAILS', RED)]):
            F = Frame(260, 320 + k * 290, 860, 200, 0, 8, 0, 100)
            card(c, 200, 290 + k * 290, 980, 260, 20, CARD, aa)
            text(c, lab, 230, 330 + k * 290, 22, 'head', cl, 'l', aa, ls=2)
            pts = [(0, 20), (1, 55), (2, 35), (3, 70), (4, 48), (5, 66 if (diverge and k == 1) else 90), (6, 50 if (diverge and k == 1) else 72), (7, 40 if (diverge and k == 1) else 96)]
            hline(c, F, 70, 2.6, 8, FAINT, 3, aa, dash=[10, 8])
            swing_chart(c, F, pts, P(t, t0, 1.8), cl, 5, aa)
            ok = not (diverge and k == 1)
            ba = P(t, t0 + 1.9 + k * .3, .4) * aa
            badge(c, 1130, 410 + k * 290, 28, 'ok' if ok else 'no', ba)
    a2 = stage(t, b, 2, 4)
    if a2 > 0:
        two_charts(a2, False, b[2] + .2)
        with pop(c, t, b[2] + 2.6, 1480, 560) as a:
            card(c, 1250, 400, 470, 220, 24, LGREEN, a * a2, border=GREEN)
            text(c, 'BOTH CONFIRM', 1485, 480, 34, 'head', GREEN, 'c', a * a2, ls=2)
            text(c, 'Bull market signal', 1485, 540, 28, 'semi', INK, 'c', a * a2)
        ta = P(t, b[3], .5) * a2
        if ta > 0:
            card(c, 1250, 660, 470, 170, 20, CARD, ta)
            text(c, 'Same day? Not needed.', 1485, 720, 26, 'bold', INK, 'c', ta)
            text(c, 'Closer together = stronger', 1485, 770, 26, 'semi', GOLD, 'c', ta)
    a4 = stage(t, b, 4, 6)
    if a4 > 0:
        two_charts(a4, True, b[4] + .2)
        with pop(c, t, b[4] + 2.6, 1480, 500) as a:
            card(c, 1250, 380, 470, 250, 24, LRED, a * a4, border=RED)
            warn(c, 1485, 450, .6, a * a4, RED)
            text(c, 'DIVERGENCE', 1485, 540, 34, 'head', RED, 'c', a * a4, ls=2)
            text(c, 'A warning, not a signal', 1485, 590, 26, 'semi', INK, 'c', a * a4)
        ra = P(t, b[5], .5) * a4
        if ra > 0:
            card(c, 1250, 670, 470, 160, 20, CARD, ra)
            text(c, 'Rails today:', 1485, 720, 24, 'semi', MUTED, 'c', ra)
            text(c, 'Dow Jones Transportation', 1485, 760, 26, 'bold', INK, 'c', ra)
            text(c, 'Average', 1485, 796, 26, 'bold', INK, 'c', ra)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        text(c, 'CONFIRMATION', 960, 330, 40, 'head', NAVY, 'c', a6, ls=6)
        items = ['Price breaks out', 'Volume expands', 'Related market agrees', 'Bigger trend points the same way']
        for i, it in enumerate(items):
            y = 400 + i * 110
            with pop(c, t, b[6] + .5 + i * .45, 960, y + 40) as a:
                card(c, 560, y, 800, 86, 18, CARD, a * a6)
                badge(c, 616, y + 43, 24, 'ok', a * a6, P(t, b[6] + .7 + i * .45, .4))
                text(c, it, 670, y + 54, 30, 'semi', INK, 'l', a * a6)

# ------------------------------------------------------------ 2.5 volume & persistence
@scene('c2s5')
def c2s5(c, t, b):
    a1 = stage(t, b, 0, 3)
    if a1 > 0:
        pts = [(0, 20), (4, 45), (6, 37), (10, 64), (12, 55), (16, 86)]
        n = 17; ys = path_line([(i / 16, v) for i, v in pts], n)
        F = Frame(260, 320, 1000, 300, -.5, 16.5, 10, 95)
        V = Frame(260, 660, 1000, 170, -.5, 16.5, 0, 1)
        card(c, 200, 290, 1140, 580, 24, CARD, a1)
        series(c, F, range(n), ys, P(t, .3, 1.8), NAVY, 5, a1)
        vols = [(.8 if ys[i] >= ys[i - 1] else .35) + .1 * math.sin(i) if i else .5 for i in range(n)]
        cols = [GREEN if i and ys[i] >= ys[i - 1] else RED for i in range(n)]
        vbars(c, V, vols, n * P(t, b[1], 1.6), 0, a1, cols, vmax=1)
        text(c, 'VOLUME', 230, 650, 18, 'semi', MUTED, 'l', a1, ls=3)
        la = P(t, b[1] + 1.4, .5) * a1
        tag(c, 1550, 420, 'Heavy volume on rallies', GREEN, WHITE, 26, la, 'c')
        tag(c, 1550, 500, 'Light volume on dips', RED, WHITE, 26, la, 'c')
        sa = P(t, b[2], .5) * a1
        if sa > 0:
            card(c, 1390, 600, 330, 240, 20, NAVY, sa)
            text(c, 'SIGNALS COME', 1555, 660, 22, 'semi', LGOLD, 'c', sa, ls=3)
            text(c, 'FROM', 1555, 690, 22, 'semi', LGOLD, 'c', sa, ls=3)
            text(c, 'Closing', 1555, 760, 46, 'head', WHITE, 'c', sa)
            text(c, 'prices', 1555, 806, 46, 'head', WHITE, 'c', sa)
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        with pop(c, t, b[3], 600, 600) as a:
            gavel(c, 560, 560, 1.6, t, a * a3, 0)
        with pop(c, t, b[3] + .5, 1220, 560) as a:
            card(c, 860, 420, 760, 280, 26, NAVY, a * a3)
            text(c, 'A trend is in effect', 1240, 520, 46, 'serif', WHITE, 'c', a * a3)
            text(c, 'until it gives definite', 1240, 580, 46, 'serif', WHITE, 'c', a * a3)
            text(c, 'signals of reversal.', 1240, 640, 46, 'serif', LGOLD, 'c', a * a3)
        q = P(t, b[4], .5) * a3
        bubble(c, 870, 760, 460, 90, '"Prices feel too high..."', q, 30, 'serif', MUTED, CARD, 'bl')
        pill(c, 1400, 785, 'Wait for evidence', 28, GREEN, WHITE, P(t, b[4] + 1, .4) * a3, 'semi', ls=1)
    a5 = stage(t, b, 5, 7)
    if a5 > 0:
        def panel(x, kind, t0, aa):
            card(c, x, 290, 760, 580, 24, CARD, aa)
            F = Frame(x + 60, 380, 640, 380, 0, 6, 0, 100)
            if kind == 'fail':
                pts = [(0, 30), (1, 80), (2, 50), (3, 70), (4, 25)]
                labs = [(1, 80, 'A'), (2, 50, 'B'), (3, 70, 'C')]
                sig = (3.55, 50)
                title_, sub_ = 'FAILURE SWING', 'C fails below A, then B breaks'
            else:
                pts = [(0, 30), (1, 70), (2, 45), (3, 85), (3.9, 38), (4.7, 62), (5.6, 15)]
                labs = [(1, 70, 'A'), (2, 45, 'B'), (3, 85, 'C'), (3.9, 38, 'D'), (4.7, 62, 'E')]
                sig = (3.3, 45)
                title_, sub_ = 'NON-FAILURE SWING', 'C beats A, then B breaks'
            text(c, title_, x + 380, 340, 30, 'head', NAVY, 'c', aa, ls=2)
            swing_chart(c, F, pts, P(t, t0, 2.2), NAVY, 5, aa)
            hline(c, F, labs[1][1], labs[1][0], 6, RED, 3, aa * P(t, t0 + 1, .4), dash=[10, 8])
            for j, (i, v, L_) in enumerate(labs):
                la = P(t, t0 + .3 + j * .35, .3) * aa
                circle(c, *F.P(i, v), 8, NAVY, la)
                text(c, L_, F.X(i), F.Y(v) + (-22 if L_ in 'ACE' else 46), 30, 'head', GOLD, 'c', la)
            sa = P(t, t0 + 2.2, .4) * aa
            glow_dot(c, *F.P(*sig), 10, RED, t, sa)
            tag(c, F.X(sig[0]) + 110, F.Y(sig[1]) + 20, 'SELL' if kind == 'fail' else 'Some sell here', RED, WHITE, 22, sa, 'c')
            if kind != 'fail':
                sb = P(t, t0 + 3.2, .4) * aa
                hline(c, F, 38, 3.9, 6, RED, 3, sb, dash=[10, 8])
                glow_dot(c, *F.P(5.15, 38), 10, RED, t, sb)
                tag(c, F.X(5.15), F.Y(38) + 30, 'Others wait for this', RED, WHITE, 22, sb, 'c')
            text(c, sub_, x + 380, 840, 24, 'semi', MUTED, 'c', aa)
        panel(160, 'fail', b[5] + .2, a5)
        if t > b[6] - .3: panel(1000, 'non', b[6] + .2, a5 * P(t, b[6], .5))
    a7 = P(t, b[7], .5)
    if a7 > 0:
        hit = P(t, b[7] + .6, .25, lambda x: x * x)
        gavel(c, 760, 560, 1.8, t, a7, hit)
        if hit >= 1:
            for k in range(8):
                ang = k * math.pi / 4; r = 60 + 80 * P(t, b[7] + .85, .5)
                line(c, 790 + math.cos(ang) * r * .6, 690 + math.sin(ang) * r * .3, 790 + math.cos(ang) * r, 690 + math.sin(ang) * r * .5, GOLD, 4, a7 * (1 - P(t, b[7] + 1.3, .5)))
        text(c, 'Innocent until', 1300, 540, 60, 'serif', NAVY, 'c', P(t, b[7] + .9, .5))
        text(c, 'proven guilty', 1300, 620, 60, 'serif', NAVY, 'c', P(t, b[7] + 1.1, .5))

# ------------------------------------------------------------ 2.6 closes, lines, lateness
@scene('c2s6')
def c2s6(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        O, Hh, L, C = path_ohlc([(0, 40), (.35, 70), (.55, 55), (.8, 72), (1, 82)], 18, 11, .02, .015)
        Hh[13] = 92; C[13] = 74; O[13] = 72
        C[16] = 88; O[16] = 79; Hh[16] = 90; L[16] = 78
        F = Frame(300, 340, 1000, 480, -1, 18, 30, 100)
        card(c, 250, 300, 1110, 560, 24, CARD, a1)
        hline(c, F, 80, None, None, GOLD, 3, a1 * P(t, b[1], .4), dash=[12, 8], label='Previous peak', lab_side='r')
        candles(c, F, O, Hh, L, C, 17 * P(t, b[1] + .2, 2.2), a=a1)
        x1 = P(t, b[1] + 2.4, .4) * a1
        cross(c, F.X(13), F.Y(Hh[13]) - 40, 1.4, RED, x1, P(t, b[1] + 2.4, .4))
        tag(c, F.X(13), F.Y(Hh[13]) - 120, 'Above only intraday: no', RED, WHITE, 22, x1, 'c')
        x2 = P(t, b[1] + 3, .4) * a1
        badge(c, F.X(16), F.Y(C[16]) - 70, 24, 'ok', x2)
        tag(c, 1600, 420, 'Close above: counts', GREEN, WHITE, 24, x2, 'c')
    a2 = stage(t, b, 2, 3)
    if a2 > 0:
        F = Frame(260, 340, 1400, 460, 0, 40, 0, 100)
        card(c, 200, 300, 1520, 560, 24, CARD, a2)
        rnd = random.Random(5)
        ys = [20 + i * 2.5 for i in range(12)] + [48 + 5 * math.sin(i * 1.3) + rnd.gauss(0, 1.2) for i in range(18)] + [55 + i * 3.2 for i in range(11)]
        zone(c, F, 11.5, 29.5, 40, 56, GOLD, .16 * P(t, b[2] + 1.2, .5) * a2)
        series(c, F, range(len(ys)), ys, P(t, b[2] + .2, 2.4), NAVY, 5, a2)
        tag(c, F.X(20.5), F.Y(56) - 64, 'The line: 2 to 3+ weeks, within about 5%', GOLD, WHITE, 24, P(t, b[2] + 1.4, .5) * a2, 'c')
        ba = P(t, b[2] + b.d[2] * .7, .5) * a2
        arrow(c, F.X(31), F.Y(52), F.X(37), F.Y(80), GREEN, 6, ba, 1, 22)
        text(c, 'Breakout: bullish', F.X(36), F.Y(84), 26, 'bold', GREEN, 'r', ba)
        text(c, '(breakdown: bearish)', F.X(36), F.Y(84) + 34, 22, 'semi', RED, 'r', ba)
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        F = Frame(260, 330, 1400, 470, 0, 100, 0, 100)
        card(c, 200, 300, 1520, 560, 24, CARD, a3)
        xs = list(range(101)); ys = [8 + 84 * math.sin(math.pi * x / 100) ** 1.4 for x in xs]
        series(c, F, xs, ys, P(t, b[3], 1.6), NAVY, 6, a3)
        ma = P(t, b[3] + 1.6, .5) * a3
        zone(c, F, 0, 22, 0, 100, MUTED, .12 * ma); zone(c, F, 78, 100, 0, 100, MUTED, .12 * ma)
        glow_dot(c, *F.P(22, ys[22]), 10, GREEN, t, ma); glow_dot(c, *F.P(78, ys[78]), 10, RED, t, ma)
        tag(c, F.X(11), F.Y(80), 'missed', MUTED, WHITE, 22, ma, 'c'); tag(c, F.X(89), F.Y(80), 'missed', MUTED, WHITE, 22, ma, 'c')
        text(c, 'Signals often miss around 20 to 25% of the move', 960, 840, 28, 'semi', MUTED, 'c', ma)
        ga = P(t, b[4], .5) * a3
        zone(c, F, 22, 78, 0, 100, GREEN, .12 * ga)
        tag(c, F.X(50), F.Y(50), 'The big middle', GREEN, WHITE, 30, ga, 'c')
    a5 = P(t, b[5], .5)
    if a5 > 0:
        blocks = ['Trends', 'Confirmation', 'Volume', 'Patience']
        for i, bl in enumerate(blocks):
            x = 360 + i * 310
            with pop(c, t, b[5] + .3 + i * .4, x + 140, 720) as a:
                card(c, x, 660, 280, 120, 16, [NAVY, BLUE, GREEN, GOLD][i], a * a5)
                text(c, bl, x + 140, 732, 32, 'bold', WHITE, 'c', a * a5)
        fa = P(t, b[6], .6)
        for i, nm in enumerate(['Trendlines', 'Patterns', 'Indicators', 'Systems']):
            x = 420 + i * 290
            with pop(c, t, b[6] + .2 + i * .25, x + 120, 520) as a:
                card(c, x, 460, 240, 150, 16, CARD, a * fa, border=FAINT)
                text(c, nm, x + 120, 545, 28, 'semi', INK, 'c', a * fa)
        text(c, 'DOW THEORY: THE FOUNDATION', 960, 860, 28, 'head', NAVY, 'c', a5, ls=4)
        text(c, 'Everything that follows builds on it', 960, 380, 34, 'serif', MUTED, 'c', fa)
