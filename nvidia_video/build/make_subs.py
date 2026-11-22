"""subtitles.srt from the exact per-sentence narration timings."""
import re, sys
from pathlib import Path
import plan

FIX = [("S and P 500", "S&P 500"), ("twenty twenty-six", "2026"), ("What If", "'What If'")]

def fmt(t):
    ms = int(round(t * 1000)); h, ms = divmod(ms, 3600000); m, ms = divmod(ms, 60000); s, ms = divmod(ms, 1000)
    return f"{h:02d}:{m:02d}:{s:02d},{ms:03d}"

def wrap2(text, width=42):
    if len(text) <= width: return text
    words = text.split(); best = None
    for i in range(1, len(words)):
        a, b = " ".join(words[:i]), " ".join(words[i:])
        score = max(len(a), len(b))
        if best is None or score < best[0]: best = (score, a, b)
    return best[1] + "\n" + best[2]

def split_long(text, start, end, limit=84):
    if len(text) <= limit: return [(text, start, end)]
    # split at the punctuation mark closest to the middle
    cands = [m.end() for m in re.finditer(r"[,:;]\s|\.\.\.\s", text)]
    if not cands:
        words = text.split(); mid = len(words) // 2
        cut = len(" ".join(words[:mid])) + 1
    else:
        cut = min(cands, key=lambda c: abs(c - len(text) / 2))
    a, b = text[:cut].strip(), text[cut:].strip()
    tm = start + (end - start) * len(a) / len(text)
    return split_long(a, start, tm, limit) + split_long(b, tm, end, limit)

cues = []
segs = plan.TIMINGS
for i, s in enumerate(segs):
    txt = s["text"]
    for a, b in FIX: txt = txt.replace(a, b)
    st, en = s["start"] + plan.VO, s["end"] + plan.VO
    nxt = segs[i + 1]["start"] + plan.VO if i + 1 < len(segs) else en + 2
    for part, a, b in split_long(txt, st, en):
        cues.append([part, a, b])
# minimum 1.0 s on screen, never overlapping the next cue
for i, c in enumerate(cues):
    nxt = cues[i + 1][1] if i + 1 < len(cues) else c[2] + 3
    c[2] = min(max(c[2] + 0.15, c[1] + 1.0), nxt - 0.04)
out = Path(sys.argv[1])
out.write_text("\n".join(f"{k + 1}\n{fmt(a)} --> {fmt(b)}\n{wrap2(t)}\n" for k, (t, a, b) in enumerate(cues)), encoding="utf-8")
print(len(cues), "cues ->", out)
