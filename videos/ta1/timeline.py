"""Scene timing built from the measured duration of every narration chunk."""
import json, re
from script_p1 import SCENES, CHAPTERS

LEAD, LEAD_FIRST, LEAD_HOOK = 0.6, 0.8, 0.5
TAIL, TAIL_OUTRO = 1.4, 3.5

def ends_sentence(s): return bool(re.search(r"[.!?]['\")]?$", s.strip()))

class Beats:
    def __init__(self, starts, durs, end):
        self.s, self.d, self.end = starts, durs, end
    def __getitem__(self, i): return self.s[i] if i < len(self.s) else self.end
    def e(self, i): return self.s[i] + self.d[i] if i < len(self.s) else self.end   # end of chunk i
    @property
    def n(self): return len(self.s)
    @property
    def key_t(self): return self.s[-1]

def meta():
    out, seen = [], set()
    for sc in SCENES:
        ch = sc["ch"]
        first = 1 <= ch <= 8 and ch not in seen
        if 1 <= ch <= 8: seen.add(ch)
        same = [s["id"] for s in SCENES if s["ch"] == ch]
        out.append(dict(sc, first=first, idx=same.index(sc["id"]), count=len(same)))
    return out

def build(timing):
    """returns list of (scene_meta, Beats, start_time_in_video)."""
    res, T = [], 0.0
    for m in meta():
        rec = timing.get(m["id"])
        if rec is None:  # not generated yet: estimate from word count (previews only)
            parts = re.split(r"\{\d+\}", m["text"])
            rec = [dict(display=p.strip(), dur=len(p.split()) / 2.3) for p in parts]
        lead = LEAD_HOOK if m["id"] == "hook" else LEAD_FIRST if m["first"] else LEAD
        starts, durs, t = [], [], lead
        for i, r in enumerate(rec):
            starts.append(t); durs.append(r["dur"])
            gap = 0.42 if ends_sentence(r["display"]) else 0.2
            if m["first"] and i == 0: gap += 0.7
            if m["id"] == "recap": gap += 0.35
            t += r["dur"] + gap
        end = starts[-1] + durs[-1] + (TAIL_OUTRO if m["id"] == "outro" else TAIL)
        end = round(end * 30) / 30
        res.append((m, Beats(starts, durs, end), T))
        T += end
    return res

def load(build_dir):
    return build(json.load(open(f"{build_dir}/timing.json")))
