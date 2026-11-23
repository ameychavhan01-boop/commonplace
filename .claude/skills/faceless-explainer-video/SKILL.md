---
name: faceless-explainer-video
description: Produce a complete, upload-ready faceless YouTube explainer video end-to-end (research with sources, script, free Kokoro narration, original music and sound effects, code-drawn cartoon illustrations and animated charts, 1080p MP4, subtitles, thumbnail and YouTube title/description/tags). Use this skill whenever the user asks to make, create or produce a YouTube video, a "What If" video, a business/finance/tech explainer, a faceless channel video, a video about a company, stock, country or economic event, or says things like "make a video on X", "next video", "same as last video" — even if they don't mention YouTube, scripts or animation explicitly.
---

# Faceless explainer video: full pipeline

This skill turns one topic into a finished video plus everything needed to upload it. It was built with
a real channel owner who has **no coding or editing skills**, so do every step yourself, explain progress
in one short line per stage, and hand over finished files, not instructions.

What the user approved on the first video (treat as defaults unless they say otherwise):

| Area | Default |
|---|---|
| Format | 1920x1080, 30 fps, H.264 + AAC, 6–8 min |
| Voice | Kokoro TTS (free, Apache-2.0), voice `am_michael`, speed 0.97, US English, generated sentence by sentence, numbers spelled out |
| Music | The original **cinematic score** in `audio_gen.py` (moods follow the story). The user rejected lo-fi. |
| Mix | Music **18 LU under the voice** (pro reference ≈ 20; the first video used 11); master and voice-only both at **−15 LUFS, true peak −2 dB** |
| Visuals | **Pro style** (see `references/pro_style_guide.md`): new picture every ~3.5 s, camera pushing on almost every shot, black handwritten text cards every 15–25 s, lighting moods per scene, expressive cartoon cast in rich little worlds, data drawn as objects, hand-lettered marker labels; corner badge + time labels |
| Paid AI art | Optional only. If ElevenLabs (or any paid tool) has no credits, don't wait: use the doodles |
| Style | Simple English a 12-year-old understands, "you", short sentences; no politics, no stock tips, no real logos/photos |

The user values **speed**: they said "make the video fast, I want it now". Keep momentum, avoid long
detours, don't re-ask settled questions, and render in the background while doing other work.

## Workflow

Create a project folder (e.g. `<repo>/<topic_slug>/`). Copy the scripts in and run setup once:

```bash
SKILL=<path to this skill>
mkdir -p <project> && cp $SKILL/scripts/* <project>/
export VIDEO_ASSETS=$HOME/.video_assets     # models, fonts, map data (shared across videos)
bash <project>/setup.sh                    # ~360 MB first time; free, commercial-use licences
```

Then work through the stages. Read `references/pro_style_guide.md` (what makes the user's reference
video look professional, with measured targets) and `references/scene_api.md` (every scene type and the
files you need to write) before writing the script and plan. `examples/nvidia/` is a complete approved video.

### 1. Research (save every fact with a link)
- Use web search (and the TradingView MCP when available, for prices) to collect current facts. Write
  `sources.md`: a table of fact, value, source links.
- Never invent numbers. If sources disagree, use the cautious figure ("about", "estimated") and say why.
- **Compute market values yourself**: last close × shares outstanding (from the latest 10-Q/annual report
  cover). Headlines lag by days; on the first video, reports said $3.9T while the true value was $3.0T.
- Check leadership and recent news (CEO changes, investigations). Keep political, legal and personal
  scandals out of the script, but mention them to the user once so they're not surprised.
- If the user hands you numbers that disagree with the data, show them the calculation politely and
  use the verified figure.

### 2. Script, then wait for OK
- ~1,000–1,100 spoken words. With `am_michael` at 0.97 the measured pace is ~137 wpm including pauses,
  so 1,000 words ≈ 7.3 min and 1,150 words ≈ 8.4 min. Size the script to land inside 6–8 min.
- Structure that worked: hook with the biggest number in the first 15 s → simple explanation (analogies)
  → a timeline (Hour 1, Day 1, Week 1 …) → a dedicated India section (the audience) → recovery →
  lesson + twist + a comment question → "subscribe" line.
- Write for the pro rhythm: short punchy lines that can stand alone on a black text card (questions,
  "Not yet.", chapter names), a concrete metaphor for every abstract idea, a recurring set or motif,
  an ordinary-person "what this means for you" scene, and an ending that calls back to the opening image.
- Show the script and **wait for the user's OK** before generating anything expensive. When they ask for
  fixes, reply with only the changed lines.

### 3. Narration
Write `narration.py` (one entry per sentence or phrase, with a pause and a speed factor), then run
`python make_voice.py` (defaults: am_michael, 0.97, pauses ×0.6). It writes `work/voice/narration.wav`
plus `timings.json`, the exact start and end of every sentence, which drives all picture timing.
- `tts.speakable()` spells out numbers; add any mispronounced names to the `IPA` dict in `tts.py` and
  check them with `tts.to_phonemes(text, "en-us")`. Indian place names and NVIDIA/CUDA/TPU are already fixed.
- QC: per-sentence speaking rate outliers, no gaps > 0.7 s inside a sentence, loudness near −15 LUFS.
- If the user asks to hear voices, render 3–4 candidates on the first two sentences and send the clips.

### 4. Plan the pictures
Write `plan.py` (scene list keyed to narration segments and words) and `doodle_scenes.py`
(one drawing per illustration id), as described in `references/scene_api.md`.
- Run `python plan.py`: aim for an average of ≤ 3.5 s per scene. Split any static scene longer than ~6 s at
  a word cue (animated charts and map pins can run a little longer).
- Apply the pro checklist: ~1 `text` card per 15–25 s on the punchiest lines; `grade=` on every scene
  whose mood isn't neutral (crash red, boom green, night, sepia history, warm hope); `trans="burst"` on
  2–5 shock reveals; characters with emotion (`mood`, ties, glasses); labels on objects in `marker` font;
  white/yellow text on a plate over red or busy scenes.
- Every on-screen number must match `sources.md`; label estimates "estimated" and dates "as of …".
- India maps use the Natural Earth **India point-of-view** borders (from setup.sh). Never draw India's
  borders any other way.
- Names of companies as plain text are fine; never draw logos or real people.

### 5. Look before you render
```bash
python render.py stills work/stills 1 25 60 120 200 300 400 480   # pick times across the video
```
Tile them into a contact sheet (ffmpeg `tile=4x2`) and inspect: text overlapping corner labels (keep
titles at y ≥ 150), labels cut off at edges, overlapping chart labels, mid-animation glitches. Also run a
glyph audit: the fonts lack emoji, ✓ and ⏸, and Poppins has no arrows (Anton has ↓ and →).

### 6. Audio + full render + encode (one command)
```bash
THUMB_TOP="NVIDIA" THUMB_BIG="GONE?" THUMB_TAG="WHAT IF..." bash build_all.sh
```
This makes the score and sound effects, mixes to −15 LUFS / −2 dBTP, renders (~2× real time on 4
cores; run it in the background), encodes **final_video_1080p.mp4 (~3.3 Mbps)**, **final_video_720p.mp4**
and a voice-only copy, builds `thumbnail.jpg` and `subtitles.srt`, and checks that every MP4 decodes
with zero errors. Never let two encoders write the same output file: the first video got corrupted that way.

### 7. YouTube details
Write `youtube_details.txt`: final title + 2 alternatives, description (summary, "thought experiment,
not financial advice", chapters with real timestamps from `timings.json`, starting 0:00, each ≥ 10 s),
source links, credits line (original music/art, synthetic voice), 15 tags, a pinned-comment question, and
an upload checklist (subtitles upload, end-screen start time = total − 10 s, synthetic-content answer).
Keep the description under 5,000 characters.

### 8. Deliver
- The chat file-send limit is small (one upload over ~470 MB failed). Send the **720p first, then
  the 1080p** (each well under 250 MB), then thumbnail, srt, details, sources. Send videos one per call so
  one failure doesn't block the others. If a send fails, re-encode smaller instead of retrying.
- Tell the user which file to upload and the 5–6 upload steps in plain words.
- Commit code and text files to the branch; keep `*.mp4` out of git (GitHub's limit is 100 MB per file).

## Optional: AI illustrations
If the user has paid image credits (e.g. the ElevenLabs connector), generate the `images.py` prompts (one
fixed style prompt + scene text, "no text, no logos, no real people", 16:9, 1 generation each; about 211
credits per image) and save them as `illustrations/imgNN.png`. The renderer automatically prefers a PNG
over the doodle. First test with a single image: a failed generation costs nothing and tells you the
balance. If credits run out, finish with doodles. The user explicitly prefers a finished video now over
waiting.

## Files in this skill
- `scripts/`: the pipeline. `setup.sh` (assets), `make_voice.py` + `tts.py` (narration), `audio_gen.py`
  (score + SFX), `mix.py`, `gfx.py` (drawing kit), `doodles.py` (cartoon building blocks),
  `scenes_lib.py` (scene types), `render.py`, `make_subs.py`, `make_thumb.py`, `build_all.sh`.
- `references/scene_api.md`: how to write `narration.py`, `plan.py` and `doodle_scenes.py`; every scene type.
- `references/pro_style_guide.md`: study of the user's pro reference video, with measured pacing, camera,
  colour, sound, characters, text cards and thumbnail rules, and how our code reproduces each.
- `examples/nvidia/`: the approved first video ("What If NVIDIA Vanished Tomorrow?"): script, sources,
  narration, plan, doodle scenes, image prompts, YouTube details. Copy and adapt rather than starting blank.
