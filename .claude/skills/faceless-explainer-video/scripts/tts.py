"""Narration engine: Kokoro-82M (Apache-2.0) via kokoro-onnx (MIT).

Generates speech sentence by sentence, joins with natural pauses, removes
clicks with short fades, and returns per-sentence timings (for subtitles and
scene sync). Post-processing (EQ / compression / loudness) is done by
`polish()` with ffmpeg.
"""
import json, re, subprocess, sys
from pathlib import Path
import numpy as np
import soundfile as sf

from gfx import SCRATCH   # VIDEO_ASSETS folder (models/ lives there)
MODEL = SCRATCH / "models/kokoro-v1.0.onnx"
VOICES = SCRATCH / "models/voices-v1.0.bin"
SR = 24000

_k = None
def kokoro():
    global _k
    if _k is None:
        from kokoro_onnx import Kokoro
        _k = Kokoro(str(MODEL), str(VOICES))
    return _k

def voice_style(spec):
    """spec: 'am_michael' or {'am_michael':0.6,'am_onyx':0.4}"""
    k = kokoro()
    if isinstance(spec, str):
        return spec
    return sum(k.get_voice_style(v) * w for v, w in spec.items())

def lang_of(spec):
    name = spec if isinstance(spec, str) else max(spec, key=spec.get)
    return "en-gb" if name.startswith("b") else "en-us"

# Words the phonemizer gets wrong -> exact IPA (inserted directly as phonemes).
IPA = {
    "Gurugram": "ɡˈʊɹʊɡɹˌɑːm",
    "Bengaluru": "bˈɛŋɡəlˌuːɹuː",
    "Jamnagar": "dʒˈɑːmnəɡɚ",
    "Sarvam": "sˈʌɹvəm",
    "Hyderabad": "hˈaɪdəɹəbˌæd",
    "TPUs": "tˌiːpˌiːjˈuːz",
    "GPUs": "dʒˌiːpˌiːjˈuːz",
    "HCLTech": "ˈeɪtʃ sˌiː ˈɛl tˈɛk",
    "Infosys": "ˈɪnfəsˌɪs",
    "Pune": "pˈuːneɪ",
    "CUDA": "kˈuːdə",
    "NVIDIA's": "ˈɛnvˈɪdiəz",
    "IndiaAI": "ˈɪndiə ˌeɪˈaɪ",
}
WORD_RE = None

ONES = "zero one two three four five six seven eight nine ten eleven twelve thirteen fourteen fifteen sixteen seventeen eighteen nineteen".split()
TENS = "_ _ twenty thirty forty fifty sixty seventy eighty ninety".split()

def int_words(n):
    if n < 20: return ONES[n]
    if n < 100: return TENS[n // 10] + ("-" + ONES[n % 10] if n % 10 else "")
    if n < 1000: return ONES[n // 100] + " hundred" + (" " + int_words(n % 100) if n % 100 else "")
    for div, name in ((10 ** 9, "billion"), (10 ** 6, "million"), (1000, "thousand")):
        if n >= div:
            return int_words(n // div) + " " + name + (" " + int_words(n % div) if n % div else "")

def speakable(text):
    """Spell out numbers in words (US style) so the voice reads them cleanly."""
    import re as _re
    def num(m):
        raw = m.group(0).replace(",", "")
        if "." in raw:
            a, b = raw.split(".")
            return int_words(int(a)) + " point " + " ".join(ONES[int(d)] for d in b)
        return int_words(int(raw))
    text = _re.sub(r"(?<![\w.])\d[\d,]*(?:\.\d+)?", num, text)
    text = text.replace("TSMC", "T S M C")
    return text

def to_phonemes(text, lang):
    """Phonemize with espeak, swapping in exact IPA for known problem words."""
    import re as _re
    k = kokoro()
    pat = _re.compile(r"\b(" + "|".join(map(_re.escape, IPA)) + r")\b")
    out = []; pos = 0
    for m in pat.finditer(text):
        chunk = text[pos:m.start()]
        if chunk.strip():
            p = k.tokenizer.phonemize(chunk, lang).strip()
            lead = _re.match(r"^[.,!?;:…]+", p)
            if lead and out:
                out[-1] += lead.group(0); p = p[lead.end():].strip()
            if p:
                out.append(p)
        out.append(IPA[m.group(1)])
        pos = m.end()
    tail = text[pos:]
    if tail.strip():
        p = k.tokenizer.phonemize(tail, lang).strip()
        # punctuation-only tails ("." "," "?") must attach to previous word
        lead = _re.match(r"^[.,!?;:…]+", p)
        if lead and out:
            out[-1] += lead.group(0); p = p[lead.end():].strip()
        if p:
            out.append(p)
    return " ".join(out)

def trim(a, thr=0.008):
    idx = np.where(np.abs(a) > thr)[0]
    if len(idx) == 0:
        return a
    s = max(0, idx[0] - int(0.02 * SR)); e = min(len(a), idx[-1] + int(0.06 * SR))
    return a[s:e]

def fade(a, ms_in=6, ms_out=25):
    a = a.copy()
    n1 = int(SR * ms_in / 1000); n2 = int(SR * ms_out / 1000)
    a[:n1] *= np.linspace(0, 1, n1)
    a[-n2:] *= np.linspace(1, 0, n2)
    return a

def synth(segments, voice, base_speed=0.92):
    """segments: list of dicts {text, pause (s after), speed (mult), id}"""
    k = kokoro()
    style = voice_style(voice); lang = lang_of(voice)
    out = []; timings = []; t = 0.0
    for seg in segments:
        sp = base_speed * seg.get("speed", 1.0)
        ph = to_phonemes(speakable(seg["text"]), lang)
        a, sr = k.create(ph, voice=style, speed=sp, lang=lang, is_phonemes=True)
        assert sr == SR
        a = fade(trim(a.astype(np.float32)))
        timings.append({"id": seg.get("id"), "text": seg["text"], "start": round(t, 3),
                        "end": round(t + len(a) / SR, 3)})
        out.append(a); t += len(a) / SR
        p = seg.get("pause", 0.35)
        out.append(np.zeros(int(p * SR), np.float32)); t += p
    return np.concatenate(out), timings

def polish(src, dst, lufs=-14.0):
    """Clean + warm + even + loudness-normalise a voice track."""
    chain = ",".join([
        "highpass=f=70",
        "adeclick",
        "equalizer=f=160:t=q:w=1.0:g=2.0",     # warmth
        "equalizer=f=350:t=q:w=1.2:g=-1.5",    # remove boxiness
        "equalizer=f=3200:t=q:w=1.5:g=1.5",    # presence / clarity
        "equalizer=f=7000:t=q:w=2.0:g=-2.0",   # soften sibilance
        "acompressor=threshold=-20dB:ratio=2.5:attack=8:release=120:makeup=2",
        "aresample=48000",
    ])
    tmp = str(dst) + ".pre.wav"
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", str(src), "-af", chain, tmp], check=True)
    # two-pass loudnorm
    r = subprocess.run(["ffmpeg", "-i", tmp, "-af", f"loudnorm=I={lufs}:TP=-1.5:LRA=7:print_format=json",
                        "-f", "null", "-"], capture_output=True, text=True)
    m = json.loads(r.stderr[r.stderr.rindex("{"):])
    ln = (f"loudnorm=I={lufs}:TP=-1.5:LRA=7:measured_I={m['input_i']}:measured_TP={m['input_tp']}:"
          f"measured_LRA={m['input_lra']}:measured_thresh={m['input_thresh']}:offset={m['target_offset']}:linear=true")
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-i", tmp, "-af", ln, "-ar", "48000", str(dst)], check=True)
    Path(tmp).unlink()
