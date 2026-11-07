"""Original lo-fi background music, generated from scratch (no samples).
E-piano chords (FM), sine bass, soft kick, light swung hats, faint vinyl noise.
Usage: python music.py OUT.wav SECONDS"""
import sys, math
import numpy as np, soundfile as sf

SR = 48000
BPM = 76
BEAT = 60 / BPM
BAR = 4 * BEAT
rng = np.random.default_rng(7)

def mtof(m): return 440.0 * 2 ** ((m - 69) / 12)

# chord: (bass midi, [voicing midi])
PROG_A = [(41, [57, 60, 64, 67]), (40, [55, 59, 62, 64]), (38, [53, 57, 60, 64]), (36, [52, 55, 59, 62])]   # Fmaj9 Em7 Dm9 Cmaj7
PROG_B = [(34, [50, 53, 57, 62]), (33, [52, 55, 60, 64]), (31, [53, 58, 62, 65]), (36, [52, 58, 62, 67])]   # Bbmaj7 Am7 Gm7 C9sus

def epiano(freq, dur, vel):
    n = int(dur * SR); t = np.arange(n) / SR
    idx = 1.1 * np.exp(-t * 3.0) + .15
    car = np.sin(2 * np.pi * freq * t + idx * np.sin(2 * np.pi * freq * t))
    car += .18 * np.sin(2 * np.pi * 2 * freq * t) * np.exp(-t * 4)
    env = (1 - np.exp(-t / .006)) * np.exp(-t / 1.9)
    rel = np.clip((dur - t) / .25, 0, 1)
    trem = 1 + .07 * np.sin(2 * np.pi * 4.6 * t)
    return (car * env * rel * trem * vel).astype(np.float32)

def bass(freq, dur, vel):
    n = int(dur * SR); t = np.arange(n) / SR
    s = np.sin(2 * np.pi * freq * t) + .25 * np.sin(2 * np.pi * 2 * freq * t) + .08 * np.sin(2 * np.pi * 3 * freq * t)
    env = (1 - np.exp(-t / .012)) * np.exp(-t / .9) * np.clip((dur - t) / .08, 0, 1)
    return (np.tanh(1.4 * s) * env * vel).astype(np.float32)

def kick(vel):
    n = int(.42 * SR); t = np.arange(n) / SR
    f = 46 + 80 * np.exp(-t / .035)
    ph = 2 * np.pi * np.cumsum(f) / SR
    return (np.sin(ph) * np.exp(-t / .16) * vel).astype(np.float32)

def onepole_lp(x, fc):
    a = math.exp(-2 * math.pi * fc / SR)
    from scipy.signal import lfilter
    return lfilter([1 - a], [1, -a], x).astype(np.float32)

def noise_hit(dur, decay, hp=True, vel=1.0):
    n = int(dur * SR); t = np.arange(n) / SR
    x = rng.standard_normal(n).astype(np.float32)
    if hp: x = x - onepole_lp(x, 6000)
    else: x = onepole_lp(x - onepole_lp(x, 900), 3500)
    return (x * np.exp(-t / decay) * vel).astype(np.float32)

def add(buf, sig, start):
    i = int(start * SR)
    if i >= len(buf): return
    j = min(len(buf), i + len(sig)); buf[i:j] += sig[:j - i]

def render(total):
    n = int(total * SR) + SR
    keys = np.zeros(n, np.float32); low = np.zeros(n, np.float32); drums = np.zeros(n, np.float32)
    kenv = np.zeros(n, np.float32)
    nbars = int(total / BAR) + 2
    hat = noise_hit(.08, .022, True, 1.0); snare = noise_hit(.25, .07, False, 1.0); kk = kick(1.0)
    for bi in range(nbars):
        t0 = bi * BAR
        section = (bi // 8) % 4
        prog = PROG_A if section in (0, 2) else PROG_B
        b_midi, voicing = prog[bi % 4]
        drums_on = bi >= 2 and not (bi % 32 in (28, 29, 30, 31))
        # e-piano: main stab + light second stab
        for k, m in enumerate(voicing):
            v = .16 * (0.85 + .3 * rng.random())
            add(keys, epiano(mtof(m), BAR * 1.05, v), t0 + k * .018 + rng.random() * .006)
        if rng.random() < .7:
            for k, m in enumerate(voicing[1:]):
                add(keys, epiano(mtof(m + (12 if rng.random() < .15 else 0)), BEAT * 1.4, .075), t0 + 2.5 * BEAT + .06 + k * .02)
        if bi % 2 == 1 and rng.random() < .6:
            m = voicing[-1] + 12 + int(rng.choice([0, 2, -1, 3]))
            add(keys, epiano(mtof(m), BEAT * 2, .05), t0 + 3.5 * BEAT + .05)
        # bass
        if bi >= 1:
            add(low, bass(mtof(b_midi), BEAT * 1.6, .2), t0)
            add(low, bass(mtof(b_midi + (7 if rng.random() < .5 else 12)), BEAT * .9, .13), t0 + 2.5 * BEAT + .05)
        if drums_on:
            for beat in (0, 2):
                add(drums, kk * .3, t0 + beat * BEAT); add(kenv, np.exp(-np.arange(int(.3 * SR)) / SR / .12).astype(np.float32), t0 + beat * BEAT)
            if rng.random() < .35:
                add(drums, kk * .2, t0 + 3.5 * BEAT + .05)
            for beat in (1, 3):
                add(drums, snare * .16, t0 + beat * BEAT + .012)
            for e in range(8):
                sw = .055 if e % 2 else 0
                add(drums, hat * (.06 if e % 2 else .085) * (0.8 + .4 * rng.random()), t0 + e * BEAT / 2 + sw)
    keys = onepole_lp(keys, 3200)
    duck = 1 - .28 * np.clip(kenv, 0, 1)
    mix = keys * duck + low * (1 - .15 * np.clip(kenv, 0, 1)) + drums
    vinyl = onepole_lp(rng.standard_normal(n).astype(np.float32), 2500) * .004
    clicks = (rng.random(n) < 1.5 / SR).astype(np.float32) * rng.uniform(.02, .06, n).astype(np.float32)
    mix += vinyl + onepole_lp(clicks, 4000)
    mix = mix[:int(total * SR)]
    fi, fo = int(3 * SR), int(6 * SR)
    mix[:fi] *= np.linspace(0, 1, fi, dtype=np.float32); mix[-fo:] *= np.linspace(1, 0, fo, dtype=np.float32)
    return mix / (np.abs(mix).max() + 1e-9) * .8

if __name__ == '__main__':
    out, sec = sys.argv[1], float(sys.argv[2])
    m = render(sec)
    sf.write(out, m, SR, subtype='FLOAT')
    print('music', out, len(m) / SR, 's')
