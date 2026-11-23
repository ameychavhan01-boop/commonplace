"""Final audio mix: narration + lo-fi music (about 11 dB under the voice) + subtle SFX.
Master and the voice-only version are both normalised to -15 LUFS, true peak about -2 dB.
usage: python mix.py VOICE.wav MUSIC_SFX_DIR OUT_MIX.wav OUT_VOICE_ONLY.wav"""
import json, subprocess, sys
import numpy as np, soundfile as sf
import pyloudnorm as pyln
from scipy.signal import butter, sosfilt
import plan

SR = 48000
LUFS, TP = -15.0, -2.0
MUSIC_UNDER = 11.0        # LU below the voice
voice_p, adir, out_mix, out_vo = sys.argv[1:5]
n = int((plan.TOTAL + 0.3) * SR)
meter = pyln.Meter(SR)

v, sr = sf.read(voice_p)
if v.ndim > 1: v = v.mean(1)
assert sr == SR
voice = np.zeros(n); i0 = int(plan.VO * SR); voice[i0:i0 + len(v)] = v[:n - i0]

music, _ = sf.read(f"{adir}/music.wav")
mus = np.zeros((n, 2)); L = min(n, len(music)); mus[:L] = music[:L]
mus = sosfilt(butter(2, 40, 'hp', fs=SR, output='sos'), mus, axis=0)
# small dip in the voice's presence range so words stay crisp
mid = sosfilt(butter(2, [1200, 3800], 'bp', fs=SR, output='sos'), mus, axis=0)
mus = mus - 0.3 * mid

v_lufs = meter.integrated_loudness(voice)
m_lufs = meter.integrated_loudness(mus)
mus *= 10 ** ((v_lufs - MUSIC_UNDER - m_lufs) / 20)

sfx = np.zeros((n, 2)); cache = {}
for t, name, gain in plan.sfx_events():
    if name not in cache:
        x, _ = sf.read(f"{adir}/sfx_{name}.wav"); cache[name] = x
    x = cache[name] * gain * 0.30
    j = int(t * SR); L = min(len(x), n - j)
    if L > 0 and j >= 0:
        sfx[j:j + L, 0] += x[:L]; sfx[j:j + L, 1] += x[:L]

def master(x, path):
    tmp = path + ".pre.wav"
    sf.write(tmp, x.astype(np.float32), SR, subtype="FLOAT")
    r = subprocess.run(["ffmpeg", "-i", tmp, "-af", f"loudnorm=I={LUFS}:TP={TP}:LRA=9:print_format=json", "-f", "null", "-"],
                       capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):])
    ln = (f"loudnorm=I={LUFS}:TP={TP}:LRA=9:measured_I={m['input_i']}:measured_TP={m['input_tp']}:measured_LRA={m['input_lra']}:"
          f"measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", ln + ",aresample=48000", "-c:a", "pcm_s16le", path], check=True)
    subprocess.run(["rm", "-f", tmp])

master(mus + sfx + voice[:, None], out_mix)
master(np.stack([voice, voice], 1), out_vo)
print(f"voice {v_lufs:.1f} LUFS, music set to {v_lufs - MUSIC_UNDER:.1f} LUFS ({MUSIC_UNDER} LU under)")
