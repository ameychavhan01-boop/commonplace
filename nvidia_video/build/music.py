"""Original lo-fi background music, composed in code (no samples, royalty-free, owned by the channel).

- 76 BPM
- Soft electric piano (FM-style synthesis, gentle tremolo) looping a calm jazzy progression,
  one chord per bar: Fmaj9, Em7, Dm9, Cmaj7, Bbmaj7, Am7, Gm7, C9sus
- Gentle bass, soft kick, light snare, lightly swung hi-hats
- Faint vinyl crackle
- The piano dips slightly on each kick (sidechain "pump")
usage: python music.py OUT.wav SECONDS
"""
import sys
import numpy as np
import soundfile as sf
from scipy.signal import butter, sosfilt, fftconvolve

SR = 48000
BPM = 76
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(76)

def hz(m): return 440.0 * 2 ** ((m - 69) / 12)

# voicings (MIDI), bass root
CHORDS = [
    ("Fmaj9",  [53, 57, 60, 64, 67], 41),   # F A C E G
    ("Em7",    [52, 55, 59, 62],     40),   # E G B D
    ("Dm9",    [50, 53, 57, 60, 64], 38),   # D F A C E
    ("Cmaj7",  [48, 52, 55, 59],     36),   # C E G B
    ("Bbmaj7", [46, 50, 53, 57],     34),   # Bb D F A
    ("Am7",    [45, 48, 52, 55],     33),   # A C E G
    ("Gm7",    [43, 46, 50, 53],     31),   # G Bb D F
    ("C9sus",  [48, 53, 55, 58, 62], 36),   # C F G Bb D
]

def epiano(f, dur, vel=0.8):
    """FM electric piano: carrier + 1:1 modulator with decaying index, bell-ish tine on top."""
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 1.6 * vel * np.exp(-t * 3.5) + 0.25
    mod = np.sin(2 * np.pi * f * t)
    car = np.sin(2 * np.pi * f * t + idx * mod)
    tine = 0.18 * np.sin(2 * np.pi * f * 14 * t) * np.exp(-t * 28)
    env = np.exp(-t * 1.1) * 0.85 + 0.15 * np.exp(-t * 0.25)
    att = int(0.006 * SR); env[:att] *= np.linspace(0, 1, att)
    rel = int(0.15 * SR); env[-rel:] *= np.linspace(1, 0, rel)
    return (car + tine) * env * vel

def bass(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.2 * np.sin(4 * np.pi * f * t)
    env = np.minimum(1, t / 0.015) * np.exp(-t * 1.4)
    rel = int(0.08 * SR); env[-rel:] *= np.linspace(1, 0, rel)
    return x * env

def kick():
    n = int(0.4 * SR); t = np.arange(n) / SR
    f = 48 + 60 * np.exp(-t * 28)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 8)

def snare():
    n = int(0.25 * SR); t = np.arange(n) / SR
    nz = sosfilt(butter(2, [1200, 6000], 'bp', fs=SR, output='sos'), rng.standard_normal(n))
    body = np.sin(2 * np.pi * 190 * t) * np.exp(-t * 30)
    return (nz * np.exp(-t * 22) * 0.7 + body * 0.5)

def hat(open_=False):
    n = int((0.12 if open_ else 0.05) * SR); t = np.arange(n) / SR
    nz = sosfilt(butter(4, 7000, 'hp', fs=SR, output='sos'), rng.standard_normal(n))
    return nz * np.exp(-t * (25 if open_ else 70))

def add(buf, x, t0, gain=1.0):
    j = int(t0 * SR)
    if j >= len(buf): return
    L = min(len(x), len(buf) - j); buf[j:j + L] += x[:L] * gain

def compose(total):
    n = int((total + 3) * SR)
    keys = np.zeros(n); bs = np.zeros(n); drums = np.zeros(n); hats = np.zeros(n)
    kick_times = []
    bar = 0; t = 0.0
    swing = 0.12 * BEAT   # off-beat 8ths pushed late (light swing)
    while t < total + 1:
        name, notes, root = CHORDS[bar % 8]
        # piano: chord on beat 1 (slight strum), soft re-hit on the "and" of 2, top note on 4
        for k, m in enumerate(notes):
            add(keys, epiano(hz(m), BAR * 0.95, 0.55 + 0.1 * rng.random()), t + k * 0.012 + rng.uniform(0, 0.006))
        for k, m in enumerate(notes[1:]):
            add(keys, epiano(hz(m), BEAT * 1.4, 0.32), t + 1.5 * BEAT + swing + k * 0.01)
        add(keys, epiano(hz(notes[-1] + 12), BEAT, 0.25), t + 3 * BEAT + swing)
        # bass: root on 1, fifth-ish pickup on 3
        add(bs, bass(hz(root), BEAT * 1.9), t)
        add(bs, bass(hz(root + 7 if bar % 2 == 0 else root + 12), BEAT * 0.9), t + 2.5 * BEAT + swing, 0.7)
        # drums
        for b in (0, 2.5):
            add(drums, kick(), t + b * BEAT + (swing if b % 1 else 0), 0.9); kick_times.append(t + b * BEAT + (swing if b % 1 else 0))
        for b in (1, 3):
            add(drums, snare(), t + b * BEAT, 0.45)
        for e in range(8):
            off = (e // 2) * BEAT + (e % 2) * (BEAT / 2 + swing)
            add(hats, hat(open_=(e == 7)), t + off, 0.20 if e % 2 == 0 else 0.13)
        t += BAR; bar += 1
    # sidechain pump on the keys: dip ~3 dB on each kick, recover over ~250 ms
    pump = np.ones(n)
    tt = np.arange(int(0.35 * SR)) / SR
    shape = 1 - 0.3 * np.exp(-tt / 0.12)
    for kt in kick_times:
        j = int(kt * SR); L = min(len(shape), n - j)
        if L > 0: pump[j:j + L] = np.minimum(pump[j:j + L], shape[:L])
    keys *= pump
    # warm the keys (lo-fi): gentle low-pass + light saturation, small room reverb
    keys = sosfilt(butter(2, 3800, 'lp', fs=SR, output='sos'), keys)
    keys = np.tanh(keys * 0.9)
    ir_t = np.arange(int(1.6 * SR)) / SR
    ir = rng.standard_normal(len(ir_t)) * np.exp(-ir_t * 3.0)
    ir = sosfilt(butter(2, 4000, 'lp', fs=SR, output='sos'), ir); ir /= np.sqrt(np.sum(ir ** 2))
    keys_wet = fftconvolve(keys, ir)[:n]
    keys = keys * 0.8 + keys_wet * 0.25
    bs = sosfilt(butter(2, 220, 'lp', fs=SR, output='sos'), bs)
    drums = sosfilt(butter(2, 6000, 'lp', fs=SR, output='sos'), drums)
    # vinyl crackle: faint hiss + sparse random pops
    hiss = sosfilt(butter(2, [800, 9000], 'bp', fs=SR, output='sos'), rng.standard_normal(n)) * 0.012
    pops = np.zeros(n)
    for j in rng.integers(0, n, int(total * 9)):
        L = int(rng.uniform(0.0003, 0.0015) * SR)
        pops[j:j + L] += rng.uniform(-1, 1) * rng.uniform(0.05, 0.25) * np.exp(-np.arange(min(L, n - j)) / (L / 3))
    crackle = hiss + sosfilt(butter(2, 2500, 'hp', fs=SR, output='sos'), pops) * 0.6
    # stereo
    L_ = keys * 0.95 + bs * 0.9 + drums * 0.8 + hats * 0.7 + crackle
    R_ = np.roll(keys, int(0.009 * SR)) * 0.95 + bs * 0.9 + drums * 0.8 + np.roll(hats, int(0.003 * SR)) * 0.85 + np.roll(crackle, 977)
    out = np.stack([L_, R_], 1)[:int(total * SR)]
    fi = int(2.0 * SR); out[:fi] *= np.linspace(0, 1, fi)[:, None]
    fo = int(4.0 * SR); out[-fo:] *= np.linspace(1, 0, fo)[:, None]
    return out / np.max(np.abs(out)) * 0.8

if __name__ == "__main__":
    total = float(sys.argv[2])
    m = compose(total)
    sf.write(sys.argv[1], m, SR)
    print("lo-fi music", round(len(m) / SR, 1), "s @", BPM, "BPM")
