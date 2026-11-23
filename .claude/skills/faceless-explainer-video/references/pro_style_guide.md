# Pro style guide (from a frame-by-frame study of a top finance-explainer video)

The user supplied a reference video in the target style: a 15-minute cartoon finance explainer about
NVIDIA and an "AI bubble" (CEOzoned / Paper Billions-type channel). It was analysed in Nov 2026 with scene-cut
detection, 239 shot frames, colour, camera-motion and audio measurements. Use this guide when planning
every video. The goal is to make ours feel like that: rich little cartoon worlds, constant motion,
a rhythm of picture → punchline card → picture.

Contents: 1. Numbers to hit · 2. Story rhythm · 3. Characters · 4. Worlds & lighting · 5. Data as objects ·
6. Text & labels · 7. Camera & transitions · 8. Sound · 9. Thumbnail · 10. How our code does each

## 1. Numbers to hit (measured)
| metric | reference | our target |
|---|---|---|
| shot length | mean 3.8 s, median 3.2 s; 70% of shots 2–5 s; 12–21 cuts every minute | same; split anything static > 6 s |
| black text cards | 18% of shots, ~2.7 s each, one every ~17 s | 1 every 15–25 s |
| camera | moves in 91% of shots; push-in 64% / pull-out 23%; ~4%/s zoom (≈15% over a shot) | `push` 0.12–0.2 per shot, mostly in |
| brightness | mean 127/255; 21% of shots dark (night/crash), 39% bright | mix dark and bright scenes; never all-dark |
| palette | saturated pixels: blue 29%, green 27%, orange 22%, red 10%, yellow 7% | blue/green/orange base, red only for danger |
| loudness | −14.6 LUFS, very even (LRA 2.3), peak −3 dB | −15 LUFS, −2 dBTP (user's spec) |
| music | always present, ~20 dB under the voice (bed −36 dB vs speech −16 dB) | `MUSIC_UNDER` 18 (default) |
| pauses | short: median 0.33 s, ~17 per minute | keep narration tight; long pauses only before reveals |

## 2. Story rhythm
- **Cold open in 5 s**: the hero image (glowing chip, worried mascot), a comic speed-line burst, then the
  title + the shock number ("NVIDIA −$400B") on screen by second 4. No slow intro.
- **Text-card beats**: the narrator's key line appears alone as white handwriting on black ("Nobody",
  "So why did the stock…", "The Cracks", "Did the Bubble Pop?"). They do three jobs: punchline,
  question that pulls the viewer forward, and **chapter title** ("The Midterms", "The One-Day Party").
- **Recurring sets**: one location is built once and revisited (the trading floor appears ~10 times:
  green and celebrating on "WEDNESDAY", red and panicking on "THURSDAY"; a bank street at night; a family
  kitchen). Same set + different lighting/props = continuity and cheap production.
- **Recurring motifs/callbacks**: a green balloon + stopwatch = "the bubble"; a glass sphere of chips; the
  glowing chip on a cliff opens **and closes** the video (bookend).
- **Concrete metaphors for every abstract idea**: debt = a weighing scale tipping; profits = a smiling
  green blob bar; "circular financing" = two characters passing one money bag; rules = an empty lectern
  labelled "RULE: (NONE)"; history = sepia railway-mania flashback.
- **Time anchors**: day tags bottom-left ("WEDNESDAY", "THURSDAY"), wall clocks with "10:33 AM ET",
  calendar pages ("5 NOV").
- **Ordinary-person angle**: a family kitchen, an electric bill, a retirement fund on a phone (POV hands):
  the "what does this mean for you" scenes.

## 3. Characters
- Big round heads (~40% of body height), tiny bean bodies, thin stick legs with round feet, mitten hands.
- Eyes: dots when calm; **big white eyes with small pupils when shocked/worried**. **Eyebrows carry the
  emotion**, plus sweat drops for worry, and an open "O" mouth for shock.
- Archetype cast with costume cues: executives (dark suit, red tie), traders (shirt + tie, arms up),
  workers (hard hats), politicians (podium), ordinary people (casual colours), personified objects
  (a building with a face, a cloud with eyes, a dog barking "WOOF!").
- Characters are small in the frame (¼–⅓ height). The **world** is the star; characters act in it.
- The reference uses a caricature of the real CEO as a mascot. **Our default avoids likenesses of real
  people** (user's rule); use an invented archetype mascot unless the user explicitly asks otherwise.

## 4. Worlds & lighting
- Full environments with depth: street facades with signs, office interiors with windows to a skyline,
  diners, trading floors with ticker boards, ports with crates, maps on desks, the Capitol.
- **Lighting moods** grade whole scenes: night blue with warm lit windows; green glow for euphoria and
  chips; **red alarm tint** for crashes; golden sunset for hope or a peak; sepia for history.
- Practical light: lamps casting a spotlight pool on the floor, screens lighting faces, rim glow around
  the hero object. Soft vignette on almost every shot.
- Subtle paper/grain texture; flat colours with gentle shading; dark brown/near-black outlines.

## 5. Data as objects (not bare charts)
- Line charts drawn **in the world**: a character rides the curve over a sunset landscape; a price line
  over a city of bars; whiteboard charts with marker labels.
- Bars with faces, money piles, vault dials, gauges ("VIX"), scales, pie charts on a table that a
  character slices, a magnifying glass over the key number.
- Documents as evidence: earnings-call transcript card with the quote highlighted, a newspaper front page
  ("THE CAPITOL LEDGER" + quote), a social-media post card, a news broadcast lower-third with ticker.
- Maps: simple flat colours, a pin + label, stacks of tags piling up on states.

## 6. Text & labels
- **Hand-lettered marker** for every in-scene label and number ("THE AI BUBBLE?", "$1.2T", "−$776B").
  Ours: font `marker` (Permanent Marker) for labels, `script` (Caveat) for text cards.
- Labels sit on objects (signs, boxes, tags) or in small dark plates, rarely floating.
- Lower-thirds for names/roles ("MICHAEL BURRY, called the 2008 crash").
- Readability: on red-graded or busy scenes use white/yellow text on a dark plate, never red on red.

## 7. Camera & transitions
- Almost every shot moves: slow push-in (most), pull-outs to reveal, pans across wide sets.
- Mostly **hard cuts**; accents: **comic speed-line burst** on shocks, **white flash / fog** for a time
  skip, the same set re-cut from a closer angle for emphasis.

## 8. Sound
- One continuous music bed, low (~20 dB under speech), never dropping to silence.
- Narration delivered tightly with short pauses; the text cards land on the key line.

## 9. Thumbnail
- One huge expressive character (≈40% of the frame) in peril (clinging to a cracking glowing chip on
  a cliff), dark dramatic background with a single strong glow colour.
- **Two text blocks max**: company name in white + the shock number in red ("NVIDIA −$400B"), heavy sans,
  top of frame, readable at phone size.

## 10. How our code does each
| technique | how |
|---|---|
| text-card beats | `sc(i, "text", text="So who steps in?")`; chapter titles: `chapter=True` |
| lighting moods | any scene: `grade="crash"|"boom"|"night"|"sepia"|"warm"|"cold"`, `grade_at=` to fade it in |
| shock accent | `trans="burst"` (speed lines) on the reveal scene; `trans="flash"` for time skips |
| camera push | doodle/illus scenes push 16% by default; `push=0.2` for drama, `b` zoom < `a` zoom for a pull-out |
| expressive cast | `person(..., mood="worried"|"shock"|"angry"|"happy"|"sad", tie=RED, glasses=True, hair=...)` |
| spotlight | in a doodle: `f[:] = spotlight(f, cx, cy, rx, ry)` |
| recurring set | write one doodle function with state params (e.g. `mood`), reuse it across sections with different `grade` |
| marker labels | `KW(...)` now defaults to the `marker` font; use `style="plate"` on busy/graded scenes |
| music level | `MUSIC_UNDER=18` (default; reference ≈ 20) |
