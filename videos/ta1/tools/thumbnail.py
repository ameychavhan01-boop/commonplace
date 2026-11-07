"""YouTube thumbnail 1280x720. Usage: python tools/thumbnail.py OUT.png"""
import sys, os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import cairocffi as cairo
from engine import *
from scenes.data import nifty_d20, idx

W2, H2 = 1280, 720
s = cairo.ImageSurface(cairo.FORMAT_RGB24, W2, H2); c = cairo.Context(s)
g = cairo.LinearGradient(0, 0, W2, H2); g.add_color_stop_rgb(0, *mix(NAVY, (0, 0, 0), .15)); g.add_color_stop_rgb(1, *mix(NAVY, BLUE, .25))
c.set_source(g); c.paint()
for x in range(20, W2, 28):
    for y in range(20, H2, 28): circle(c, x, y, 1.1, WHITE, .05)
ring(c, 1150, 90, 210, GOLD, 2, .12); ring(c, 120, 690, 260, WHITE, 2, .06)

# right: real Nifty 2020 V with the news contrast
d = nifty_d20(); C = d['c']; n = idx(d, '2021-02-15') + 1
card(c, 640, 150, 600, 380, 22, CARD, 1, depth=1.5)
F = Frame(670, 200, 540, 300, 0, n - 1, 7000, 15800)
series(c, F, range(n), C[:n], 1, NAVY, 5, 1, GREEN, .25)
il = idx(d, '2020-03-23')
glow_dot(c, F.X(il), F.Y(C[il]), 9, RED, 0, 1, False)
glow_dot(c, F.X(n - 1), F.Y(C[n - 1]), 9, GREEN, 0, 1, False)
text(c, 'NIFTY 50  ·  2020 TO 2021', 672, 186, 20, 'semi', MUTED, 'l', 1, ls=2)
with xf(c, 800, 590, rot=-.06):
    card(c, 640, 520, 350, 130, 14, CARD, 1, depth=1.4)
    text(c, 'THE NEWS', 672, 556, 18, 'semi', MUTED, 'l', 1, ls=3)
    text(c, 'GDP -23.9%', 662, 618, 48, 'head', RED, 'l', 1)
with xf(c, 1120, 560, rot=.05):
    card(c, 995, 500, 260, 130, 14, GREEN, 1, depth=1.4)
    text(c, 'THE PRICE', 1020, 536, 18, 'semi', LGREEN, 'l', 1, ls=3)
    text(c, '+50%', 1018, 604, 64, 'head', WHITE, 'l', 1)

# left: title
pill(c, 56, 52, 'JOHN J. MURPHY  ·  BOOK SUMMARY', 20, GOLD, NAVY, 1, 'semi', ls=2)
text(c, 'TECHNICAL', 52, 200, 92, 'head', WHITE, 'l')
text(c, 'ANALYSIS', 52, 298, 92, 'head', GOLD, 'l')
text(c, 'The chart knew', 56, 382, 44, 'serif', WHITE, 'l')
text(c, 'before the news.', 56, 432, 44, 'serif', WHITE, 'l')
rrect(c, 0, 470, 600, 74, 0); col(c, RED); c.fill()
text(c, '10 LESSONS · 64 MIN · PART 1', 56, 520, 34, 'head', WHITE, 'l', 1, ls=1)
text(c, 'Dow Theory · Trends · Patterns · Volume', 56, 600, 22, 'semi', LGOLD, 'l')
text(c, 'Real Nifty 50 & Bitcoin charts', 56, 636, 20, 'semi', WHITE, 'l', .85)
s.write_to_png(sys.argv[1])
print('thumbnail', sys.argv[1])
