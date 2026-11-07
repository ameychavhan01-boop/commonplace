"""Generate narration chunk by chunk (between {n} beat markers) with Kokoro, and record real durations.
Usage: python tts.py BUILD_DIR MODEL_DIR [scene_id ...]"""
import os, re, sys, json, hashlib, time
import numpy as np, soundfile as sf
from kokoro_onnx import Kokoro
from script_p1 import SCENES
from speech import spoken

VOICE, SPEED, LANG = "am_michael", 0.97, "en-us"

def chunks_of(text):
    parts = re.split(r"\{(\d+)\}", text)
    out = [parts[0]]
    for i in range(1, len(parts), 2):
        assert int(parts[i]) == len(out), f"marker order {parts[i]}"
        out.append(parts[i + 1])
    return [p.strip() for p in out]

def trim(a, sr, thr_db=-42):
    if len(a) == 0: return a
    env = np.abs(a)
    thr = 10 ** (thr_db / 20) * max(1e-6, env.max())
    idx = np.where(env > thr)[0]
    if len(idx) == 0: return a
    s = max(0, idx[0] - int(0.02 * sr)); e = min(len(a), idx[-1] + int(0.06 * sr))
    return a[s:e]

def main():
    build, models = sys.argv[1], sys.argv[2]
    only = set(sys.argv[3:])
    os.makedirs(f"{build}/tts", exist_ok=True)
    k = Kokoro(f"{models}/kokoro-v1.0.onnx", f"{models}/voices-v1.0.bin")
    tpath = f"{build}/timing.json"
    timing = json.load(open(tpath)) if os.path.exists(tpath) else {}
    t0 = time.time()
    for sc in SCENES:
        if only and sc["id"] not in only: continue
        ch = chunks_of(sc["text"])
        rec = []
        for i, disp in enumerate(ch):
            sp = spoken(disp)
            h = hashlib.md5(f"{VOICE}|{SPEED}|{sp}".encode()).hexdigest()[:10]
            fn = f"{build}/tts/{sc['id']}_{i:02d}_{h}.wav"
            if not os.path.exists(fn):
                a, sr = k.create(sp, voice=VOICE, speed=SPEED, lang=LANG)
                a = trim(np.asarray(a, dtype=np.float32), sr)
                sf.write(fn, a, sr)
            info = sf.info(fn)
            rec.append(dict(file=fn, display=disp, spoken=sp, dur=info.frames / info.samplerate))
        timing[sc["id"]] = rec
        json.dump(timing, open(tpath, "w"), indent=1)
        tot = sum(r["dur"] for r in rec)
        print(f"{sc['id']:7s} chunks={len(rec):2d} voice={tot:6.1f}s  elapsed={time.time()-t0:6.0f}s", flush=True)

if __name__ == "__main__":
    main()
