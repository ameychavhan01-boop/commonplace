# Market Wizards — Style Sample 01

A 2-minute visual-identity test: JSR logo sting → cold open → series title → chapter card → an animated lesson on risk per trade and position sizing.

- Video: `output/market-wizards-sample-01.mp4`
- Script and timecodes: `narration-script.md`
- Preview stills: `output/stills/`

## Re-render
```bash
python3 render.py            # full video (~1.5 min on 4 cores)
python3 render.py --stills   # quick preview frames only
```
Requires Python 3 with Pillow and NumPy, plus ffmpeg with libx264.

## Swapping in the real JSR logo
Save the logo as `assets/jsr_logo.png` and re-render. A square PNG works best; transparent or black backgrounds are both fine. The renderer fits the logo inside the round frame automatically.
