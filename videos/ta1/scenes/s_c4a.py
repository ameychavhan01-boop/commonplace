from engine import *
from . import scene
from .common import *
from .data import btc_w, btc_d, nifty_w, idx

def zig(c, x, y, w, h, kind, p=1.0, a=1.0, cl=NAVY, dots=True, t=0.0, lw=5):
    pts = pattern_pts(kind, x, y, w, h)
    polyline(c, pts, cl, lw, a, p)
    if dots:
        for j, (px, py) in enumerate(pts[1:-1], 1):
            if j / (len(pts) - 1) > p: break
            pk = py < pts[j - 1][1]
            circle(c, px, py, 9, RED if pk else GREEN, a)
    return pts

# ------------------------------------------------------------ 4.1 what a trend is
@scene('c4s1')
def c4s1(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        with pop(c, t, b[1], 960, 520) as a:
            text(c, 'TREND', 960, 450, 120, 'head', NAVY, 'c', a * a1, ls=10)
            text(c, '=  the direction of the market', 960, 540, 44, 'serif', INK, 'c', a * a1)
        for i, (ang, cl) in enumerate([(-.6, GREEN), (0, GOLD), (.6, RED)]):
            x = 700 + i * 260
            arrow(c, x - 80 * math.cos(ang), 700 - 80 * math.sin(ang), x + 80 * math.cos(ang), 700 + 80 * math.sin(ang), cl, 10, P(t, b[1] + 1 + i * .3, .4) * a1, P(t, b[1] + 1 + i * .3, .6), 30)
    a2 = stage(t, b, 2, 3)
    if a2 > 0:
        k = P(t, b[2] + 1.2, 1.2, eio)
        pts = pattern_pts('up', 220, 360, 1480, 420)
        c.new_path(); c.move_to(220, 800)
        for px, py in pts: c.line_to(px, lerp(py, py, 1))
        c.line_to(1700, 800); c.close_path()
        g = cairo.LinearGradient(0, 360, 0, 800); g.add_color_stop_rgba(0, *BLUE, .35 * a2 * (1 - k)); g.add_color_stop_rgba(1, *NAVY, .5 * a2 * (1 - k)); c.set_source(g); c.fill()
        for px, py in pts[1:-1]:
            if py < 500: c.new_path(); c.move_to(px - 40, py + 36); c.line_to(px, py); c.line_to(px + 40, py + 36); col(c, WHITE, .8 * a2 * (1 - k)); c.fill()
        zig(c, 220, 360, 1480, 420, 'up', P(t, b[2] + 1.0, 1.4), a2 * max(k, .001) if k > 0 else 0)
        text(c, 'Peaks and troughs, like a mountain range', 960, 860, 30, 'serif', MUTED, 'c', P(t, b[2] + .4, .5) * a2)
    a3 = stage(t, b, 3, 6)
    if a3 > 0:
        panels = [('UPTREND', 'up', GREEN, 'Rising peaks & troughs', b[3]), ('DOWNTREND', 'down', RED, 'Falling peaks & troughs', b[4]), ('SIDEWAYS', 'side', GOLD, 'Horizontal: a trading range', b[5])]
        for i, (ttl, k, cl, sub, t0) in enumerate(panels):
            x = 160 + i * 545
            with pop(c, t, t0, x + 260, 560) as a:
                if a <= 0: continue
                card(c, x, 320, 520, 520, 24, CARD, a * a3)
                text(c, ttl, x + 260, 380, 32, 'head', cl, 'c', a * a3, ls=3)
                zig(c, x + 50, 430, 420, 280, k, P(t, t0 + .2, 1.3), a * a3, NAVY, True, t, 5)
                text(c, sub, x + 260, 790, 24, 'semi', MUTED, 'c', a * a3)
                if k == 'side':
                    line(c, x + 50, 430 + 280 * .2, x + 470, 430 + 280 * .2, RED, 3, a * a3 * P(t, t0 + 1.4, .4), [10, 8])
                    line(c, x + 50, 430 + 280 * .78, x + 470, 430 + 280 * .78, GREEN, 3, a * a3 * P(t, t0 + 1.4, .4), [10, 8])
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        cx, cy, r = 700, 580, 200
        k = P(t, b[6] + .4, 1.2, eio)
        c.new_path(); c.arc(cx, cy, r, -math.pi / 2, -math.pi / 2 + 2 * math.pi * (2 / 3) * k); col(c, NAVY, a6); c.set_line_width(70); c.stroke()
        c.new_path(); c.arc(cx, cy, r, -math.pi / 2 + 2 * math.pi * (2 / 3), -math.pi / 2 + 2 * math.pi * (2 / 3 + (1 / 3) * P(t, b[6] + 1.4, .8, eio))); col(c, GOLD, a6); c.set_line_width(70); c.stroke()
        text(c, '1/3', cx, cy + 30, 90, 'head', GOLD, 'c', P(t, b[6] + 1.8, .5) * a6)
        la = P(t, b[6] + 2, .5) * a6
        label_card(c, 1050, 400, 640, 140, 'Sideways', 'Perhaps a third of the time, or more', la, GOLD, 34, 26)
        label_card(c, 1050, 580, 640, 140, 'Trending', 'Up or down: the rest of the time', la, NAVY, 34, 26)
    a7 = P(t, b[7], .5)
    if a7 > 0:
        for i, (ttl, k, ok) in enumerate([('Trending market', 'up', True), ('Sideways market', 'side', False)]):
            x = 230 + i * 760
            with pop(c, t, b[7] + i * .5, x + 340, 560) as a:
                card(c, x, 330, 690, 440, 24, LGREEN if ok else LRED, a * a7)
                text(c, ttl, x + 345, 390, 32, 'head', GREEN if ok else RED, 'c', a * a7)
                zig(c, x + 70, 430, 550, 220, k, 1, a * a7, NAVY, False)
                text(c, 'Trend-following tools shine' if ok else 'Trend-following tools struggle', x + 345, 730, 26, 'semi', INK, 'c', a * a7)
                badge(c, x + 640, 360, 30, 'ok' if ok else 'no', a * a7)
        pill(c, 960, 820, 'Part of the skill: knowing when NOT to trade', 28, NAVY, WHITE, P(t, b[7] + b.d[7] * .5, .5), 'semi', 'c', ls=0)

# ------------------------------------------------------------ 4.2 three sizes
@scene('c4s2')
def c4s2(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        rows = [('MAJOR', 'more than a year', 1300, NAVY), ('INTERMEDIATE', '3 weeks to several months', 620, BLUE), ('NEAR-TERM', 'less than 2 to 3 weeks', 160, GOLD)]
        for i, (lab, sub, w_, cl) in enumerate(rows):
            y = 360 + i * 170
            with rise(c, t, b[1] + .2 + i * b.d[1] * .28) as a:
                text(c, lab, 220, y + 10, 30, 'head', cl, 'l', a * a1, ls=2)
                text(c, sub, 220, y + 48, 24, 'semi', MUTED, 'l', a * a1)
                rrect(c, 640, y - 20, w_ * P(t, b[1] + .4 + i * b.d[1] * .28, .9, eio) + 8, 56, 28); col(c, cl, a * a1); c.fill()
    a2 = stage(t, b, 2, 4)
    if a2 > 0:
        rnd = random.Random(9)
        panels = []
        for k in range(3):
            x = 150 + k * 560
            ys = path_line(PATTERNS['up'], 60)
            ys = [v + rnd.gauss(0, .02 * (k + 1)) for v in ys]
            panels.append((x, ys))
        for k, (x, ys) in enumerate(panels):
            with pop(c, t, b[2] + .2 + k * .8, x + 250, 560) as a:
                if a <= 0: continue
                card(c, x, 340, 500, 400, 22, CARD, a * a2)
                F = Frame(x + 40, 400, 420, 280, 0, 59, -.1, 1.1)
                series(c, F, range(60), ys, P(t, b[2] + .3 + k * .8, 1.2), [NAVY, BLUE, GOLD][k], 4, a * a2)
                lab = ['MAJOR', 'INTERMEDIATE', 'NEAR-TERM'][k]
                text(c, lab, x + 250, 712, 26, 'head', [NAVY, BLUE, GOLD][k], 'c', a * a2, ls=2)
                if k < 2:
                    za = P(t, b[2] + .9 + k * .8, .4) * a2
                    zx0, zx1 = F.X(24), F.X(40)
                    rrect(c, zx0, 470, zx1 - zx0, 150, 8); col(c, GOLD, za); c.set_line_width(3); c.stroke()
                    line(c, zx1, 470, x + 560, 340, GOLD, 2, za * .7, [6, 6])
                    line(c, zx1, 620, x + 560, 740, GOLD, 2, za * .7, [6, 6])
        ta = P(t, b[3], .5) * a2
        for i, s_ in enumerate(['= the tide', '= the waves', '= the ripples']):
            pill(c, 400 + i * 560, 780, s_, 26, [NAVY, BLUE, GOLD][i], WHITE, ta * P(t, b[3] + i * .3, .4), 'serif', 'c', ls=0)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        for i, (ttl, ok) in enumerate([('With the tide', True), ('Against the current', False)]):
            x = 180 + i * 800
            with pop(c, t, b[4] + i * b.d[4] * .45, x + 380, 560) as a:
                if a <= 0: continue
                card(c, x, 330, 760, 460, 24, CARD, a * a4)
                c.save(); rrect(c, x, 330, 760, 460, 24); c.clip()
                c.rectangle(x, 560, 760, 230); col(c, LBLUE, a * a4); c.fill()
                for q in range(6):
                    u = ((t * .3 + q / 6) % 1)
                    arrow(c, x + u * 760 - 60, 640 + (q % 2) * 70, x + u * 760, 640 + (q % 2) * 70, BLUE, 4, a * a4 * .6)
                sx = x + 380 + (40 if ok else -10) * math.sin(t)
                avatar(c, sx, 540, .7, SKIN[1], HAIR[0], RED, 'short', mood='happy' if ok else 'worried', t=t, a=a * a4, body=False, look=1 if ok else -1)
                c.restore()
                text(c, ttl, x + 380, 400, 34, 'head', GREEN if ok else RED, 'c', a * a4)
                text(c, 'Buying a dip in a major uptrend' if ok else 'Buying a dip in a major downtrend', x + 380, 450, 24, 'semi', MUTED, 'c', a * a4)
                badge(c, x + 700, 380, 28, 'ok' if ok else 'no', a * a4)
    a5 = P(t, b[5], .5)
    if a5 > 0:
        avatar(c, 520, 560, 1.15, SKIN[0], HAIR[1], BLUE, 'short', mood='happy', t=t, a=a5)
        avatar(c, 1400, 560, 1.15, SKIN[2], HAIR[2], GOLD, 'curly', mood='worried', t=t, seed=3, a=a5)
        bubble(c, 300, 330, 440, 100, '"It\'s going up!"', a5, 36, 'serif', GREEN, CARD, 'br')
        bubble(c, 1180, 330, 460, 100, '"It\'s going down!"', a5, 36, 'serif', RED, CARD, 'bl')
        pill(c, 520, 760, 'Looking at: MAJOR trend', 24, NAVY, WHITE, P(t, b[5] + 1, .4), 'semi', 'c', ls=1)
        pill(c, 1400, 760, 'Looking at: NEAR-TERM trend', 24, GOLD, WHITE, P(t, b[5] + 1.3, .4), 'semi', 'c', ls=1)
        text(c, 'Both can be right', 960, 580, 34, 'serif', MUTED, 'c', P(t, b[5] + 2, .5))

# ------------------------------------------------------------ 4.3 support & resistance
@scene('c4s3')
def c4s3(c, t, b):
    aA = stage(t, b, 0, 3)
    if aA > 0:
        F = Frame(240, 330, 1100, 470, 0, 100, 0, 100)
        card(c, 190, 300, 1200, 540, 24, CARD, aA)
        xs = list(range(101)); ys = [50 + 28 * math.sin(x / 100 * 2 * math.pi * 3.2) + 3 * math.sin(x * 1.3) for x in xs]
        series(c, F, xs, ys, P(t, .4, 2.5), NAVY, 5, aA)
        sa = P(t, b[1], .5) * aA
        hline(c, F, 22, cl=GREEN, lw=5, a=sa, prog=P(t, b[1], .8), label='SUPPORT', size=24)
        for q in range(3):
            arrow(c, F.X(15 + q * 31), F.Y(5), F.X(15 + q * 31), F.Y(18), GREEN, 5, sa * P(t, b[1] + 1 + q * .3, .4), 1, 16)
        ra = P(t, b[2], .5) * aA
        hline(c, F, 78, cl=RED, lw=5, a=ra, prog=P(t, b[2], .8), label='RESISTANCE', size=24)
        for q in range(3):
            arrow(c, F.X(8 + q * 31), F.Y(97), F.X(8 + q * 31), F.Y(83), RED, 5, ra * P(t, b[2] + 1 + q * .3, .4), 1, 16)
        text(c, 'Buyers overpower sellers', 1560, F.Y(22) + 80, 24, 'semi', GREEN, 'c', sa)
        text(c, 'Sellers overpower buyers', 1560, F.Y(78) + 80, 24, 'semi', RED, 'c', ra)
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        card(c, 560, 300, 800, 560, 24, CARD, a3)
        c.rectangle(560, 320, 800, 26); col(c, RED, a3); c.fill()
        c.rectangle(560, 814, 800, 26); col(c, GREEN, a3); c.fill()
        text(c, 'CEILING  =  RESISTANCE', 960, 390, 28, 'head', RED, 'c', a3, ls=2)
        text(c, 'FLOOR  =  SUPPORT', 960, 790, 28, 'head', GREEN, 'c', a3, ls=2)
        u = (t * .8) % 1; by = 420 + 300 * (1 - abs(2 * u - 1)) ** .7
        circle(c, 960 + 140 * math.sin(t * .9), by, 36, GOLD, a3)
    a4 = stage(t, b, 4, 6)
    if a4 > 0:
        for i, (ttl, kind) in enumerate([('Uptrend: ceilings get broken', 'up'), ('Downtrend: floors give way', 'down')]):
            x = 170 + i * 800
            with pop(c, t, b[4] + i * .6, x + 380, 560) as a:
                if a <= 0: continue
                card(c, x, 320, 780, 470, 24, CARD, a * a4)
                text(c, ttl, x + 390, 370, 28, 'bold', GREEN if kind == 'up' else RED, 'c', a * a4)
                pts = pattern_pts(kind, x + 60, 410, 660, 320)
                polyline(c, pts, NAVY, 5, a * a4, P(t, b[4] + .3 + i * .6, 1.5))
                for j in (1, 3) if kind == 'up' else (1, 3):
                    px, py = pts[j]
                    line(c, px - 40, py, px + 230, py, RED if kind == 'up' else GREEN, 3, a * a4 * P(t, b[4] + .8 + j * .2, .4), [10, 8])
        wa = P(t, b[5], .5) * a4
        if wa > 0:
            card(c, 520, 800, 880, 90, 20, LGOLD, wa, border=GOLD)
            warn(c, 580, 846, .38, wa)
            text(c, 'Warning: a rally fails below the last peak, or a dip breaks the last trough', 980, 856, 22, 'semi', INK, 'c', wa)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        d = btc_w(); i1 = idx(d, '2024-11-04'); n = i1
        O, Hh, L, C = d['o'], d['h'], d['l'], d['c']
        F = Frame(200, 330, 1380, 470, -1, n, 23000, 80000)
        chart_card(c, F, a6, 'BITCOIN', 'weekly, Sep 2023 to Oct 2024', 'Data: TradingView · BITSTAMP:BTCUSD')
        ygrid(c, F, [30000, 40000, 50000, 60000, 70000], fmt_k, a6)
        xlabels(c, F, [(idx(d, '2023-10-02'), 'Oct 23'), (idx(d, '2024-01-01'), 'Jan 24'), (idx(d, '2024-04-01'), 'Apr'), (idx(d, '2024-07-01'), 'Jul'), (idx(d, '2024-10-07'), 'Oct')], a6)
        candles(c, F, O, Hh, L, C, n * P(t, b[6] + .2, 1.8), a=a6)
        im = idx(d, '2024-03-11')
        ra = P(t, b[6] + 1.6, .5) * a6
        hline(c, F, 73794, im, n, RED, 4, ra, P(t, b[6] + 1.6, .8), [14, 8])
        tag(c, F.X(im), F.Y(73794) - 70, 'Mar 2024 high $73,794', RED, WHITE, 22, ra, 'c', point=(F.X(im), F.Y(73794) - 8))
        for k, (ds, lab) in enumerate((('2024-06-03', 'June: stalled'), ('2024-10-28', 'Oct: stalled'))):
            i = idx(d, ds); ta = P(t, b[6] + 2.6 + k * .7, .4) * a6
            glow_dot(c, F.X(i), F.Y(Hh[i]), 8, GOLD, t, ta)
            tag(c, F.X(i), F.Y(Hh[i]) + 40, lab, GOLD, WHITE, 20, ta, 'c')
        ha = P(t, b[7], .5) * a6
        if ha > 0:
            card(c, 1220, 680, 330, 110, 18, NAVY, ha)
            text(c, 'Held for almost', 1385, 722, 22, 'semi', LGOLD, 'c', ha)
            text(c, '8 months', 1385, 770, 38, 'head', WHITE, 'c', ha)

# ------------------------------------------------------------ 4.4 psychology
@scene('c4s4')
def c4s4(c, t, b):
    aC = P(t, .3, .5) * (1 - P(t, b[6] - .3, .4))
    F = Frame(220, 340, 700, 440, 0, 60, 0, 100)
    xs = list(range(61))
    ys = [40 + 6 * math.sin(x * .9) if x < 28 else (40 + (x - 28) * 2.4 if x < 44 else 78 - (x - 44) * 4 if x < 52 else 46 + (x - 52) * 4) for x in xs]
    if aC > 0:
        card(c, 180, 300, 780, 560, 24, CARD, aC)
        za = P(t, b[1], .5) * aC
        zone(c, F, 0, 28, 33, 47, GOLD, .18 * za)
        text(c, 'the range', F.X(14), F.Y(47) - 12, 22, 'semi', GOLD, 'c', za)
        series(c, F, xs, ys, P(t, b[1] + .3, 2.2) * (1 if t < b[5] else 1), NAVY, 5, aC)
        sa = P(t, b[5], .5) * aC
        if sa > 0:
            zone(c, F, 28, 60, 33, 47, GREEN, .25 * sa)
            tag(c, F.X(52), F.Y(33) + 40, 'NEW SUPPORT', GREEN, WHITE, 24, sa, 'c')
    groups = [('LONGS', 'Bought in the range', '"I\'ll buy more on a dip"', GREEN, 'happy', b[2]),
              ('SHORTS', 'Sold in the range', '"Get me out at break-even!"', RED, 'worried', b[3]),
              ('UNCOMMITTED', 'Watched or sold early', '"Next dip, I\'m in"', BLUE, 'smile', b[4])]
    for i, (lab, sub, quote, cl, mood, t0) in enumerate(groups):
        y = 300 + i * 190
        with pop(c, t, t0, 1360, y + 85) as a:
            if a <= 0: continue
            ga = a * (1 - P(t, b[6] - .3, .4))
            card(c, 1000, y, 760, 170, 22, CARD, ga, border=cl, bw=3)
            avatar(c, 1080, y + 70, .62, SKIN[i], HAIR[i], cl, ['short', 'long', 'curly'][i], mood=mood, t=t, seed=i, a=ga)
            text(c, lab, 1170, y + 56, 28, 'head', cl, 'l', ga, ls=2)
            text(c, sub, 1170, y + 92, 22, 'semi', MUTED, 'l', ga)
            text(c, quote, 1170, y + 136, 26, 'serif', INK, 'l', ga)
            ba = P(t, b[5] + i * .2, .4) * ga
            if ba > 0:
                pill(c, 1740, y + 18, 'BUYS', 18, GREEN, WHITE, ba, 'semi', 'r', ls=2)
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        for i, (lab, sub, kind) in enumerate([('TIME', 'longer in the area', 'clock'), ('VOLUME', 'more traded there', 'vol'), ('RECENCY', 'more recent', 'cal')]):
            x = 200 + i * 530
            with pop(c, t, b[6] + .3 + i * .5, x + 240, 560) as a:
                card(c, x, 320, 480, 440, 24, CARD, a * a6)
                if kind == 'clock': clock(c, x + 240, 450, 70, t * 4, a * a6)
                elif kind == 'vol':
                    for q, hh in enumerate([40, 70, 110, 90, 130]):
                        c.rectangle(x + 150 + q * 40, 520 - hh, 28, hh); col(c, BLUE, a * a6); c.fill()
                else: calendar(c, x + 240, 450, .9, a * a6)
                text(c, lab, x + 240, 600, 32, 'head', NAVY, 'c', a * a6, ls=3)
                text(c, sub, x + 240, 640, 24, 'semi', MUTED, 'c', a * a6)
                rrect(c, x + 60, 690, 360, 18, 9); col(c, GRID, a * a6); c.fill()
                rrect(c, x + 60, 690, 360 * P(t, b[6] + .8 + i * .5, 1, eio), 18, 9); col(c, GREEN, a * a6); c.fill()
        text(c, '= a stronger level', 960, 830, 32, 'serif', INK, 'c', P(t, b[6] + 2.4, .5) * a6)
    a7 = P(t, b[7], .5)
    if a7 > 0:
        with pop(c, t, b[7], 960, 560) as a:
            card(c, 360, 330, 1200, 480, 26, NAVY, a * a7)
            for k, (lv, lab) in enumerate([(0, 'Where many bought'), (1, 'Where many sold'), (2, 'Where many waited')]):
                yy = 430 + k * 110
                line(c, 440, yy, 440 + 520 * P(t, b[7] + .4 + k * .3, .6), yy, [GREEN, RED, GOLD][k], 6, a * a7, [16, 10])
                text(c, lab, 1000, yy + 10, 30, 'semi', WHITE, 'l', a * a7 * P(t, b[7] + .6 + k * .3, .4))
            text(c, "The market's memory", 960, 770, 44, 'serif', LGOLD, 'c', a * a7)

# ------------------------------------------------------------ 4.5 role reversal
@scene('c4s5')
def c4s5(c, t, b):
    aS = stage(t, b, 0, 3)
    if aS > 0:
        F = Frame(240, 350, 1100, 440, 0, 100, 0, 100)
        card(c, 190, 310, 1200, 540, 24, CARD, aS)
        xs = list(range(101))
        ys = [40 + 20 * abs(math.sin(x / 9)) if x < 40 else (60 + (x - 40) * 1.6 if x < 58 else 88 - (x - 58) * 1.4 if x < 75 else 64 + (x - 75) * 1.3) for x in xs]
        k = P(t, .4, b[1] + 2 - .4, lambda u: u)
        series(c, F, xs, ys, k, NAVY, 5, aS)
        sw = P(t, b[1] + 1, .8)
        cl = mix(RED, GREEN, sw)
        hline(c, F, 61, cl=cl, lw=5, a=aS)
        text(c, 'RESISTANCE', F.X(2), F.Y(61) - 16, 24, 'head', RED, 'l', aS * (1 - sw), ls=2)
        text(c, 'SUPPORT', F.X(2), F.Y(61) - 16, 24, 'head', GREEN, 'l', aS * sw, ls=2)
        ta = P(t, b[1] + 1.8, .4) * aS
        glow_dot(c, F.X(75), F.Y(64), 9, GREEN, t, ta)
        tag(c, F.X(75), F.Y(64) + 40, 'Old ceiling, new floor', GREEN, WHITE, 22, ta, 'c')
        pa = P(t, b[2], .5) * aS
        if pa > 0:
            avatar(c, 1580, 500, 1.0, SKIN[1], HAIR[0], BLUE, 'short', mood='worried', t=t, a=pa)
            bubble(c, 1400, 300, 420, 110, '"I missed it. If it comes back, I buy."', pa, 26, 'serif', INK, CARD, 'bl')
    aB = P(t, b[3], .5)
    if aB > 0:
        d = btc_w(); O, Hh, L, C = d['o'], d['h'], d['l'], d['c']; n = len(C)
        F = Frame(190, 330, 1400, 480, -1, n, 23000, 130000)
        chart_card(c, F, aB, 'BITCOIN', 'weekly, Sep 2023 to Aug 2025', 'Data: TradingView · BITSTAMP:BTCUSD')
        ygrid(c, F, [25000, 50000, 75000, 100000, 125000], fmt_k, aB)
        xlabels(c, F, [(idx(d, '2024-01-01'), 'Jan 24'), (idx(d, '2024-07-01'), 'Jul 24'), (idx(d, '2025-01-06'), 'Jan 25'), (idx(d, '2025-07-07'), 'Jul 25')], aB)
        ib, ia, ip = idx(d, '2024-11-04'), idx(d, '2025-04-07'), idx(d, '2025-08-11')
        upto = lerp(ib, ib, 1)
        k = ib + 1 + (idx(d, '2025-01-20') - ib) * P(t, b[4], 1.6) + (n - idx(d, '2025-01-20')) * P(t, b[5], 2.0) * (1 if t > b[5] else 0)
        candles(c, F, O, Hh, L, C, max(ib + 1, k) * P(t, b[3], 1.2) if t < b[4] else k, a=aB)
        im = idx(d, '2024-03-11')
        sw = P(t, b[5] + 1.5, .8)
        hl = mix(RED, GREEN, P(t, b[3] + 1.5, .8))
        hline(c, F, 73794, im, n, hl, 4, aB, P(t, b[3] + .6, 1.0), [14, 8])
        tag(c, F.X(im) - 10, F.Y(73794) - 70, '$73,794 ceiling', RED, WHITE, 20, P(t, b[3] + .8, .4) * aB, 'c', point=(F.X(im), F.Y(73794) - 8))
        ba = P(t, b[3] + 1.5, .5) * aB
        glow_dot(c, F.X(ib), F.Y(C[ib]), 9, GREEN, t, ba)
        tag(c, F.X(ib) - 20, F.Y(C[ib]) + 30, 'Breakout: 6 Nov 2024', GREEN, WHITE, 20, ba, 'c')
        ra = P(t, b[4] + 1.4, .5) * aB
        tag(c, F.X(idx(d, '2024-12-16')), F.Y(109000) - 50, 'Well above $100k', NAVY, WHITE, 20, ra, 'c')
        aa = P(t, b[5] + 1.6, .5) * aB
        if t > b[5] + 1:
            glow_dot(c, F.X(ia), F.Y(74434), 10, GREEN, t, aa)
            tag(c, F.X(ia), F.Y(74434) + 34, 'Apr 2025 low $74,434', GREEN, WHITE, 20, aa, 'c')
        wa = P(t, b[6], .5) * aB
        if wa > 0:
            card(c, 240, 370, 320, 110, 18, NAVY, wa)
            text(c, 'Old resistance held', 400, 412, 22, 'semi', LGOLD, 'c', wa)
            text(c, 'within ~1%', 400, 460, 36, 'head', WHITE, 'c', wa)
        pa = P(t, b[7], .5) * aB
        if pa > 0:
            glow_dot(c, F.X(ip), F.Y(124517), 9, GOLD, t, pa)
            tag(c, F.X(ip) - 160, F.Y(124517) - 10, 'New highs above $120k', GOLD, WHITE, 20, pa, 'c')

# ------------------------------------------------------------ 4.6 round numbers & filters
@scene('c4s6')
def c4s6(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        nums = ['10', '50', '100', '1,000', '10,000', '100,000']
        for i, s_ in enumerate(nums):
            x = 260 + i * 280; y = 560 + 40 * math.sin(t * 1.2 + i)
            with pop(c, t, b[1] + .2 + i * .25, x, y) as a:
                circle(c, x, y, 110, [NAVY, BLUE, GOLD, GREEN, RED, NAVY][i], a * a1 * .95)
                text(c, s_, x, y + 16, fit_size(c, s_, 'head', 52, 180), 'head', WHITE, 'c', a * a1)
        text(c, 'People think in round numbers', 960, 820, 34, 'serif', MUTED, 'c', P(t, b[1] + 1.6, .5) * a1)
    a2 = stage(t, b, 2, 4)
    if a2 > 0:
        d = btc_d(); O, Hh, L, C = d['o'], d['h'], d['l'], d['c']
        s0 = idx(d, '2024-11-20'); n = len(C)
        F = Frame(200, 330, 1200, 470, s0 - 1, n, 88000, 112000)
        chart_card(c, F, a2, 'BITCOIN', 'daily, Nov 2024 to Jan 2025', 'Data: TradingView · BITSTAMP:BTCUSD')
        ygrid(c, F, [90000, 95000, 100000, 105000, 110000], fmt_k, a2)
        xlabels(c, F, [(idx(d, '2024-12-01'), 'Dec'), (idx(d, '2025-01-01'), 'Jan')], a2)
        hline(c, F, 100000, cl=GOLD, lw=4, a=a2, prog=P(t, b[2] + .2, .8))
        candles(c, F, O, Hh, L, C, (n - s0) * P(t, b[2] + .4, 2.2), start=s0, a=a2)
        i5 = idx(d, '2024-12-05')
        fa = P(t, b[2] + 1.5, .4) * a2
        glow_dot(c, F.X(i5), F.Y(Hh[i5]), 8, GOLD, t, fa)
        tag(c, F.X(i5), F.Y(Hh[i5]) - 60, 'First trade above $100k: 5 Dec 2024', GOLD, WHITE, 20, fa, 'c')
        cross_n = sum(1 for i in range(i5, n) if (C[i] - 100000) * (C[i - 1] - 100000) < 0)
        ca = P(t, b[2] + 3.0, .5) * a2
        card(c, 1530, 380, 240, 170, 20, NAVY, ca)
        text(c, str(cross_n), 1650, 470, 70, 'head', GOLD, 'c', ca)
        text(c, 'closes crossed $100k', 1650, 515, 20, 'semi', WHITE, 'c', ca)
        na = P(t, b[3], .5) * a2
        card(c, 1530, 590, 240, 200, 20, CARD, na)
        text(c, 'NIFTY 50', 1650, 635, 20, 'semi', MUTED, 'c', na, ls=3)
        text(c, '20,000', 1650, 690, 40, 'head', NAVY, 'c', na)
        text(c, '25,000', 1650, 745, 40, 'head', NAVY, 'c', na)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        F = Frame(300, 360, 900, 420, 0, 10, 96, 104)
        card(c, 250, 320, 1000, 520, 24, CARD, a4)
        hline(c, F, 100, cl=GOLD, lw=5, a=a4, label='100 (round number)', size=22)
        rnd = random.Random(3)
        for q in range(26):
            circle(c, F.X(1 + q * .3), F.Y(100) + rnd.gauss(0, 3), 6, MUTED, a4 * .7 * P(t, b[4] + .4, .5))
        text(c, "everyone's orders", F.X(4.8), F.Y(100) + 50, 22, 'semi', MUTED, 'c', P(t, b[4] + .6, .4) * a4)
        ba = P(t, b[4] + b.d[4] * .5, .5) * a4
        hline(c, F, 100.9, 6, 10, GREEN, 4, ba, label='Buy just above', size=22)
        sa = P(t, b[4] + b.d[4] * .7, .5) * a4
        hline(c, F, 98.9, 6, 10, RED, 4, sa, label='Stop just below', size=22)
        text(c, 'Avoid the obvious number', 1500, 560, 30, 'serif', NAVY, 'c', P(t, b[4] + 1, .5) * a4)
    a5 = P(t, b[5], .5)
    if a5 > 0:
        cur = 0 if t < b[6] else 1 if t < b[7] else 2
        for i, (ttl, sub) in enumerate([('Just a poke?', 'One brief move through'), ('Price filter', 'Close ~3% beyond (longer-term)'), ('Time filter', 'Two-day rule: 2 closes beyond')]):
            x = 170 + i * 540
            on = i <= cur
            with pop(c, t, [b[5], b[6], b[7]][i], x + 255, 560) as a:
                if a <= 0: continue
                card(c, x, 320, 510, 470, 24, CARD, a * a5, border=GOLD if i == cur else None, bw=3)
                text(c, ttl, x + 255, 375, 30, 'head', NAVY, 'c', a * a5)
                text(c, sub, x + 255, 412, 22, 'semi', MUTED, 'c', a * a5)
                F = Frame(x + 40, 450, 430, 290, 0, 10, 96.5, 105)
                hline(c, F, 100, cl=GOLD, lw=4, a=a * a5)
                if i == 0:
                    O, Hh, L, C = [99, 98.5, 99.2, 99.6, 99, 98.4], [99.6, 99.4, 99.8, 101.8, 99.7, 99], [98, 97.6, 98.6, 99, 98.2, 97.6], [98.5, 99.2, 99.6, 99, 98.4, 98.8]
                    Fq = Frame(x + 60, 450, 390, 290, -1, 6, 96.5, 105)
                    candles(c, Fq, O, Hh, L, C, 6, a=a * a5)
                    badge(c, Fq.X(3), Fq.Y(101.8) - 30, 18, 'no', a * a5 * P(t, b[5] + 1, .4))
                elif i == 1:
                    zone(c, F, None, None, 100, 103, GREEN, .15 * a * a5)
                    text(c, '+3%', F.x + F.w - 6, F.Y(103) + 26, 22, 'head', GREEN, 'r', a * a5)
                    O, Hh, L, C = [98.5, 99, 99.6, 101.2, 103.4], [99.4, 99.9, 101.6, 103.8, 104.6], [98, 98.6, 99.2, 100.8, 102.8], [99, 99.6, 101.2, 103.4, 104.2]
                    Fq = Frame(x + 60, 450, 390, 290, -1, 5, 96.5, 105)
                    candles(c, Fq, O, Hh, L, C, 5 * P(t, b[6] + .3, 1.2), a=a * a5)
                    badge(c, Fq.X(3) + 50, Fq.Y(104.6) + 10, 18, 'ok', a * a5 * P(t, b[6] + 1.6, .4))
                else:
                    O, Hh, L, C = [98.5, 99.2, 99.8, 100.9, 101.6], [99.5, 100, 101.4, 102, 102.6], [98.2, 98.8, 99.5, 100.4, 101.1], [99.2, 99.8, 100.9, 101.6, 102.3]
                    Fq = Frame(x + 60, 450, 390, 290, -1, 5, 96.5, 105)
                    candles(c, Fq, O, Hh, L, C, 5 * P(t, b[7] + .3, 1.2), a=a * a5)
                    for q, dd in enumerate((2, 3)):
                        pill(c, Fq.X(dd), 700, f'Day {q+1}', 14, NAVY, WHITE, a * a5 * P(t, b[7] + 1.3 + q * .4, .4), 'semi', 'c', ls=0)
                    badge(c, Fq.X(3) + 50, Fq.Y(102.6), 18, 'ok', a * a5 * P(t, b[7] + 2.2, .4))
        a8 = P(t, b[8], .5)
        if a8 > 0:
            card(c, 400, 810, 1120, 80, 20, NAVY, a8)
            text(c, 'Too tight: whipsaws   ·   Too loose: late   ·   Some filter beats none', 960, 862, 26, 'semi', WHITE, 'c', a8)
