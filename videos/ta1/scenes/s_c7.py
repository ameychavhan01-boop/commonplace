from engine import *
from . import scene
from .common import *
from .data import btc_d, idx

# ------------------------------------------------------------ 7.1 volume
@scene('c7s1')
def c7s1(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        items = [('PRICE', 'most important', NAVY, 'candles'), ('VOLUME', 'confirms', BLUE, 'vol'), ('OPEN INTEREST', 'confirms (futures)', GOLD, 'oi')]
        for i, (ttl, sub, cl, k) in enumerate(items):
            x = 220 + i * 520
            with pop(c, t, b[1] + .3 + i * .5, x + 230, 560) as a:
                card(c, x, 340 + (0 if i == 0 else 40), 460, 400 - (0 if i == 0 else 40), 24, CARD, a * a1, border=cl, bw=4 if i == 0 else 2)
                text(c, ttl, x + 230, 420 + (0 if i == 0 else 30), 34, 'head', cl, 'c', a * a1, ls=2)
                text(c, sub, x + 230, 460 + (0 if i == 0 else 30), 24, 'semi', MUTED, 'c', a * a1)
                if k == 'candles':
                    for q, (o, cc) in enumerate([(20, -20), (-10, 30), (30, -30), (-20, 25)]):
                        xx = x + 140 + q * 60; c.rectangle(xx - 14, 580 + min(o, cc), 28, abs(o - cc)); col(c, GREEN if cc < o else RED, a * a1); c.fill()
                elif k == 'vol':
                    for q, hh in enumerate([60, 90, 50, 120, 80]): c.rectangle(x + 120 + q * 50, 680 - hh, 34, hh); col(c, BLUE, a * a1); c.fill()
                else: polyline(c, [(x + 110, 660), (x + 180, 630), (x + 250, 640), (x + 330, 580)], GOLD, 6, a * a1)
        da = P(t, b[2], .5) * a1
        pill(c, 960, 800, 'Volume = the intensity, the urgency, behind a move', 26, NAVY, WHITE, da, 'semi', 'c', ls=0)
    aV = stage(t, b, 3, 6)
    if aV > 0:
        n = 30
        keys = [(0, 20), (.2, 48), (.3, 40), (.55, 72), (.65, 63), (.9, 92), (1, 88)]
        O, Hh, L, C = path_ohlc(keys, n, 13, .01, .01)
        F = Frame(240, 330, 1100, 330, -1, n, 10, 100); Vf = Frame(240, 700, 1100, 150, -1, n, 0, 1)
        card(c, 190, 300, 1200, 580, 24, CARD, aV)
        late = P(t, b[5], .6)
        V = []
        for i in range(n):
            up = C[i] >= O[i]
            v = (1.0 if up else .45) + .1 * math.sin(i)
            if i > 20 and up: v *= lerp(1, .45 - (i - 20) * .03, late)
            V.append(v)
        candles(c, F, O, Hh, L, C, n * P(t, b[3], 1.6), a=aV)
        vbars(c, Vf, V, n * P(t, b[3] + .2, 1.6), 0, aV, [GREEN if C[i] >= O[i] else RED for i in range(n)], vmax=1.2)
        ha = P(t, b[4], .5) * aV * (1 - late)
        tag(c, 1600, 420, 'Heavy on up days', GREEN, WHITE, 24, ha, 'c'); tag(c, 1600, 470, 'Light on down days', RED, WHITE, 24, ha, 'c')
        tag(c, 1600, 540, '= a healthy trend', NAVY, WHITE, 24, ha, 'c')
        if late > 0:
            tag(c, 1600, 420, 'Rallies on lighter', GOLD, WHITE, 24, late * aV, 'c'); tag(c, 1600, 470, 'and lighter volume', GOLD, WHITE, 24, late * aV, 'c')
            tag(c, 1600, 540, 'Volume often precedes price', RED, WHITE, 24, P(t, b[5] + 1.2, .5) * aV, 'c')
            zone(c, Vf, 20.5, 30, 0, 1.2, GOLD, .15 * late * aV)
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        for i, k in enumerate(['hs', 'tri', 'flag']):
            x = 230 + i * 510
            with pop(c, t, b[6] + .2 + i * .4, x + 220, 560) as a:
                mini_chart_card(c, x, 380, 440, 300, k, a * a6, NAVY, ['Head & shoulders', 'Triangle', 'Breakout'][i])
                badge(c, x + 400, 410, 24, 'ok', a * a6 * P(t, b[6] + .6 + i * .4, .4))
        text(c, 'More convincing when volume behaves as expected', 960, 780, 30, 'serif', MUTED, 'c', P(t, b[6] + 1.6, .5) * a6)
    a7 = P(t, b[7], .5)
    if a7 > 0:
        quiet = P(t, b[7] + b.d[7] * .45, .8)
        card(c, 230, 360, 1460, 440, 26, CARD, a7)
        cx = 760 + 40 * math.sin(t * 2) * (1 - quiet * .5)
        rrect(c, cx - 200, 560, 400, 90, 36); col(c, RED, a7); c.fill()
        rrect(c, cx - 120, 500, 220, 80, 30); col(c, mix(RED, (0, 0, 0), .15), a7); c.fill()
        rrect(c, cx - 100, 515, 80, 50, 10); col(c, LBLUE, a7); c.fill(); rrect(c, cx, 515, 80, 50, 10); col(c, LBLUE, a7); c.fill()
        for wx in (cx - 120, cx + 120):
            circle(c, wx, 655, 36, INK, a7); circle(c, wx, 655, 14, FAINT, a7)
        for q in range(4):
            line(c, cx - 240 - q * 40, 580 + q * 16, cx - 300 - q * 40, 580 + q * 16, FAINT, 5, a7 * (1 - quiet))
        for q in range(3):
            ring(c, cx + 260, 590, 30 + q * 24, BLUE, 4, a7 * (1 - quiet) * (.6 - q * .15), .25, -.25 * math.pi)
        speedometer(c, 1360, 640, 150, .7 - .2 * quiet, a7, 'speed = price')
        text(c, 'engine = volume', 760, 760, 28, 'semi', BLUE, 'c', a7)
        text(c, 'Engine quiet = coasting', 960, 850, 32, 'serif', RED, 'c', quiet * a7)

# ------------------------------------------------------------ 7.2 OBV
@scene('c7s2')
def c7s2(c, t, b):
    a0 = stage(t, b, 0, 1)
    if a0 > 0:
        with pop(c, t, .4, 960, 560) as a:
            card(c, 460, 380, 1000, 330, 26, NAVY, a * a0)
            text(c, 'ON-BALANCE VOLUME', 960, 470, 44, 'head', WHITE, 'c', a * a0, ls=4)
            text(c, 'Joseph Granville  ·  1963', 960, 540, 32, 'serif', LGOLD, 'c', a * a0)
            text(c, "Granville's New Key to Stock Market Profits", 960, 610, 28, 'serif', WHITE, 'c', a * a0)
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        with pop(c, t, b[1], 960, 420) as a:
            card(c, 300, 320, 640, 200, 22, LGREEN, a * a1, border=GREEN)
            text(c, 'Close higher', 620, 400, 36, 'bold', GREEN, 'c', a * a1); text(c, '+ add the volume', 620, 460, 30, 'semi', INK, 'c', a * a1)
            card(c, 980, 320, 640, 200, 22, LRED, a * a1, border=RED)
            text(c, 'Close lower', 1300, 400, 36, 'bold', RED, 'c', a * a1); text(c, '- subtract the volume', 1300, 460, 30, 'semi', INK, 'c', a * a1)
        ta = P(t, b[2], .5) * a1
        if ta > 0:
            rows = [('Day', 'Price', 'Volume', 'OBV'), ('1', 'up', '100', '100'), ('2', 'up', '150', '250'), ('3', 'down', '80', '170')]
            card(c, 500, 560, 920, 320, 22, CARD, ta)
            for r, row in enumerate(rows):
                ra = ta if r == 0 else P(t, b[2] + (r - 1) * b.d[2] * .3, .4) * ta
                for k, cell in enumerate(row):
                    x = 620 + k * 220; y = 615 + r * 70
                    clr = (GREEN if cell == 'up' else RED if cell == 'down' else GOLD if k == 3 and r else MUTED if r == 0 else INK)
                    text(c, cell, x, y, 30 if r else 22, 'head' if k == 3 and r else 'semi', clr, 'c', ra)
                if r == 0: line(c, 540, 635, 1380, 635, LINE, 2, ta)
    a3 = stage(t, b, 3, 5)
    if a3 > 0:
        P1 = Frame(260, 330, 900, 250, 0, 10, 0, 100); V1 = Frame(260, 630, 900, 220, 0, 10, 0, 100)
        card(c, 210, 300, 1000, 580, 24, CARD, a3)
        text(c, 'PRICE', 240, 345, 20, 'head', NAVY, 'l', a3, ls=3); text(c, 'OBV', 240, 625, 20, 'head', GOLD, 'l', a3, ls=3)
        div = P(t, b[4], .5)
        pp = [(0, 20), (2, 50), (3, 38), (5.5, 68), (6.5, 55), (9, 88), (10, 82)]
        vv = [(0, 20), (2, 55), (3, 45), (5.5, 75), (6.5, 62), (9, lerp(92, 66, div)), (10, lerp(88, 58, div))]
        polyline(c, [P1.P(*p_) for p_ in pp], NAVY, 5, a3, P(t, b[3], 1.6))
        polyline(c, [V1.P(*p_) for p_ in vv], GOLD, 5, a3, P(t, b[3] + .3, 1.6))
        ca = P(t, b[3] + 1.8, .5) * a3 * (1 - div)
        pill(c, 1500, 560, 'Rising together = confirmed', 26, GREEN, WHITE, ca, 'semi', 'c', ls=0)
        if div > 0:
            seg(c, P1, 5.5, 68, 9, 88, GREEN, 4, div * a3); seg(c, V1, 5.5, 75, 9, 66, RED, 4, div * a3)
            pill(c, 1500, 520, 'Price: new high', 26, GREEN, WHITE, div * a3, 'semi', 'c', ls=0)
            pill(c, 1500, 590, 'OBV: no new high', 26, RED, WHITE, div * a3, 'semi', 'c', ls=0)
            pill(c, 1500, 660, '= DIVERGENCE', 28, GOLD, WHITE, P(t, b[4] + 1, .4) * a3, 'semi', 'c', ls=2)
    a5 = P(t, b[5], .5)
    if a5 > 0:
        d = btc_d(); C, V = d['c'], d['v']; n = len(C)
        obv = [0.0]
        for i in range(1, n): obv.append(obv[-1] + (V[i] if C[i] > C[i - 1] else -V[i] if C[i] < C[i - 1] else 0))
        F = Frame(240, 350, 1220, 270, 0, n - 1, 64000, 114000)
        G = Frame(240, 670, 1220, 180, 0, n - 1, min(obv) * 1.05 - 1000, max(obv) * 1.05 + 1000)
        card(c, 190, 300, 1350, 590, 24, CARD, a5)
        text(c, 'BITCOIN  ·  daily close', 240, 330, 22, 'semi', INK, 'l', a5)
        text(c, 'ON-BALANCE VOLUME  ·  calculated from Bitstamp volume', 240, 660, 20, 'semi', GOLD, 'l', a5)
        ygrid(c, F, [70000, 80000, 90000, 100000], fmt_k, a5, size=16)
        series(c, F, range(n), C, P(t, b[5] + .2, 2.2), NAVY, 3.5, a5)
        series(c, G, range(n), obv, P(t, b[5] + .5, 2.2), GOLD, 3.5, a5, GOLD, .12)
        xlabels(c, G, [(idx(d, '2024-11-01'), 'Nov'), (idx(d, '2024-12-01'), 'Dec'), (idx(d, '2025-01-01'), 'Jan')], a5, 16)
        text(c, 'Data: TradingView · BITSTAMP:BTCUSD', 1520, 880, 16, 'med', FAINT, 'r', a5)
        ra = P(t, b[5] + 2.6, .5)
        tag(c, 1680, 420, 'Nov: price and OBV', GREEN, WHITE, 22, ra, 'c')
        tag(c, 1680, 466, 'rise together', GREEN, WHITE, 22, ra, 'c')
    a6 = P(t, b[6], .5)
    if a6 > 0:
        card(c, 1570, 560, 230, 250, 20, NAVY, a6)
        text(c, 'Refinements', 1685, 615, 22, 'semi', LGOLD, 'c', a6)
        text(c, 'weight by', 1685, 655, 22, 'semi', WHITE, 'c', a6)
        text(c, 'where the close', 1685, 685, 22, 'semi', WHITE, 'c', a6)
        text(c, 'sits in the range', 1685, 715, 22, 'semi', WHITE, 'c', a6)
        text(c, 'Follow the money', 1685, 775, 22, 'bold', GOLD, 'c', P(t, b[6] + 1.2, .5))

# ------------------------------------------------------------ 7.3 open interest
@scene('c7s3')
def c7s3(c, t, b):
    aA = stage(t, b, 0, 6)
    if aA > 0:
        with pop(c, t, .3, 480, 450) as a:
            card(c, 200, 320, 560, 260, 24, CARD, a * aA)
            text(c, 'Nifty futures', 330, 390, 28, 'bold', NAVY, 'l', a * aA)
            text(c, 'Bitcoin futures', 330, 440, 28, 'bold', ORANGE, 'l', a * aA)
            coin(c, 280, 380, 22, '₹', NAVY, a * aA); btc(c, 280, 430, 22, a * aA)
            text(c, 'Futures & options only', 480, 530, 22, 'semi', MUTED, 'c', a * aA)
        oi_val = 0
        steps_ = [(b[2], 1, 'New buyer + new seller', '+1', GREEN), (b[3], 0, 'New buyer replaces old buyer', '0', MUTED), (b[3] + b.d[3] * .5, 0, 'New seller replaces old seller', '0', MUTED), (b[4], -1, 'Old buyer + old seller exit', '-1', RED)]
        for t0, dv, *_ in steps_:
            if t >= t0 + .6: oi_val += dv
        ca = P(t, b[1], .5) * aA
        card(c, 860, 320, 860, 260, 24, NAVY, ca)
        text(c, 'OPEN INTEREST', 1290, 380, 24, 'semi', LGOLD, 'c', ca, ls=4)
        text(c, f'{1000 + oi_val:,} contracts', 1290, 460, 52, 'head', WHITE, 'c', ca)
        handshake(c, 1290, 508, .9, ca)
        text(c, 'one buyer + one seller = one contract', 1290, 560, 18, 'semi', LGOLD, 'c', ca)
        for i, (t0, dv, lab, d_, cl) in enumerate(steps_):
            y = 620 + i * 66
            with rise(c, t, t0) as a:
                card(c, 200, y, 1520, 56, 14, CARD, a * aA)
                text(c, lab, 240, y + 37, 26, 'semi', INK, 'l', a * aA)
                pill(c, 1690, y + 8, f'OI {d_}', 22, cl, WHITE, a * aA, 'semi', 'r', ls=1)
        ma = P(t, b[5], .5) * aA
        if ma > 0:
            card(c, 860, 320, 860, 260, 24, CARD, ma, border=GOLD, bw=3)
            text(c, 'Rising OI: new money flowing in', 1290, 420, 32, 'bold', GREEN, 'c', ma)
            text(c, 'Falling OI: money leaving', 1290, 490, 32, 'bold', RED, 'c', ma)
    aT = P(t, b[6], .5)
    if aT > 0:
        rows = [('↑', '↑', 'New buying', 'STRONG', GREEN, b[6]), ('↑', '↓', 'Short covering', 'WEAK', RED, b[7]),
                ('↓', '↑', 'Aggressive new selling', 'BEARISH', RED, b[8]), ('↓', '↓', 'Longs liquidating', 'STRONGER WHEN DONE', GOLD, b[9])]
        card(c, 220, 300, 1480, 90, 18, NAVY, aT)
        for k, h_ in enumerate(['PRICE', 'OPEN INTEREST', 'WHAT IT MEANS', 'VERDICT']):
            text(c, h_, [330, 600, 980, 1460][k], 356, 22, 'semi', LGOLD, 'c', aT, ls=3)
        for i, (pr, oi, mean, ver, cl, t0) in enumerate(rows):
            y = 410 + i * 118
            with rise(c, t, t0 + (.3 if i == 0 else 0)) as a:
                card(c, 220, y, 1480, 100, 18, CARD, a * aT)
                for k, (sym, xx) in enumerate(((pr, 330), (oi, 600))):
                    circle(c, xx, y + 50, 34, GREEN if sym == '↑' else RED, a * aT)
                    text(c, sym, xx, y + 66, 44, 'head', WHITE, 'c', a * aT)
                text(c, mean, 980, y + 62, 30, 'semi', INK, 'c', a * aT)
                pill(c, 1460, y + 28, ver, 22, cl, WHITE, a * aT, 'semi', 'c', ls=2)

# ------------------------------------------------------------ 7.4 climaxes & COT
@scene('c7s4')
def c7s4(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        for i, (ttl, kind, t0) in enumerate([('BLOWOFF AT A TOP', 'top', b[1]), ('SELLING CLIMAX AT A BOTTOM', 'bot', b[2])]):
            x = 180 + i * 800
            with pop(c, t, t0, x + 380, 560) as a:
                if a <= 0: continue
                card(c, x, 300, 760, 580, 24, CARD, a * a1)
                text(c, ttl, x + 380, 350, 26, 'head', RED if kind == 'top' else GREEN, 'c', a * a1, ls=2)
                F = Frame(x + 50, 380, 660, 250, 0, 20, 0, 100); V = Frame(x + 50, 660, 660, 110, -.5, 20.5, 0, 1); OI = Frame(x + 50, 660, 660, 110, 0, 20, 0, 100)
                if kind == 'top':
                    ys = [20 + i_ * 2 + (i_ - 14) ** 2 * 1.4 * (i_ > 14) for i_ in range(21)]
                    vs = [.3 + .02 * i_ + (.6 if i_ > 15 else 0) for i_ in range(21)]
                    ois = [30 + i_ * 3 if i_ < 15 else 72 - (i_ - 15) * 6 for i_ in range(21)]
                else:
                    ys = [90 - i_ * 2 - (i_ - 14) ** 2 * 1.4 * (i_ > 14) for i_ in range(21)]
                    vs = [.3 + .02 * i_ + (.6 if i_ > 15 else 0) for i_ in range(21)]
                    ois = [40 + i_ * 2 if i_ < 16 else 70 - (i_ - 16) * 7 for i_ in range(21)]
                series(c, F, range(21), ys, P(t, t0 + .2, 1.6), NAVY, 5, a * a1)
                vbars(c, V, vs, 21 * P(t, t0 + .3, 1.6), 0, a * a1, [BLUE] * 21, vmax=1)
                series(c, OI, range(21), ois, P(t, t0 + .5, 1.6), GOLD, 4, a * a1)
                text(c, 'volume', x + 60, 800, 20, 'semi', BLUE, 'l', a * a1); text(c, 'open interest', x + 180, 800, 20, 'semi', GOLD, 'l', a * a1)
                text(c, 'Huge volume, OI starts to fall' if kind == 'top' else 'Panic volume, then exhaustion', x + 380, 850, 24, 'semi', INK, 'c', a * a1)
    a3 = stage(t, b, 3, 6)
    if a3 > 0:
        with pop(c, t, b[3], 960, 360) as a:
            card(c, 420, 300, 1080, 120, 22, NAVY, a * a3)
            text(c, 'COMMITMENTS OF TRADERS REPORT', 960, 352, 30, 'head', WHITE, 'c', a * a3, ls=3)
            text(c, 'published by the U.S. Commodity Futures Trading Commission', 960, 392, 22, 'semi', LGOLD, 'c', a * a3)
        groups = [('Commercials', 'hedgers using the market in business', NAVY, 'side', GOLD, True), ('Large speculators', 'big funds', BLUE, 'short', None, False), ('Small traders', 'individuals', GOLD, 'curly', None, False)]
        for i, (ttl, sub, cl, sty, tie, glasses) in enumerate(groups):
            x = 300 + i * 450
            with pop(c, t, b[4] + i * b.d[4] * .3, x + 160, 640) as a:
                card(c, x, 460, 360, 400, 24, CARD, a * a3, border=GOLD if (i == 0 and t > b[5]) else None, bw=4)
                avatar(c, x + 180, 560, .95, SKIN[i], HAIR[i], cl, sty, tie=tie, glasses=glasses, t=t, seed=i, a=a * a3)
                text(c, ttl, x + 180, 750, 30, 'bold', INK, 'c', a * a3)
                text(c, sub, x + 180, 790, 21, 'semi', MUTED, 'c', a * a3)
        sa = P(t, b[5], .5) * a3
        pill(c, 480, 470, 'SMART MONEY', 20, GOLD, WHITE, sa, 'semi', 'c', ls=2)
        pill(c, 1380, 470, 'BE WARY AT EXTREMES', 20, RED, WHITE, P(t, b[5] + 1.2, .4) * a3, 'semi', 'c', ls=2)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        with pop(c, t, b[6], 960, 560) as a:
            card(c, 360, 400, 1200, 320, 26, NAVY, a * a6)
            text(c, 'Price tells you what happened.', 960, 520, 46, 'serif', WHITE, 'c', a * a6)
            text(c, 'Volume and open interest tell you the conviction.', 960, 600, 36, 'serif', LGOLD, 'c', a * a6)
