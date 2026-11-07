from engine import *
from . import scene
from .common import *
from .data import nifty_m, nifty_w, nifty_d24, btc_m, idx

# ------------------------------------------------------------ 8.1 long-range perspective
@scene('c8s1')
def c8s1(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        bars = [('Daily chart', '6 to 9 months', 220, FAINT), ('Weekly chart', 'several years', 700, BLUE), ('Monthly chart', 'decades', 1300, NAVY)]
        for i, (lab, sub, w_, cl) in enumerate(bars):
            y = 380 + i * 150
            with rise(c, t, b[1] + .3 + i * .5 + (b.d[1] * .4 if i else 0)) as a:
                text(c, lab, 220, y + 10, 32, 'head', cl if i else MUTED, 'l', a * a1)
                text(c, sub, 220, y + 46, 24, 'semi', MUTED, 'l', a * a1)
                rrect(c, 520, y - 24, w_ * P(t, b[1] + .5 + i * .5 + (b.d[1] * .4 if i else 0), .9, eio) + 8, 60, 30); col(c, cl, a * a1); c.fill()
        ma = P(t, b[2], .5) * a1
        pill(c, 960, 840, 'See the major trend and the major support & resistance', 26, NAVY, WHITE, ma, 'semi', 'c', ls=0)
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        d = nifty_m(); C, Hh, L = d['c'], d['h'], d['l']; n = len(C)
        F = Frame(220, 330, 1280, 480, 0, n - 1, 250, 32000, log=True)
        chart_card(c, F, a3, 'NIFTY 50', 'monthly, log scale, 1990 to 2026', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [300, 1000, 3000, 10000, 30000], a=a3)
        xlabels(c, F, [(idx(d, f'{y}-01-01'), str(y)) for y in (1991, 2000, 2008, 2020)], a3)
        series(c, F, range(n), C, P(t, b[3] + .2, 1.8), NAVY, 3.5, a3, BLUE, .12)
        i0, i1 = idx(d, '2008-01-01'), idx(d, '2008-10-01')
        za = P(t, b[3] + 2.2, .5) * a3
        zone(c, F, i0 - 1, i1 + 3, 1500, 9000, RED, .12 * za)
        measure(c, F.X(i1) + 40, F.Y(6357), F.Y(2253), RED, za, P(t, b[3] + 2.2, .8), '2008: -65%', 'r')
        ta = P(t, b[3] + b.d[3] * .6, .5) * a3
        card(c, 1560, 420, 230, 250, 20, NAVY, ta)
        text(c, 'On a daily chart:', 1675, 470, 20, 'semi', LGOLD, 'c', ta)
        text(c, 'terrifying', 1675, 510, 30, 'bold', RED, 'c', ta)
        text(c, 'On a monthly:', 1675, 570, 20, 'semi', LGOLD, 'c', ta)
        text(c, 'a deep correction', 1675, 606, 24, 'bold', WHITE, 'c', ta)
        text(c, 'in an uptrend', 1675, 638, 24, 'bold', WHITE, 'c', ta)
    a4 = stage(t, b, 4, 6)
    if a4 > 0:
        sets = [('MONTHLY', nifty_m()['c'][-160:], True, NAVY), ('WEEKLY', nifty_w()['c'][-160:], False, BLUE), ('DAILY', nifty_d24()['c'], False, GREEN), ('INTRADAY', None, False, GOLD)]
        for i, (lab, data, lg, cl) in enumerate(sets):
            x = 170 + i * 410
            with pop(c, t, b[4] + .3 + i * .6, x + 180, 560) as a:
                if a <= 0: continue
                card(c, x, 360, 370, 330, 22, CARD, a * a4, border=cl, bw=3)
                text(c, f'{i+1}. {lab}', x + 185, 410, 26, 'head', cl, 'c', a * a4, ls=2)
                if data:
                    F = Frame(x + 30, 440, 310, 200, 0, len(data) - 1, min(data) * .97, max(data) * 1.03, log=lg)
                    series(c, F, range(len(data)), data, 1, cl, 3, a * a4)
                else:
                    rnd = random.Random(2); v = 50; pts = []
                    for q in range(60): v += rnd.gauss(0, 2); pts.append(v)
                    F = Frame(x + 30, 440, 310, 200, 0, 59, min(pts) - 3, max(pts) + 3); series(c, F, range(60), pts, 1, cl, 3, a * a4)
                if i < 3: arrow(c, x + 372, 525, x + 406, 525, GOLD, 5, a * a4, 1, 14)
        da = P(t, b[5], .5) * a4
        pill(c, 560, 760, 'Long-term chart = DIRECTION', 28, NAVY, WHITE, da, 'semi', 'c', ls=1)
        pill(c, 1360, 760, 'Short-term chart = WHEN TO ACT', 28, GOLD, WHITE, P(t, b[5] + b.d[5] * .45, .5) * a4, 'semi', 'c', ls=1)
    a6 = stage(t, b, 6, 7)
    if a6 > 0:
        with pop(c, t, b[6], 960, 560) as a:
            card(c, 460, 380, 1000, 330, 26, LGOLD, a * a6, border=GOLD)
            warn(c, 620, 500, .8, a * a6, GOLD)
            text(c, 'Not for timing', 720, 520, 48, 'head', NAVY, 'l', a * a6)
            text(c, 'Perspective, not entry points', 720, 590, 32, 'serif', INK, 'l', a * a6)
    a7 = P(t, b[7], .5)
    if a7 > 0:
        d = nifty_m(); C, L = d['c'], d['l']; n = len(C)
        F = Frame(220, 330, 1280, 480, 0, n - 1, 250, 32000, log=True)
        chart_card(c, F, a7, 'NIFTY 50', 'monthly, log scale', 'Data: TradingView · NSE:NIFTY')
        series(c, F, range(n), C, 1, NAVY, 3.5, a7, BLUE, .12)
        i1, i2 = idx(d, '2003-04-01'), idx(d, '2020-03-02')
        seg(c, F, i1, L[i1], i2, L[i2], GREEN, 4, a7 * P(t, b[7] + .5, .5), P(t, b[7] + .5, 1), ext=.25)
        tag(c, F.X(idx(d, '2012-01-02')), F.Y(2600), 'trendline', GREEN, WHITE, 20, P(t, b[7] + 1.2, .4) * a7, 'c')
        hline(c, F, 6357, idx(d, '2008-01-01'), idx(d, '2014-06-02'), RED, 3, a7 * P(t, b[7] + 1.6, .5), P(t, b[7] + 1.6, .8), [10, 8])
        tag(c, F.X(idx(d, '2011-01-03')), F.Y(6357) - 60, '2008 high: resistance for years', RED, WHITE, 20, P(t, b[7] + 2.2, .4) * a7, 'c')
        for q, s_ in enumerate(['Trendlines', 'Support & resistance', 'Retracements']):
            pill(c, 1660, 450 + q * 70, s_, 22, NAVY, WHITE, P(t, b[7] + 2.6 + q * .3, .4), 'semi', 'c', ls=0)

# ------------------------------------------------------------ 8.2 Bitcoin long term
@scene('c8s2')
def c8s2(c, t, b):
    d = btc_m(); C, Hh, L = d['c'], d['h'], d['l']; n = len(C)
    aC = P(t, .3, .5) * (1 - P(t, b[6] - .3, .4))
    if aC > 0:
        F = Frame(210, 330, 1300, 500, 0, n - 1, 1.5, 200000, log=True)
        chart_card(c, F, aC, 'BITCOIN', 'monthly, log scale, 2011 to 2026', 'Data: TradingView · BITSTAMP:BTCUSD')
        ygrid(c, F, [10, 100, 1000, 10000, 100000], fmt_k, aC)
        xlabels(c, F, [(idx(d, f'{y}-01-01'), str(y)) for y in (2012, 2014, 2016, 2018, 2020, 2022, 2024, 2026)], aC)
        series(c, F, range(n), C, P(t, b[1], 2.2), ORANGE, 3.5, aC, ORANGE, .12)
        dds = [(('2013-11-01', 1163), ('2015-01-01', 152.4), '-87%', b[2] + .3), (('2017-12-01', 19666), ('2018-12-01', 3122.28), '-84%', b[2] + b.d[2] * .4),
               (('2021-11-01', 69000), ('2022-11-01', 15479), '-78%', b[2] + b.d[2] * .75), (('2025-10-01', 126272), ('2026-07-01', 57734.63), '-54%', b[3] + .4)]
        for (d1, p1), (d2, p2), lab, t0 in dds:
            i1, i2 = idx(d, d1), idx(d, d2)
            ma = P(t, t0, .5) * aC
            measure(c, F.X(i2) + 18, F.Y(p1), F.Y(p2), RED, ma, P(t, t0, .8), lab, 'r', 3, 18)
        sa = P(t, b[4] + b.d[4] * .4, .5) * aC
        if sa > 0:
            pk = [('2013-11-01', 1163), ('2017-12-01', 19666), ('2021-11-01', 69000), ('2025-10-01', 126272)]
            tr = [('2011-11-01', 2.22), ('2015-01-01', 152.4), ('2018-12-01', 3122.28), ('2022-11-01', 15479), ('2026-07-01', 57734.63)]
            polyline(c, [F.P(idx(d, ds), p) for ds, p in pk], GREEN, 3, sa, P(t, b[4] + b.d[4] * .4, 1), [10, 8])
            polyline(c, [F.P(idx(d, ds), p) for ds, p in tr], GREEN, 3, sa, P(t, b[4] + b.d[4] * .6, 1), [10, 8])
            for ds, p in pk: glow_dot(c, F.X(idx(d, ds)), F.Y(p), 7, GREEN, t, sa, False)
            for ds, p in tr: glow_dot(c, F.X(idx(d, ds)), F.Y(p), 7, BLUE, t, sa, False)
        ra = P(t, b[5], .5) * aC
        card(c, 1580, 420, 220, 300, 20, NAVY, ra)
        text(c, 'Rising peaks', 1690, 500, 26, 'bold', WHITE, 'c', ra)
        text(c, 'Rising troughs', 1690, 545, 26, 'bold', WHITE, 'c', ra)
        text(c, "= Dow's", 1690, 610, 24, 'semi', LGOLD, 'c', ra)
        text(c, 'uptrend', 1690, 645, 24, 'semi', LGOLD, 'c', ra)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, (lab, mood) in enumerate([('remember', 'neutral'), ('hope', 'happy'), ('fear', 'worried'), ('repeat', 'smile')]):
            x = 300 + i * 440
            with pop(c, t, b[6] + .2 + i * .35, x, 520) as a:
                avatar(c, x, 500, 1.0, SKIN[i], HAIR[i], [NAVY, GREEN, RED, GOLD][i], ['side', 'long', 'curly', 'short'][i], mood=mood, t=t, seed=i, a=a * a6)
                text(c, lab.upper(), x, 700, 30, 'head', [NAVY, GREEN, RED, GOLD][i], 'c', a * a6, ls=3)
        text(c, 'The chart is a record of human behaviour', 960, 800, 36, 'serif', INK, 'c', P(t, b[6] + 1.6, .5) * a6)
