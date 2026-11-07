"""Assemble narration + music, normalize loudness, write final and voice-only audio, captions and chapters.
Usage: python audio.py BUILD OUTDIR"""
import sys, json, re, subprocess
import numpy as np, soundfile as sf
from scipy.signal import resample_poly
from scipy.ndimage import maximum_filter1d, minimum_filter1d, uniform_filter1d
import timeline
from script_p1 import CHAPTERS

SR = 48000

def lufs(path):
    out = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', path, '-af', 'ebur128=peak=true', '-f', 'null', '-'],
                         capture_output=True, text=True).stderr
    I = float(re.findall(r'I:\s+(-?[\d.]+) LUFS', out)[-1])
    pk = re.findall(r'Peak:\s+(-?[\d.]+|-inf) dBFS', out)
    return I, (float(pk[-1]) if pk and pk[-1] != '-inf' else None)

def limiter(x, ceiling=10 ** (-2.2 / 20), look=0.004):
    w = max(1, int(look * SR))
    env = maximum_filter1d(np.abs(x), size=2 * w + 1)
    g = np.minimum(1.0, ceiling / np.maximum(env, 1e-9)).astype(np.float32)
    g = minimum_filter1d(g, size=2 * w + 1)
    g = uniform_filter1d(g, size=w)
    return (x * g).astype(np.float32)

def normalize(x, tmp, target=-15.0):
    for _ in range(3):
        sf.write(tmp, x, SR, subtype='FLOAT')
        I, _ = lufs(tmp)
        x = limiter(x * np.float32(10 ** ((target - I) / 20)))
        if abs(I - target) < .3: break
    sf.write(tmp, x, SR, subtype='FLOAT')
    return x, lufs(tmp)

def fmt_ts(t, srt=True):
    h, r = divmod(t, 3600); m, s = divmod(r, 60)
    if srt: return f'{int(h):02d}:{int(m):02d}:{int(s):02d},{int(round((s % 1) * 1000)) % 1000:03d}'
    return f'{int(h)}:{int(m):02d}:{int(s):02d}' if h else f'{int(m)}:{int(s):02d}'

def cues_for(text, start, dur, maxc=42):
    keep = text.replace('Nifty 50', 'Nifty\u00a050').replace('John J. Murphy', 'John\u00a0J.\u00a0Murphy')
    sents = [x for x in re.split(r'(?<=[.!?])\s+', keep.strip()) if x]
    blocks = []
    for snt in sents:
        lines, cur = [], ''
        for w in snt.split(' '):
            if len(cur) + 1 + len(w) > maxc and cur: lines.append(cur); cur = w
            else: cur = (cur + ' ' + w).strip()
        if cur: lines.append(cur)
        for i in range(0, len(lines), 2): blocks.append(lines[i:i + 2])
    merged = []
    for bl in blocks:
        if merged and len(merged[-1]) == 1 and len(bl) == 1 and len(merged[-1][0]) + len(bl[0]) < 70:
            merged[-1] = merged[-1] + bl
        else: merged.append(bl)
    total = sum(len(' '.join(g)) for g in merged) or 1
    out, t = [], start
    for g in merged:
        d = dur * len(' '.join(g)) / total
        out.append((t, t + d - .04, '\n'.join(g).replace('\u00a0', ' '))); t += d
    return out

def main():
    build, outdir = sys.argv[1], sys.argv[2]
    tl = timeline.load(build)
    timing = json.load(open(f'{build}/timing.json'))
    total = sum(b.end for m, b, T in tl)
    n = int(total * SR) + 1
    voice = np.zeros(n, np.float32)
    cues, chapters = [], []
    for m, b, T in tl:
        for i, rec in enumerate(timing[m['id']]):
            a, sr = sf.read(rec['file'], dtype='float32')
            a = resample_poly(a, SR // sr, 1).astype(np.float32) if sr != SR else a
            st = int((T + b.s[i]) * SR)
            voice[st:st + len(a)] += a[:max(0, n - st)]
            cues += cues_for(rec['display'], T + b.s[i], rec['dur'])
        if m['id'] == 'hook': chapters.append((T, 'Hook: the chart knew first'))
        elif m['id'] == 'intro': chapters.append((T, 'The book and the plan'))
        elif m['first']: chapters.append((T, f"Chapter {m['ch']}: {CHAPTERS[m['ch']]}"))
        elif m['id'] == 'recap': chapters.append((T, 'Recap: the 10 biggest lessons'))
        elif m['id'] == 'outro': chapters.append((T, 'Part 2 preview and outro'))
    sf.write(f'{build}/voice_raw.wav', voice, SR, subtype='FLOAT')
    Lv, _ = lufs(f'{build}/voice_raw.wav')
    mus, msr = sf.read(f'{build}/music.wav', dtype='float32')
    mus = np.pad(mus, (0, max(0, n - len(mus))))[:n]
    sf.write(f'{build}/music_trim.wav', mus, SR, subtype='FLOAT')
    Lm, _ = lufs(f'{build}/music_trim.wav')
    mus *= np.float32(10 ** ((Lv - 11.0 - Lm) / 20))
    print(f'voice {Lv:.1f} LUFS, music {Lm:.1f} -> {Lv-11:.1f} LUFS')
    mix, (Im, Pm) = normalize(voice + mus, f'{build}/mix_tmp.wav')
    vo, (Iv, Pv) = normalize(voice.copy(), f'{build}/vo_tmp.wav')
    sf.write(f'{outdir}/final_audio.wav', np.stack([mix, mix], 1), SR, subtype='PCM_16')
    sf.write(f'{outdir}/voice_only_audio.wav', np.stack([vo, vo], 1), SR, subtype='PCM_16')
    print(f'final mix {Im:.2f} LUFS peak {Pm} dBFS | voice-only {Iv:.2f} LUFS peak {Pv} dBFS | {total/60:.2f} min')
    with open(f'{outdir}/captions_en.srt', 'w') as f:
        for k, (a, b_, tx) in enumerate(cues, 1):
            f.write(f'{k}\n{fmt_ts(a)} --> {fmt_ts(b_)}\n{tx}\n\n')
    json.dump([(fmt_ts(t, False), lab) for t, lab in chapters], open(f'{build}/chapters.json', 'w'), indent=1)
    print('cues', len(cues)); print('\n'.join(f'{fmt_ts(t, False)} {lab}' for t, lab in chapters))

if __name__ == '__main__':
    main()
