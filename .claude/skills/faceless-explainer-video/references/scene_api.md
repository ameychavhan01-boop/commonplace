# Writing a video: narration.py, plan.py, doodle_scenes.py

Contents: 1. Project layout · 2. narration.py · 3. plan.py (timing helpers, scene list, overlays, SFX) ·
4. Scene types · 5. doodle_scenes.py · 6. Gotchas

The fastest route is to copy `examples/nvidia/{narration,plan,doodle_scenes,images}.py` into the project
and rewrite the content while keeping the structure.

## 1. Project layout
```
<project>/
  *.py, *.sh            copied from the skill's scripts/
  narration.py          what is said (you write)
  plan.py               what is shown, when (you write; copy the example's helpers + bottom section)
  doodle_scenes.py      one cartoon per illustration id (you write)
  images.py             optional AI-image prompts (only if paid image credits exist)
  timings.json          written by make_voice.py (sentence start/end in seconds)
  illustrations/        optional imgNN.png AI art; a PNG wins over the doodle
  work/                 intermediate audio/video
  deliverables/         final files (build_all.sh)
```
Scripts import each other from the current folder, so always run them from the project folder.
`VIDEO_ASSETS` must point at the folder `setup.sh` filled (default `~/.video_assets`).

## 2. narration.py
```python
SEGMENTS = [  # (section, text, pause_after_s, speed_factor)  speed < 1 = slower (use 0.9 on big numbers)
  ("hook", "It's 7 AM.", 0.55, 1.0),
  ("hook", "And it all happened because one company, worth about three trillion dollars, disappeared overnight.", 0.9, 0.9),
  ...
]
CHAPTERS = {"hook": "The morning NVIDIA disappears", ...}          # YouTube chapter names per section
SECTION_MOOD = {"hook": "tense", "what": "curious", ...}           # music: tense, curious, dark, tension, drive, warm, hopeful, reflective
SUB_FIX = [("S and P 500", "S&P 500"), ("twenty twenty-six", "2026")]   # spoken -> written in subtitles
```
- Split long sentences into several segments: every segment is a possible picture change and its own
  subtitle line.
- Write years in words ("twenty twenty-six") so they're said as a year; other digits are spelled
  automatically by `tts.speakable`.
- Pauses: 0.3–0.4 s between quick phrases, 0.6 s normal, 0.9 s after a dramatic line, 1.1 s at a section end.
  `make_voice.py` scales them (×0.6 by default).

## 3. plan.py
Keep the example's top part (imports, `TIMINGS`, `VO=0.4`, `END_DUR=10`, `TOTAL`, `seg_start`, `word_t`,
`T`, `sc`, `KW`, `BADGE`) and bottom part (sorting/end times, `LABELS`, `NO_OVERLAY`, `sfx_events`,
`__main__` stats). Replace only the scene list in the middle.

### Timing references (`at`, cues, sfx times)
| form | meaning |
|---|---|
| `12` (int) | start of narration segment 12 (scene starts 0.12 s early) |
| `(12, "word")` | the moment segment 12 reaches "word" (estimated from character position) |
| `(12, "word", True)` | just after "word" |
| `3.5` (float) | absolute seconds (in `cues`), or seconds after scene start (in `sfx`/`kw`) |
| `"name"` (str) | a named cue from this scene's `cues=dict(name=...)` |

```python
sc(6, "illus", img="img05", a=(0.5, 0.45, 1.3), b=(0.5, 0.5, 1.0),
   cues=dict(n=(6, "worth")),
   kw=[KW("$3 TRILLION", "n", size=190, y=H * 0.42, sub="market value · 20 Nov 2026")],
   sfx=[("n", "pop", 0.8)])
```
`sc(at, kind, sfx=[(at, name, gain)], cues={}, lead=0.12, trans="fade"|"slide", **params)`. Use
`trans="slide"` (+ a whoosh) for the first scene of each section.

**SFX names:** whoosh, whoosh_down, pop, click, boom, powerdown, glitch, ticker (counting), riser, ding.
Gains 0.3–0.8. Pop on keywords and numbers, boom on shocking facts, ticker under count-ups.

**Overlays:** `BADGE = "THOUGHT EXPERIMENT"` (or None) top-left. `LABELS = [(time, "7:00 AM"), ...]`
top-right time/section labels. `NO_OVERLAY = [(start, end)]` hides both, e.g. on the title card and end screen.

**KW (keyword) items:** `KW(text, t, size=120, y=H*0.84, x=W/2, color=YELLOW, style="stroke"|"plate",
sub="small line under", rot=0)`. Plate = dark box behind the text, best for captions on busy art.

## 4. Scene types (`kind`)
| kind | key params | use for |
|---|---|---|
| `illus` | `img`, `a`/`b` = (x, y, zoom) start→end camera, `kw`, `shake_at`, `tint=(color, amt)` | story moments (AI art or doodle) |
| `big` | `lines=[(text, font, size, color)]`, `bg` dark/paper, `style` pop/glitch/stamp/type, `note`, `note_at`, `underline`, `line_at=[cue,...]` | punchy words: "NOTHING.", "DAY 1", "THE TWIST" |
| `counter` | `value`, `prefix`, `suffix`, `decimals`, `final` (text shown at the end), `label`, `sub`, `color`, `size`, `y`, `count_dur`, cue `num`, `stamp`, `grid=dict(n, cols, cell, y0)` | big numbers counting up |
| `bars` | `title`, `items=[(label, value, color, "value text")]`, `max`, `note`, `callout` + cue `callout`, cues `bar0`, `bar1` | comparisons (company vs GDP) |
| `pie` | `share` 0..1, `big`, `label`, `note`, `color`, `bg`, cue `remove` + `remove_text` (slice flies off) | shares (~80%, ~5% of index) |
| `line` | `points=[(label, value)]`, `ymin`, `ymax`, `grid`, `xticks`, `title`, `source`, cues `draw0`/`draw1`, `kmin`/`kmax` (reveal part of the line), `ann=[dict(text, t, x, y, size, color)]` | real price/market-value history |
| `india` | `draw` (outline draws on), `glow`, `fill`, `scale`, `cx`, `cy`, `title`, `title_y`, `pins=[(city, label, cue)]`, `chip=(x, y)` (wires to a chip), `cards=[dict(title, text, t, x, y)]` | India section; cities in `scenes_lib.CITIES` (add lon/lat for new ones) |
| `world` | `mode` pulses (markets) / darkwave (lights going off) / flows (money leaving India) / zoom_india, `title`, `note` | global effects |
| `chip` | `mode` gpu (`caption`) / parallel (cue `big`) / engine / dissolve (`word`, `label`, cues `go`, `label`) / darkchips (cue `off`) / price (`label`) | tech explainer beats |
| `cards` | `cards=[dict(title, text, color, size, t)]`, `title`, `card_h`, `stamp`, `note`, `bg` | lists of names / reasons |
| `timeline` | `steps=[...]`, `cur` (highlighted index), `title` | "HOUR 1 → … → YEAR 1" roadmaps |
| `code` | cue `stop` (typing stops, "CONNECTION LOST") | software stopping / rewriting |
| `tiles` | `title`, `note`, cue `off` | many services going dark |
| `progress` | cue `stop` | slowing down → stopped |
| `network` | `mode` spof (cue `fail`) / chain (`chain=[a, b, c]`) | dependency, single point of failure |
| `towers` | `before`, `after`, cue `split` | one giant → many players |
| `title` | `img`, `lines=[(text, color, size)]` (1–3 lines) | title card (~3 s, after the hook) |
| `end` | `img`, `lines=(line1, line2)` | 10 s end screen with 2 empty video frames + subscribe dot |

Colours from gfx: `INK, DARK, PAPER, RED, YELLOW, LIME, TEAL, ORANGE, BLUE, WHITE, SAFFRON, INGREEN`.
Fonts: `anton` (big condensed), `xbold`/`bold`/`semi`/`black` (Poppins), `hand` (Patrick Hand notes).
Canvas is 1920×1080 (`W`, `H`).

## 5. doodle_scenes.py
```python
from gfx import *
from doodles import *

def d_bedroom(f, t, fi):            # f = 1920x1080 RGB frame (paper or dark bg already drawn), t = seconds into scene
    sun(f, 1560, 260, 80, fi, t)
    box(f, 220, 560, 1050, 760, (150, 120, 200), INK, 7, fi, r=30, seed=1)
    person(f, 520, 590, 1.1, (240, 200, 120), "neutral", fi, 3)
    clock(f, 1420, 520, 90, 7, 0, fi, t, seed=6)

DOODLES = {"img01": d_bedroom, ...}       # every img id used in plan.py
NIGHT = {"img12", ...}                     # ids drawn on the dark background
DOODLE_KW = {"img01": "7:00 AM"}           # caption for doodle scenes that have no kw of their own
```
Building blocks in `doodles.py`: `person(f, x, feet_y, scale, shirt, mood=neutral|happy|sad|shock, fi, seed,
skin=SKIN|SKIN2, arms=down|up, t)`, `phone(..., screen=spinner|redchart|pie|game|alert|dark)`,
`laptop(..., screen=spinner|glitch|code|chip|blank)`, `clock(f, x, y, r, hh, mm, ...)`, `rack`, `racks_scene`,
`building`, `skyline(f, fi, lit, base, seed, skip)`, `sun`, `moon`, `factory(f, x, base, s, fi, t, running)`,
`money`, `question`, `screen_box(..., content=blank|blank_dark|molecule|cross|redchart)`; from gfx: `box`,
`poly`, `circle_pts`, `rect_pts`, `rrect_pts`, `arrow`, `glow`, `chip`, `put_text`.
- Keep the main drawing between y≈150 and y≈850: the bottom strip is where captions sit.
- Animate gently with `t` (blinking lights, rising arrows, falling dominoes, people waving).
- Draw generic people with dot eyes; use `SKIN2` for Indian characters in the India section.
- Render all doodles to a contact sheet and look at it before the full render.

## 6. Gotchas (learned the hard way)
- Never write `$`-numbers into narration; write words ("three trillion dollars"). On screen, digits are fine.
- Anton has ↓ and →; no font has emoji, ✓ or ⏸. Write words or draw the shape instead.
- Titles and charts must sit at y ≥ 150 or they collide with the badge and time label.
- If the voice is slower than planned, scenes stretch: re-run `python plan.py` after every voice change
  and split scenes longer than ~6 s.
- Encode to a temp file, verify (`ffmpeg -v error -i f -f null -`), then move it into place.
- Chat file-send limits are low: keep videos you send under ~250 MB.
