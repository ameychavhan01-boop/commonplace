# Episode 01 — Michael Marcus: *The Trader Who Learned to Survive*

| File | Purpose |
|---|---|
| `dossier.md`, `claims.md`, `sources.md` | Research: timeline, 19 dimensions, claim register, source register |
| `outline.md`, `script.md`, `fact-check.md` | Chapter architecture, narration script with claim IDs, fact-check report |
| `audio/chNN.mp3` | Atlas narration (ElevenLabs, `eleven_v4`), one file per chapter |
| `build/parse_script.py` | script.md → `build/chapters.json` (narration + visual cues) |
| `build/align.py` | Sentence timing from pauses in the audio → `build/timeline.json` (subtitles, cues, audio layout) |
| `build/render_episode.py` | Renders the episode (scenes, chapter cards, subtitles, music bed, loudness-normalised mix) |

## Rebuild
```bash
python3 build/parse_script.py
python3 build/align.py
python3 build/render_episode.py --stills      # one preview still per scene
python3 build/render_episode.py --range 0 30  # short preview with audio
python3 build/render_episode.py               # full render → output/ (not committed; >100 MB)
```
Runtime ≈ 35 min. Narration ≈ 32.7 min. Rendering ≈ 45–60 min on 4 cores.
