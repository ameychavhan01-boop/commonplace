"""Scene plan: every visual is tied to a narration segment (or a word inside it)
so pictures change exactly when the narrator gets there."""
import json
from pathlib import Path
from gfx import *

HERE = Path(__file__).parent
TIMINGS = json.load(open(HERE / "timings.json"))
VO = 0.4                                   # narration starts at 0.4 s
BADGE = "THOUGHT EXPERIMENT"               # top-left corner badge (None to hide)
END_DUR = 10.0
NARR_END = TIMINGS[-1]["end"] + VO
TOTAL = NARR_END + END_DUR

def seg_start(i): return TIMINGS[i]["start"] + VO
def seg_end(i): return TIMINGS[i]["end"] + VO
def word_t(i, word, after=False):
    s = TIMINGS[i]; txt = s["text"]
    k = txt.find(word)
    if k < 0: raise ValueError(f"'{word}' not in segment {i}: {txt}")
    if after: k += len(word)
    return s["start"] + VO + (s["end"] - s["start"]) * k / len(txt)
def T(x):
    if isinstance(x, (int,)) and not isinstance(x, bool): return seg_start(x)
    if isinstance(x, float): return x
    if isinstance(x, tuple): return word_t(*x)
    raise ValueError(x)

SCENES = []
def sc(at, kind, sfx=(), cues=None, lead=0.12, trans="fade", **p):
    SCENES.append(dict(start=T(at) - (lead if isinstance(at, int) else 0.05), kind=kind, p=p,
                       cues={k: T(v) for k, v in (cues or {}).items()}, sfx=list(sfx), trans=trans))

# NVIDIA market value, daily closes x 24.1B shares (TradingView NASDAQ:NVDA; 10-Q share count)
CLOSES = [("1 Oct", 230.86), ("2 Oct", 233.95), ("5 Oct", 238.90), ("6 Oct", 239.24), ("7 Oct", 237.47), ("8 Oct", 230.48),
          ("9 Oct", 229.28), ("12 Oct", 226.32), ("13 Oct", 228.52), ("14 Oct", 221.30), ("15 Oct", 217.23), ("16 Oct", 214.13),
          ("19 Oct", 217.09), ("20 Oct", 216.47), ("21 Oct", 221.97), ("22 Oct", 212.21), ("23 Oct", 210.96), ("26 Oct", 216.00),
          ("27 Oct", 217.94), ("28 Oct", 215.38), ("29 Oct", 213.66), ("30 Oct", 204.64), ("2 Nov", 202.06), ("3 Nov", 206.69),
          ("4 Nov", 200.13), ("5 Nov", 181.60), ("6 Nov", 186.64), ("9 Nov", 178.67), ("10 Nov", 168.89), ("11 Nov", 173.73),
          ("12 Nov", 166.19), ("13 Nov", 162.85), ("16 Nov", 156.14), ("17 Nov", 155.46), ("18 Nov", 150.96), ("19 Nov", 145.98),
          ("20 Nov", 125.53)]
MCAP = [(d, c * 24.1 / 1000) for d, c in CLOSES]   # $ trillions

KW = lambda text, t, **k: dict(text=text, t=t, **k)

# =============================================================== 1. HOOK
sc(0, "illus", img="img01", a=(0.5, 0.55, 1.0), b=(0.62, 0.5, 1.25), lead=0.4, sfx=[(0.3, "ding", 0.5)])
sc(1, "illus", img="img02", a=(0.5, 0.5, 1.05), b=(0.5, 0.45, 1.3))
sc(2, "text", text="Nothing.", sfx=[(0, "glitch", 0.5)])
sc(3, "illus", img="img03", a=(0.4, 0.5, 1.15), b=(0.6, 0.5, 1.15))
sc(4, "text", text="Nothing.", color=(255, 120, 120), sfx=[(0, "glitch", 0.6)])
sc(5, "illus", img="img04", a=(0.5, 0.5, 1.1), b=(0.5, 0.45, 1.35), shake_at=0.2, tint=(RED, 0.18),
   sfx=[(0.1, "boom", 0.35)])
sc(6, "illus", img="img05", a=(0.5, 0.45, 1.3), b=(0.5, 0.5, 1.0),
   cues=dict(n=(6, "worth"), g=(6, "disappeared")),
   kw=[KW("$3 TRILLION", "n", size=190, y=H * 0.42, sub="market value · 20 Nov 2026")],
   sfx=[("n", "pop", 0.8)])
sc((6, "disappeared"), "illus", img="img05", a=(0.5, 0.35, 1.7), b=(0.5, 0.3, 2.1), shake_at=0.1, trans="burst", grade="crash",
   kw=[KW("GONE. OVERNIGHT.", 0.05, size=150, y=H * 0.82, color=WHITE, style="plate")], sfx=[(0.05, "boom", 0.8)])
sc(7, "big", lines=[("THOUGHT", "anton", 230, YELLOW), ("EXPERIMENT", "anton", 230, YELLOW)], style="stamp",
   bg="dark", sfx=[(0.05, "boom", 0.4)])
sc(8, "big", lines=[("EVERY NUMBER", "anton", 170, WHITE), ("IS REAL", "anton", 170, LIME)],
   note="(sources in the description)", note_at=0.6, underline=560, ucolor=LIME, sfx=[(0.3, "pop", 0.6)])
sc(9, "title", img="img06", lines=[("WHAT IF", WHITE, 150), ("NVIDIA VANISHED", YELLOW, 210), ("TOMORROW?", WHITE, 170)], sfx=[(-0.6, "riser", 0.5), (0.2, "boom", 0.6)])

# =============================================================== 2. WHAT NVIDIA DOES
sc(10, "big", lines=[("WHAT DOES NVIDIA", "anton", 150, INK), ("ACTUALLY DO?", "anton", 150, RED)], bg="paper",
   trans="slide", sfx=[(0, "whoosh", 0.6)])
sc(11, "chip", mode="gpu", sfx=[(0.15, "pop", 0.7)])
sc(12, "illus", img="img07", a=(0.5, 0.5, 1.0), b=(0.5, 0.48, 1.18), cues=dict(c=(12, "one very")),
   kw=[KW("CPU = 1 SMART CHEF", "c", size=120, y=H * 0.84, style="plate", color=YELLOW)], sfx=[("c", "pop", 0.6)])
sc(13, "illus", img="img08", a=(0.5, 0.5, 1.35), b=(0.5, 0.5, 1.0), cues=dict(c=(13, "thousands")),
   kw=[KW("GPU = THOUSANDS OF COOKS", "c", size=110, y=H * 0.84, style="plate", color=LIME)], sfx=[("c", "pop", 0.6)])
sc(14, "big", lines=[("WHAT AI NEEDS:", "anton", 180, WHITE)], bg="dark")
sc((14, "billions"), "chip", mode="parallel", cues=dict(big=(14, "all at once")), sfx=[(0.1, "whoosh", 0.4), ("big", "pop", 0.7)])
sc(15, "chip", mode="engine", sfx=[(0.6, "pop", 0.6)])
sc(16, "illus", img="img09", a=(0.3, 0.5, 1.2), b=(0.7, 0.5, 1.2))
sc(17, "pie", share=0.80, big="~80%", label="OF AI CHIPS IN DATA CENTERS", note="estimated · ranges 70–85%",
   color=LIME, bg="dark", sfx=[(0.15, "ticker", 0.4), (0.55, "pop", 0.7)])
sc(18, "text", text="But chips are only half the story.")
sc(19, "big", lines=[("CUDA", "anton", 300, LIME)], style="type", bg="dark", note="NVIDIA's software platform",
   sfx=[(0.05, "ticker", 0.3)])
sc(20, "illus", img="img10", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.2), cues=dict(c=(20, "language")),
   kw=[KW("CUDA = THE LANGUAGE", "c", size=120, y=H * 0.84, style="plate", color=LIME)], sfx=[("c", "pop", 0.6)])
sc(21, "counter", value=11, suffix=" MILLION", label="DEVELOPERS BUILD ON CUDA", sub="according to NVIDIA",
   cues=dict(num=(21, "11")), size=200, sfx=[("num", "ticker", 0.4), ("num", "pop", 0.5)])
sc(22, "big", lines=[("20 YEARS OF", "anton", 120, WHITE), ("CODE · TOOLS · HABITS", "anton", 140, YELLOW)],
   stagger=0.5, sfx=[(0.6, "pop", 0.5)])
sc(23, "big", lines=[("HABITS.", "anton", 280, YELLOW)], bg="dark", underline=700, note="remember this word",
   note_at=1.0, sfx=[(0.1, "boom", 0.35)])
sc(26, "big", lines=[("IN JUST", "anton", 150, INK), ("3 MONTHS...", "anton", 230, ORANGE)], bg="paper")
sc((26, "NVIDIA made"), "counter", value=115.8, decimals=1, prefix="$", suffix=" BILLION", label="NVIDIA SALES IN 3 MONTHS",
   sub="quarter ended 25 Oct 2026", cues=dict(num=(26, "115.8")), size=200, color=LIME,
   sfx=[("num", "ticker", 0.4), ("num", "pop", 0.6)])
sc(27, "bars", title="WHERE THE MONEY CAME FROM", bg="dark",
   items=[("DATA CENTERS", 107.6, LIME, "$107.6B"), ("EVERYTHING ELSE", 8.2, (150, 160, 180), "$8.2B")],
   max=115.8, note="Q3 fiscal 2027 · NVIDIA results", cues=dict(bar0=(27, "107.6"), bar1=(27, "of that")),
   sfx=[("bar0", "pop", 0.5)])
sc((27, "the giant"), "illus", img="img11", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.15),
   kw=[KW("WHERE AI LIVES", 0.2, size=120, y=H * 0.84, style="plate", color=YELLOW)])

# =============================================================== 3. HOUR 1
sc(28, "timeline", cur=-1, title="LET'S PLAY IT OUT", trans="slide", sfx=[(0, "whoosh", 0.6)])
sc(29, "illus", img="img12", a=(0.5, 0.4, 1.25), b=(0.5, 0.5, 1.0), sfx=[(0.1, "ding", 0.35)])
sc(30, "chip", mode="dissolve", word="NVIDIA", label="GONE.", cues=dict(go=(30, "is gone"), label=(30, "gone")),
   sfx=[("go", "whoosh_down", 0.6)])
sc(31, "world", mode="darkwave", title="EVERY CHIP GOES DARK", cues=dict(title=(31, "goes dark")),
   sfx=[(0.3, "powerdown", 0.6)])
sc(32, "big", lines=[("HOUR 1", "anton", 300, YELLOW)], style="stamp", bg="dark", sfx=[(0.05, "boom", 0.5)])
sc(33, "illus", img="img13", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.3), grade="night",
   kw=[KW("AI GOES DARK", 0.3, size=170, y=H * 0.8, color=WHITE)], sfx=[(0.1, "powerdown", 0.6)])
sc(34, "illus", img="img14", a=(0.45, 0.5, 1.15), b=(0.55, 0.5, 1.15), cues=dict(n=(34, "nearly")),
   kw=[KW("NEARLY 1 BILLION PEOPLE A WEEK", "n", size=96, y=H * 0.78, sub="ChatGPT weekly users (OpenAI, 2026)")],
   sfx=[("n", "pop", 0.6)])
sc(35, "illus", img="img15", a=(0.5, 0.5, 1.1), b=(0.5, 0.45, 1.3),
   kw=[KW("IMAGE MAKERS: FROZEN", 0.2, size=110, y=H * 0.84, style="plate", color=(120, 200, 255))], sfx=[(0.2, "glitch", 0.4)])
sc(36, "illus", img="img16", a=(0.4, 0.5, 1.2), b=(0.55, 0.5, 1.2),
   kw=[KW("VOICE ASSISTANTS: SILENT", 0.2, size=110, y=H * 0.84, style="plate", color=YELLOW)], sfx=[(0.2, "pop", 0.4)])
sc(37, "code", cues=dict(stop=(37, "halfway")), sfx=[("stop", "glitch", 0.6)])
sc(38, "tiles", title="AI SERVICES", note="a few run on their own chips", cues=dict(off=(38, "survive")),
   sfx=[("off", "powerdown", 0.5)])
sc(39, "illus", img="img17", a=(0.4, 0.5, 1.15), b=(0.7, 0.5, 1.35), cues=dict(c=(39, "own chips")),
   kw=[KW("GOOGLE: ITS OWN CHIPS (TPUs)", "c", size=100, y=H * 0.84, style="plate", color=(120, 200, 255))],
   sfx=[("c", "pop", 0.5)])
sc(40, "pie", share=0.80, big="MOST AI", label="WAS BUILT ON NVIDIA", note="~80% of AI chips (estimated)", color=LIME,
   bg="dark", sfx=[(0.5, "pop", 0.5)])
sc(41, "big", lines=[("SO IT STOPS.", "anton", 220, RED)], style="glitch", bg="dark", sfx=[(0.05, "powerdown", 0.5)])
sc(42, "big", lines=[("NOT JUST", "anton", 170, INK), ("CHATBOTS", "anton", 210, RED)], bg="paper")
sc(43, "illus", img="img18", a=(0.5, 0.5, 1.0), b=(0.55, 0.45, 1.2),
   kw=[KW("HOSPITALS", 0.15, size=130, y=H * 0.84, style="plate", color=WHITE)], sfx=[(0.15, "pop", 0.4)])
sc(44, "illus", img="img19", a=(0.45, 0.5, 1.2), b=(0.55, 0.5, 1.05),
   kw=[KW("BANKS", 0.15, size=130, y=H * 0.84, style="plate", color=WHITE)], sfx=[(0.15, "pop", 0.4)])
sc(45, "illus", img="img20", a=(0.5, 0.5, 1.2), b=(0.5, 0.5, 1.0),
   kw=[KW("WEATHER FORECASTS", 0.1, size=120, y=H * 0.84, style="plate", color=WHITE)], sfx=[(0.1, "pop", 0.4)])
sc(46, "illus", img="img21", a=(0.5, 0.5, 1.0), b=(0.6, 0.5, 1.2),
   kw=[KW("MEDICINE RESEARCH", 0.15, size=120, y=H * 0.84, style="plate", color=WHITE)], sfx=[(0.15, "pop", 0.4)])
sc(47, "progress", cues=dict(stop=(48, "stops")), sfx=[((48, "stops"), "powerdown", 0.5)])

# =============================================================== 4. DAY 1
sc(49, "big", lines=[("DAY 1", "anton", 300, YELLOW)], style="stamp", bg="dark", trans="slide",
   sfx=[(0, "whoosh", 0.6), (0.1, "boom", 0.5)])
sc(50, "illus", img="img22", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.15), sfx=[(0.2, "ding", 0.4)])
sc(51, "illus", img="img22", a=(0.4, 0.45, 1.5), b=(0.45, 0.4, 1.8), grade="crash",
   kw=[KW("THIS IS WHERE IT GETS SCARY", 0.4, size=100, y=H * 0.84, style="plate", color=WHITE)])
sc(52, "pie", share=0.05, big="~5%", label="OF THE S&P 500 IS NVIDIA", note="America's 500 biggest companies · est. 20 Nov 2026",
   color=LIME, bg="paper", big_color=LIME, cues=dict(), sfx=[(0.55, "pop", 0.6)])
sc((52, "America's"), "illus", img="img22", a=(0.5, 0.5, 1.0), b=(0.6, 0.5, 1.2),
   kw=[KW("AMERICA'S 500 BIGGEST COMPANIES", 0.1, size=100, y=H * 0.84, style="plate", color=WHITE)])
sc(53, "illus", img="img23", a=(0.5, 0.5, 1.1), b=(0.55, 0.45, 1.35), cues=dict(c=(53, "index fund")),
   kw=[KW("YOUR INDEX FUND", "c", size=130, y=H * 0.84, style="plate", color=YELLOW)], sfx=[("c", "pop", 0.5)])
sc((53, "maybe"), "illus", img="img23", a=(0.6, 0.45, 1.8), b=(0.62, 0.42, 2.1),
   kw=[KW("WITHOUT YOU EVEN KNOWING", 0.1, size=110, y=H * 0.84, style="plate", color=WHITE)])
sc(54, "pie", share=0.05, big="→ $0", label="THAT SLICE GOES TO ZERO", color=LIME, bg="dark",
   cues=dict(remove=(54, "zero")), sfx=[((54, "zero"), "whoosh_down", 0.6)])
sc(55, "counter", value=3, suffix=" TRILLION", prefix="$", final="$3,000,000,000,000", label="GONE IN ONE MORNING",
   cues=dict(num=55, label=56), size=200, color=RED, count_dur=1.0,
   sfx=[(0.05, "ticker", 0.4), (1.1, "boom", 0.7)])
sc((56, "one morning"), "illus", img="img24", a=(0.5, 0.5, 1.0), b=(0.5, 0.4, 1.2), grade="crash")
sc(57, "bars", title="NVIDIA vs INDIA'S WHOLE ECONOMY", bg="paper",
   items=[("NVIDIA", 3.03, LIME, "$3.0T"), ("INDIA GDP", 4.06, SAFFRON, "$4.06T")], max=4.4,
   note="NVIDIA value 20 Nov 2026 · India GDP 2026: IMF", callout="≈ 3/4 OF INDIA'S ECONOMY",
   cues=dict(bar0=57, bar1=(57, "India's"), callout=(57, "three-quarters")), sfx=[("callout", "pop", 0.6)])
sc(58, "india", draw=True, glow=True, title="HOLD THAT THOUGHT...", title_y=110, title_size=90, cy=620, scale=21,
   sfx=[(0.1, "whoosh", 0.4)])
sc(59, "big", lines=[("IT DOESN'T", "anton", 180, WHITE), ("STOP THERE", "anton", 180, RED)], bg="dark")
sc(60, "illus", img="img25", a=(0.2, 0.5, 1.4), b=(0.35, 0.5, 1.4),
   kw=[KW("PARTS MAKERS", 0.1, size=120, y=H * 0.84, style="plate", color=YELLOW)], sfx=[(0.1, "pop", 0.4)])
sc(61, "illus", img="img25", a=(0.45, 0.5, 1.4), b=(0.6, 0.5, 1.4),
   kw=[KW("CHIP RENTERS", 0.1, size=120, y=H * 0.84, style="plate", color=YELLOW)], sfx=[(0.1, "pop", 0.4)])
sc(62, "illus", img="img25", a=(0.7, 0.5, 1.4), b=(0.5, 0.5, 1.0),
   kw=[KW("AI STARTUPS", 0.1, size=120, y=H * 0.84, style="plate", color=YELLOW)], sfx=[(0.1, "pop", 0.4)])
sc(63, "illus", img="img26", a=(0.5, 0.5, 1.0), b=(0.5, 0.4, 1.2), cues=dict(c=(63, "nobody")),
   kw=[KW("WHAT IS ANYTHING WORTH?", "c", size=110, y=H * 0.84, style="plate", color=WHITE)])
sc(64, "big", lines=[("A REAL-WORLD", "anton", 150, WHITE), ("HINT", "anton", 240, YELLOW)], bg="dark",
   note="real data, October–November 2026")
sc(65, "line", points=MCAP, ymin=2.0, ymax=6.4, grid=[3, 4, 5, 6], xticks=[0, 3, 22, 36],
   title="NVIDIA MARKET VALUE ($ TRILLIONS)", source="daily close × 24.1B shares · TradingView, SEC 10-Q",
   cues=dict(draw0=(65, "In early"), draw1=(65, "5.8"), peak=(65, "5.8")), kmax=3 / 36,
   ann=[dict(text="PEAK ~$5.8T · 6 OCT", t="peak", x=560, y=215, size=58, color=LIME)],
   sfx=[("peak", "pop", 0.5)])
sc(66, "line", points=MCAP, ymin=2.0, ymax=6.4, grid=[3, 4, 5, 6], xticks=[0, 3, 22, 36],
   title="NVIDIA MARKET VALUE ($ TRILLIONS)", source="daily close × 24.1B shares · TradingView, SEC 10-Q",
   cues=dict(draw0=66, draw1=(66, "of that"), loss=(66, "2.7")), kmin=3 / 36,
   ann=[dict(text="PEAK ~$5.8T · 6 OCT", t=0.0, x=560, y=215, size=58, color=LIME),
        dict(text="−$2.7 TRILLION", t="loss", x=820, y=760, size=120, color=RED)],
   sfx=[("loss", "boom", 0.6)])
sc(67, "world", mode="pulses", title="MARKETS EVERYWHERE FELT IT", sfx=[(0.3, "pop", 0.3)])
sc(68, "illus", img="img05", a=(0.5, 0.35, 1.6), b=(0.5, 0.45, 1.1), cues=dict(c=(68, "gone at once")), grade="crash", grade_at=1.5,
   kw=[KW("NOW IMAGINE: ALL AT ONCE", "c", size=120, y=H * 0.82, color=WHITE, style="plate")], sfx=[("c", "boom", 0.7)])

# =============================================================== 5. WEEK 1
sc(69, "big", lines=[("WEEK 1", "anton", 300, YELLOW)], style="stamp", bg="dark", trans="slide",
   sfx=[(0, "whoosh", 0.6), (0.1, "boom", 0.5)])
sc(70, "illus", img="img27", a=(0.5, 0.5, 1.0), b=(0.5, 0.45, 1.25), shake_at=0.6,
   kw=[KW("THE TECH GIANTS PANIC", 0.4, size=120, y=H * 0.84, style="plate", color=RED)])
sc(71, "counter", value=500, prefix="$", suffix=" BILLION", label="OF CHIP ORDERS LINED UP",
   sub="NVIDIA's own estimate (Oct 2025), through 2026", cues=dict(num=(71, "500")),
   size=210, color=LIME, sfx=[("num", "ticker", 0.4)])
sc((71, "chip orders"), "illus", img="img29", a=(0.85, 0.7, 1.9), b=(0.75, 0.7, 1.9),
   kw=[KW("$500 BILLION OF ORDERS WAITING", 0.1, size=100, y=H * 0.84, style="plate", color=LIME)])
sc(72, "cards", title="ALL WAITING FOR CHIPS", bg="dark",
   cards=[dict(title="MICROSOFT", size=58, t="c0"), dict(title="AMAZON", size=58, t="c1"),
          dict(title="META", size=58, t="c2"), dict(title="OPENAI", size=58, t="c3")],
   card_h=260, cues=dict(c0=(72, "Microsoft"), c1=(72, "Amazon"), c2=(72, "Meta"), c3=(72, "OpenAI")),
   sfx=[((72, "Microsoft"), "pop", 0.4), ((72, "Amazon"), "pop", 0.4),
                                         ((72, "Meta"), "pop", 0.4), ((72, "OpenAI"), "pop", 0.4)])
sc(73, "illus", img="img28", a=(0.5, 0.5, 1.15), b=(0.5, 0.5, 1.0), cues=dict(c=(73, "nothing")),
   kw=[KW("ORDERS: CANCELLED", 0.1, size=130, y=H * 0.16, color=RED, rot=-5), KW("...NOTHING.", "c", size=150, y=H * 0.82, color=WHITE)],
   sfx=[(0.1, "boom", 0.5)])
sc(74, "text", text="So who steps in?")
sc(75, "illus", img="img43", a=(0.3, 0.5, 1.3), b=(0.45, 0.5, 1.3), cues=dict(c=(75, "OpenAI")),
   kw=[KW("AMD: AI CHIPS", 0.1, size=130, y=H * 0.15, style="plate", color=WHITE),
       KW("+ A DEAL WITH OPENAI", "c", size=110, y=H * 0.84, style="plate", color=ORANGE)], sfx=[(0.1, "pop", 0.5)])
sc(76, "cards", title="THE RIVALS", bg="paper",
   cards=[dict(title="AMD", text="AI chips + OpenAI deal", color=(255, 214, 200), t="c0"),
          dict(title="GOOGLE", text="its own TPUs", color=(205, 228, 255), t="c1"),
          dict(title="AMAZON", text="its own Trainium", color=(255, 236, 190), t="c2")],
   cues=dict(c0=76, c1=(76, "Google"), c2=77), sfx=[((76, "Google"), "pop", 0.5), (77, "pop", 0.5)])
sc(78, "text", text="So why not just switch?")
sc(79, "cards", title="3 REASONS", bg="dark",
   cards=[dict(title="1", text="FACTORIES", t="c0", color=YELLOW, size=140), dict(title="2", text="CUDA", t="c1", color=LIME, size=140),
          dict(title="3", text="THE FULL PACKAGE", t="c2", color=ORANGE, size=140)], card_h=330,
   cues=dict(c0=79, c1=(79, "reasons"), c2=(79, "reasons", True)), sfx=[(0.2, "pop", 0.5)])
sc(80, "illus", img="img29", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.2), cues=dict(c=(81, "booked")),
   kw=[KW("1. FACTORIES", 0.15, size=120, y=H * 0.15, style="plate", color=YELLOW),
       KW("BOOKED SOLID", "c", size=150, y=H * 0.8, color=RED, rot=-6)], sfx=[("c", "boom", 0.4)])
sc((81, "the factories"), "illus", img="img29", a=(0.75, 0.6, 1.6), b=(0.7, 0.55, 1.9),
   kw=[KW("YEARS TO BUILD", 0.1, size=120, y=H * 0.15, style="plate", color=YELLOW)])
sc(82, "big", lines=[("2. CUDA", "anton", 260, LIME)], bg="dark", note="remember those habits?", note_at="n",
   cues=dict(n=(83, "Remember")))
sc(84, "code", cues=dict(stop=999.0), sfx=[(0.1, "ticker", 0.3)])
sc(85, "illus", img="img30", a=(0.5, 0.5, 1.35), b=(0.5, 0.5, 1.0), cues=dict(c=(85, "one book")),
   kw=[KW("ONE BOOK AT A TIME", "c", size=140, y=H * 0.84, style="plate", color=YELLOW)])
sc(86, "big", lines=[("3. THE FULL", "anton", 170, WHITE), ("PACKAGE", "anton", 220, ORANGE)], bg="dark")
sc(88, "cards", title="THE WHOLE MACHINE", bg="paper",
   cards=[dict(title="CHIPS", t="c0", color=(220, 245, 200)), dict(title="CABLES", t="c1", color=(255, 236, 190)),
          dict(title="NETWORK", t="c2", color=(205, 228, 255)), dict(title="SOFTWARE", t="c3", color=(255, 214, 200))],
   cues=dict(c0=87, c1=(88, "cables"), c2=(88, "networking"), c3=(88, "software")), card_h=300,
   sfx=[((88, "cables"), "pop", 0.4), ((88, "networking"), "pop", 0.4), ((88, "software"), "pop", 0.4)])
sc(89, "illus", img="img31", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.2), cues=dict(c=(90, "whole puzzle")),
   kw=[KW("NOBODY HAS THE WHOLE PUZZLE", "c", size=110, y=H * 0.84, style="plate", color=WHITE)])
sc(91, "illus", img="img32", a=(0.5, 0.55, 1.0), b=(0.5, 0.45, 1.25), cues=dict(c=(91, "shoots up")),
   kw=[KW("PRICES SHOOT UP", "c", size=140, y=H * 0.82, color=RED)], sfx=[("c", "riser", 0.4)])
sc(92, "chip", mode="price", label="AI POWER = A LUXURY", sfx=[(0.8, "ding", 0.4)])

# =============================================================== 6. INDIA
sc(93, "world", mode="zoom_india", title="NOW... WHAT ABOUT INDIA?", title_y=140, trans="slide",
   sfx=[(0, "whoosh", 0.6), (0.4, "riser", 0.3)])
sc(94, "india", glow=True, title="NOT WATCHING FROM FAR AWAY", title_size=80, scale=21, cy=620)
sc(95, "india", chip=(1600, 520), scale=21, cx=760, cy=600, title="WIRED INTO NVIDIA", title_size=96,
   cues=dict(chip=(95, "wired")), sfx=[((95, "wired"), "pop", 0.5)])
sc(96, "india", scale=21, cy=600, title="THOUSANDS OF NVIDIA ENGINEERS", title_size=78,
   pins=[("Bengaluru", "BENGALURU", "p0"), ("Hyderabad", "HYDERABAD", "p1"), ("Pune", "PUNE", "p2"),
         ("Gurugram", "GURUGRAM", "p3")],
   cues=dict(p0=(96, "Bengaluru"), p1=(96, "Hyderabad"), p2=(96, "Pune"), p3=(96, "Gurugram")),
   sfx=[((96, "Bengaluru"), "pop", 0.5), ((96, "Hyderabad"), "pop", 0.5), ((96, "Pune"), "pop", 0.5),
        ((96, "Gurugram"), "pop", 0.5)])
sc(97, "illus", img="img33", a=(0.3, 0.5, 1.2), b=(0.65, 0.5, 1.2))
sc(98, "illus", img="img34", a=(0.5, 0.5, 1.0), b=(0.5, 0.45, 1.3), cues=dict(c=(98, "no company")), grade="cold",
   kw=[KW("...WITH NO COMPANY", "c", size=130, y=H * 0.84, color=WHITE)], sfx=[("c", "boom", 0.4)])
sc(99, "big", lines=[("THE IndiaAI", "anton", 190, SAFFRON), ("MISSION", "anton", 190, WHITE)], bg="dark",
   note="India's national AI programme")
sc(100, "counter", value=38000, suffix="+", label="GPUs FOR INDIAN STARTUPS & RESEARCHERS",
   sub="mostly NVIDIA chips · IndiaAI compute portal", cues=dict(num=(100, "38,000")), color=SAFFRON,
   grid=dict(n=380, cols=38, cell=20, y0=190, color=(90, 110, 70)), y=640, size=200, label_size=50,
   sfx=[("num", "ticker", 0.4), ("num", "pop", 0.5)])
sc((100, "available"), "cards", title="FOR INDIA'S OWN AI", bg="paper",
   cards=[dict(title="STARTUPS", t="c0", color=(255, 225, 190)), dict(title="RESEARCHERS", t="c1", color=(210, 235, 210), size=60)],
   cues=dict(c0=(100, "startups"), c1=(100, "researchers")), card_h=280,
   sfx=[((100, "startups"), "pop", 0.4), ((100, "researchers"), "pop", 0.4)])
sc((100, "most of them"), "chip", mode="gpu", caption="MOST OF THEM: NVIDIA CHIPS", sfx=[(0.15, "pop", 0.5)])
sc(101, "big", lines=[("SARVAM AI", "anton", 200, SAFFRON)], bg="dark", note="an Indian AI startup", note_at=0.4)
sc((101, "4,096"), "counter", value=4096, label="NVIDIA H100 CHIPS", sub="used to train Sarvam AI's 105-billion-parameter model",
   cues=dict(num=0.05), size=220, color=LIME, sfx=[("num", "ticker", 0.4), ("num", "pop", 0.5)])
sc(102, "illus", img="img35", a=(0.5, 0.5, 1.0), b=(0.55, 0.5, 1.2), cues=dict(c=(102, "loses")),
   kw=[KW("INDIA'S AI DREAM LOSES ITS ENGINE", "c", size=100, y=H * 0.84, style="plate", color=SAFFRON)])
sc(103, "illus", img="img36", a=(0.3, 0.5, 1.2), b=(0.6, 0.5, 1.2),
   kw=[KW("INDIA'S NEW AI DATA CENTERS", 0.2, size=100, y=H * 0.15, style="plate", color=WHITE)])
sc(104, "india", scale=19, cx=620, cy=600, title="BUILT AROUND NVIDIA", title_size=90, title_x=1300,
   pins=[("Jamnagar", "JAMNAGAR (RELIANCE)", "p0")], cues=dict(p0=(104, "Jamnagar")),
   sfx=[((104, "Jamnagar"), "pop", 0.5)])
sc((104, "Yotta's"), "counter", value=20736, label="NVIDIA CHIPS IN YOTTA'S PLANNED CLUSTER", sub="Yotta Data Services, India",
   cues=dict(num=0.1), size=210, color=LIME, label_size=50, sfx=[(0.1, "ticker", 0.4), (1.2, "pop", 0.5)])
sc((104, "they were built"), "illus", img="img36", a=(0.5, 0.35, 1.5), b=(0.5, 0.4, 1.25),
   kw=[KW("ALL BUILT AROUND NVIDIA", 0.1, size=120, y=H * 0.84, style="plate", color=YELLOW)])
sc(105, "illus", img="img36", a=(0.7, 0.55, 1.6), b=(0.6, 0.5, 1.9),
   kw=[KW("BILLIONS OF DOLLARS: STUCK", 0.3, size=120, y=H * 0.84, color=RED)], sfx=[(0.3, "boom", 0.4)])
sc(106, "counter", value=315, prefix="$", suffix=" BILLION", label="INDIA'S TECH INDUSTRY (REVENUE)",
   sub="NASSCOM estimate, FY2026", cues=dict(num=(106, "315")), size=210, color=YELLOW,
   label_size=52, sfx=[("num", "ticker", 0.4), ("num", "pop", 0.5)])
sc((106, "with nearly"), "counter", value=6, prefix="~", suffix=" MILLION", label="TECH WORKERS IN INDIA",
   sub="NASSCOM estimate, FY2026 (5.95 million)", cues=dict(num=0.1), size=230, color=SAFFRON,
   sfx=[(0.1, "ticker", 0.3), (1.1, "pop", 0.5)])
sc(107, "cards", title="ALL BUILD ON NVIDIA TOOLS", bg="paper",
   cards=[dict(title="INFOSYS", size=60, t="c0"), dict(title="TCS", size=70, t="c1"),
          dict(title="WIPRO", size=64, t="c2"), dict(title="HCLTECH", size=58, t="c3")], card_h=250,
   cues=dict(c0=(107, "Infosys"), c1=(107, "TCS"), c2=(107, "Wipro"), c3=(107, "HCLTech")),
   sfx=[((107, "Infosys"), "pop", 0.4), ((107, "TCS"), "pop", 0.4), ((107, "Wipro"), "pop", 0.4), ((107, "HCLTech"), "pop", 0.4)])
sc((107, "all build"), "illus", img="img33", a=(0.6, 0.5, 1.5), b=(0.4, 0.5, 1.5),
   kw=[KW("AI SERVICES FOR CLIENTS WORLDWIDE", 0.1, size=96, y=H * 0.84, style="plate", color=WHITE)])
sc(108, "illus", img="img37", a=(0.5, 0.5, 1.0), b=(0.4, 0.5, 1.2),
   kw=[KW("PROJECTS: FROZEN", 0.1, size=130, y=H * 0.84, style="plate", color=(120, 200, 255))], sfx=[(0.1, "glitch", 0.3)])
sc(109, "illus", img="img37", a=(0.7, 0.45, 1.6), b=(0.75, 0.45, 1.8),
   kw=[KW("CLIENTS: PAUSE", 0.1, size=130, y=H * 0.84, style="plate", color=YELLOW)], sfx=[(0.1, "pop", 0.4)])
sc(110, "big", lines=[("HIRING", "anton", 200, WHITE), ("SLOWS ↓", "anton", 200, RED)], bg="dark")
sc(111, "big", lines=[("WHAT ABOUT", "anton", 160, INK), ("GAMERS?", "anton", 230, TEAL)], bg="paper",
   note="here's a surprise...", note_at="n", cues=dict(n=112))
sc(113, "counter", value=555, suffix=" MILLION", label="GAMERS IN INDIA — MOSTLY ON PHONES",
   sub="Lumikai report, 2025 data", cues=dict(num=(113, "555")), size=210, color=TEAL, label_size=52,
   sfx=[("num", "ticker", 0.4), ("num", "pop", 0.5)])
sc((113, "and phones"), "big", lines=[("PHONES MOSTLY USE", "anton", 150, WHITE), ("OTHER CHIPS", "anton", 220, TEAL)], bg="dark")
sc(114, "illus", img="img38", a=(0.5, 0.5, 1.0), b=(0.5, 0.45, 1.2),
   kw=[KW("MOBILE GAMING SURVIVES!", 0.2, size=120, y=H * 0.84, style="plate", color=LIME)], sfx=[(0.2, "ding", 0.5)])
sc(115, "illus", img="img39", a=(0.5, 0.5, 1.0), b=(0.6, 0.5, 1.3), cues=dict(c=(116, "rare")),
   kw=[KW("GRAPHICS CARDS: RARE & EXPENSIVE", "c", size=100, y=H * 0.84, style="plate", color=RED)],
   sfx=[("c", "pop", 0.5)])
sc(117, "text", text="And the stock market?")
sc(118, "world", mode="flows", title="FOREIGN MONEY COULD RUSH OUT", size=84,
   note="a common pattern in panics — not a forecast")
sc((118, "to play"), "illus", img="img26", a=(0.5, 0.5, 1.3), b=(0.5, 0.45, 1.5),
   kw=[KW("\"PLAY IT SAFE\"", 0.1, size=140, y=H * 0.84, style="plate", color=YELLOW)])
sc(119, "cards", title="COULD FEEL THE PRESSURE", bg="dark",
   cards=[dict(title="SENSEX ↓", t="c0", color=(255, 205, 205), size=70), dict(title="NIFTY ↓", t="c1", color=(255, 205, 205), size=70),
          dict(title="RUPEE ↓", t="c2", color=(255, 225, 190), size=70)], card_h=260,
   cues=dict(c0=(119, "Sensex"), c1=(119, "Nifty"), c2=(119, "rupee")), note="thought experiment — not a prediction",
   sfx=[((119, "Sensex"), "pop", 0.4), ((119, "Nifty"), "pop", 0.4), ((119, "rupee"), "pop", 0.4)])
sc(120, "illus", img="img40", a=(0.5, 0.5, 1.0), b=(0.5, 0.45, 1.2),
   kw=[KW("EVEN WITH NO LINK TO NVIDIA", 0.6, size=100, y=H * 0.84, style="plate", color=WHITE)])
sc(121, "big", lines=[("BUT HERE'S THE", "anton", 150, WHITE), ("OTHER SIDE", "anton", 210, LIME)], bg="dark",
   sfx=[(0.1, "whoosh", 0.4)])
sc(122, "illus", img="img41", a=(0.5, 0.5, 1.3), b=(0.5, 0.5, 1.1),
   kw=[KW("REWRITE AI SOFTWARE FOR NEW CHIPS", 0.3, size=100, y=H * 0.84, style="plate", color=WHITE)])
sc((122, "who has"), "illus", img="img41", a=(0.35, 0.5, 1.7), b=(0.3, 0.5, 2.0),
   kw=[KW("WHO HAS MILLIONS OF ENGINEERS?", 0.1, size=100, y=H * 0.84, style="plate", color=YELLOW)])
sc(123, "india", glow=True, scale=21, cy=600, title="INDIA DOES.", title_size=170, title_y=540, fill=(70, 90, 70),
   sfx=[(0.05, "boom", 0.5), (0.1, "ding", 0.5)])

# =============================================================== 7. REBUILD
sc(124, "timeline", cur=3, title="MONTH 6", trans="slide", sfx=[(0, "whoosh", 0.6)])
sc(125, "illus", img="img42", a=(0.5, 0.5, 1.2), b=(0.5, 0.5, 1.0), grade="warm", trans="flash",
   kw=[KW("THE WORLD REBUILDS", 0.3, size=130, y=H * 0.84, style="plate", color=LIME)])
sc(126, "illus", img="img43", a=(0.3, 0.5, 1.2), b=(0.6, 0.5, 1.2),
   kw=[KW("AMD & GOOGLE: FULL SPEED", 0.2, size=110, y=H * 0.84, style="plate", color=WHITE)])
sc(127, "illus", img="img44", a=(0.5, 0.5, 1.0), b=(0.5, 0.55, 1.2),
   kw=[KW("NEW FACTORIES", 0.2, size=120, y=H * 0.84, style="plate", color=YELLOW)])
sc(128, "code", cues=dict(stop=999.0))
sc(129, "illus", img="img45", a=(0.3, 0.5, 1.4), b=(0.4, 0.5, 1.4),
   kw=[KW("SOME OF THE BEST IN THE WORLD", 0.3, size=100, y=H * 0.84, style="plate", color=WHITE)])
sc((129, "get hired"), "illus", img="img45", a=(0.75, 0.5, 1.4), b=(0.6, 0.5, 1.1),
   kw=[KW("HIRED BY RIVALS", 0.05, size=130, y=H * 0.84, style="plate", color=LIME)], sfx=[(0.05, "pop", 0.5)])
sc(130, "big", lines=[("THE KNOWLEDGE", "anton", 150, WHITE), ("DIDN'T VANISH.", "anton", 150, WHITE),
                      ("IT MOVED.", "anton", 200, LIME)], line_at=["l0", "l1", "l2"],
   cues=dict(l0=130, l1=(130, "vanish"), l2=131), bg="dark", sfx=[(131, "pop", 0.5)])
sc(132, "illus", img="img13", a=(0.5, 0.5, 1.3), b=(0.5, 0.5, 1.1), tint=(LIME, 0.12),
   kw=[KW("AI COMES BACK", 0.1, size=130, y=H * 0.15, style="plate", color=LIME),
       KW("SLOWER · MORE EXPENSIVE", "c", size=110, y=H * 0.84, color=YELLOW)], cues=dict(c=133))
sc(134, "big", lines=[("THE FUTURE:", "anton", 150, WHITE), ("PAUSED", "anton", 240, YELLOW)],
   bg="dark", stagger=0.3)
sc(135, "timeline", cur=4, title="YEAR 1", sfx=[(0, "whoosh", 0.5)])
sc(136, "towers", before="1 GIANT", after="5–6 CHIPMAKERS", cues=dict(split=(137, "five")), sfx=[((137, "five"), "pop", 0.5)])
sc(138, "illus", img="img46", a=(0.5, 0.5, 1.25), b=(0.5, 0.5, 1.0),
   kw=[KW("MORE COMPETITION", 0.1, size=130, y=H * 0.15, style="plate", color=LIME)])
sc(140, "illus", img="img46", a=(0.3, 0.6, 1.6), b=(0.6, 0.55, 1.6),
   kw=[KW("A STRONGER SYSTEM", 0.2, size=140, y=H * 0.84, color=WHITE)])

# =============================================================== 8. LESSON
sc(141, "big", lines=[("THE LESSON", "anton", 250, YELLOW)], bg="dark", trans="slide", sfx=[(0, "whoosh", 0.6)])
sc(142, "network", mode="spof", cues=dict(fail=(142, "single point")), sfx=[((142, "single point"), "boom", 0.5)])
sc(143, "illus", img="img47", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.15),
   kw=[KW("ONLY ONE BRIDGE", 0.3, size=130, y=H * 0.15, style="plate", color=WHITE)])
sc(144, "illus", img="img47", a=(0.5, 0.55, 1.5), b=(0.5, 0.55, 2.0), cues=dict(c=(144, "until")), shake_at=2.0, grade="crash", grade_at=1.8,
   kw=[KW("...UNTIL IT DOESN'T.", "c", size=140, y=H * 0.84, color=WHITE, style="plate")], sfx=[("c", "boom", 0.7)])
sc(145, "big", lines=[("THE TWIST", "anton", 260, RED)], style="stamp", bg="dark", sfx=[(-0.5, "riser", 0.4), (0.05, "boom", 0.4)])
sc(146, "illus", img="img48", a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.2),
   kw=[KW("NVIDIA DESIGNS THE CHIPS", 0.3, size=120, y=H * 0.84, style="plate", color=LIME)])
sc(147, "illus", img="img49", a=(0.5, 0.5, 1.2), b=(0.5, 0.5, 1.0), cues=dict(c=(147, "TSMC")),
   kw=[KW("TSMC MAKES THEM", "c", size=150, y=H * 0.84, style="plate", color=ORANGE)], sfx=[("c", "pop", 0.6)])
sc(148, "network", mode="chain", chain=["THE WORLD", "NVIDIA", "TSMC"], sfx=[(0.3, "pop", 0.4), (1.0, "pop", 0.4), (1.7, "pop", 0.4)])
sc(149, "illus", img="img50", a=(0.5, 0.5, 1.0), b=(0.5, 0.45, 1.25), cues=dict(c=(150, "next")),
   kw=[KW("WHICH COMPANY IS NEXT?", "c", size=140, y=H * 0.84, color=YELLOW)], sfx=[("c", "pop", 0.6)])
sc(151, "big", lines=[("TELL ME IN", "anton", 150, WHITE), ("THE COMMENTS ↓", "anton", 190, YELLOW)], bg="dark",
   note="Which company does the world depend on next?", note_at=0.6)
sc(152, "end", img="img51", lines=("SUBSCRIBE FOR MORE", "'WHAT IF' STORIES"), trans="slide", sfx=[(0, "whoosh", 0.5), (1.3, "pop", 0.6)])

# ---------------------------------------------------------------- finalize timing
SCENES.sort(key=lambda s: s["start"])
SCENES[0]["start"] = 0.0
for a, b in zip(SCENES, SCENES[1:]):
    a["end"] = b["start"]
SCENES[-1]["end"] = TOTAL

# corner time labels
LABELS = [(0.0, "7:00 AM"), (seg_start(10) - 0.1, "THE BASICS"), (seg_start(29) - 0.1, "12:00 AM"),
          (seg_start(32) - 0.1, "HOUR 1"), (seg_start(49) - 0.1, "DAY 1 · 9:30 AM"), (seg_start(69) - 0.1, "WEEK 1"),
          (seg_start(93) - 0.1, "INDIA"), (seg_start(124) - 0.1, "MONTH 6"), (seg_start(135) - 0.1, "YEAR 1"),
          (seg_start(141) - 0.1, "THE LESSON")]
NO_OVERLAY = [(seg_start(9) - 0.15, seg_start(10) - 0.15), (seg_start(152) - 0.15, TOTAL + 1)]

def sfx_events():
    ev = []
    for s in SCENES:
        for at, name, gain in s["sfx"]:
            if isinstance(at, str): t = s["cues"][at]
            elif isinstance(at, (int, tuple)) and not isinstance(at, bool): t = T(at)
            else: t = s["start"] + at
            ev.append((round(t, 3), name, gain))
    return sorted(ev)

if __name__ == "__main__":
    print(len(SCENES), "scenes;", f"total {TOTAL:.1f}s; avg {TOTAL/len(SCENES):.2f}s per scene")
    durs = [s["end"] - s["start"] for s in SCENES]
    print("longest:", sorted(((round(d, 1), s["kind"], s["p"].get("img", "")) for d, s in zip(durs, SCENES)), reverse=True)[:8])
    print("shortest:", sorted((round(d, 2), s["kind"]) for d, s in zip(durs, SCENES))[:5])
    imgs = sorted({s["p"]["img"] for s in SCENES if "img" in s["p"]} | {"img06", "img51"})
    print(len(imgs), "unique illustrations;", len([s for s in SCENES if s["kind"] in ("illus",)]), "illustration scenes")
    print(len(sfx_events()), "sfx events")
