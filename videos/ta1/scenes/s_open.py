from engine import *
from . import scene
from .data import nifty_d20, nifty_m, btc_m, idx
from script_p1 import LESSONS

# ================================================================== HOOK
@scene('hook')
def hook(c, t, b):
    d = nifty_d20(); C = d['c']; n = len(C)
    i_jan, i_low, i_low_c = idx(d, '2020-01-20'), idx(d, '2020-03-24'), idx(d, '2020-03-23')
    i_aug, i_dbl = idx(d, '2020-08-31'), idx(d, '2021-02-15')
    F = Frame(170, 300, 1020, 500, 0, n - 1, 6500, 16500)
    stA = 1 - P(t, b[5] - .3, .6)
    if stA > 0:
        with alpha_group(c, stA):
            ca = P(t, .15, .6)
            with rise(c, t, .15) as ra:
                chart_card(c, F, ca, title='NIFTY 50', sub='daily close, 2020 to 2021', src='Data: TradingView · NSE:NIFTY')
                ygrid(c, F, [8000, 10000, 12000, 14000, 16000], a=ca)
                xlabels(c, F, [(idx(d, '2020-01-01'), 'Jan 2020'), (idx(d, '2020-04-01'), 'Apr'), (idx(d, '2020-07-01'), 'Jul'),
                               (idx(d, '2020-10-01'), 'Oct'), (idx(d, '2021-01-01'), 'Jan 2021')], ca)
                k = lerp(0, i_low, P(t, .7, b.d[0] * .5, eio))
                if t > b[1]: k = lerp(i_low, i_aug, P(t, b[1], b.d[1] * .85, eio))
                if t > b[3]: k = lerp(i_aug, i_dbl, P(t, b[3], b.d[3] * .8, eio))
                head = series(c, F, range(n), C, p=k / (n - 1), cl=NAVY, lw=4, fill=BLUE, fill_a=.18, a=ca)
                if head and ca > .5: glow_dot(c, head[0], head[1], 7, GOLD, t)
                # Jan high
                ja = P(t, 1.4, .5)
                glow_dot(c, F.X(i_jan), F.Y(12430.5), 6, NAVY, t, ja, False)
                tag(c, F.X(i_jan) + 10, F.Y(12430.5) - 70, 'High 12,430', NAVY, WHITE, 20, ja, 'c', point=(F.X(i_jan), F.Y(12430.5) - 10))
                la = P(t, .7 + b.d[0] * .5, .5)
                if la > 0:
                    glow_dot(c, F.X(i_low), F.Y(7511.1), 8, RED, t, la)
                    tag(c, F.X(i_low) + 120, F.Y(7511.1) + 24, '24 Mar 2020 · low 7,511', RED, WHITE, 20, la, 'c', point=(F.X(i_low) + 6, F.Y(7511.1) + 6))
                    mx = F.X(i_low) + 70
                    measure(c, F.X(i_low) + 70, F.Y(12430.5), F.Y(7511.1), RED, la, P(t, .9 + b.d[0] * .5, .8), '-39.6% in 2 months', 'r')
                aa = P(t, b[2] + b.d[2] * .45, .5)
                if aa > 0:
                    glow_dot(c, F.X(i_aug), F.Y(11387.5), 8, GREEN, t, aa)
                    tag(c, F.X(i_aug), F.Y(11387.5) - 120, '31 Aug 2020 · 11,387', NAVY, WHITE, 20, aa, 'c', point=(F.X(i_aug), F.Y(11387.5) - 12))
                    tag(c, F.X(i_aug), F.Y(11387.5) - 72, '+50% from the low', GREEN, WHITE, 20, P(t, b[2] + b.d[2] * .7, .5), 'c')
                da = P(t, b[3] + b.d[3] * .6, .5)
                if da > 0:
                    glow_dot(c, F.X(i_dbl), F.Y(15314.7), 8, GREEN, t, da)
                    measure(c, F.X(n - 1) + 36, F.Y(7610.25), F.Y(15314.7), GREEN, da, P(t, b[3] + b.d[3] * .6, .9), 'x2', 'l')
                    tag(c, F.X(i_dbl) - 150, F.Y(15314.7) - 30, '15 Feb 2021 · 15,315', GREEN, WHITE, 20, da, 'c')
            # right column: ticker
            ta_ = P(t, .5, .6)
            card(c, 1330, 240, 470, 150, 20, NAVY, ta_)
            kk = int(min(n - 1, max(0, round(k))))
            v = C[kk]
            text(c, 'NIFTY 50', 1362, 290, 22, 'semi', LGOLD, 'l', ta_, ls=3)
            text(c, d['date'][kk].strftime('%d %b %Y'), 1768, 290, 22, 'med', WHITE, 'r', ta_ * .8)
            chg = v / C[0] - 1
            text(c, f'{v:,.0f}', 1362, 362, 64, 'head', WHITE, 'l', ta_)
            pill(c, 1768, 322, f'{chg*100:+.1f}%', 22, GREEN if chg >= 0 else RED, WHITE, ta_, 'semi', 'r', ls=0)
            # newspapers
            na = 1 - P(t, b[4] - .2, .5)
            n1 = P(t, b[0] + b.d[0] * .6, .5)
            with pop(c, t, b[0] + b.d[0] * .6, 1565, 540) as a1:
                if a1: newspaper(c, 1335, 430, 460, 210, 'NATIONAL LOCKDOWN', a1 * na, '24 March 2020 · 21 days', RED, -.025)
            with pop(c, t, b[1] + b.d[1] * .3, 1575, 640) as a2:
                if a2: newspaper(c, 1345, 540, 460, 210, 'GDP  -23.9%', a2 * na, 'Worst quarter on record', RED, .02)
            pa = P(t, b[2] + b.d[2] * .75, .5) * na
            if pa > 0:
                card(c, 1335, 785, 220, 90, 16, LRED, pa); text(c, 'NEWS', 1445, 822, 20, 'semi', RED, 'c', pa, ls=3); text(c, 'Worst ever  ↓', 1445, 856, 24, 'bold', RED, 'c', pa)
                card(c, 1575, 785, 220, 90, 16, LGREEN, pa); text(c, 'PRICE', 1685, 822, 20, 'semi', GREEN, 'c', pa, ls=3); text(c, '+50%  ↑', 1685, 856, 24, 'bold', GREEN, 'c', pa)
            # avatars
            if t > b[4] - .2:
                with pop(c, t, b[4], 1450, 560) as a3:
                    if a3:
                        avatar(c, 1450, 520, 1.0, SKIN[1], HAIR[0], hexc('#7A8794'), 'short', mood='worried', t=t, a=a3)
                        newspaper(c, 1385, 600, 130, 90, 'BAD NEWS', a3, None, RED, -.08)
                        bubble(c, 1335, 410, 230, 70, 'The news said...', a3, 22, tail='bl')
                with pop(c, t, b[4] + b.d[4] * .35, 1690, 560) as a4:
                    if a4:
                        avatar(c, 1690, 520, 1.0, SKIN[0], HAIR[1], BLUE, 'side', glasses=True, mood='smile', t=t, seed=2, a=a4)
                        chart_icon(c, 1690, 650, .8, a4, True)
                        bubble(c, 1585, 410, 220, 70, 'The price said...', a4, 22, tail='br')
                ok = P(t, b[4] + b.d[4] * .7, .5)
                if ok: badge(c, 1760, 470, 26, 'ok', ok)
    # stage B: question
    if b[5] - .3 < t < b[6] + .6:
        qa = P(t, b[5], .6) * (1 - P(t, b[6] - .2, .5))
        with rise(c, t, b[5]) as ra:
            text(c, 'How can a line on a chart', W / 2, 430, 70, 'serif', INK, 'c', qa)
            text(c, 'move before the facts are known?', W / 2, 520, 70, 'serif', INK, 'c', qa)
        q2 = P(t, b[5] + b.d[5] * .55, .6) * (1 - P(t, b[6] - .2, .5))
        text(c, 'And can you learn to read it?', W / 2, 640, 44, 'semi', GOLD, 'c', q2)
        pts = [(760 + i * 40, 780 - 50 * math.sin(i * .7) - i * 6) for i in range(11)]
        polyline(c, pts, NAVY, 5, q2, P(t, b[5] + 1, 2.5))
        magnifier(c, 760 + 400 * P(t, b[5] + 1, 3, eio), 760, 46, q2)
    # stage C: book reveal
    if t > b[6] - .2:
        ba = P(t, b[6], .7)
        with pop(c, t, b[6], 640, 560, .7) as a5:
            if a5: book3d(c, 640, 560, 360, 490, t, a5)
        x0 = 920
        text(c, 'TECHNICAL ANALYSIS', x0, 450, 74, 'head', NAVY, 'l', P(t, b[6] + .3, .6))
        text(c, 'OF THE FINANCIAL MARKETS', x0, 520, 46, 'head', GOLD, 'l', P(t, b[6] + .5, .6))
        text(c, 'John J. Murphy', x0, 590, 40, 'serif', INK, 'l', P(t, b[6] + .7, .6))
        pa = P(t, b[6] + 1.1, .6)
        pill(c, x0, 640, 'PART 1 OF 3  ·  READING THE CHART', 24, RED, WHITE, pa, 'semi', ls=2)

# ================================================================== INTRO
@scene('intro')
def intro(c, t, b):
    header(c, 'INTRODUCTION', 'The Bible of Technical Analysis', 0, 0, P(t, .1, .6))
    stA = 1 - P(t, b[4] - .3, .6)
    if stA > 0:
        with alpha_group(c, stA):
            with pop(c, t, .3, 400, 560, .7) as a:
                if a: book3d(c, 400, 570, 330, 450, t, a)
            # chunk 0: title
            a0 = P(t, .6, .6) * (1 - P(t, b[1] - .2, .5))
            text(c, 'Technical Analysis of the', 700, 460, 58, 'serif', INK, 'l', a0)
            text(c, 'Financial Markets', 700, 535, 58, 'serif', INK, 'l', a0)
            text(c, 'JOHN J. MURPHY', 702, 610, 28, 'semi', GOLD, 'l', a0, ls=5)
            # chunk 1: Murphy, CNBC, editions
            a1 = P(t, b[1], .6) * (1 - P(t, b[2] - .3, .5))
            if a1 > 0:
                with pop(c, t, b[1], 800, 420) as aa:
                    avatar(c, 800, 380, 1.05, SKIN[3], HAIR[3], NAVY, 'side', tie=RED, glasses=True, t=t, a=aa * a1)
                    text(c, 'Market analyst', 800, 560, 24, 'semi', INK, 'c', aa * a1)
                with pop(c, t, b[1] + b.d[1] * .2, 1060, 400) as aa:
                    tv(c, 1060, 390, .9, aa * a1, t)
                    text(c, 'CNBC technical analyst', 1060, 530, 24, 'semi', INK, 'c', aa * a1)
                    text(c, 'for 7 years', 1060, 562, 22, 'med', MUTED, 'c', aa * a1)
                e1 = P(t, b[1] + b.d[1] * .45, .6) * a1
                card(c, 1240, 300, 540, 120, 18, CARD, e1); text(c, '1986', 1270, 352, 34, 'head', MUTED, 'l', e1)
                text(c, 'Technical Analysis of the', 1380, 342, 24, 'serif', INK, 'l', e1); text(c, 'Futures Markets', 1380, 376, 24, 'serif', INK, 'l', e1)
                arrow(c, 1510, 432, 1510, 478, GOLD, 4, e1, P(t, b[1] + b.d[1] * .55, .5))
                e2 = P(t, b[1] + b.d[1] * .6, .6) * a1
                card(c, 1240, 490, 540, 120, 18, LGOLD, e2, border=GOLD); text(c, '1999', 1270, 542, 34, 'head', GOLD, 'l', e2)
                text(c, 'Technical Analysis of the', 1380, 532, 24, 'serif', INK, 'l', e2); text(c, 'Financial Markets', 1380, 566, 24, 'serif', INK, 'l', e2)
                for i, m in enumerate(['Stocks', 'Bonds', 'Currencies', 'Commodities']):
                    with pop(c, t, b[1] + b.d[1] * .72 + i * .18, 790 + i * 250, 700) as aa:
                        pill(c, 790 + i * 250, 680, m, 24, NAVY, WHITE, aa * a1, 'semi', 'c', ls=1)
            # chunk 2: stats
            a2 = P(t, b[2], .5) * (1 - P(t, b[3] - .3, .5))
            if a2 > 0:
                for i, (num, lab, isnum) in enumerate([(500, 'pages and more', True), (19, 'chapters', True), (None, 'what many traders call it', False)]):
                    x = 700 + i * 370
                    with pop(c, t, b[2] + i * .5, x + 165, 520) as aa:
                        card(c, x, 360, 330, 320, 24, CARD, aa * a2)
                        if isnum: counter(c, t, b[2] + i * .5, 1.2, 0, num, x + 165, 520, 110, (lambda v, q=num: f'{v:,.0f}' + ('+' if q == 500 else '')), 'head', NAVY, 'c', aa * a2)
                        else:
                            text(c, '"The bible', x + 165, 480, 44, 'serif', NAVY, 'c', aa * a2); text(c, 'of technical', x + 165, 530, 44, 'serif', NAVY, 'c', aa * a2); text(c, 'analysis"', x + 165, 580, 44, 'serif', NAVY, 'c', aa * a2)
                        text(c, lab, x + 165, 630, 24, 'med', MUTED, 'c', aa * a2)
            # chunk 3: scoreboard
            a3 = P(t, b[3], .5)
            if a3 > 0:
                labels = [('Fear', RED), ('Hope', GREEN), ('News', BLUE), ('Opinions', GOLD), ('Rumours', MUTED)]
                for i, (lab, cl) in enumerate(labels):
                    y = 330 + i * 92
                    with pop(c, t, b[3] + i * .2, 790, y + 30) as aa:
                        pill(c, 700, y, lab, 26, cl, WHITE, aa * a3, 'semi', ls=1)
                    for k in range(3):
                        ph = ((t * .5 + i * .23 + k / 3) % 1)
                        circle(c, lerp(900, 1250, ph), lerp(y + 25, 520, ph), 6, cl, a3 * P(t, b[3] + 1, .5) * (1 - ph) * .9)
                card(c, 1270, 380, 500, 290, 24, NAVY, a3)
                text(c, 'THE SCOREBOARD', 1520, 430, 22, 'semi', LGOLD, 'c', a3, ls=4)
                v = 24000 + 900 * math.sin(t * .9) + 400 * math.sin(t * 2.3)
                text(c, f'{v:,.0f}', 1520, 525, 84, 'head', WHITE, 'c', a3)
                text(c, 'PRICE', 1520, 570, 22, 'semi', LGOLD, 'c', a3, ls=4)
                pts = [(1320 + i * 20, 640 - 30 * (.5 + .5 * math.sin(i * .5 + t * 2))) for i in range(21)]
                polyline(c, pts, GOLD, 3, a3)
                g = P(t, b[3] + b.d[3] * .62, .5)
                if g > 0:
                    pill(c, 1270, 720, 'Guessing', 26, LINE, MUTED, g, 'semi', ls=1)
                    line(c, 1270, 745, 1270 + 160 * P(t, b[3] + b.d[3] * .7, .4), 745, RED, 4, g)
                    arrow(c, 1450, 744, 1530, 744, GOLD, 4, g, P(t, b[3] + b.d[3] * .72, .4))
                    pill(c, 1550, 720, 'Probabilities', 26, GOLD, WHITE, P(t, b[3] + b.d[3] * .78, .4), 'semi', ls=1)
    # stage B: three parts
    stB = P(t, b[4], .6) * (1 - P(t, b[8] - .3, .5))
    if stB > 0:
        parts = [('PART 1', 'Reading the Chart', ['Philosophy & Dow Theory', 'Chart construction', 'Trend, support & resistance', 'Trendlines & channels', 'Reversal patterns', 'Continuation patterns', 'Volume & open interest', 'Long-term charts']),
                 ('PART 2', 'Indicators & Other Lenses', ['Moving averages', 'Oscillators: RSI, MACD', 'Stochastics', 'Contrary opinion', 'Point & figure', 'Candlesticks', 'Advanced indicators']),
                 ('PART 3', 'Waves, Systems & Discipline', ['Elliott Wave & Fibonacci', 'Time cycles', 'Trading systems', 'Money management', 'Intermarket analysis', 'Stock market breadth', "Murphy's checklist"])]
        for i, (p, ttl, items) in enumerate(parts):
            x = 150 + i * 545; hi = P(t, b[5 + i], .5) * (1 - (P(t, b[6 + i] - .2, .5) if i < 2 else 0))
            with pop(c, t, b[4] + .3 + i * .25, x + 255, 560) as aa:
                if aa:
                    with xf(c, x + 255, 560, 1 + .03 * hi):
                        card(c, x, 270, 510, 600, 26, CARD, aa * stB, border=GOLD if hi > .05 else None, bw=3)
                        text(c, p, x + 40, 330, 24, 'semi', GOLD, 'l', aa * stB, ls=4)
                        if i == 0: pill(c, x + 470, 302, 'THIS VIDEO', 18, RED, WHITE, aa * stB, 'semi', 'r', ls=2)
                        text(c, ttl, x + 40, 385, fit_size(c, ttl, 'head', 36, 440), 'head', NAVY, 'l', aa * stB)
                        line(c, x + 40, 410, x + 140, 410, GOLD, 4, aa * stB)
                        for j, it in enumerate(items):
                            ia = aa * stB * (.45 + .55 * P(t, b[5 + i] + j * .25, .4))
                            circle(c, x + 50, 456 + j * 50, 6, GOLD if hi > .05 else FAINT, ia)
                            text(c, it, x + 70, 464 + j * 50, 25, 'med', INK, 'l', ia)
    # stage C: markets + disclaimer + open book
    stC = P(t, b[8], .6)
    if stC > 0:
        nm, bm = nifty_m(), btc_m()
        fade_c = 1 - P(t, b[10] - .1, .5)
        for k, (d, name, sub, cl) in enumerate([(nm, 'NIFTY 50', 'monthly, log scale, 1990 to 2026', NAVY), (bm, 'BITCOIN', 'monthly, log scale, 2011 to 2026', ORANGE)]):
            F = Frame(200 + k * 820, 360, 640, 360, 0, len(d['c']) - 1, min(d['l']) * .9, max(d['h']) * 1.1, log=True)
            with pop(c, t, b[8] + k * .4, F.x + 320, 540) as aa:
                if aa:
                    chart_card(c, F, aa * stC * fade_c, title=name, sub=sub, src='Data: TradingView')
                    series(c, F, range(len(d['c'])), d['c'], P(t, b[8] + .3 + k * .4, 2.2, eio), cl, 3, aa * stC * fade_c, fill=cl, fill_a=.12)
        da = P(t, b[9], .5) * fade_c
        if da > 0:
            card(c, 560, 800, 800, 100, 20, LGOLD, da, border=GOLD)
            text(c, 'Educational summary in my own words', 960, 842, 28, 'semi', INK, 'c', da)
            text(c, 'Not financial advice', 960, 878, 24, 'med', MUTED, 'c', da)
        oa = P(t, b[10], .6)
        if oa > 0:
            s = lerp(.7, 1.0, P(t, b[10], 1.4, eio))
            with xf(c, W / 2, 540, s):
                book3d(c, W / 2, 540, 330, 450, t, oa)
            text(c, "Let's open the book", W / 2, 860, 34, 'serif', NAVY, 'c', P(t, b[10] + .5, .6))

# ================================================================== RECAP
@scene('recap')
def recap(c, t, b):
    header(c, 'RECAP', 'The 10 Biggest Lessons from Part 1', 0, 0, P(t, .1, .6))
    for i, (ttl, sub) in enumerate(LESSONS):
        col_, row = divmod(i, 5)
        x, y = 120 + col_ * 850, 250 + row * 132
        t0 = b[i + 1]
        with pop(c, t, t0, x + 400, y + 58, .5) as a:
            if a:
                active = 1 - P(t, b[i + 2] if i + 2 < b.n else b.end, .6) if i < 9 else 1
                card(c, x, y, 830, 116, 20, CARD, a, border=GOLD if active > .5 else None, bw=3)
                circle(c, x + 64, y + 58, 36, GOLD if active > .5 else NAVY, a)
                text(c, str(i + 1), x + 64, y + 72, 38, 'head', WHITE, 'c', a)
                text(c, ttl, x + 124, y + 52, 32, 'bold', INK, 'l', a)
                text(c, sub, x + 124, y + 90, 25, 'serif', MUTED, 'l', a)
                check(c, x + 780, y + 58, 1.1, GREEN, a, P(t, t0 + .4, .5))

# ================================================================== OUTRO
@scene('outro')
def outro(c, t, b):
    with pop(c, t, .2, 400, 520, .7) as a:
        if a: book3d(c, 400, 520, 340, 470, t, a)
    a0 = P(t, .4, .6)
    text(c, 'Part 1 complete', 760, 300, 30, 'semi', GOLD, 'l', a0, ls=3)
    text(c, 'You can now read the chart:', 760, 370, 52, 'head', NAVY, 'l', a0)
    for i, w_ in enumerate(['Trends', 'Levels', 'Patterns', 'Volume']):
        with pop(c, t, .8 + i * .25, 830 + i * 230, 440) as aa:
            pill(c, 760 + i * 230, 412, w_, 28, NAVY, WHITE, aa * (1 - P(t, b[1] - .3, .4)), 'semi', ls=1)
    a1 = P(t, b[1], .5) * (1 - P(t, b[3] - .3, .4))
    if a1 > 0:
        text(c, 'NEXT  ·  PART 2', 760, 520, 26, 'semi', RED, 'l', a1, ls=4)
        for i, w_ in enumerate(['Moving averages', 'RSI & MACD', 'Contrary opinion', 'Candlesticks', 'Point & figure']):
            with pop(c, t, b[1] + .3 + i * .25, 900 + (i % 3) * 300, 580 + (i // 3) * 74) as aa:
                card(c, 760 + (i % 3) * 330, 548 + (i // 3) * 82, 310, 62, 31, CARD, aa * a1, border=GOLD)
                text(c, w_, 760 + (i % 3) * 330 + 155, 588 + (i // 3) * 82, 25, 'semi', INK, 'c', aa * a1)
    a2 = P(t, b[2], .5) * (1 - P(t, b[3] - .3, .4))
    if a2 > 0:
        pill(c, 230, 790, 'GET THE BOOK', 26, GOLD, WHITE, a2, 'semi', ls=3)
    a3 = P(t, b[3], .5) * (1 - P(t, b[4] - .3, .4))
    if a3 > 0:
        with pop(c, t, b[3], 1200, 560) as aa:
            bubble(c, 760, 470, 980, 190, 'Which idea surprised you most, and which will you try first on a real chart?', aa * a3, 34, 'serif', INK, CARD, 'bl', GOLD)
        text(c, 'Tell me in the comments', 800, 740, 28, 'semi', MUTED, 'l', a3)
    a4 = P(t, b[4], .5)
    if a4 > 0:
        pul = 1 + .05 * max(0, wave(t, 1.1))
        with pop(c, t, b[4], 1130, 560) as aa:
            with xf(c, 1130, 560, pul):
                rrect(c, 920, 515, 420, 96, 48); col(c, RED, aa); c.fill()
                text(c, 'SUBSCRIBE', 1130, 578, 40, 'head', WHITE, 'c', aa, ls=3)
        with pop(c, t, b[4] + .5, 1460, 565) as aa:
            if aa: bell(c, 1460, 600, 1.2, t, aa)
    a5 = P(t, b[5], .6)
    text(c, 'The trend is your friend, until it ends.', 1130, 760, 44, 'serif', NAVY, 'c', a5)
    fa = P(t, b[5] + .4, .6)
    text(c, 'Unofficial summary written in our own words · not affiliated with the author or publisher', W / 2, 990, 22, 'med', MUTED, 'c', fa)
    text(c, 'Educational content, not financial advice · Market data: TradingView', W / 2, 1024, 20, 'med', FAINT, 'c', fa)
