"""Final audio mix: narration + ducked music + SFX, mastered to -14 LUFS / -1.5 dBTP.
usage: python mix.py VOICE.wav MUSIC_SFX_DIR OUT.wav"""
import json, subprocess, sys
import numpy as np, soundfile as sf
from scipy.signal import butter, sosfilt, resample_poly
import plan

SR = 48000
voice_p, adir, out = sys.argv[1], sys.argv[2], sys.argv[3]
n = int((plan.TOTAL + 0.5) * SR)

v, sr = sf.read(voice_p)
if v.ndim > 1: v = v.mean(1)
assert sr == SR
voice = np.zeros(n); i0 = int(plan.VO * SR); voice[i0:i0 + len(v)] = v[:n - i0]

music, _ = sf.read(f"{adir}/music.wav")
mus = np.zeros((n, 2)); mus[:min(n, len(music))] = music[:n]
# carve a little space for the voice (gentle dip 1-4 kHz) and remove sub rumble
mus = sosfilt(butter(2, 45, 'hp', fs=SR, output='sos'), mus, axis=0)
from scipy.signal import iirpeak
mid = sosfilt(butter(2, [1000, 4000], 'bp', fs=SR, output='sos'), mus, axis=0)
mus = mus - 0.35 * mid

# ---- ducking: envelope follower on the voice
def rms_db(x): return 20 * np.log10(np.sqrt(np.mean(x ** 2)) + 1e-9)
hop = 480
frames = voice[: len(voice) // hop * hop].reshape(-1, hop)
env = np.sqrt((frames ** 2).mean(1))
active = (env > 0.01).astype(float)
sm = np.zeros_like(active); a_att, a_rel = 1 - np.exp(-1 / 8), 1 - np.exp(-1 / 45)   # ~80 ms attack, ~450 ms release
for k in range(1, len(active)):
    a = a_att if active[k] > sm[k - 1] else a_rel
    sm[k] = sm[k - 1] + a * (active[k] - sm[k - 1])
duck = np.repeat(sm, hop); duck = np.pad(duck, (0, n - len(duck)), constant_values=duck[-1])

speech_db = rms_db(voice[voice != 0][np.abs(voice[voice != 0]) > 0.01])
mus_db = rms_db(mus.mean(1))
under = 10 ** ((speech_db - 21 - mus_db) / 20)   # music 21 dB under speech while talking
gaps = 10 ** ((speech_db - 13 - mus_db) / 20)    # 13 dB under in pauses / title / end screen
mgain = gaps + (under - gaps) * duck
mus = mus * mgain[:, None]

# ---- SFX
sfx = np.zeros((n, 2)); cache = {}
for t, name, gain in plan.sfx_events():
    if name not in cache:
        x, _ = sf.read(f"{adir}/sfx_{name}.wav"); cache[name] = x
    x = cache[name] * gain * 0.32
    j = int(t * SR); L = min(len(x), n - j)
    if L > 0 and j >= 0:
        sfx[j:j + L, 0] += x[:L]; sfx[j:j + L, 1] += x[:L]

mixd = mus + sfx + voice[:, None]
peak = np.abs(mixd).max()
if peak > 0.98: mixd *= 0.98 / peak
tmp = out + ".pre.wav"
sf.write(tmp, mixd.astype(np.float32), SR, subtype="FLOAT")
r = subprocess.run(["ffmpeg", "-i", tmp, "-af", "loudnorm=I=-14:TP=-1.5:LRA=9:print_format=json", "-f", "null", "-"],
                   capture_output=True, text=True)
m = json.loads(r.stderr[r.stderr.rindex("{"):])
ln = (f"loudnorm=I=-14:TP=-1.5:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
      f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", ln + ",aresample=48000", "-c:a", "pcm_s16le", out], check=True)
print("speech", round(speech_db, 1), "dB; music under/gap gain", round(20 * np.log10(under), 1), round(20 * np.log10(gaps), 1))
