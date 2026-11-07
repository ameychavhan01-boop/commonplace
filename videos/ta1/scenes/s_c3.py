from engine import *
from . import scene
from .common import *
from .data import btc_d, btc_m, nifty_d20, nifty_w, nifty_m, idx

def pnf(closes, box, rev=3):
    """point & figure columns: list of (kind 'X'/'O', lo_box, hi_box)."""
    cols = []
    b0 = math.floor(closes[0] / box)
    kind, lo, hi = None, b0, b0
    for p in closes[1:]:
        bb = p / box
        if kind in (None, 'X'):
            if math.floor(bb) > hi: hi = math.floor(bb); kind = 'X'
            elif kind == 'X' and math.ceil(bb) <= hi - rev:
                cols.append(('X', lo, hi)); kind = 'O'; hi = hi - 1; lo = math.ceil(bb)
            elif kind is None and math.ceil(bb) < lo: lo = math.ceil(bb); kind = 'O'
        else:
            if math.ceil(bb) < lo: lo = math.ceil(bb)
            elif math.floor(bb) >= lo + rev:
                cols.append(('O', lo, hi)); kind = 'X'; lo = lo + 1; hi = math.floor(bb)
    cols.append((kind or 'X', lo, hi))
    return cols

def draw_pnf(c, x, y, w, h, cols, box, pmin, pmax, a=1.0, prog=1.0, size=None):
    n = len(cols); cw = min(w / max(n, 1), 64)
    x = x + (w - cw * n) / 2
    bh = h / ((pmax - pmin) / box)
    sz = min(cw, bh) * .82
    shown = n * prog
    for i, (k, lo, hi) in enumerate(cols):
        if i >= shown: break
        cx = x + (i + .5) * cw
        for bx in range(lo, hi + 1):
            cy = y + h - ((bx + .5) * box - pmin) / (pmax - pmin) * h
            if k == 'X':
                line(c, cx - sz / 2, cy - sz / 2, cx + sz / 2, cy + sz / 2, GREEN, 3, a)
                line(c, cx + sz / 2, cy - sz / 2, cx - sz / 2, cy + sz / 2, GREEN, 3, a)
            else:
                ring(c, cx, cy, sz / 2, RED, 3, a)

TYPES = [('Line chart', 'Connects the closes'), ('Bar chart', 'Open, high, low, close'), ('Candlestick', 'Body from open to close'), ('Point & figure', "Only price changes: X's and O's")]

# ------------------------------------------------------------ 3.1 four ways
@scene('c3s1')
def c3s1(c, t, b):
    d = btc_d(); O, Hh, L, C = d['o'], d['h'], d['l'], d['c']; n = len(C)
    cur = -1 if t < b[2] else 0 if t < b[3] else 1 if t < b[4] else 2 if t < b[5] else 3
    aM = stage(t, b, 1, 6)
    if aM > 0:
        F = Frame(210, 350, 1080, 450, -1, n, 62000, 112000)
        chart_card(c, F, aM, 'BITCOIN', 'daily, Oct 2024 to Jan 2025', 'Data: TradingView · BITSTAMP:BTCUSD')
        ygrid(c, F, [70000, 80000, 90000, 100000, 110000], fmt_k, aM)
        xlabels(c, F, [(idx(d, '2024-11-01'), 'Nov'), (idx(d, '2024-12-01'), 'Dec'), (idx(d, '2025-01-01'), 'Jan')], aM)
        la = aM * (1 - P(t, b[3] - .2, .5)) * P(t, b[2], .3)
        if la > 0: series(c, F, range(n), C, P(t, b[2], 1.8), NAVY, 4, la, BLUE, .12)
        ba = aM * P(t, b[3], .5) * (1 - P(t, b[4] - .2, .5))
        if ba > 0: ohlc(c, F, O, Hh, L, C, n * P(t, b[3], 1.5), a=ba, lw=2.2, cl=NAVY)
        ca = aM * P(t, b[4], .5) * (1 - P(t, b[5] - .2, .5))
        if ca > 0: candles(c, F, O, Hh, L, C, n * P(t, b[4], 1.5), a=ca)
        pa = aM * P(t, b[5], .5)
        if pa > 0:
            cols = pnf(C, 2000)
            c.save(); c.rectangle(F.x, F.y, F.w, F.h); c.clip()
            draw_pnf(c, F.x + 40, F.y, F.w - 80, F.h, cols, 2000, 62000, 112000, pa, P(t, b[5] + .2, 2.0))
            c.restore()
            tag(c, F.x + F.w / 2, F.y + F.h - 50, 'Box $2,000 · 3-box reversal · no time axis', NAVY, WHITE, 20, pa * P(t, b[5] + 1.5, .5), 'c')
        for i, (nm, sub) in enumerate(TYPES):
            y = 330 + i * 125
            on = 1 if i == cur else 0
            with pop(c, t, b[1] + .3 + i * .2, 1560, y + 50) as a:
                card(c, 1390, y, 380, 105, 18, NAVY if on else CARD, a * aM, border=None if on else LINE)
                text(c, nm, 1420, y + 46, 28, 'bold', WHITE if on else INK, 'l', a * aM)
                text(c, sub, 1420, y + 80, 21, 'med', LGOLD if on else MUTED, 'l', a * aM)
                if i >= 2: text(c, 'PART 2', 1752, y + 30, 16, 'semi', GOLD, 'r', a * aM, ls=2)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, (nm, sub) in enumerate(TYPES):
            r, cc = divmod(i, 2)
            x, y = 200 + cc * 780, 280 + r * 285
            F = Frame(x + 40, y + 60, 620, 170, -1, n, 62000, 112000)
            with pop(c, t, b[6] + .2 + i * .25, x + 360, y + 140) as a:
                card(c, x, y, 740, 260, 20, CARD, a * a6)
                text(c, nm, x + 30, y + 44, 26, 'bold', NAVY, 'l', a * a6)
                if i == 0: series(c, F, range(n), C, 1, NAVY, 3, a * a6)
                elif i == 1: ohlc(c, F, O, Hh, L, C, n, a=a * a6, lw=1.6, cl=NAVY)
                elif i == 2: candles(c, F, O, Hh, L, C, n, a=a * a6)
                else: draw_pnf(c, F.x, F.y, F.w, F.h, pnf(C, 2000), 2000, 62000, 112000, a * a6, 1)
        text(c, 'Same data. Four lenses.', 960, 880, 30, 'serif', MUTED, 'c', P(t, b[6] + 1.4, .5))

# ------------------------------------------------------------ 3.2 anatomy of a bar
def _day_path():
    rnd = random.Random(21); v = 100.0; out = [v]
    targets = [(0, 100), (60, 107.5), (120, 97), (200, 104)]
    for i in range(1, 201):
        for j in range(len(targets) - 1):
            if targets[j][0] <= i <= targets[j + 1][0]:
                f = (i - targets[j][0]) / (targets[j + 1][0] - targets[j][0]); base = lerp(targets[j][1], targets[j + 1][1], f)
        v = base + rnd.gauss(0, .45); out.append(v)
    out[0] = 100; out[-1] = 104
    return out
DAY = _day_path()

@scene('c3s2')
def c3s2(c, t, b):
    o, cl_ = DAY[0], DAY[-1]; hi, lo = max(DAY), min(DAY)
    ih, il = DAY.index(hi), DAY.index(lo)
    F = Frame(220, 340, 820, 420, 0, 200, 94, 110)
    aP = P(t, .3, .5)
    card(c, 180, 300, 900, 520, 24, CARD, aP)
    text(c, 'ONE TRADING DAY', 1050, 340, 20, 'semi', MUTED, 'r', aP, ls=3)
    text(c, 'open', F.X(0), F.y + F.h + 34, 20, 'med', MUTED, 'c', aP); text(c, 'close', F.X(200), F.y + F.h + 34, 20, 'med', MUTED, 'c', aP)
    k = lerp(0, 200, P(t, b[1] + .3, max(1, b[3] - b[1]), lambda x: x))
    head = series(c, F, range(201), DAY, k / 200, NAVY, 3, aP)
    if head and k < 200: glow_dot(c, head[0], head[1], 6, GOLD, t, aP)
    marks = [('OPEN', 0, o, BLUE, b[1] + .2), ('HIGH', ih, hi, GREEN, b[2] + .3), ('LOW', il, lo, RED, b[2] + 1.0), ('CLOSE', 200, cl_, GOLD, b[3] + .4)]
    for lab, i, p, colr, t0 in marks:
        if k < i - .5 and lab != 'OPEN': continue
        ma = P(t, max(t0, 0), .4) * aP
        glow_dot(c, F.X(i), F.Y(p), 8, colr, t, ma, False)
        tag(c, F.X(i) + (40 if lab == 'OPEN' else 0), F.Y(p) + (-62 if lab in ('HIGH', 'CLOSE') else 22), f'{lab} {p:.1f}', colr, WHITE, 20, ma, 'c')
    # bar construction
    ba = P(t, b[4], .5)
    if ba > 0:
        bx = 1270
        for lab, i, p, colr, t0 in marks:
            line(c, F.X(i) + 10, F.Y(p), bx - 70, F.Y(p), colr, 2, ba * .6, [6, 8], P(t, b[4] + .2, .8))
        line(c, bx, F.Y(hi), bx, F.Y(lo), NAVY, 8, ba, p=P(t, b[4] + .5, .6))
        line(c, bx - 40, F.Y(o), bx, F.Y(o), NAVY, 8, ba, p=P(t, b[4] + 1.0, .4))
        line(c, bx, F.Y(cl_), bx + 40, F.Y(cl_), NAVY, 8, ba, p=P(t, b[4] + 1.3, .4))
        text(c, 'BAR', bx, F.y + F.h + 40, 24, 'head', NAVY, 'c', ba, ls=3)
        text(c, 'open', bx - 54, F.Y(o) + 8, 20, 'semi', BLUE, 'r', P(t, b[4] + 1.1, .4) * ba)
        text(c, 'close', bx + 54, F.Y(cl_) + 8, 20, 'semi', GOLD, 'l', P(t, b[4] + 1.4, .4) * ba)
    ca = P(t, b[5], .5)
    if ca > 0:
        cx = 1560
        line(c, cx, F.Y(hi), cx, F.Y(lo), GREEN, 4, ca, p=P(t, b[5] + .2, .5))
        hgt = (F.Y(o) - F.Y(cl_)) * P(t, b[5] + .5, .6)
        c.rectangle(cx - 34, F.Y(o) - hgt, 68, hgt); col(c, GREEN, ca); c.fill()
        text(c, 'CANDLE', cx, F.y + F.h + 40, 24, 'head', GREEN, 'c', ca, ls=3)
        text(c, 'wick', cx + 46, F.Y(hi) + 30, 20, 'semi', MUTED, 'l', ca)
        text(c, 'body', cx + 46, (F.Y(o) + F.Y(cl_)) / 2 + 6, 20, 'semi', MUTED, 'l', ca)
        tag(c, 1745, 690, 'Close > open: green', GREEN, WHITE, 20, P(t, b[5] + 1.2, .4) * ca, 'c')
        tag(c, 1745, 738, 'Close < open: red', RED, WHITE, 20, P(t, b[5] + 1.5, .4) * ca, 'c')
    va = P(t, b[6], .5)
    if va > 0:
        V = Frame(1180, 850, 560, 50, 0, 6, 0, 1)
        for i, v_ in enumerate([.4, .6, .5, .9, .7, .55, .8]):
            hh = v_ * 50 * P(t, b[6] + i * .1, .4)
            c.rectangle(1190 + i * 80, 900 - hh, 50, hh); col(c, BLUE, va * .8); c.fill()
        text(c, 'VOLUME', 1180, 840, 18, 'semi', MUTED, 'l', va, ls=3)
        pts = [(1215 + i * 80, 880 - 30 * (.4 + .1 * i)) for i in range(7)]
        polyline(c, pts, GOLD, 4, va * P(t, b[6] + 1.2, .4), P(t, b[6] + 1.2, .8))
        text(c, 'open interest (futures)', 1740, 828, 18, 'semi', GOLD, 'r', va * P(t, b[6] + 1.2, .4))
    sa = P(t, b[7], .5)
    if sa > 0:
        for i, w_ in enumerate(['Open', 'High', 'Low', 'Close', '+ Volume']):
            pill(c, 230 + i * 160, 870, w_, 22, [BLUE, GREEN, RED, GOLD, NAVY][i], WHITE, P(t, b[7] + i * .15, .4), 'semi', ls=1)

# ------------------------------------------------------------ 3.3 arithmetic vs log
@scene('c3s3')
def c3s3(c, t, b):
    aR = stage(t, b, 0, 4)
    if aR > 0:
        # arithmetic ruler
        x0, y0, y1 = 420, 820, 330
        card(c, 220, 290, 660, 590, 24, CARD, aR)
        text(c, 'ARITHMETIC', 550, 340, 24, 'head', NAVY, 'c', aR, ls=3)
        def ya(v): return lerp(y0, y1 + 60, v / 1200)
        line(c, x0, y0, x0, y1 + 60, INK, 3, aR)
        for v in range(0, 1201, 200):
            line(c, x0 - 10, ya(v), x0, ya(v), INK, 2, aR); text(c, f'{v:,}', x0 - 18, ya(v) + 7, 18, 'med', MUTED, 'r', aR)
        m1 = P(t, b[1] + .3, .6) * aR; m2 = P(t, b[1] + 1.0, .6) * aR
        for (v0, v1_, xx, m, lab2) in ((100, 200, 520, m1, '+100%'), (1000, 1100, 700, m2, '+10%')):
            c.rectangle(xx - 30, ya(v1_), 60, ya(v0) - ya(v1_)); col(c, GOLD, m * .8); c.fill()
            text(c, f'{v0:,} to {v1_:,}', xx, ya(v1_) - 14, 20, 'semi', INK, 'c', m)
            sw = P(t, b[2], .4)
            text(c, '+100 pts', xx, ya(v0) + 30, 22, 'bold', NAVY, 'c', m * (1 - sw))
            text(c, lab2, xx, ya(v0) + 30, 26, 'head', GREEN if lab2 == '+100%' else RED, 'c', m * sw)
        la = P(t, b[3], .5) * aR
        if la > 0:
            card(c, 1040, 290, 660, 590, 24, CARD, la)
            text(c, 'LOGARITHMIC', 1370, 340, 24, 'head', GOLD, 'c', la, ls=3)
            xl = 1240
            def yl(v): return lerp(y0, y1 + 60, math.log10(v / 5) / math.log10(40000 / 5))
            line(c, xl, y0, xl, y1 + 60, INK, 3, la)
            for v in (10, 40, 160, 640, 2560, 10240, 40960):
                line(c, xl - 10, yl(v), xl, yl(v), INK, 2, la); text(c, f'{v:,}', xl - 18, yl(v) + 7, 16, 'med', MUTED, 'r', la)
            for (v0, xx, t0) in ((10, 1360, b[3] + .4), (10240, 1560, b[3] + 1.1)):
                m = P(t, t0, .6) * la
                c.rectangle(xx - 30, yl(v0 * 2), 60, yl(v0) - yl(v0 * 2)); col(c, GREEN, m * .8); c.fill()
                text(c, f'{v0:,} to {v0*2:,}', xx, yl(v0 * 2) - 14, 20, 'semi', INK, 'c', m)
                text(c, 'x2', xx, yl(v0) + 30, 26, 'head', GREEN, 'c', m)
            text(c, 'Equal distance = equal % change', 1370, 860, 22, 'semi', MUTED, 'c', la)
    aB = stage(t, b, 4, 6)
    if aB > 0:
        d = btc_m(); C = d['c']; n = len(C)
        F = Frame(220, 330, 1380, 470, 0, n - 1, 1.5, 150000)
        k = P(t, b[5], 1.8, eio)
        lo_l, hi_l = math.log(1.5), math.log(150000)
        def Y(v):
            ylin = F.y + F.h - (v - 0) / (150000) * F.h
            ylog = F.y + F.h - (math.log(max(v, 1.5)) - lo_l) / (hi_l - lo_l) * F.h
            return lerp(ylin, ylog, k)
        chart_card(c, F, aB, 'BITCOIN', 'monthly, 2011 to 2026', 'Data: TradingView · BITSTAMP:BTCUSD')
        ticks = [10, 100, 1000, 10000, 100000] if k > .5 else [25000, 50000, 75000, 100000, 125000]
        ga = abs(k - .5) * 2
        for v in ticks:
            y = Y(v); line(c, F.x, y, F.x + F.w, y, GRID, 1.5, aB * ga); text(c, fmt_k(v), F.x + F.w + 12, y + 6, 18, 'med', MUTED, 'l', aB * ga)
        xlabels(c, F, [(idx(d, f'{y}-01-01'), str(y)) for y in (2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026)], aB)
        pts = [(F.X(i), Y(v)) for i, v in enumerate(C)]
        polyline(c, pts, ORANGE, 3.5, aB, P(t, b[4] + .2, 1.6))
        i17 = idx(d, '2017-01-01')
        fa = P(t, b[4] + 2.0, .5) * aB * (1 - P(t, b[5], .5))
        zone(c, F, 0, i17, 0, 1e9, RED, 0)
        c.rectangle(F.x, F.y + F.h - 40, F.X(i17) - F.x, 40); col(c, RED, .12 * fa); c.fill()
        tag(c, (F.x + F.X(i17)) / 2, F.y + F.h - 110, 'Flat? It went from about $10 to $1,000+', RED, WHITE, 22, fa, 'c')
        sw = P(t, b[5], .5) * aB
        pill(c, F.x + 10, F.y + 10, 'LOG SCALE' if k > .5 else 'ARITHMETIC SCALE', 20, GOLD if k > .5 else NAVY, WHITE, aB, 'semi', ls=2)
        if k > .9:
            for (ds, lab) in (('2013-11-01', '2013 bubble'), ('2017-12-01', '2017 bubble'), ('2021-11-01', '2021 peak')):
                i = idx(d, ds); ta = P(t, b[5] + 2 + (0 if '2013' in lab else .3 if '2017' in lab else .6), .4) * aB
                tag(c, F.X(i), Y(d['h'][i]) - 56, lab, NAVY, WHITE, 18, ta, 'c')
    a6 = P(t, b[6], .5)
    if a6 > 0:
        d = btc_m(); C = d['c']
        with pop(c, t, b[6], 560, 580) as a:
            label_card(c, 220, 380, 680, 400, 'Big moves, long periods', 'Use a log scale for the truer picture', a * a6, GOLD, 38, 28)
            F1 = Frame(270, 540, 580, 200, 0, len(C) - 1, 2, 150000, log=True)
            series(c, F1, range(len(C)), C, 1, ORANGE, 3, a * a6)
        with pop(c, t, b[6] + b.d[6] * .45, 1360, 580) as a:
            label_card(c, 1020, 380, 680, 400, 'Short-term trading', 'The difference is small', a * a6, NAVY, 38, 28)
            dd = btc_d(); F2 = Frame(1070, 540, 580, 200, 60, 104, 88000, 110000)
            candles(c, F2, dd['o'], dd['h'], dd['l'], dd['c'], 44, start=60, a=a * a6)

# ------------------------------------------------------------ 3.4 time frames
@scene('c3s4')
def c3s4(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        for i, lab in enumerate(['1 minute', '1 hour', '1 day', '1 week', '1 month']):
            x = 230 + i * 365
            with pop(c, t, b[1] + .2 + i * .3, x + 140, 560) as a:
                card(c, x, 420, 300, 280, 22, CARD, a * a1)
                cx = x + 150
                line(c, cx, 470, cx, 620, INK, 4, a * a1)
                c.rectangle(cx - 26, 500, 52, 90); col(c, GREEN if i % 2 == 0 else RED, a * a1); c.fill()
                text(c, lab, cx, 670, 30, 'bold', NAVY, 'c', a * a1)
        text(c, 'One bar can be any period', 960, 800, 32, 'serif', MUTED, 'c', P(t, b[1] + 1.8, .5) * a1)
    aC = stage(t, b, 2, 4)
    if aC > 0:
        dd, dw, dm = nifty_d20(), nifty_w(), nifty_m()
        i0 = idx(dd, '2020-06-01')
        sets = [('DAILY', '6 to 9 months', dd['c'][i0:], b[2]), ('WEEKLY', 'several years', dw['c'], b[3]), ('MONTHLY', 'decades', dm['c'], b[3] + b.d[3] * .45)]
        for k, (lab, sub, data, t0) in enumerate(sets):
            x = 170 + k * 540
            with pop(c, t, t0, x + 250, 560) as a:
                if a <= 0: continue
                F = Frame(x + 30, 400, 440, 300, 0, len(data) - 1, min(data) * .95, max(data) * 1.05, log=(k == 2))
                card(c, x, 330, 500, 470, 22, CARD, a * aC)
                text(c, lab, x + 30, 375, 26, 'head', NAVY, 'l', a * aC, ls=2)
                text(c, sub, x + 470, 375, 22, 'semi', GOLD, 'r', a * aC)
                series(c, F, range(len(data)), data, P(t, t0 + .2, 1.2), NAVY, 3, a * aC, BLUE, .12)
                text(c, 'Nifty 50 · TradingView', x + 250, 770, 18, 'med', FAINT, 'c', a * aC)
    def nested(cx, t0, aa, sc=1.0):
        stepsL = ['Monthly', 'Weekly', 'Daily', 'Intraday']
        for i, s_ in enumerate(stepsL):
            w_ = (620 - i * 130) * sc; h_ = (440 - i * 95) * sc
            yy = 580 - 440 * sc / 2 + i * 62 * sc
            with pop(c, t, t0 + .3 + i * .55, cx, yy + h_ / 2) as a:
                rrect(c, cx - w_ / 2, yy, w_, h_, 22 * sc); col(c, [NAVY, BLUE, GREEN, GOLD][i], a * aa); c.fill()
                text(c, f'{i+1}. {s_}', cx, yy + 40 * sc, 26 * sc, 'head', WHITE, 'c', a * aa)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        nested(960, b[4], a4)
        text(c, 'Big picture first', 400, 560, 32, 'serif', NAVY, 'c', P(t, b[4] + .6, .5) * a4)
        text(c, 'Precise timing last', 1520, 560, 32, 'serif', GOLD, 'c', P(t, b[4] + 2.2, .5) * a4)
    a5 = P(t, b[5], .5) * (1 - P(t, b[6] - .2, .4))
    if a5 > 0:
        for i, (lab, kind) in enumerate([('Country', 'c'), ('City', 'g'), ('Street', 's')]):
            x = 200 + i * 540
            with pop(c, t, b[5] + .2 + i * .6, x + 240, 560) as a:
                card(c, x, 360, 480, 400, 22, CARD, a * a5)
                if kind == 'c':
                    pts = [(x + 120, 470), (x + 220, 420), (x + 330, 450), (x + 380, 560), (x + 300, 680), (x + 180, 660), (x + 110, 580)]
                    c.new_path(); c.move_to(*pts[0])
                    for p_ in pts[1:]: c.line_to(*p_)
                    c.close_path(); col(c, LGREEN, a * a5); c.fill_preserve(); col(c, GREEN, a * a5); c.set_line_width(3); c.stroke()
                    glow_dot(c, x + 260, 560, 8, RED, t, a * a5)
                elif kind == 'g':
                    for gx in range(5): line(c, x + 80 + gx * 80, 420, x + 80 + gx * 80, 700, LINE, 6, a * a5)
                    for gy in range(4): line(c, x + 60, 450 + gy * 80, x + 420, 450 + gy * 80, LINE, 6, a * a5)
                    glow_dot(c, x + 240, 530, 8, RED, t, a * a5)
                else:
                    c.rectangle(x + 40, 560, 400, 90); col(c, LINE, a * a5); c.fill()
                    for k in range(6): line(c, x + 60 + k * 70, 605, x + 100 + k * 70, 605, WHITE, 5, a * a5)
                    wx = x + 120 + 200 * P(t, b[5] + 2, 4, lambda u: u)
                    avatar(c, wx, 470, .5, mood='smile', t=t, a=a * a5)
                    arrow(c, wx + 40, 520, wx + 120, 520, RED, 4, a * a5)
                text(c, lab, x + 240, 735, 30, 'bold', NAVY, 'c', a * a5)
        text(c, 'Only the street? You can walk confidently the wrong way.', 960, 840, 30, 'serif', RED, 'c', P(t, b[5] + b.d[5] * .6, .5) * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        nested(600, b[6] - .3, a6, .9)
        with pop(c, t, b[6] + .6, 1400, 560) as a:
            card(c, 1060, 450, 680, 230, 26, NAVY, a * a6)
            text(c, 'MORE IN', 1400, 515, 22, 'semi', LGOLD, 'c', a * a6, ls=5)
            text(c, 'Chapter 8: Long-Term Charts', 1400, 590, 40, 'serif', WHITE, 'c', a * a6)
