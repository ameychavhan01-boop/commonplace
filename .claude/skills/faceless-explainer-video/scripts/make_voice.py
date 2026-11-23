"""Render the full narration.  usage: python make_voice.py [voice=am_michael] [speed=0.97] [outdir=work/voice] [pause_scale=0.6]
Run inside the project folder (needs narration.py). Writes narration.wav (-15 LUFS), narration_raw.wav, timings.json."""
import json, sys
from pathlib import Path
import soundfile as sf
sys.path.insert(0, str(Path(__file__).parent))
import tts
from narration import SEGMENTS

voice = sys.argv[1] if len(sys.argv) > 1 else "am_michael"   # user-approved default
if voice == "deep_blend":
    voice = {"am_michael": 0.6, "am_onyx": 0.4}
speed = float(sys.argv[2]) if len(sys.argv) > 2 else 0.97
out = Path(sys.argv[3] if len(sys.argv) > 3 else "work/voice")
out.mkdir(parents=True, exist_ok=True)

PAUSE_SCALE = float(sys.argv[4]) if len(sys.argv) > 4 else 0.6
segs = [dict(id=i, section=s, text=t, pause=p * PAUSE_SCALE, speed=v) for i, (s, t, p, v) in enumerate(SEGMENTS)]
audio, timings = tts.synth(segs, voice, base_speed=speed)
for t, s in zip(timings, segs):
    t["section"] = s["section"]
sf.write(out / "narration_raw.wav", audio, tts.SR)
tts.polish(out / "narration_raw.wav", out / "narration.wav", lufs=-15.0)
json.dump(timings, open(out / "timings.json", "w"), indent=1)
words = sum(len(s["text"].split()) for s in segs)
dur = timings[-1]["end"]
print(f"{dur:.1f}s  ({dur/60:.2f} min)  {words} words  {words/(dur/60):.0f} wpm")
