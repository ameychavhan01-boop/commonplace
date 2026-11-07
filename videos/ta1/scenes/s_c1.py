from engine import *
from . import scene
from .common import *
from .data import nifty_d20, nifty_m, nifty_w, btc_w, idx

# ------------------------------------------------------------ 1.1 What TA is
@scene('c1s1')
def c1s1(c, t, b):
    a1 = stage(t, b, 1, 4)
    if a1 > 0:
        with rise(c, t, b[1]):
            card(c, 260, 262, 1400, 150, 24, CARD, a1)
            magnifier(c, 352, 330, 34, a1)
            text(c, 'Technical analysis is the study of', 440, 322, 40, 'serif', INK, 'l', a1)
            text(c, 'market action', 440, 372, 40, 'serifb', NAVY, 'l', a1)
            w0 = tw(c, 'market action', 40, 'serifb')
            text(c, ', mainly through charts, to forecast price trends.', 440 + w0, 372, 40, 'serif', INK, 'l', a1)
            hl = P(t, b[2], .7)
            line(c, 440, 386, 440 + w0 * hl, 386, GOLD, 6, a1)
    a2 = stage(t, b, 2, 3)
    items = [('PRICE', 'What was paid', 'candles'), ('VOLUME', 'How much was traded', 'vol'), ('OPEN INTEREST', 'Contracts still open', 'oi')]
    for i, (ttl, sub, kind) in enumerate(items):
        x = 300 + i * 450
        with pop(c, t, b[2] + .5 + i * .45, x + 190, 610) as a:
            if a <= 0 or a2 <= 0: continue
            aa = a * a2
            card(c, x, 460, 380, 320, 24, CARD, aa)
            cx, cy = x + 190, 580
            if kind == 'candles':
                for k, (o, cl_) in enumerate([(30, -10), (-5, 25), (20, -30), (-25, 15)]):
                    xx = cx - 75 + k * 50; top, bot = min(o, cl_), max(o, cl_)
                    line(c, xx, cy + top - 25, xx, cy + bot + 25, INK, 3, aa)
                    c.rectangle(xx - 13, cy + top, 26, bot - top); col(c, GREEN if cl_ < o else RED, aa); c.fill()
            elif kind == 'vol':
                for k, hh in enumerate([50, 80, 40, 110, 70, 95]):
                    c.rectangle(cx - 95 + k * 33, cy + 55 - hh * (.6 + .4 * abs(math.sin(t + k))), 24, hh * (.6 + .4 * abs(math.sin(t + k)))); col(c, BLUE, aa * .8); c.fill()
            else:
                handshake(c, cx, cy + 6, 1.1, aa)
            text(c, ttl, cx, 712, 30, 'head', NAVY, 'c', aa, ls=2)
            text(c, sub, cx, 750, 24, 'med', MUTED, 'c', aa)
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        for i, lab in enumerate(['Balance sheet', 'Rate forecast', 'Analyst opinion']):
            x = 330 + i * 230
            with pop(c, t, b[3] + i * .2, x, 610) as a:
                doc(c, x, 590, 1.2, a * a3, title=lab.split()[0][:7].upper())
                text(c, lab, x, 700, 22, 'semi', MUTED, 'c', a * a3)
                cross(c, x, 590, 2.2, RED, a * a3, P(t, b[3] + .6 + i * .2, .4))
        arrow(c, 1010, 600, 1150, 600, GOLD, 5, a3, P(t, b[3] + 1.2, .5))
        with pop(c, t, b[3] + 1.5, 1420, 600) as a:
            card(c, 1200, 470, 440, 270, 24, LGREEN, a * a3, border=GREEN)
            chart_icon(c, 1420, 570, 1.3, a * a3)
            text(c, 'The market itself', 1420, 700, 30, 'bold', GREEN, 'c', a * a3)
    if t > b[4] - .3:
        temple(c, t, 460, 360, 1000, ['Market action\ndiscounts everything', 'Prices move\nin trends', 'History\nrepeats itself'],
               [b[5] + .2, b[5] + b.d[5] * .4, b[5] + b.d[5] * .72], b[4] + .3, P(t, b[4] - .2, .5))

# ------------------------------------------------------------ 1.2 discounts everything
@scene('c1s2')
def c1s2(c, t, b):
    aA = 1 - P(t, b[2] - .25, .45)
    if aA > 0:
        fa = P(t, .3, .6) * aA
        funnel(c, 960, 560, 1.4, fa)
        icons = [('Earnings', 'doc'), ('Interest rates', 'pct'), ('Politics', 'flag'), ('Weather', 'cloud'), ('Rumours', 'bubble'), ('Mood', 'face')]
        for i, (lab, kind) in enumerate(icons):
            t0 = b[1] + i * b.d[1] / 7.5
            ang = math.pi * (1.08 + i * .168)
            x0, y0 = 960 + math.cos(ang) * 560, 410 + math.sin(ang) * 120
            fall = P(t, t0 + 1.4, .9, lambda x: x * x)
            x, y = lerp(x0, 960, fall), lerp(y0, 560, fall)
            ia = P(t, t0, .4) * (1 - fall) * aA
            if ia <= 0: continue
            with xf(c, x, y, 1 - .5 * fall):
                if kind == 'doc': doc(c, x, y, .7, ia, title='EPS')
                elif kind == 'pct': coin(c, x, y, 40, '%', BLUE, ia)
                elif kind == 'flag':
                    line(c, x - 20, y + 40, x - 20, y - 40, INK, 5, ia); c.new_path(); c.move_to(x - 18, y - 40); c.line_to(x + 34, y - 26); c.line_to(x - 18, y - 10); c.close_path(); col(c, RED, ia); c.fill()
                elif kind == 'cloud': cloud(c, x, y, 1.1, ia, LBLUE)
                elif kind == 'bubble': bubble(c, x - 45, y - 30, 90, 56, '...', ia, 30, 'head', INK, CARD)
                else: avatar(c, x, y - 10, .45, mood='worried', t=t, a=ia, body=False)
                text(c, lab, x, y + 70, 22, 'semi', INK, 'c', ia)
        pa = P(t, b[1] + 1.5, .5) * aA
        card(c, 810, 700, 300, 120, 20, NAVY, pa)
        text(c, 'PRICE', 960, 740, 20, 'semi', LGOLD, 'c', pa, ls=4)
        text(c, f'{24312 + 180 * math.sin(t * 1.7) + 90 * math.sin(t * 3.1):,.0f}', 960, 798, 50, 'head', WHITE, 'c', pa)
    aB = stage(t, b, 2, 5)
    if aB > 0:
        tilt = lerp(-1, 1, P(t, b[2] + b.d[2] * .5, 1.0, eio)) - 2 * P(t, b[3] - .3, 1.0, eio)
        scale_balance(c, 600, 560, 1.25, tilt, aB, 'DEMAND', 'SUPPLY')
        up = clamp(-tilt * .5 + .5)
        ax = 960
        arrow(c, ax, 690, ax, 470, GREEN, 8, aB * up, 1, 26)
        text(c, 'Prices rise', ax + 40, 590, 30, 'bold', GREEN, 'l', aB * up)
        arrow(c, ax, 470, ax, 690, RED, 8, aB * (1 - up), 1, 26)
        text(c, 'Prices fall', ax + 40, 590, 30, 'bold', RED, 'l', aB * (1 - up))
        chain = [('Price rising', GREEN), ('Demand > Supply', NAVY), ('Fundamentals bullish', GOLD)]
        for i, (lab, cl) in enumerate(chain):
            with pop(c, t, b[3] + i * .55, 1450, 400 + i * 150) as a:
                pill(c, 1450, 370 + i * 150, lab, 30, cl, WHITE, a * aB, 'semi', 'c', ls=1)
            if i: arrow(c, 1450, 370 + (i - 1) * 150 + 66, 1450, 370 + i * 150 - 10, GOLD, 4, aB, P(t, b[3] + i * .55 - .1, .4), 14)
        q = P(t, b[3] + b.d[3] * .7, .5) * aB
        text(c, '...even if nobody knows why yet', 1450, 860, 26, 'serif', MUTED, 'c', q)
        ia = P(t, b[4], .5) * aB
        if ia > 0:
            card(c, 1150, 300, 620, 600, 24, CARD, ia * .0)
    aC = stage(t, b, 5, 6)
    if aC > 0:
        d = nifty_d20(); n = idx(d, '2020-12-31')
        F = Frame(210, 330, 1100, 460, 0, n, 7000, 14500)
        chart_card(c, F, aC, 'NIFTY 50', 'daily close, 2020', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [8000, 10000, 12000, 14000], a=aC)
        xlabels(c, F, [(idx(d, f'2020-{m:02d}-01'), lab) for m, lab in ((1, 'Jan'), (4, 'Apr'), (7, 'Jul'), (10, 'Oct'))], aC)
        series(c, F, range(n + 1), d['c'][:n + 1], P(t, b[5], 2.0, eio), NAVY, 4, aC, BLUE, .15)
        il, ia_ = idx(d, '2020-03-24'), idx(d, '2020-08-31')
        g1 = P(t, b[5] + 1.0, .5) * aC
        glow_dot(c, F.X(il), F.Y(7511), 9, GREEN, t, g1)
        tag(c, F.X(il) + 30, F.Y(7511) + 30, 'Price turns: 24 Mar', GREEN, WHITE, 22, g1, 'l')
        g2 = P(t, b[5] + 2.0, .5) * aC
        glow_dot(c, F.X(ia_), F.Y(d['c'][ia_]), 9, RED, t, g2)
        tag(c, F.X(ia_), F.Y(d['c'][ia_]) - 90, 'GDP -23.9% reported: 31 Aug', RED, WHITE, 22, g2, 'c', point=(F.X(ia_), F.Y(d['c'][ia_]) - 12))
        g3 = P(t, b[5] + 3.0, .6) * aC
        card(c, 1440, 380, 340, 330, 24, NAVY, g3)
        text(c, 'The chart moved', 1610, 470, 30, 'bold', WHITE, 'c', g3)
        text(c, '5 months', 1610, 560, 64, 'head', GOLD, 'c', g3)
        text(c, 'before the data', 1610, 620, 30, 'bold', WHITE, 'c', g3)
    aD = P(t, b[6], .5)
    if aD > 0:
        crowd(c, t, 330, 470, 4, .75, ['happy', 'worried', 'smile', 'shock'], aD, 140)
        text(c, 'Bullish and bearish psychology', 540, 720, 28, 'semi', INK, 'c', aD)
        arrow(c, 860, 520, 1020, 520, GOLD, 6, aD, P(t, b[6] + .5, .5))
        with pop(c, t, b[6] + .8, 1350, 520) as a:
            card(c, 1090, 330, 520, 380, 24, CARD, a * aD, border=GOLD, bw=4)
            mini_pattern(c, 'up', 1140, 380, 420, 230, NAVY, P(t, b[6] + 1, 1.2), a * aD, 5)
            text(c, 'The chart is a mirror', 1350, 670, 30, 'bold', NAVY, 'c', a * aD)
        text(c, 'Charts reflect the crowd. They do not move the market.', 960, 830, 30, 'serif', MUTED, 'c', P(t, b[6] + 1.6, .6))

# ------------------------------------------------------------ 1.3 trends
@scene('c1s3')
def c1s3(c, t, b):
    a1 = stage(t, b, 0, 2)
    if a1 > 0:
        pts = pattern_pts('up', 260, 330, 1100, 460)
        polyline(c, pts, NAVY, 6, a1, P(t, .3, 2.5, eio))
        g = P(t, b[1] + .5, .5) * a1
        ring(c, pts[1][0], pts[1][1], 60, GOLD, 5, g, P(t, b[1] + .5, .8))
        tag(c, pts[1][0], pts[1][1] + 80, 'Spot it early', GOLD, WHITE, 26, g, 'c')
        arrow(c, pts[2][0] + 40, pts[2][1] - 140, pts[5][0] - 40, pts[5][1] - 140, GREEN, 7, P(t, b[1] + 1.4, .5) * a1, P(t, b[1] + 1.4, 1.2), 24)
        tag(c, 1560, 400, 'Trade with the trend', GREEN, WHITE, 26, P(t, b[1] + 2, .5) * a1, 'c')
    a2 = stage(t, b, 2, 3)
    if a2 > 0:
        with pop(c, t, b[2], 960, 560) as a:
            card(c, 260, 400, 1400, 300, 30, NAVY, a * a2)
            text(c, 'A trend in motion is more likely', 960, 530, 56, 'serif', WHITE, 'c', a * a2)
            text(c, 'to continue than to reverse.', 960, 610, 56, 'serif', LGOLD, 'c', a * a2)
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        text(c, "Newton's first law of motion", 960, 320, 36, 'bold', NAVY, 'c', a3)
        line(c, 200, 640, 1720, 640, LINE, 6, a3)
        u = P(t, b[3] + .3, b.d[3] * .75, lambda x: x)
        bx = lerp(260, 1420, u)
        for k in range(4): line(c, bx - 60 - k * 28, 560 + k * 18, bx - 110 - k * 28, 560 + k * 18, FAINT, 4, a3 * .7)
        circle(c, bx, 590, 50, GOLD, a3); ring(c, bx, 590, 50, mix(GOLD, (0, 0, 0), .2), 4, a3)
        line(c, bx, 590, bx + math.cos(u * 30) * 40, 590 + math.sin(u * 30) * 40, WHITE, 4, a3)
        text(c, 'keeps moving...', 700, 720, 30, 'serif', MUTED, 'c', a3 * P(t, b[3] + 1, .5))
        fa = P(t, b[3] + b.d[3] * .6, .5) * a3
        c.rectangle(1500, 470, 40, 170); col(c, RED, fa); c.fill()
        text(c, '...until a force acts', 1520, 440, 30, 'serif', RED, 'c', fa)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        d = nifty_m(); n = len(d['c'])
        F = Frame(200, 320, 1380, 470, 0, n - 1, 250, 30000, log=True)
        chart_card(c, F, a4, 'NIFTY 50', 'monthly, log scale, 1990 to 2026', 'Data: TradingView · NSE:NIFTY')
        ygrid(c, F, [300, 1000, 3000, 10000, 30000], a=a4)
        xlabels(c, F, [(idx(d, f'{y}-01-01'), str(y)) for y in (1991, 2000, 2010, 2020)], a4)
        pr = P(t, b[4] + .2, b.d[4] * .8, eio)
        series(c, F, range(n), d['c'], pr, NAVY, 3.5, a4, BLUE, .15)
        yr = d['date'][min(n - 1, int(pr * (n - 1)))].year
        text(c, str(yr), F.x + F.w - 16, F.y + 56, 52, 'head', GOLD, 'r', a4)
        for ds, lab, hi_ds in (('2008-10-01', '2008: -65%', '2008-01-01'), ('2020-03-02', '2020: -40%', '2020-01-01')):
            i = idx(d, ds)
            ta = P(t, b[4] + .2 + b.d[4] * .8 * i / n, .4) * a4
            tag(c, F.X(i), F.Y(d['l'][i]) + 26, lab, RED, WHITE, 20, ta, 'c')
        arrow(c, F.X(5), F.Y(500), F.X(n - 8), F.Y(22000), GREEN, 8, P(t, b[4] + b.d[4] * .85, .5) * a4 * .7, P(t, b[4] + b.d[4] * .85, .8), 28, dash=[18, 12])
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        with pop(c, t, b[5], 560, 580) as a:
            label_card(c, 220, 400, 680, 360, 'Predict tops & bottoms', 'Guessing where a trend will end', a * a5, RED, 36, 28, LRED)
            badge(c, 820, 450, 30, 'no', a * a5)
            mini_pattern(c, 'hs', 290, 560, 540, 160, RED, 1, a * a5 * .6, 4)
            for qx in (430, 650): text(c, '?', qx, 590, 48, 'head', RED, 'c', a * a5)
        with pop(c, t, b[5] + b.d[5] * .4, 1360, 580) as a:
            label_card(c, 1020, 400, 680, 360, 'Find the trend & stay with it', 'Until the evidence says it changed', a * a5, GREEN, 36, 28, LGREEN)
            badge(c, 1620, 450, 30, 'ok', a * a5)
            mini_pattern(c, 'up', 1090, 560, 540, 160, GREEN, P(t, b[5] + b.d[5] * .4, 1.2), a * a5, 5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        with pop(c, t, b[6], 640, 580) as a:
            bubble(c, 180, 470, 660, 170, '"What will happen?"', a * a6, 46, 'serif', MUTED, CARD, 'bl')
            line(c, 230, 555, 230 + 560 * P(t, b[6] + .9, .5), 555, RED, 6, a * a6)
        with pop(c, t, b[6] + 1.2, 1300, 600) as a:
            bubble(c, 920, 470, 820, 170, '"What is the trend right now?"', a * a6, 46, 'serif', WHITE, NAVY, 'br')

# ------------------------------------------------------------ 1.4 history repeats
@scene('c1s4')
def c1s4(c, t, b):
    a1 = stage(t, b, 1, 2)
    if a1 > 0:
        v = .5 + .48 * math.sin((t - b[1]) * 1.3)
        speedometer(c, 960, 520, 190, v, a1)
        text(c, 'FEAR', 790, 560, 28, 'head', RED, 'c', a1); text(c, 'GREED', 1130, 560, 28, 'head', GREEN, 'c', a1)
        moods = ['worried' if v < .5 else 'happy'] * 6
        crowd(c, t, 410, 730, 6, .55, moods, a1, 220)
    a2 = stage(t, b, 2, 4)
    kinds = [('hs', 'Head & shoulders'), ('dtop', 'Double top'), ('tri', 'Triangle'), ('flag', 'Flag')]
    if a2 > 0:
        for i, (k, lab) in enumerate(kinds):
            x = 170 + i * 405
            with pop(c, t, b[2] + .3 + i * .4, x + 180, 540) as a:
                mini_chart_card(c, x, 390, 360, 300, k, a * a2, NAVY, lab, P(t, b[2] + .5 + i * .4, 1.0))
            mood = 'Bearish mood' if k in ('hs', 'dtop') else 'Bullish mood'
            ma = P(t, b[3] + i * .35, .4) * a2
            pill(c, x + 180, 720, mood, 24, RED if 'Bear' in mood else GREEN, WHITE, ma, 'semi', 'c', ls=1)
        text(c, 'Catalogued over the past century', 960, 850, 32, 'serif', MUTED, 'c', a2 * P(t, b[2] + 2.2, .6))
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        with pop(c, t, b[4], 520, 560) as a:
            crowd(c, t, 340, 520, 3, .8, ['worried', 'happy', 'shock'], a * a4, 180)
            text(c, 'Human nature', 520, 760, 34, 'bold', NAVY, 'c', a * a4)
        text(c, '=', 960, 590, 110, 'head', GOLD, 'c', P(t, b[4] + .8, .4) * a4)
        with pop(c, t, b[4] + 1.2, 1400, 560) as a:
            mini_chart_card(c, 1200, 400, 400, 300, 'hs', a * a4, NAVY, None, 1)
            text(c, 'Same patterns', 1400, 760, 34, 'bold', NAVY, 'c', a * a4)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        with pop(c, t, b[5], 960, 560) as a:
            card(c, 260, 400, 1400, 300, 30, NAVY, a * a5)
            text(c, 'PREMISE 3 IN ONE LINE', 960, 470, 22, 'semi', GOLD, 'c', a * a5, ls=5)
            text(c, 'The key to understanding the future', 960, 560, 52, 'serif', WHITE, 'c', a * a5)
            text(c, 'lies in a study of the past.', 960, 630, 52, 'serif', LGOLD, 'c', a * a5)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for i, (lab, cl) in enumerate([('Stocks', NAVY), ('Commodities', GOLD), ('Crypto', ORANGE)]):
            x = 210 + i * 520
            with pop(c, t, b[6] + i * .4, x + 230, 560) as a:
                card(c, x, 360, 460, 380, 24, CARD, a * a6)
                text(c, lab, x + 230, 420, 32, 'bold', cl, 'c', a * a6)
                mini_pattern(c, 'hs', x + 40, 450, 380, 220, cl, P(t, b[6] + .3 + i * .4, 1.0), a * a6, 5)
        text(c, 'Different markets. Same emotions. Same shapes.', 960, 820, 34, 'serif', INK, 'c', P(t, b[6] + 1.6, .6))

# ------------------------------------------------------------ 1.5 technical vs fundamental
@scene('c1s5')
def c1s5(c, t, b):
    aA = 1 - P(t, b[4] - .25, .4)
    if aA > 0:
        with pop(c, t, .3, 330, 470) as a:
            avatar(c, 330, 430, 1.15, SKIN[2], HAIR[2], NAVY, 'short', tie=GOLD, glasses=True, t=t, a=a * aA)
            text(c, 'Fundamental analyst', 330, 640, 28, 'bold', INK, 'c', a * aA)
        with pop(c, t, .6, 1590, 470) as a:
            avatar(c, 1590, 430, 1.15, SKIN[3], HAIR[4], GREEN, 'long', t=t, seed=3, a=a * aA)
            text(c, 'Technical analyst', 1590, 640, 28, 'bold', INK, 'c', a * aA)
        qa = P(t, b[1], .5) * aA
        with pop(c, t, b[1], 960, 400) as a:
            circle(c, 960, 400, 86, GOLD, a * aA); text(c, '?', 960, 440, 110, 'head', WHITE, 'c', a * aA)
        text(c, 'Which way will prices move?', 960, 540, 32, 'serif', INK, 'c', qa)
        ca = P(t, b[2], .5) * aA
        if ca > 0:
            for i, (lab, kind) in enumerate([('Earnings', 'doc'), ('Economy', 'fac'), ('Supply & demand', 'bal')]):
                x = 175 + i * 165
                with pop(c, t, b[2] + .3 + i * .3, x, 760) as a:
                    if kind == 'doc': doc(c, x, 750, .7, a * aA, title='EPS')
                    elif kind == 'fac': factory(c, x, 760, .8, t, a * aA)
                    else: coin(c, x, 750, 40, '$', GOLD, a * aA)
                    text(c, lab, x, 830, 20, 'semi', MUTED, 'c', a * aA)
            pill(c, 330, 860, 'STUDIES THE CAUSE  ·  WHY?', 22, NAVY, WHITE, ca, 'semi', 'c', ls=2)
        ea = P(t, b[3], .5) * aA
        if ea > 0:
            with pop(c, t, b[3] + .2, 1590, 760) as a:
                chart_icon(c, 1590, 760, 1.2, a * aA)
            pill(c, 1590, 860, 'STUDIES THE EFFECT  ·  WHAT?', 22, GREEN, WHITE, ea, 'semi', 'c', ls=2)
            arrow(c, 720, 760, 1200, 760, GOLD, 6, ea, P(t, b[3] + .5, .8), 22)
            text(c, 'CAUSE  →  EFFECT', 960, 730, 24, 'semi', MUTED, 'c', ea, ls=3)
    aB = stage(t, b, 4, 6)
    if aB > 0:
        F = Frame(240, 330, 1300, 440, 0, 100, 0, 100)
        card(c, 200, 290, 1520, 560, 24, CARD, aB)
        xs = list(range(101)); ys = [15 + 70 / (1 + math.exp(-(x - 45) / 9)) + 3 * math.sin(x * .7) for x in xs]
        series(c, F, xs, ys, P(t, b[4] + .2, 2.4, eio), NAVY, 5, aB, BLUE, .15)
        g1 = P(t, b[4] + 1.0, .5) * aB
        glow_dot(c, F.X(22), F.Y(ys[22]), 10, GREEN, t, g1)
        tag(c, F.X(22), F.Y(ys[22]) - 100, 'Price starts moving', GREEN, WHITE, 24, g1, 'c', point=(F.X(22), F.Y(ys[22]) - 14))
        g2 = P(t, b[4] + 2.6, .5) * aB
        zone(c, F, 22, 78, 0, 100, GOLD, .10 * g2)
        glow_dot(c, F.X(78), F.Y(ys[78]), 10, RED, t, g2)
        tag(c, F.X(78), F.Y(ys[78]) + 40, 'Fundamentals become clear', RED, WHITE, 24, g2, 'c')
        text(c, 'Much of the move has already happened', F.X(50), F.y + F.h - 30, 28, 'serif', GOLD, 'c', g2)
        g3 = P(t, b[5], .5) * aB
        pill(c, F.X(22) - 40, 790, 'Technicians act here', 24, NAVY, WHITE, g3, 'semi', 'l', ls=1)
    aC = P(t, b[6], .5)
    if aC > 0:
        circle(c, 810, 560, 240, BLUE, aC * .18); ring(c, 810, 560, 240, BLUE, 4, aC)
        circle(c, 1110, 560, 240, GREEN, aC * .18); ring(c, 1110, 560, 240, GREEN, 4, aC)
        text(c, 'Fundamental', 690, 570, 32, 'bold', BLUE, 'c', aC)
        text(c, 'Technical', 1230, 570, 32, 'bold', GREEN, 'c', aC)
        text(c, 'Most', 960, 548, 28, 'bold', INK, 'c', P(t, b[6] + .6, .5)); text(c, 'traders', 960, 584, 28, 'bold', INK, 'c', P(t, b[6] + .6, .5))
        va = P(t, b[6] + b.d[6] * .5, .5)
        pill(c, 960, 830, 'When they disagree, trust the chart: that is where money votes', 26, NAVY, WHITE, va, 'semi', 'c', ls=0)

# ------------------------------------------------------------ 1.6 timing & flexibility
@scene('c1s6')
def c1s6(c, t, b):
    a1 = stage(t, b, 1, 3)
    if a1 > 0:
        with pop(c, t, b[1], 520, 560) as a:
            label_card(c, 200, 380, 640, 330, 'WHAT to buy', 'Fundamental analysis', a * a1, BLUE, 44, 28)
            doc(c, 700, 600, 1, a * a1, title='VALUE')
        with pop(c, t, b[1] + b.d[1] * .4, 1400, 560) as a:
            label_card(c, 1080, 380, 640, 330, 'WHEN to buy & sell', 'Technical analysis', a * a1, GREEN, 44, 28, LGREEN)
            clock(c, 1600, 600, 70, t * 3, a * a1)
        la = P(t, b[2], .5) * a1
        if la > 0:
            F = Frame(240, 760, 1440, 130, 0, 40, 0, 100)
            ys = [55 - 30 * math.sin(i / 40 * math.pi * 1.2) * (1 if i < 14 else 0) + (i - 14) * 2.6 * (i >= 14) for i in range(41)]
            ys = [55 - (i * 2.4 if i < 12 else 28 - (i - 12) * 3.6) for i in range(41)]
            series(c, F, range(41), ys, P(t, b[2], 2), NAVY, 4, la)
            glow_dot(c, F.X(2), F.Y(ys[2]), 8, RED, t, la)
            tag(c, F.X(2) + 20, F.Y(ys[2]) - 46, 'Right direction, entered too early: stopped out', RED, WHITE, 20, P(t, b[2] + 1.2, .5) * a1, 'l')
    a3 = stage(t, b, 3, 4)
    if a3 > 0:
        mk = [('Stocks', 'chart'), ('Bonds', 'doc'), ('Currencies', 'fx'), ('Commodities', 'gold'), ('Crypto', 'btc')]
        for i, (lab, k) in enumerate(mk):
            x = 260 + i * 350
            with pop(c, t, b[3] + .3 + i * .3, x, 540) as a:
                card(c, x - 140, 400, 280, 300, 24, CARD, a * a3)
                if k == 'chart': chart_icon(c, x, 520, 1.1, a * a3)
                elif k == 'doc': doc(c, x, 520, .9, a * a3, title='BOND')
                elif k == 'fx': coin(c, x - 30, 520, 44, '₹', GREEN, a * a3); coin(c, x + 30, 530, 44, '$', BLUE, a * a3)
                elif k == 'gold':
                    c.new_path(); c.move_to(x - 70, 560); c.line_to(x - 46, 490); c.line_to(x + 46, 490); c.line_to(x + 70, 560); c.close_path(); col(c, GOLD, a * a3); c.fill()
                else: btc(c, x, 520, 52, a * a3, t * .8)
                text(c, lab, x, 650, 28, 'bold', INK, 'c', a * a3)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        for i, (lab, seed) in enumerate([('5-minute', 3), ('Daily', 5), ('Monthly', 9)]):
            x = 200 + i * 540
            with pop(c, t, b[4] + .2 + i * .4, x + 240, 560) as a:
                card(c, x, 360, 480, 380, 24, CARD, a * a4)
                O, Hh, L, C = path_ohlc([(0, 20), (.3, 55), (.45, 42), (.8, 85), (1, 78)], 26, seed, .03, .02)
                F = Frame(x + 40, 400, 400, 250, -1, 26, 0, 100)
                candles(c, F, O, Hh, L, C, 26 * P(t, b[4] + .3 + i * .4, 1.2), a=a * a4)
                text(c, lab, x + 240, 710, 30, 'bold', NAVY, 'c', a * a4)
        text(c, 'The same principles on every time frame', 960, 830, 32, 'serif', MUTED, 'c', P(t, b[4] + 1.8, .5) * a4)
    a5 = stage(t, b, 5, 6)
    if a5 > 0:
        rnd = random.Random(4)
        for k in range(18):
            r, cc = divmod(k, 6)
            x, y = 200 + cc * 260, 330 + r * 190
            trend = k in (1, 4, 8, 11, 15)
            hl = P(t, b[5] + b.d[5] * .5, .5) if trend else 0
            with pop(c, t, b[5] + k * .06, x + 115, y + 80) as a:
                card(c, x, y, 230, 160, 16, CARD, a * a5 * (1 - .55 * P(t, b[5] + b.d[5] * .5, .5) * (not trend)), border=GREEN if hl > .3 else None, bw=4)
                kind = rnd.choice(['up', 'down']) if trend else 'side'
                mini_pattern(c, kind, x + 20, y + 20, 190, 110, GREEN if trend and hl > .3 else NAVY, 1, a * a5, 3)
    a6 = P(t, b[6], .5)
    if a6 > 0:
        for k, (d, name, cl, pct) in enumerate([(nifty_w(), 'NIFTY 50', NAVY, .07), (btc_w(), 'BITCOIN', ORANGE, .12)]):
            n = len(d['c'])
            lo, hi = min(d['l']), max(d['h'])
            F = Frame(170 + k * 830, 360, 680, 400, 0, n - 1, lo * .92, hi * 1.06)
            with pop(c, t, b[6] + k * .4, F.x + 340, 560) as a:
                if a <= 0: continue
                chart_card(c, F, a * a6, name, 'weekly', 'Data: TradingView')
                series(c, F, range(n), d['c'], P(t, b[6] + .2 + k * .4, 1.6, eio), cl, 3, a * a6)
                pv = pivots(d['h'], d['l'], pct)
                for j, (i, p, kind) in enumerate(pv):
                    pa = P(t, b[6] + 1.8 + j * .08, .3) * a * a6
                    circle(c, F.X(i), F.Y(p), 7, GREEN if kind == 'L' else RED, pa)
        text(c, 'Peaks, troughs and trends, in any market', 960, 890, 28, 'serif', MUTED, 'c', P(t, b[6] + 2.4, .5))

# ------------------------------------------------------------ 1.7 criticisms
@scene('c1s7')
def c1s7(c, t, b):
    cur = 0 if t < b[4] else 1 if t < b[5] else 2
    sa = P(t, b[1], .5)
    steps(c, ['Self-fulfilling', 'Past data', 'Random walk'], cur, 1800, 196, sa * (1 - P(t, b[7] - .3, .4)))
    a1 = stage(t, b, 1, 4)
    if a1 > 0:
        with pop(c, t, b[1], 470, 360) as a:
            card(c, 160, 270, 620, 150, 22, LRED, a * a1)
            text(c, 'CRITICISM 1', 200, 318, 20, 'semi', RED, 'l', a * a1, ls=4)
            text(c, '"It\'s a self-fulfilling prophecy"', 200, 378, 34, 'serif', INK, 'l', a * a1)
        crowd(c, t, 250, 560, 4, .62, ['smile'] * 4, P(t, b[1] + 1, .5) * a1 * (1 - P(t, b[2] - .2, .4)), 120)
        mini_chart_card(c, 260, 700, 380, 160, 'up', P(t, b[1] + 1, .5) * a1 * (1 - P(t, b[2] - .2, .4)))
        a2 = P(t, b[2], .5) * a1
        if a2 > 0:
            avatar(c, 1050, 600, 1.0, SKIN[1], HAIR[0], BLUE, 'short', t=t, a=a2)
            avatar(c, 1530, 600, 1.0, SKIN[3], HAIR[1], GOLD, 'long', t=t, seed=2, a=a2)
            bubble(c, 890, 400, 300, 90, 'Buy now!', a2, 34, 'bold', GREEN, CARD, 'bl')
            bubble(c, 1380, 400, 300, 90, 'Wait...', a2, 34, 'bold', RED, CARD, 'br')
            text(c, 'Chart reading is subjective: closer to an art', 1290, 830, 30, 'serif', INK, 'c', P(t, b[2] + 1, .5) * a1)
        a3 = P(t, b[3], .5) * a1
        if a3 > 0:
            card(c, 160, 460, 620, 420, 24, CARD, a3)
            F = Frame(200, 520, 540, 300, 0, 30, 0, 100)
            ys = [30 + (i * .4 if i < 12 else 4.8 + (i - 12) * 4.5 if i < 15 else 18 + 55 - (i - 15) * 2) for i in range(31)]
            series(c, F, range(31), ys, P(t, b[3], 1.4), NAVY, 4, a3)
            glow_dot(c, F.X(13), F.Y(ys[13]), 8, GOLD, t, P(t, b[3] + .8, .4) * a3)
            tag(c, F.X(13), F.Y(ys[13]) - 230, 'Everyone acts at once', GOLD, WHITE, 22, P(t, b[3] + .9, .4) * a3, 'c')
            text(c, 'The market jumps ahead, the signal fails', 470, 860, 24, 'serif', RED, 'c', P(t, b[3] + 1.6, .5) * a3)
    a4 = stage(t, b, 4, 5)
    if a4 > 0:
        with pop(c, t, b[4], 960, 350) as a:
            card(c, 460, 270, 1000, 150, 22, LRED, a * a4)
            text(c, 'CRITICISM 2', 960, 318, 20, 'semi', RED, 'c', a * a4, ls=4)
            text(c, '"The past can\'t predict the future"', 960, 378, 34, 'serif', INK, 'c', a * a4)
        with pop(c, t, b[4] + .8, 330, 640) as a:
            calendar(c, 330, 620, 1.3, a * a4, 'Past data')
        for i, (lab, k) in enumerate([('Weather forecasts', 'cloud'), ('Economic forecasts', 'chart'), ('Fundamental analysis', 'doc')]):
            y = 520 + i * 130
            with pop(c, t, b[4] + 1.4 + i * .4, 1300, y) as a:
                if k == 'cloud': cloud(c, 1000, y, 1.0, a * a4, LBLUE)
                elif k == 'chart': chart_icon(c, 1000, y, .7, a * a4)
                else: doc(c, 1000, y, .55, a * a4)
                text(c, lab, 1070, y + 12, 32, 'bold', INK, 'l', a * a4)
            arrow(c, 450, 620, 920, y, GOLD, 4, a4, P(t, b[4] + 1.2 + i * .4, .5), 16)
    a5 = P(t, b[5], .5) * (1 - P(t, b[7] - .3, .4))
    if a5 > 0:
        with pop(c, t, b[5], 960, 350) as a:
            card(c, 460, 270, 1000, 150, 22, LRED, a * a5)
            text(c, 'CRITICISM 3', 960, 318, 20, 'semi', RED, 'c', a * a5, ls=4)
            text(c, '"Prices are a random walk"', 960, 378, 34, 'serif', INK, 'c', a * a5)
        rnd = random.Random(7); v = 50; noise = []
        for i in range(160): v += rnd.gauss(0, 2.2); noise.append(v)
        F1 = Frame(200, 480, 700, 330, 0, 159, min(noise) - 5, max(noise) + 5)
        card(c, 160, 450, 780, 420, 24, CARD, a5)
        series(c, F1, range(160), noise, P(t, b[5] + .5, 2), MUTED, 3, a5)
        text(c, 'Short term: plenty of noise', 550, 850, 26, 'semi', MUTED, 'c', a5)
        a6 = P(t, b[6], .5) * a5
        if a6 > 0:
            card(c, 980, 450, 780, 420, 24, CARD, a6)
            rnd2 = random.Random(3); v = 20; ys = []
            for i in range(160): v += .55 + rnd2.gauss(0, 2.2); ys.append(v)
            F2 = Frame(1020, 480, 700, 330, 0, 159, min(ys) - 5, max(ys) + 5)
            series(c, F2, range(160), ys, P(t, b[6], 2), NAVY, 3, a6)
            seg(c, F2, 0, ys[0] - 4, 159, ys[-1] - 4, GREEN, 6, a6, P(t, b[6] + 1.5, 1), dash=[16, 10])
            text(c, 'Longer term: clear trends', 1370, 850, 26, 'semi', GREEN, 'c', a6)
    a7 = P(t, b[7], .5)
    if a7 > 0:
        (lx, ly), (rx, ry) = scale_balance(c, 960, 560, 1.6, lerp(.0, .5, P(t, b[7] + .5, 1, eio)), a7, None, None)
        text(c, 'Not perfect', lx, ly + 190, 32, 'bold', MUTED, 'c', a7)
        text(c, 'Sound principles', rx + 40, ry + 190, 32, 'bold', GREEN, 'c', a7)
        badge(c, rx + 40, ry + 240, 22, 'ok', P(t, b[7] + 1.2, .4))
