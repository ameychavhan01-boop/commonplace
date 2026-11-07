from engine import *
from . import scene
from .common import *
from .data import nifty_d20, nifty_d24, nifty_w, idx

def touch_dot(c, F, i, p, t, a, cl=GOLD): glow_dot(c, F.X(i), F.Y(p), 9, cl, t, a)

# ------------------------------------------------------------ 4.7 trendlines
@scene('c4s7')
def c4s7(c, t, b):
    a1 = stage(t, b, 0, 2)
    if a1 > 0:
        for k, (ttl, kind, cl) in enumerate([('UP TRENDLINE', 'up', GREEN), ('DOWN TRENDLINE', 'down', RED)]):
            x = 180 + k * 800
            with pop(c, t, .4 + k * .4 + (b[1] - .4 if k else 0) * 0, x + 380, 560) as a:
                if a <= 0: continue
                card(c, x, 320, 760, 500, 24, CARD, a * a1)
                text(c, ttl, x + 380, 375, 30, 'head', cl, 'c', a * a1, ls=3)
                pts = pattern_pts(kind, x + 60, 420, 640, 340)
                polyline(c, pts, NAVY, 5, a * a1, P(t, .6 + k * .5, 1.6))
                if kind == 'up': p1, p2 = pts[0], pts[4]
                else: p1, p2 = pts[0], pts[4]
                (x1, y1), (x2, y2) = p1, p2
                ex = x1 + (x2 - x1) * 1.5; ey = y1 + (y2 - y1) * 1.5
                line(c, x1, y1, ex, ey, cl, 5, a * a1, p=P(t, b[1] + .3 + k * b.d[1] * .4, 1))
                text(c, 'along the lows' if kind == 'up' else 'along the peaks', x + 380, 790, 24, 'semi', MUTED, 'c', a * a1 * P(t, b[1] + .6 + k * b.d[1] * .4, .4))
    a2 = stage(t, b, 2, 4)
    F = Frame(240, 340, 1100, 460, 0, 100, 0, 100)
    xs = list(range(101))
    lows = [(8, 19), (40, 35), (72, 51)]
    keys = [(0, 23), (8, 19), (24, 40), (40, 35), (56, 58), (72, 51), (88, 70), (100, 58)]
    ys = path_line([(k / 100, v) for k, v in keys], 101)
    ys = [v + (0 if min(abs(x - i) for i, _ in lows) < 4 else 1.2 * math.sin(x * 1.7)) for x, v in enumerate(ys)]
    if a2 > 0:
        card(c, 190, 300, 1200, 540, 24, CARD, a2)
        k = 101 if t > b[3] else lerp(45, 101, P(t, b[2] + 1.6, 2.0))
        series(c, F, xs[:int(k)], ys[:int(k)], 1, NAVY, 5, a2)
        tl = lambda x: 15 + .5 * x
        for j, (i, p_) in enumerate(lows[:2]):
            touch_dot(c, F, i, ys[i], t, P(t, b[2] + .3 + j * .4, .4) * a2)
        tent = P(t, b[2] + 1.0, .6) * a2
        seg(c, F, 0, tl(0), 100, tl(100), GOLD, 4, tent * (1 - P(t, b[2] + 3.5, .4)), P(t, b[2] + 1, .8), [14, 10])
        tag(c, 1570, 420, 'Two points: tentative', GOLD, WHITE, 24, tent * (1 - P(t, b[2] + 3.5, .4)), 'c')
        conf = P(t, b[2] + 3.5, .5) * a2
        seg(c, F, 0, tl(0), 100, tl(100), GREEN, 5, conf)
        touch_dot(c, F, 72, ys[72], t, conf, GREEN)
        tag(c, 1570, 420, 'Third touch: confirmed', GREEN, WHITE, 24, conf, 'c')
        ga = P(t, b[3], .5) * a2
        if ga > 0:
            for j, (i, p_) in enumerate(lows):
                pill(c, F.X(i), F.Y(ys[i]) + 30, 'BUY AREA', 16, GREEN, WHITE, ga * P(t, b[3] + j * .3, .3), 'semi', 'c', ls=1)
            ba = P(t, b[3] + b.d[3] * .55, .5) * a2
            card(c, 1440, 520, 300, 170, 20, LRED, ba, border=RED)
            warn(c, 1500, 580, .4, ba, RED)
            text(c, 'Close below', 1610, 590, 24, 'bold', RED, 'l', ba)
            text(c, 'the line =', 1610, 622, 24, 'bold', RED, 'l', ba)
            text(c, 'first warning', 1480, 666, 24, 'semi', INK, 'l', ba)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        for i, (ttl, sub, kind) in enumerate([('LENGTH', 'longer = more significant', 'len'), ('TOUCHES', 'more tests = stronger', 'tch'), ('ANGLE', 'not too steep', 'ang')]):
            x = 190 + i * 530
            with pop(c, t, b[4] + .3 + i * b.d[4] * .25, x + 250, 560) as a:
                card(c, x, 330, 500, 440, 24, CARD, a * a4)
                text(c, ttl, x + 250, 400, 36, 'head', NAVY, 'c', a * a4, ls=3)
                text(c, sub, x + 250, 440, 24, 'semi', MUTED, 'c', a * a4)
                if kind == 'len': line(c, x + 60, 640, x + 440, 560, GREEN, 6, a * a4); line(c, x + 60, 700, x + 200, 672, FAINT, 6, a * a4)
                elif kind == 'tch':
                    line(c, x + 60, 660, x + 440, 560, GREEN, 5, a * a4)
                    for q in range(4): circle(c, x + 80 + q * 115, 655 - q * 30, 10, GOLD, a * a4)
                else:
                    for q, (ang, cl) in enumerate([(70, RED), (45, GREEN), (20, FAINT)]):
                        r = 200; ax, ay = x + 120, 700
                        line(c, ax, ay, ax + r * math.cos(math.radians(ang)), ay - r * math.sin(math.radians(ang)), cl, 5, a * a4)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        ax, ay, r = 620, 780, 420
        c.new_path(); c.arc(ax, ay, r, math.pi, 2 * math.pi); col(c, CARD, a5); c.fill()
        c.new_path(); c.arc(ax, ay, r, math.pi, 2 * math.pi); col(c, LINE, a5); c.set_line_width(3); c.stroke()
        for dgr in range(0, 181, 15):
            rr = math.radians(dgr)
            line(c, ax + math.cos(rr) * (r - 24), ay - math.sin(rr) * (r - 24), ax + math.cos(rr) * r, ay - math.sin(rr) * r, MUTED, 2, a5)
        for q, (ang, cl, lab, t0) in enumerate([(70, RED, 'Too steep: breaks quickly', b[5] + .3), (45, GREEN, '45°: most reliable', b[5] + b.d[5] * .45), (18, MUTED, 'Too flat: weak trend', b[5] + .9)]):
            k = P(t, t0, .7) * a5
            rr = math.radians(ang)
            line(c, ax, ay, ax + math.cos(rr) * (r + 20) * k, ay - math.sin(rr) * (r + 20) * k, cl, 7, a5)
            tag(c, ax + math.cos(rr) * (r + 40) + 160, ay - math.sin(rr) * (r + 40) - 20, lab, cl, WHITE, 24, k, 'c')
        text(c, 'The angle W. D. Gann favoured', 1500, 760, 28, 'serif', MUTED, 'c', P(t, b[5] + b.d[5] * .6, .5) * a5)
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        F2 = Frame(240, 340, 1300, 460, 0, 100, 0, 100)
        card(c, 190, 300, 1420, 540, 24, CARD, a6)
        xs2 = list(range(101))
        ys2 = [20 + x * .6 + 6 * math.sin(x / 6) if x < 60 else (56 - (x - 60) * 1.2 if x < 70 else 44 + (x - 70) * 1.25 if x < 80 else 56.5 - (x - 80) * 1.4) for x in xs2]
        series(c, F2, xs2, ys2, P(t, b[6], 2.4), NAVY, 5, a6)
        seg(c, F2, 0, 14, 100, 14 + 100 * .6, GREEN, 5, a6, P(t, b[6] + .2, .8))
        sa = P(t, b[6] + 1.6, .5) * a6
        touch_dot(c, F2, 80, ys2[80], t, sa, RED)
        tag(c, F2.X(80), F2.Y(ys2[80]) - 80, 'Old line now resistance', RED, WHITE, 24, sa, 'c', point=(F2.X(80), F2.Y(ys2[80]) - 12))
    a7 = P(t, b[7], .5)
    if a7 > 0:
        d = nifty_w(); C = d['c']; n = idx(d, '2021-06-28')
        F3 = Frame(220, 340, 1300, 440, 0, n, 7000, 17000)
        chart_card(c, F3, a7, 'NIFTY 50', 'weekly, 2020 to 2021', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F3, [8000, 10000, 12000, 14000, 16000], a=a7)
        series(c, F3, range(n + 1), C[:n + 1], P(t, b[7] + .2, 1.4), NAVY, 3.5, a7)
        L = d['l']
        i1, i2 = 3, 29
        sl = (L[i2] - L[i1]) / (i2 - i1)
        ru = P(t, b[7] + 1.4, 1.2, eio)
        (x1, y1), (x2, y2) = F3.P(i1, L[i1]), F3.P(i2, L[i2])
        ang = math.atan2(y2 - y1, x2 - x1)
        cxr, cyr = lerp(x1 - 200, (x1 + x2) / 2, ru), lerp(y1 + 200 * math.tan(-ang) * 0, (y1 + y2) / 2, ru)
        cxr = lerp(x1 - 120, (x1 + x2) / 2, ru); cyr = y1 + (cxr - x1) * math.tan(ang)
        ruler(c, cxr - math.sin(ang) * 0 + 0, cyr + 26, 560, ang, a7 * (1 - P(t, b[7] + 2.9, .4)))
        seg(c, F3, i1, L[i1], i2, L[i2], GREEN, 5, P(t, b[7] + 2.6, .5) * a7, 1, ext=.6)

# ------------------------------------------------------------ 4.8 fan principle
@scene('c4s8')
def c4s8(c, t, b):
    F = Frame(260, 340, 1100, 470, 0, 100, 0, 100)
    xs = list(range(101))
    K = [(0, 10), (8, 34), (13, 38.6), (22, 62), (26, 67.2), (32, 82), (40, 60), (48, 76), (60, 68), (68, 80), (84, 58), (100, 36)]
    _ys = path_line([(k / 100, v) for k, v in K], 101)
    def pf(x): return _ys[int(x)]
    ys = [pf(x) for x in xs]
    aA = P(t, .3, .5) * (1 - P(t, b[4] - .3, .4)) + P(t, b[5], .5) * (1 if t > b[5] else 0)
    aA = min(1, aA)
    if aA > 0:
        card(c, 200, 300, 1220, 560, 24, CARD, aA)
        prog = P(t, .4, max(1, b[2] - .4), lambda u: u)
        series(c, F, xs, ys, prog if t < b[5] else 1, NAVY, 5, aA)
        c.save(); rrect(c, 200, 300, 1220, 560, 24); c.clip()
        lines = [('1', b[1] - .2, 2.2, 36), ('2', b[1] + b.d[1] * .35, 1.25, 51), ('3', b[1] + b.d[1] * .7, 58 / 60, 72)]
        for j, (lab, t0, sl, bx) in enumerate(lines):
            la = P(t, t0, .6) * aA
            cl = [RED, GOLD, GREEN][j]
            seg(c, F, 0, 10, 100, 10 + 100 * sl, cl, 4, la, P(t, t0, 1), [16, 10] if j < 2 else None)
            xl = min(96, (95 - 10) / sl)
            text(c, f'Line {lab}', F.X(xl) - 12, F.Y(10 + sl * xl) + 6, 24, 'head', cl, 'r', la)
            badge(c, F.X(bx), F.Y(ys[bx]) + 44, 18, 'no', P(t, t0 + 1.0, .4) * aA)
        c.restore()
        ra = P(t, b[2], .5) * aA
        if ra > 0:
            tag(c, F.X(80), F.Y(ys[95]) + 40, 'Third line broken = REVERSAL', RED, WHITE, 26, ra, 'c')
        bat = P(t, b[5], .5) * (1 - P(t, b[6] - .3, .4))
        if bat > 0:
            lvl = 3 - (1 if t > b[5] + 1 else 0) - (1 if t > b[5] + 2 else 0) - (1 if t > b[5] + 3 else 0)
            rrect(c, 1500, 420, 200, 320, 22); col(c, NAVY, bat); c.set_line_width(6); c.stroke()
            rrect(c, 1570, 400, 60, 22, 6); col(c, NAVY, bat); c.fill()
            for q in range(3):
                if q < lvl: rrect(c, 1520, 650 - q * 100, 160, 80, 12); col(c, [GREEN, GOLD, RED][2 - lvl] if lvl < 3 else GREEN, bat); c.fill()
            text(c, 'Trend energy', 1600, 790, 26, 'semi', INK, 'c', bat)
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        with pop(c, t, b[3], 1580, 380) as a:
            card(c, 1440, 300, 300, 200, 18, CARD, a * a3)
            text(c, 'Downtrends too', 1590, 340, 22, 'bold', INK, 'c', a * a3)
            G = Frame(1460, 360, 260, 120, 0, 10, 0, 10)
            polyline(c, [G.P(0, 9), G.P(3, 3), G.P(4, 5), G.P(6, 2), G.P(7, 4), G.P(8, 2.5), G.P(10, 6)], NAVY, 3, a * a3)
            for q, sl in enumerate((-2, -1, -.4)):
                seg(c, G, 0, 9.5, 10, 9.5 + sl * 10, [RED, GOLD, GREEN][q], 2, a * a3, 1, [6, 4] if q < 2 else None)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        items = [('3 fan lines', 'fan'), ('3 phases of a trend', 'ph'), ('3 trend sizes', 'sz'), ('3 trend directions', 'dir'), ('3 peaks in head & shoulders', 'hs'), ('1/3, 1/2, 2/3 retracements', 'ret')]
        text(c, 'THE NUMBER THREE', 960, 330, 34, 'head', GOLD, 'c', a4, ls=6)
        for i, (lab, k) in enumerate(items):
            r, cc = divmod(i, 3)
            x, y = 220 + cc * 510, 380 + r * 250
            with pop(c, t, b[4] + .4 + i * (b.d[4] * .8 / 6), x + 235, y + 110) as a:
                card(c, x, y, 470, 220, 22, CARD, a * a4)
                circle(c, x + 70, y + 110, 46, NAVY, a * a4)
                text(c, '3', x + 70, y + 130, 54, 'head', GOLD, 'c', a * a4)
                para(c, lab, x + 140, y + 100, 28, 'bold', INK, 300, 1.2, 'l', a * a4)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        hourglass(c, 1600, 540, 1.4, t, a6)
        text(c, "Don't call the top", 1600, 690, 26, 'bold', INK, 'c', a6)
        text(c, 'at the first break', 1600, 726, 26, 'bold', INK, 'c', a6)

# ------------------------------------------------------------ 4.9 channels
@scene('c4s9')
def c4s9(c, t, b):
    F = Frame(240, 340, 1160, 470, 0, 100, 0, 100)
    base = lambda x: 10 + x * .55
    W_ = 22
    def osc(x, amp=1.0): return base(x) + W_ / 2 + (W_ / 2) * amp * math.sin(x / 100 * 2 * math.pi * 3.6 - 1.6)
    stA = 1 - P(t, b[3] - .3, .4)
    card(c, 190, 300, 1270, 560, 24, CARD, P(t, .3, .5))
    if stA > 0:
        xs = list(range(101)); ys = [osc(x) for x in xs]
        series(c, F, xs, ys, P(t, .4, b[1] + 1.4), NAVY, 5, stA)
        seg(c, F, 0, base(0), 100, base(100), GREEN, 5, stA * P(t, b[1] - .4, .4), P(t, b[1] - .4, 1))
        seg(c, F, 0, base(0) + W_, 100, base(100) + W_, BLUE, 5, stA * P(t, b[1] + b.d[1] * .5, .4), P(t, b[1] + b.d[1] * .5, 1), [16, 10])
        text(c, 'Basic trendline', F.X(100) + 10, F.Y(base(100)) + 8, 22, 'bold', GREEN, 'l', stA * P(t, b[1], .4))
        text(c, 'Channel line', F.X(100) + 10, F.Y(base(100) + W_) + 8, 22, 'bold', BLUE, 'l', stA * P(t, b[1] + b.d[1] * .6, .4))
        za = P(t, b[2], .5) * stA
        if za > 0:
            c.new_path(); c.move_to(*F.P(0, base(0))); c.line_to(*F.P(100, base(100))); c.line_to(*F.P(100, base(100) + 5)); c.line_to(*F.P(0, base(0) + 5)); c.close_path(); col(c, GREEN, .2 * za); c.fill()
            c.new_path(); c.move_to(*F.P(0, base(0) + W_)); c.line_to(*F.P(100, base(100) + W_)); c.line_to(*F.P(100, base(100) + W_ - 5)); c.line_to(*F.P(0, base(0) + W_ - 5)); c.close_path(); col(c, GOLD, .25 * za); c.fill()
            tag(c, 1650, 520, 'Profit zone', GOLD, WHITE, 26, za, 'c')
            tag(c, 1650, 600, 'Buy zone', GREEN, WHITE, 26, za, 'c')
    if t > b[3] - .3:
        sB = P(t, b[3], .5) * (1 - P(t, b[4] - .3, .4))
        sC = P(t, b[4], .5) * (1 - P(t, b[5] - .3, .4))
        sD = P(t, b[5], .5)
        xs = list(range(101))
        if sB > 0:
            amp = lambda x: 1 if x < 56 else max(.35, 1 - (x - 56) / 10 * .65)
            ys = [osc(x, amp(x)) if x < 86 else osc(86, .35) - (x - 86) * 1.6 for x in xs]
            series(c, F, xs, ys, P(t, b[3], 2), NAVY, 5, sB)
            seg(c, F, 0, base(0), 100, base(100), GREEN, 5, sB); seg(c, F, 0, base(0) + W_, 100, base(100) + W_, BLUE, 5, sB, 1, [16, 10])
            ga = P(t, b[3] + 1.6, .4) * sB
            line(c, F.X(73), F.Y(osc(73, .35)) - 10, F.X(73), F.Y(base(73) + W_) + 8, RED, 3, ga, [6, 6])
            tag(c, F.X(73), F.Y(base(73) + W_) - 70, 'Fails to reach the channel line', RED, WHITE, 22, ga, 'c')
            warn(c, 1650, 560, .7, ga, RED)
            text(c, 'Early warning', 1650, 650, 26, 'bold', RED, 'c', ga)
        if sC > 0:
            kk = (base(72) + W_ + 4 - osc(56)) / 16
            ys = [osc(x) if x < 56 else osc(56) + (x - 56) * kk for x in xs]
            series(c, F, xs, ys, P(t, b[4], 2), NAVY, 5, sC)
            seg(c, F, 0, base(0), 100, base(100), GREEN, 5, sC); seg(c, F, 0, base(0) + W_, 100, base(100) + W_, BLUE, 5, sC, 1, [16, 10])
            ga = P(t, b[4] + 1.4, .4) * sC
            tag(c, 1650, 560, 'Trend accelerating', GREEN, WHITE, 26, ga, 'c')
            arrow(c, 1650, 680, 1650, 600, GREEN, 6, ga, 1, 22)
        if sD > 0:
            ys = [osc(x) if x < 58 else osc(58) - (x - 58) * 1.25 for x in xs]
            series(c, F, xs, ys, P(t, b[5], 2), NAVY, 5, sD)
            seg(c, F, 0, base(0), 100, base(100), GREEN, 5, sD); seg(c, F, 0, base(0) + W_, 100, base(100) + W_, BLUE, 5, sD, 1, [16, 10])
            ma = P(t, b[5] + 1.6, .5) * sD
            measure(c, F.X(58), F.Y(base(58)), F.Y(base(58) + W_), GOLD, ma, 1, 'width', 'l')
            y0 = F.Y(base(66)); y1 = y0 + (F.Y(base(58)) - F.Y(base(58) + W_))
            measure(c, F.X(96), y0, y1, RED, ma, P(t, b[5] + 2.2, .8), 'same distance', 'l')
            text(c, 'Breakout often travels', 1650, 540, 24, 'semi', INK, 'c', ma)
            text(c, "about the channel's width", 1650, 572, 24, 'semi', INK, 'c', ma)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, (lab, cl) in enumerate([('Where it is', NAVY), ('Where it might go', GREEN), ("Where you'd be wrong", RED)]):
            pill(c, 1650, 650 + i * 64, lab, 22, cl, WHITE, P(t, b[6] + i * .4, .4), 'semi', 'c', ls=0)

# ------------------------------------------------------------ 4.10 retracements & speedlines
@scene('c4s10')
def c4s10(c, t, b):
    aA = stage(t, b, 0, 4)
    if aA > 0:
        F = Frame(260, 340, 1000, 470, 0, 100, 0, 100)
        card(c, 210, 300, 1530, 560, 24, CARD, aA)
        deep = P(t, b[3], .5)
        def pth(x):
            if x < 50: return 8 + x * 1.7
            if x < 72: return 93 - (x - 50) * (93 - 50.5) / 22 if deep < .5 else 93 - (x - 50) * (93 - 24) / 22
            return (50.5 if deep < .5 else 24) + (x - 72) * (1.4 if deep < .5 else -.3)
        xs = list(range(101)); ys = [pth(x) for x in xs]
        prog = P(t, .4, 2.2) if t < b[3] else P(t, b[3], 2.2)
        series(c, F, xs, ys, prog, NAVY, 5, aA)
        lv = [(1 / 3, '1/3: minimum', BLUE, b[2]), (1 / 2, '1/2: most common', GOLD, b[1]), (2 / 3, '2/3: maximum', RED, b[2] + .6)]
        for f, lab, cl, t0 in lv:
            p_ = 93 - f * 85
            la = P(t, t0, .5) * aA
            hline(c, F, p_, 50, 100, cl, 3, la, P(t, t0, .8), [12, 8])
            text(c, lab, F.X(100) + 20, F.Y(p_) + 8, 24, 'bold', cl, 'l', la)
        ra = P(t, b[3] + 1.6, .4) * aA
        if ra > 0:
            glow_dot(c, F.X(72), F.Y(24), 10, RED, t, ra)
            tag(c, F.X(80), F.Y(24) + 40, 'Beyond 2/3: likely a reversal', RED, WHITE, 24, ra, 'c')
    aN = stage(t, b, 4, 6)
    if aN > 0:
        d = nifty_d20(); n = idx(d, '2020-11-30'); C = d['c']
        F = Frame(220, 340, 1260, 450, 0, n, 7000, 13300)
        chart_card(c, F, aN, 'NIFTY 50', 'daily close, 2020', 'Data: TradingView · NSE:NIFTY')
        xlabels(c, F, [(idx(d, f'2020-{m:02d}-01'), lab) for m, lab in ((1, 'Jan'), (3, 'Mar'), (5, 'May'), (7, 'Jul'), (9, 'Sep'), (11, 'Nov'))], aN)
        hi, lo = 12430.5, 7511.1
        il = idx(d, '2020-03-24')
        for f, lab, cl, t0 in ((1 / 3, '1/3  9,151', BLUE, b[4] + 1.2), (.5, '1/2  9,971', GOLD, b[4] + 1.5), (2 / 3, '2/3  10,791', RED, b[4] + 1.8)):
            hline(c, F, lo + f * (hi - lo), il, n, cl, 3, P(t, t0, .5) * aN, P(t, t0, .8), [12, 8])
            text(c, lab, F.X(n) + 12, F.Y(lo + f * (hi - lo)) + 7, 18, 'semi', cl, 'l', P(t, t0, .5) * aN)
        fa = P(t, b[5] + .3, .5) * aN
        for f, lab in ((.382, '38.2%'), (.618, '61.8%')):
            hline(c, F, lo + f * (hi - lo), il, n, MUTED, 2, fa, P(t, b[5] + .3, .8), [4, 6])
            text(c, 'Fib ' + lab, F.X(idx(d, '2020-10-20')), F.Y(lo + f * (hi - lo)) - 8, 18, 'semi', MUTED, 'c', fa)
        series(c, F, range(n + 1), C[:n + 1], P(t, b[4] + .2, 2.4), NAVY, 3.5, aN, BLUE, .1)
        hline(c, F, hi, 0, n, FAINT, 2, aN, dash=[4, 6])
        ij, iat = idx(d, '2020-07-07'), idx(d, '2020-11-09')
        ja = P(t, b[4] + b.d[4] * .55, .5) * aN
        glow_dot(c, F.X(ij), F.Y(C[ij]), 9, RED, t, ja)
        tag(c, F.X(ij) - 30, F.Y(C[ij]) - 110, '7 Jul: closes above 2/3', RED, WHITE, 20, ja, 'c', point=(F.X(ij), F.Y(C[ij]) - 12))
        aa = P(t, b[4] + b.d[4] * .8, .5) * aN
        glow_dot(c, F.X(iat), F.Y(C[iat]), 9, GREEN, t, aa)
        tag(c, F.X(iat) - 60, F.Y(C[iat]) - 80, '9 Nov: new all-time high', GREEN, WHITE, 20, aa, 'c')
        text(c, 'Fibonacci:', 1700, 600, 26, 'bold', MUTED, 'c', fa)
        text(c, 'more in Part 3', 1700, 632, 22, 'semi', GOLD, 'c', fa)
    aS = stage(t, b, 6, 9)
    if aS > 0:
        F = Frame(260, 340, 1100, 470, 0, 100, 0, 100)
        card(c, 210, 300, 1260, 560, 24, CARD, aS)
        text(c, 'SPEED RESISTANCE LINES  ·  EDSON GOULD', 240, 340, 20, 'semi', GOLD, 'l', aS, ls=3)
        ix = 50
        up = [(x, 8 + x * 1.7) for x in range(0, 51)]
        brk = P(t, b[8], .5)
        healthy = [(50, 93), (56, 74), (70, 97), (100, 99)]
        broken = [(50, 93), (56, 74), (60, 80), (70, 48.5), (80, 56), (92, 52), (100, 54)]
        def corr(x):
            kk = healthy if brk < .5 else broken
            for (x0, y0), (x1, y1) in zip(kk, kk[1:]):
                if x0 <= x <= x1: return lerp(y0, y1, (x - x0) / (x1 - x0))
            return kk[-1][1]
        dn = [(x, corr(x)) for x in range(50, 101)]
        allp = up + dn
        series(c, F, [p[0] for p in allp], [p[1] for p in allp], P(t, b[6] + .2, 2.2) if t < b[8] else 1, NAVY, 5, aS)
        va = P(t, b[7], .5) * aS
        c.save(); rrect(c, 210, 300, 1260, 560, 24); c.clip()
        if va > 0:
            line(c, F.X(50), F.Y(93), F.X(50), F.Y(8), FAINT, 3, va, [8, 8])
            for f in (1 / 3, 2 / 3):
                yv = 8 + f * 85
                circle(c, F.X(50), F.Y(yv), 8, GOLD, va)
            for f, lab, cl in ((2 / 3, '2/3 speedline', GREEN), (1 / 3, '1/3 speedline', BLUE)):
                sl = (f * 85) / 50
                k = P(t, b[7] + .6 + (0 if f > .5 else .5), 1)
                seg(c, F, 0, 8, 100, 8 + sl * 100, cl, 4, va, k)
                xe = min(100, (98 - 8) / sl)
                text(c, lab, F.X(xe) - 10, F.Y(8 + sl * xe) + 34, 22, 'bold', cl, 'r', va * k)
        c.restore()
        ha = P(t, b[7] + b.d[7] * .6, .5) * aS * (1 - brk)
        tag(c, 1660, 480, 'Holds above 2/3 line:', GREEN, WHITE, 22, ha, 'c')
        tag(c, 1660, 530, 'healthy uptrend', GREEN, WHITE, 22, ha, 'c')
        if brk > 0:
            tag(c, 1660, 480, 'Breaks 2/3 line:', RED, WHITE, 22, brk * aS, 'c')
            tag(c, 1660, 530, 'expect the 1/3 line', RED, WHITE, 22, brk * aS, 'c')
            tag(c, 1660, 600, 'Break that too:', RED, WHITE, 22, P(t, b[8] + b.d[8] * .5, .4) * aS, 'c')
            tag(c, 1660, 650, 'back to the start', RED, WHITE, 22, P(t, b[8] + b.d[8] * .5, .4) * aS, 'c')
    a9 = P(t, b[9], .5)
    if a9 > 0:
        with pop(c, t, b[9], 960, 560) as a:
            card(c, 360, 380, 1200, 360, 26, NAVY, a * a9)
            text(c, 'A pullback is expected,', 960, 500, 52, 'serif', WHITE, 'c', a * a9)
            text(c, 'with a clear line where you are wrong.', 960, 580, 44, 'serif', LGOLD, 'c', a * a9)
            for i, (f, cl) in enumerate([('1/3', BLUE), ('1/2', GOLD), ('2/3', RED)]):
                pill(c, 800 + i * 160, 640, f, 26, cl, WHITE, a * a9, 'head', 'c', ls=0)

# ------------------------------------------------------------ 4.11 reversal days
@scene('c4s11')
def c4s11(c, t, b):
    aA = stage(t, b, 0, 4)
    if aA > 0:
        O = [50, 53, 56, 58, 61, 64, 67, 72]; Cc = [53, 56, 58, 61, 64, 67, 70, 64]
        Hh = [54, 57, 59, 62, 65, 68, 71, 80]; L = [49, 52, 55, 57, 60, 63, 66, 62]
        F = Frame(280, 370, 640, 300, -1, 8, 44, 84)
        card(c, 220, 310, 760, 400, 24, CARD, aA)
        text(c, 'TOP REVERSAL DAY', 600, 352, 24, 'head', RED, 'c', aA, ls=3)
        candles(c, F, O, Hh, L, Cc, 8 * P(t, .4, 1.8), a=aA)
        ra = P(t, b[1] + .4, .5) * aA
        hline(c, F, 70, 5.5, 8, MUTED, 2, ra, dash=[6, 6])
        tag(c, F.X(7) + 30, F.Y(80) - 50, 'New high', GREEN, WHITE, 20, ra, 'c')
        tag(c, F.X(7) - 60, F.Y(64) + 70, 'Close below prior close', RED, WHITE, 20, P(t, b[1] + .9, .4) * aA, 'c')
        ba = P(t, b[2] + b.d[2] * .45, .5) * aA
        if ba > 0:
            O2 = [70, 67, 64, 61, 58, 55, 52, 48]; C2 = [67, 64, 61, 58, 55, 52, 49, 56]
            H2 = [71, 68, 65, 62, 59, 56, 53, 57]; L2 = [66, 63, 60, 57, 54, 51, 48, 40]
            G = Frame(1100, 370, 640, 300, -1, 8, 36, 76)
            card(c, 1040, 310, 760, 400, 24, CARD, ba)
            text(c, 'BOTTOM REVERSAL DAY', 1420, 352, 24, 'head', GREEN, 'c', ba, ls=3)
            candles(c, G, O2, H2, L2, C2, 8 * P(t, b[2] + b.d[2] * .45, 1.4), a=ba)
            tag(c, G.X(7) - 10, G.Y(40) + 20, 'New low', RED, WHITE, 20, P(t, b[2] + b.d[2] * .45 + 1.2, .4) * ba, 'c')
            tag(c, G.X(7) - 60, G.Y(57) - 80, 'Close above prior close', GREEN, WHITE, 20, P(t, b[2] + b.d[2] * .45 + 1.5, .4) * ba, 'c')
        oa = P(t, b[3], .5) * aA
        if oa > 0:
            card(c, 610, 730, 700, 160, 20, LGOLD, oa, border=GOLD)
            line(c, 690, 760, 690, 860, INK, 3, oa); c.rectangle(678, 785, 24, 50); col(c, GREEN, oa); c.fill()
            line(c, 760, 745, 760, 875, INK, 3, oa); c.rectangle(746, 765, 28, 95); col(c, RED, oa); c.fill()
            line(c, 670, 760, 800, 760, MUTED, 2, oa, [4, 4]); line(c, 670, 860, 800, 860, MUTED, 2, oa, [4, 4])
            text(c, 'OUTSIDE DAY', 840, 790, 26, 'head', GOLD, 'l', oa, ls=3)
            text(c, "High and low beyond yesterday's range", 840, 830, 22, 'semi', INK, 'l', oa)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        O = [80, 76, 72, 67, 62, 55, 46, 38]; Cc = [76, 72, 67, 62, 55, 46, 38, 52]
        Hh = [81, 77, 73, 68, 63, 56, 47, 53]; L = [75, 71, 66, 61, 54, 45, 37, 26]
        V = [30, 32, 35, 38, 42, 50, 62, 100]
        F = Frame(330, 350, 900, 340, -1, 8, 22, 86)
        Vf = Frame(330, 720, 900, 110, -1, 8, 0, 100)
        card(c, 270, 310, 1020, 560, 24, CARD, a4)
        candles(c, F, O, Hh, L, Cc, 8 * P(t, b[4], 1.6), a=a4)
        vbars(c, Vf, V, 8 * P(t, b[4], 1.6), 0, a4, [RED] * 7 + [GREEN], vmax=100)
        ta = P(t, b[4] + 1.6, .5) * a4
        tag(c, F.X(7), F.Y(26) + 26, 'Panic low, close strong', GREEN, WHITE, 20, ta, 'c')
        tag(c, Vf.X(7) - 200, Vf.y - 10, 'Very heavy volume', NAVY, WHITE, 20, ta, 'c')
        with pop(c, t, b[4] + 1.0, 1550, 560) as a:
            card(c, 1350, 420, 400, 260, 24, NAVY, a * a4)
            text(c, 'SELLING', 1550, 520, 44, 'head', WHITE, 'c', a * a4, ls=3)
            text(c, 'CLIMAX', 1550, 580, 44, 'head', GOLD, 'c', a * a4, ls=3)
            text(c, 'The last sellers give up', 1550, 630, 22, 'semi', LGOLD, 'c', a * a4)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        rnd = random.Random(12); O, Hh, L, Cc = path_ohlc([(0, 30), (.25, 60), (.4, 48), (.7, 80), (.85, 66), (1, 90)], 46, 4, .03, .02)
        F = Frame(260, 350, 1400, 430, -1, 46, 20, 100)
        card(c, 210, 310, 1500, 540, 24, CARD, a5)
        candles(c, F, O, Hh, L, Cc, 46 * P(t, b[5], 1.4), a=a5)
        for q, i in enumerate((6, 12, 19, 24, 31, 38, 43)):
            ma = P(t, b[5] + 1.0 + q * .2, .3) * a5
            ring(c, F.X(i), F.Y(Hh[i]) - 22, 14, MUTED, 3, ma)
        tag(c, 960, 800, 'Common, and usually only short-term turns', MUTED, WHITE, 24, P(t, b[5] + 2.4, .5) * a5, 'c')
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, (lab, w_) in enumerate([('Daily', 140), ('Weekly', 260), ('Monthly', 400)]):
            y = 400 + i * 140
            with rise(c, t, b[6] + i * .4) as a:
                text(c, lab, 420, y + 48, 34, 'head', NAVY, 'r', a * a6)
                rrect(c, 460, y + 12, w_ * P(t, b[6] + .2 + i * .4, .8, eio) * 2.4, 54, 27); col(c, [FAINT, BLUE, GOLD][i], a * a6); c.fill()
        text(c, 'Signal weight', 960, 830, 30, 'serif', MUTED, 'c', a6)

# ------------------------------------------------------------ 4.12 gaps
def gap_series():
    """schematic: range with common gap, breakaway, runaway, exhaustion; returns OHLC + gap indices"""
    O, Hh, L, C = [], [], [], []
    rnd = random.Random(5)
    def bar(o, c_, w=1.2):
        O.append(o); C.append(c_); Hh.append(max(o, c_) + abs(rnd.gauss(0, .5)) + .4); L.append(min(o, c_) - abs(rnd.gauss(0, .5)) - .4)
    p = 30.0
    for i in range(12):
        tgt = 30 + 3 * math.sin(i * 1.1)
        if i == 6: p = p + 3.2; bar(p, p + .3); continue
        bar(p, tgt); p = tgt
    p = Hh[-1] + 3; bar(p, p + 2.5); p += 2.5
    for i in range(6): bar(p, p + 1.8 + rnd.gauss(0, .4)); p = C[-1]
    p = Hh[-1] + 3; bar(p, p + 2.2); p += 2.2
    for i in range(6): bar(p, p + 1.9 + rnd.gauss(0, .4)); p = C[-1]
    p = Hh[-1] + 2.6; bar(p, p + .8); p += .8
    bar(p, p - 1.5); bar(C[-1], C[-1] - 3.5); bar(C[-1], C[-1] - 2.5); bar(C[-1], C[-1] - 1.5)
    return O, Hh, L, C, dict(common=6, breakaway=12, runaway=19, exhaustion=26)

@scene('c4s12')
def c4s12(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        F = Frame(560, 360, 800, 420, -1, 4, 0, 100)
        card(c, 500, 310, 920, 540, 24, CARD, a1)
        O, Hh, L, C = [30, 34, 62, 66], [38, 42, 70, 74], [26, 30, 58, 62], [34, 40, 66, 72]
        candles(c, F, O, Hh, L, C, 4 * P(t, b[1], 1.0), a=a1, wfrac=.4)
        ga = P(t, b[1] + 1.2, .5) * a1
        zone(c, F, 1, 2, 42, 58, GOLD, .25 * ga)
        tag(c, F.X(1.5), F.Y(50) - 20, 'GAP: no trading here', GOLD, WHITE, 24, ga, 'c')
        text(c, "today's low", F.X(2) + 60, F.Y(58) + 8, 22, 'semi', MUTED, 'l', ga)
        text(c, "yesterday's high", F.X(1) - 60, F.Y(42) + 8, 22, 'semi', MUTED, 'r', ga)
    aS = stage(t, b, 2, 7)
    if aS > 0:
        O, Hh, L, C, g = gap_series(); n = len(C)
        F = Frame(230, 360, 1460, 450, -1, n, 24, 66)
        card(c, 180, 310, 1560, 560, 24, CARD, aS)
        seq = [('common', 'Common gap', MUTED, b[3]), ('breakaway', 'Breakaway gap', GREEN, b[4]), ('runaway', 'Runaway (measuring) gap', BLUE, b[5]), ('exhaustion', 'Exhaustion gap', RED, b[6])]
        upto = 12 if t < b[4] else 19 if t < b[5] else 26 if t < b[6] else n
        t0 = b[2] if t < b[4] else b[4] if t < b[5] else b[5] if t < b[6] else b[6]
        prev = 0 if t < b[4] else 12 if t < b[5] else 19 if t < b[6] else 26
        candles(c, F, O, Hh, L, C, lerp(prev, upto, P(t, t0 + .2, 1.2)), a=aS)
        for k, lab, cl, tt in seq:
            i = g[k]
            ga = P(t, tt + .4, .4) * aS
            if ga <= 0: continue
            lo_, hi_ = (Hh[i - 1], L[i]) if L[i] > Hh[i - 1] else (L[i - 1], Hh[i])
            zone(c, F, i - 1, i, lo_, hi_, cl, .3 * ga)
            tag(c, F.X(i - .5), F.Y(hi_) - 60 if k != 'common' else F.Y(L[i]) + 50, lab, cl, WHITE, 20, ga, 'c')
        if t > b[5] + 1:
            ma = P(t, b[5] + 1.4, .5) * aS
            measure(c, F.X(3), F.Y(C[11]), F.Y((Hh[18] + L[19]) / 2), BLUE, ma, 1, 'A', 'r')
            measure(c, F.X(8), F.Y((Hh[18] + L[19]) / 2), F.Y(Hh[26]), BLUE, ma, P(t, b[5] + 1.8, .6), 'about = A', 'r')
            line(c, F.X(3) - 14, F.Y((Hh[18] + L[19]) / 2), F.X(19), F.Y((Hh[18] + L[19]) / 2), BLUE, 2, ma, [6, 6])
        if t > b[6] + 1:
            fa = P(t, b[6] + 1.6, .5) * aS
            tag(c, F.X(n - 2), F.Y(L[n - 1]) + 40, 'Gap filled: trend likely over', RED, WHITE, 20, fa, 'c')
    a7 = stage(t, b, 7, 8)
    if a7 > 0:
        O = [40, 44, 48, 60, 61, 62, 61, 46, 43]; C = [44, 48, 52, 61, 62, 61, 60, 43, 40]
        Hh = [45, 49, 53, 63, 64, 64, 63, 47, 44]; L = [39, 43, 47, 58, 59, 59, 58, 42, 38]
        F = Frame(330, 360, 1260, 420, -1, 9, 32, 70)
        card(c, 280, 310, 1360, 540, 24, CARD, a7)
        candles(c, F, O, Hh, L, C, 9 * P(t, b[7], 1.6), a=a7, wfrac=.45)
        ia = P(t, b[7] + 1.8, .5) * a7
        zone(c, F, 2.5, 6.5, 57, 65.5, GOLD, .18 * ia)
        zone(c, F, 2, 3, 53, 58, RED, .3 * ia); zone(c, F, 6, 7, 47, 58, RED, .3 * ia)
        tag(c, F.X(4.5), F.Y(65.5) - 54, 'ISLAND REVERSAL', NAVY, WHITE, 26, ia, 'c')
        text(c, 'gap up', F.X(2.5), F.Y(53) + 40, 22, 'semi', RED, 'c', ia)
        text(c, 'gap down', F.X(6.5), F.Y(47) + 40, 22, 'semi', RED, 'c', ia)
    a8 = P(t, b[8], .5)
    if a8 > 0:
        d = nifty_d24(); O, Hh, L, C = d['o'], d['h'], d['l'], d['c']; n = len(C)
        F = Frame(220, 340, 1260, 450, -1, n, 21000, 24800)
        chart_card(c, F, a8, 'NIFTY 50', 'daily, May to July 2024', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [21500, 22500, 23500, 24500], a=a8)
        xlabels(c, F, [(idx(d, '2024-05-02'), 'May'), (idx(d, '2024-06-03'), '3 Jun'), (idx(d, '2024-07-01'), 'Jul')], a8)
        i3 = idx(d, '2024-06-03')
        k = (i3 + 1) * P(t, b[8] + .2, 1.2) + (n - i3 - 1) * P(t, b[8] + b.d[8] * .45, 1.2)
        candles(c, F, O, Hh, L, C, k, a=a8)
        ga = P(t, b[8] + 1.4, .5) * a8
        zone(c, F, i3 - 1, i3, Hh[i3 - 1], L[i3], GOLD, .35 * ga)
        tag(c, F.X(i3) - 150, F.Y(L[i3]) - 40, '3 Jun: gap up 3.6% on exit polls', GOLD, WHITE, 20, ga, 'c')
        fa = P(t, b[8] + b.d[8] * .5, .5) * a8
        tag(c, F.X(i3) + 330, F.Y(21900), '4 Jun: results day, closes -5.9%', RED, WHITE, 20, fa, 'c')
        tag(c, F.X(i3) + 330, F.Y(21900) + 46, 'gap filled in one session', RED, WHITE, 20, P(t, b[8] + b.d[8] * .6, .5) * a8, 'c')
