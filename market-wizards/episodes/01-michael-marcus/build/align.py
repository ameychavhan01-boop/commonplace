#!/usr/bin/env python3
"""
Align narration audio to the script and build the episode timeline.

- splits each chapter's narration into sentences (keeping paragraph membership)
- finds pauses in the chapter audio (ffmpeg silencedetect)
- matches sentence boundaries to pauses with a small dynamic program
- lays chapters out on a single timeline with chapter cards and breathing gaps
  between paragraphs (longer when a new visual cue starts)

Output: build/timeline.json
"""
import json
import os
import re
import subprocess

HERE = os.path.dirname(os.path.abspath(__file__))
EP = os.path.dirname(HERE)
CH = json.load(open(os.path.join(HERE, "chapters.json")))

INTRO = 2.6            # JSR logo sting
CARD = 5.0             # chapter card before narration
GAP_PARA = 0.7         # pause between paragraphs
GAP_CUE = 1.6          # pause when a new visual starts
TITLE_HOLD = 7.0       # series title after the cold open
END_HOLD = 9.0         # end card


def duration(path):
    out = subprocess.run(["ffprobe", "-v", "error", "-show_entries", "format=duration", "-of", "csv=p=0", path],
                         capture_output=True, text=True).stdout
    return float(out.strip())


def silences(path, noise="-32dB", d=0.16):
    err = subprocess.run(["ffmpeg", "-hide_banner", "-nostats", "-i", path, "-af",
                          "silencedetect=noise=%s:d=%s" % (noise, d), "-f", "null", "-"],
                         capture_output=True, text=True).stderr
    starts = [float(x) for x in re.findall(r"silence_start: ([\d.]+)", err)]
    ends = [float(x) for x in re.findall(r"silence_end: ([\d.]+)", err)]
    return list(zip(starts, ends))




def sentences_of(chapter):
    out = []
    p = -1
    for it in chapter["items"]:
        if it["kind"] != "para":
            continue
        p += 1
        parts = [s.strip() for s in re.split(r'(?:(?<=[.!?…])|(?<=[.!?…]["”]))\s+(?=["“A-Z0-9])', it["text"]) if s.strip()]
        for s in parts:
            out.append(dict(text=s, para=p))
    return out


def align(sents, sil, dur):
    """Segment the audio into sentences.

    Candidate boundaries are detected pauses. Choose n-1 of them so that each
    sentence's spoken length matches its text length, while long pauses that are
    skipped (i.e. fall inside a sentence) are penalised. Sentence k starts at the
    end of its opening pause and ends at the start of its closing pause.
    """
    speech_start = sil[0][1] if sil and sil[0][0] < 0.05 else 0.0
    speech_end = sil[-1][0] if sil and sil[-1][1] > dur - 0.05 else dur
    cands = [(a, b) for a, b in sil if a > speech_start + 0.05 and b < speech_end - 0.05]
    segment(sents, cands, speech_start, speech_end)
    # second pass: re-time sentences inside each paragraph at its own pace
    for p in sorted({x["para"] for x in sents}):
        ss = [x for x in sents if x["para"] == p]
        if len(ss) < 2:
            continue
        a0, a1 = ss[0]["a0"], ss[-1]["a1"]
        inner = [(a, b) for a, b in cands if a > a0 + 0.05 and b < a1 - 0.05]
        segment(ss, inner, a0, a1)
    return len(sents) - 1, len(sents) - 1


def segment(sents, cands, speech_start, speech_end):
    m, n = len(cands), len(sents)
    w = [len(x["text"]) + 4 for x in sents]
    pause_total = sum(b - a for a, b in cands)
    cps = sum(w) / max(1e-6, (speech_end - speech_start) - pause_total * 0.6)
    pred = [x / cps for x in w]
    allow = [len(re.findall(r"[,;:—]", x["text"])) for x in sents]
    # pseudo-candidates at the ends
    pts = [(speech_start, speech_start)] + cands + [(speech_end, speech_end)]
    M = len(pts)

    def seg_cost(i, j, k):
        start, end = pts[i][1], pts[j][0]
        d = end - start
        if d <= 0.15:
            return 1e9
        c = ((d - pred[k]) ** 2) / max(pred[k], 0.6)
        inside = sorted((pts[q][1] - pts[q][0] for q in range(i + 1, j)), reverse=True)
        for r, ln in enumerate(inside):      # pauses swallowed inside this sentence
            free = 0.55 if r < allow[k] else 0.18   # commas/dashes may pause briefly
            c += 120.0 * max(0.0, ln - free) ** 2
        return c

    INF = 1e18
    dp = [[INF] * M for _ in range(n + 1)]
    bk = [[-1] * M for _ in range(n + 1)]
    dp[0][0] = 0.0
    for k in range(1, n + 1):
        jrange = range(1, M) if k < n else [M - 1]
        for j in jrange:
            if k < n and j == M - 1:
                continue
            best, arg = INF, -1
            for i in range(0, j):
                if dp[k - 1][i] >= INF:
                    continue
                c = dp[k - 1][i] + seg_cost(i, j, k - 1)
                if c < best:
                    best, arg = c, i
            dp[k][j], bk[k][j] = best, arg
    # backtrack
    idx = [M - 1]
    j = M - 1
    for k in range(n, 0, -1):
        j = bk[k][j]
        idx.append(j)
    idx = idx[::-1]                          # n+1 boundary indices
    for k, x in enumerate(sents):
        x["a0"] = pts[idx[k]][1] if k > 0 else speech_start
        x["a1"] = pts[idx[k + 1]][0] if k < n - 1 else speech_end


def main():
    timeline = dict(chapters=[], subtitles=[], cues=[], audio=[])
    t = INTRO
    for c in CH:
        cid = c["id"]
        if cid == 0:
            continue
        path = os.path.join(EP, "audio", "ch%02d.mp3" % cid)
        dur = duration(path)
        sil = silences(path)
        sents = sentences_of(c)
        hits, n = align(sents, sil, dur)
        print("ch%02d  %6.1fs  %3d sentences  %3d/%3d boundaries on pauses" % (cid, dur, len(sents), hits, n))

        # cues: which paragraph each visual precedes
        cues = []
        p = 0
        k = 0
        for it in c["items"]:
            if it["kind"] == "visual":
                cues.append(dict(chapter=cid, idx=k, para=p, text=it["text"]))
                k += 1
            else:
                p += 1
        cue_paras = {q["para"] for q in cues}

        ch_start = t
        if cid >= 2:
            t += CARD                       # chapter card (no narration)
        else:
            t += 0.6
        # paragraphs → audio segments with gaps
        paras = sorted({s["para"] for s in sents})
        para_out = {}
        for p in paras:
            ss = [s for s in sents if s["para"] == p]
            a0, a1 = ss[0]["a0"], ss[-1]["a1"]
            if p > 0:
                t += GAP_CUE if p in cue_paras else GAP_PARA
            para_out[p] = t
            timeline["audio"].append(dict(file="ch%02d.mp3" % cid, a0=a0, a1=a1, t0=t))
            for s in ss:
                timeline["subtitles"].append(dict(t0=t + (s["a0"] - a0), t1=t + (s["a1"] - a0), text=s["text"]))
            t += a1 - a0
        for q in cues:
            if cid >= 2 and q["idx"] == 0:
                q["t0"] = ch_start           # chapter card + opening visual
            else:
                q["t0"] = para_out.get(q["para"], t) - (0.4 if q["para"] > 0 else 0)
        if cid == 1:
            t += TITLE_HOLD                  # series title holds after the cold open
        elif cid == 15:
            t += END_HOLD
        else:
            t += 1.2
        timeline["cues"].extend(cues)
        timeline["chapters"].append(dict(id=cid, heading=c["heading"], t0=ch_start, t1=t))
    timeline["duration"] = t
    json.dump(timeline, open(os.path.join(HERE, "timeline.json"), "w"), indent=1, ensure_ascii=False)
    print("total runtime: %.1f s (%.1f min)" % (t, t / 60))


if __name__ == "__main__":
    main()
