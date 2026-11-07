"""Write youtube_upload_info.md and narration_script.txt. Usage: python tools/upload_info.py BUILD OUTDIR"""
import sys, os, re
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import timeline
from script_p1 import SCENES, CHAPTERS

build, out = sys.argv[1], sys.argv[2]
tl = timeline.load(build)
def ts(t):
    t = int(t); h, r = divmod(t, 3600); m, s = divmod(r, 60)
    return f'{h}:{m:02d}:{s:02d}' if h else f'{m}:{s:02d}'
total = sum(b.end for m, b, T in tl)

rows = []
for m, b, T in tl:
    if m['id'] == 'hook': lab = 'The chart knew before the news (Nifty 2020)'
    elif m['id'] == 'intro': lab = 'The book, the author and the 3-part plan'
    elif m['id'] == 'recap': lab = 'Recap: the 10 biggest lessons'
    elif m['id'] == 'outro': lab = 'Part 2 preview'
    else: lab = f"Ch {m['ch']} · {m['title']}"
    rows.append(f'{ts(T)} {lab}')

desc = f"""John J. Murphy's Technical Analysis of the Financial Markets is often called the bible of technical analysis. This is Part 1 of a deep, 3-part animated summary: how to read the chart itself.

In this part (chapters 1 to 8): the three premises of technical analysis, the six tenets of Dow Theory, how charts are built (bar, line, candlestick, point & figure, log vs arithmetic scale), trends and trendlines, support and resistance and why they reverse roles, the fan principle, channels, 1/3 - 1/2 - 2/3 retracements and speed lines, reversal days and price gaps, head and shoulders, double and triple tops, saucers and V-spikes, triangles, flags, wedges and rectangles, volume, on-balance volume, open interest, the COT report, and long-term charts.

Every real chart uses actual market data for the Nifty 50 and Bitcoin (data: TradingView), including the March 2020 Nifty V-bottom, Bitcoin's $73,800 resistance that later became support, the $100,000 round number, the June 2024 Nifty election gap and Bitcoin's long-term cycles.

CHAPTERS
""" + '\n'.join(rows) + """

Part 2 (next): moving averages, oscillators (RSI, MACD, stochastics), contrary opinion, point & figure and candlesticks.
Part 3: Elliott Wave and Fibonacci, time cycles, trading systems, money management, intermarket analysis, stock market breadth and Murphy's checklist.

Get the book: Technical Analysis of the Financial Markets, John J. Murphy (New York Institute of Finance, 1999).

Question for you: which idea from Part 1 surprised you most, and which will you try first on a real chart?

Unofficial summary written in our own words · not affiliated with the author or publisher.
Educational content only, not financial advice. Market data: TradingView (NSE:NIFTY, BITSTAMP:BTCUSD).
"""

md = f"""# YouTube upload info: Technical Analysis of the Financial Markets, Part 1

Length: {ts(total)} · 1920x1080 · 30 fps · audio normalized to -15 LUFS

## Title options
1. Technical Analysis of the Financial Markets (Part 1): Read Any Chart Like a Pro | John Murphy Book Summary
2. The Chart Knew Before the News: Technical Analysis Explained with Nifty 50 & Bitcoin (Murphy, Part 1)
3. The Bible of Technical Analysis, Animated: Trends, Support & Resistance, Patterns and Volume (Part 1 of 3)

## Description
{desc}
## Tags
technical analysis, technical analysis of the financial markets, john murphy, john j murphy, book summary, animated book summary, dow theory, support and resistance, trendlines, chart patterns, head and shoulders, double top, triangle pattern, flag pattern, wedge pattern, price gaps, fibonacci retracement, volume analysis, on balance volume, open interest, nifty 50, nifty technical analysis, bitcoin technical analysis, stock market for beginners, trading education, chart reading, how to read stock charts, candlestick charts, log scale chart, trading book summary

## Thumbnail
thumbnail.png (1280x720): "TECHNICAL ANALYSIS" with "GDP -23.9%" vs "+50%" contrast on the real Nifty 2020 chart.

## Files
- final_video.mp4: video with narration and music
- voice_only_video.mp4: same video, narration only
- captions_en.srt: English captions synced to the narration
- thumbnail.png
"""
open(os.path.join(out, 'youtube_upload_info.md'), 'w').write(md)
script = ' '.join(re.sub(r'\s*\{\d+\}\s*', ' ', s['text']).strip() for s in SCENES)
open(os.path.join(out, 'narration_script.txt'), 'w').write(re.sub(r'\s+', ' ', script).strip() + '\n')
print('written', len(rows), 'chapters;', len(script.split()), 'words')
