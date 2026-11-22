"""Original, procedurally generated music bed + sound effects (no samples, no
third-party audio: everything is synthesised from sine waves and noise here,
so it is 100% royalty-free and owned by the channel).

Music follows the story: tense hook -> curious explainer -> dark (hour 1) ->
ticking tension (day 1 / week 1) -> warm India section -> hopeful rebuild ->
reflective lesson -> uplifting end screen.
"""
import json, sys
from pathlib import Path
import numpy as np
import soundfile as sf
from scipy.signal import fftconvolve, butter, sosfilt

SR = 48000
rng = np.random.default_rng(7)
BPM = 84
BEAT = 60 / BPM
BAR = 4 * BEAT

def midi(n): return 440.0 * 2 ** ((n - 69) / 12)

# ---------------------------------------------------------------- instruments
def env_adsr(n, a, d, s, r):
    e = np.ones(n) * s
    A, D, R = int(a * SR), int(d * SR), int(r * SR)
    A = min(A, n); e[:A] = np.linspace(0, 1, A)
    D = min(D, n - A); e[A:A + D] = np.linspace(1, s, D)
    if R and R < n: e[-R:] *= np.linspace(1, 0, R)
    return e

def additive(f, n, harmonics=10, roll=1.6, detune=0.0, phase=None):
    t = np.arange(n) / SR
    out = np.zeros(n)
    for h in range(1, harmonics + 1):
        if f * h > 9000: break
        ph = rng.uniform(0, 2 * np.pi) if phase is None else phase
        out += np.sin(2 * np.pi * f * h * (1 + detune) * t + ph) / h ** roll
    return out

def pad_note(f, dur, bright=1.0):
    n = int(dur * SR)
    x = sum(additive(f, n, harmonics=8, roll=1.9 - 0.4 * bright, detune=d) for d in (-0.003, 0.0, 0.0031))
    return x * env_adsr(n, min(1.6, dur * 0.4), 0.5, 0.85, min(1.4, dur * 0.4)) / 3

def pluck(f, dur=1.8, soft=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = (np.sin(2 * np.pi * f * t) + 0.35 * np.sin(4 * np.pi * f * t) * np.exp(-t * 6)
         + 0.12 * np.sin(6 * np.pi * f * t) * np.exp(-t * 9))
    e = np.exp(-t * (2.2 / soft)); e[:int(0.004 * SR)] *= np.linspace(0, 1, int(0.004 * SR))
    return x * e

def bass_note(f, dur):
    n = int(dur * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * f * t) + 0.25 * np.sin(4 * np.pi * f * t)
    return x * env_adsr(n, 0.02, 0.3, 0.6, 0.25)

def tick(dur=0.05, hp=6000):
    n = int(dur * SR); x = rng.standard_normal(n)
    sos = butter(4, hp, 'hp', fs=SR, output='sos'); x = sosfilt(sos, x)
    return x * np.exp(-np.arange(n) / SR * 90)

def kick(dur=0.35):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 45 + 70 * np.exp(-t * 30)
    return np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 9)

def reverb(x, secs=2.8, wet=0.28):
    n = int(secs * SR); t = np.arange(n) / SR
    irs = []
    for ch in range(2):
        ir = rng.standard_normal(n) * np.exp(-t * 3.2 / secs * 2.3)
        sos = butter(2, 5000, 'lp', fs=SR, output='sos'); ir = sosfilt(sos, ir)
        irs.append(ir / np.sqrt(np.sum(ir ** 2)))
    out = np.zeros((len(x) + n - 1, 2))
    for ch in range(2):
        out[:, ch] = fftconvolve(x[:, ch], irs[ch])
    dry = np.zeros_like(out); dry[:len(x)] = x
    return dry * (1 - wet) + out * wet

# ---------------------------------------------------------------- harmony
Dm, Bb, F, C, A, Gm, Am = [62, 65, 69], [58, 62, 65], [60, 65, 69], [60, 64, 67], [61, 64, 69], [58, 62, 67], [60, 64, 69]
MOODS = {
    # chords, pad level, pluck pattern density, bass, ticks, kick, brightness
    "hook":    dict(ch=[Dm, Dm, Bb, A],  pad=0.55, pl=2, bass=0.5, tk=0.0, kk=0.35, br=0.3),
    "what":    dict(ch=[Dm, Bb, F, C],   pad=0.45, pl=4, bass=0.35, tk=0.0, kk=0.0, br=0.7),
    "hour1":   dict(ch=[Dm, Dm, Bb, Bb], pad=0.6, pl=0, bass=0.55, tk=0.0, kk=0.25, br=0.1),
    "day1":    dict(ch=[Dm, Bb, Gm, A],  pad=0.45, pl=2, bass=0.55, tk=0.18, kk=0.4, br=0.4),
    "week1":   dict(ch=[Dm, Bb, F, A],   pad=0.45, pl=4, bass=0.55, tk=0.22, kk=0.45, br=0.5),
    "india":   dict(ch=[Dm, F, C, Bb],   pad=0.5, pl=3, bass=0.4, tk=0.08, kk=0.15, br=0.8),
    "rebuild": dict(ch=[F, C, Dm, Bb],   pad=0.5, pl=4, bass=0.45, tk=0.1, kk=0.3, br=1.0),
    "lesson":  dict(ch=[Bb, F, C, Dm],   pad=0.55, pl=2, bass=0.35, tk=0.0, kk=0.0, br=0.7),
    "outro":   dict(ch=[F, C, Bb, F],    pad=0.65, pl=4, bass=0.5, tk=0.12, kk=0.4, br=1.0),
}

def compose(sections, total):
    """sections: list of (name, start_s) sorted."""
    n = int((total + 4) * SR)
    pad = np.zeros(n); pl = np.zeros(n); bs = np.zeros(n); perc = np.zeros(n)
    def mood_at(t):
        m = sections[0][0]
        for name, s in sections:
            if t >= s - 0.01: m = name
        return m
    bar_i = 0; t = 0.0
    while t < total + 2:
        mood = MOODS[mood_at(t + BAR * 0.25)]
        chord = mood["ch"][bar_i % 4]
        i0 = int(t * SR)
        # pad: chord tones + octave-down root
        for note in chord + [chord[0] - 12]:
            x = pad_note(midi(note - 12), BAR + 1.2, mood["br"]) * mood["pad"]
            pad[i0:i0 + len(x)] += x[:max(0, n - i0)]
        # bass on beats 1 and 3
        for b in (0, 2):
            x = bass_note(midi(chord[0] - 24), BEAT * 1.8) * mood["bass"]
            j = i0 + int(b * BEAT * SR); pad_len = min(len(x), n - j)
            if pad_len > 0: bs[j:j + pad_len] += x[:pad_len]
        # plucked arpeggio (8th notes, density = notes per beat pattern)
        if mood["pl"]:
            arp = chord + [chord[1] + 12, chord[2] + 12, chord[0] + 12]
            steps = {2: [0, 4], 3: [0, 3, 5], 4: [0, 2, 4, 6]}[mood["pl"]]
            for beat in range(4):
                for k, s in enumerate(steps):
                    if s >= 8: continue
                    tt = t + beat * BEAT + s * BEAT / 8 * 1.0
                    note = arp[(beat * len(steps) + k) % len(arp)]
                    x = pluck(midi(note), 1.6) * 0.22 * (0.8 + 0.2 * rng.random())
                    j = int(tt * SR); L = min(len(x), n - j)
                    if L > 0: pl[j:j + L] += x[:L]
        # percussion
        for beat in range(4):
            if mood["kk"] and beat in (0, 2):
                x = kick() * mood["kk"]; j = i0 + int(beat * BEAT * SR); L = min(len(x), n - j)
                if L > 0: perc[j:j + L] += x[:L]
            if mood["tk"]:
                for e in range(2):
                    x = tick() * mood["tk"] * (1.0 if e == 1 else 0.6)
                    j = i0 + int((beat + e / 2) * BEAT * SR); L = min(len(x), n - j)
                    if L > 0: perc[j:j + L] += x[:L]
        t += BAR; bar_i += 1
    # stereo image
    st = np.zeros((n, 2))
    st[:, 0] = pad * 0.9 + pl * 0.75 + bs + perc * 0.9
    st[:, 1] = pad * 0.9 + np.roll(pl, int(0.011 * SR)) * 0.75 + bs + np.roll(perc, int(0.004 * SR)) * 0.9
    st = reverb(st, 3.0, 0.32)[:n]
    # gentle lowpass for warmth
    sos = butter(2, 7000, 'lp', fs=SR, output='sos'); st = sosfilt(sos, st, axis=0)
    # fade in/out
    fi = int(1.5 * SR); st[:fi] *= np.linspace(0, 1, fi)[:, None]
    end = int(total * SR); fo = int(3.0 * SR)
    st[end - fo:end] *= np.linspace(1, 0, fo)[:, None]; st[end:] = 0
    st = st[:end]
    return st / np.max(np.abs(st)) * 0.8

# ---------------------------------------------------------------- SFX
def _norm(x, peak=0.9): return x / (np.max(np.abs(x)) + 1e-9) * peak

def sfx_whoosh(dur=0.7, up=True):
    n = int(dur * SR); x = rng.standard_normal(n)
    # sweep a bandpass by STFT masking
    from scipy.signal import stft, istft
    f, tt, Z = stft(x, SR, nperseg=1024)
    prog = np.linspace(0, 1, Z.shape[1]); prog = prog if up else prog[::-1]
    centre = 300 * (12 ** prog)
    mask = np.exp(-((np.log(f[:, None] + 1) - np.log(centre[None, :])) ** 2) / 0.5)
    _, y = istft(Z * mask, SR, nperseg=1024); y = y[:n]
    e = np.sin(np.linspace(0, np.pi, n)) ** 1.5
    return _norm(y * e, 0.8)

def sfx_pop(f0=900):
    n = int(0.09 * SR); t = np.arange(n) / SR
    f = f0 * np.exp(-t * 14) + 250
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 45)
    return _norm(x, 0.8)

def sfx_click():
    n = int(0.025 * SR); t = np.arange(n) / SR
    x = np.sin(2 * np.pi * 2800 * t) * np.exp(-t * 260) + 0.3 * rng.standard_normal(n) * np.exp(-t * 600)
    return _norm(x, 0.6)

def sfx_boom(dur=2.2):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 32 + 40 * np.exp(-t * 6)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * np.exp(-t * 1.8)
    nz = rng.standard_normal(n); sos = butter(4, 180, 'lp', fs=SR, output='sos')
    x += sosfilt(sos, nz) * np.exp(-t * 5) * 0.6
    x = np.tanh(x * 1.6)
    return _norm(x, 0.95)

def sfx_powerdown(dur=1.3):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 60 + 700 * np.exp(-t * 3.2)
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) + 0.4 * np.sign(np.sin(2 * np.pi * np.cumsum(f * 0.5) / SR))
    sos = butter(2, 2500, 'lp', fs=SR, output='sos'); x = sosfilt(sos, x)
    return _norm(x * np.exp(-t * 1.4), 0.7)

def sfx_glitch(dur=0.45):
    n = int(dur * SR); x = np.zeros(n); i = 0
    while i < n:
        L = int(rng.uniform(0.01, 0.05) * SR)
        f = rng.uniform(200, 2500)
        seg = np.sign(np.sin(2 * np.pi * f * np.arange(L) / SR)) * rng.uniform(0.2, 1)
        if rng.random() < 0.3: seg = rng.standard_normal(L) * 0.5
        x[i:i + L] = seg[:max(0, min(L, n - i))]; i += L + int(rng.uniform(0, 0.02) * SR)
    sos = butter(2, 5000, 'lp', fs=SR, output='sos')
    return _norm(sosfilt(sos, x), 0.55)

def sfx_ticker(dur=1.2, rate=18):
    n = int(dur * SR); x = np.zeros(n)
    for k in range(int(dur * rate)):
        c = sfx_click() * (0.5 + 0.5 * (k / (dur * rate)))
        j = int(k / rate * SR); L = min(len(c), n - j); x[j:j + L] += c[:L]
    return _norm(x, 0.5)

def sfx_riser(dur=1.4):
    n = int(dur * SR); t = np.arange(n) / SR
    f = 200 * (8 ** (t / dur))
    x = np.sin(2 * np.pi * np.cumsum(f) / SR) * 0.4 + sfx_whoosh(dur, True)[:n] * 0.6
    return _norm(x * (t / dur) ** 2, 0.7)

def sfx_ding():
    x = pluck(midi(84), 1.5, 0.6) + 0.5 * pluck(midi(91), 1.5, 0.5)
    return _norm(x, 0.6)

SFX = dict(whoosh=sfx_whoosh, whoosh_down=lambda: sfx_whoosh(0.6, False), pop=sfx_pop, click=sfx_click,
           boom=sfx_boom, powerdown=sfx_powerdown, glitch=sfx_glitch, ticker=sfx_ticker,
           riser=sfx_riser, ding=sfx_ding)

if __name__ == "__main__":
    out = Path(sys.argv[1]); out.mkdir(parents=True, exist_ok=True)
    timings = json.load(open(Path(__file__).parent / "timings.json"))
    offset = float(sys.argv[2]) if len(sys.argv) > 2 else 0.4
    total = float(sys.argv[3])
    secs = []; last = None
    for t in timings:
        if t["section"] != last:
            secs.append((t["section"], t["start"] + offset)); last = t["section"]
    secs.append(("outro", timings[-1]["end"] + offset - 1.0))
    music = compose(secs, total)
    sf.write(out / "music.wav", music, SR)
    for k, fn in SFX.items():
        sf.write(out / f"sfx_{k}.wav", fn(), SR)
    print("music", music.shape[0] / SR, "s; sections", secs)
