"""Render the video frames.  usage:
  python render.py stills OUTDIR t1 t2 ...       # PNG stills at given seconds
  python render.py video OUT.mp4 [--workers 4] [--scale 1.0] [--fps 30] [--from S] [--to E]
"""
import math, os, subprocess, sys, time
from multiprocessing import Pool
from pathlib import Path
import numpy as np
import cv2
from gfx import *
import plan
import scenes_lib as SL

_built = None
def built():
    global _built
    if _built is None:
        out = []
        for s in plan.SCENES:
            obj = SL.TYPES[s["kind"]](**s["p"])
            obj.dur = s["end"] - s["start"]
            obj.cues = {k: v - s["start"] for k, v in s["cues"].items()}
            out.append((s, obj))
        _built = out
    return _built

def label_at(t):
    lab = None
    for st, l in plan.LABELS:
        if t >= st: lab = (st, l)
    return lab

def overlays(f, t, fi):
    for a, b in plan.NO_OVERLAY:
        if a <= t < b: return
    # corner badge (top-left), e.g. "THOUGHT EXPERIMENT"; set BADGE = None in plan.py to hide it
    badge = getattr(plan, "BADGE", "THOUGHT EXPERIMENT")
    lab = label_at(t)
    if not badge:
        badge = None
    if badge is None:
        L = None
    else:
        L = text_layer(badge, "xbold", 28, WHITE)
    if L is None:
        _time_label(f, t, lab); return
    pw, ph = L.shape[1] + 64, L.shape[0] + 26
    pill = np.zeros((ph, pw, 4), np.uint8)
    cv2.rectangle(pill, (ph // 2, 0), (pw - ph // 2, ph - 1), (*DARK, 215), -1)
    cv2.circle(pill, (ph // 2, ph // 2), ph // 2, (*DARK, 215), -1, cv2.LINE_AA)
    cv2.circle(pill, (pw - ph // 2, ph // 2), ph // 2, (*DARK, 215), -1, cv2.LINE_AA)
    cv2.circle(pill, (ph // 2 + 8, ph // 2), 8, (*YELLOW, 255), -1, cv2.LINE_AA)
    blit(f, pill, 48 + pw / 2, 46 + ph / 2)
    blit(f, L, 48 + pw / 2 + 12, 46 + ph / 2)
    _time_label(f, t, lab)

def _time_label(f, t, lab):
    if lab:
        st, txt = lab
        s = ease_back(prog(t, st, 0.35), 2.0)
        L2 = text_layer(txt, "anton", 46, YELLOW)
        pw2, ph2 = L2.shape[1] + 48, L2.shape[0] + 22
        plate = np.zeros((ph2, pw2, 4), np.uint8)
        cv2.rectangle(plate, (0, 0), (pw2 - 1, ph2 - 1), (*DARK, 225), -1)
        cv2.rectangle(plate, (0, 0), (pw2 - 1, ph2 - 1), (*YELLOW, 255), 3)
        blit(f, plate, W - 48 - pw2 / 2, 46 + ph2 / 2, s)
        blit(f, L2, W - 48 - pw2 / 2, 46 + ph2 / 2, s)

def frame_at(t, fi):
    B = built()
    idx = max(i for i, (s, _) in enumerate(B) if s["start"] <= t or i == 0)
    s, obj = B[idx]
    f = obj.render(t - s["start"], fi)
    if s["p"].get("grade"):        # lighting / colour mood for the whole scene (gfx.GRADES)
        f = grade(f, s["p"]["grade"], s["p"].get("grade_amt", 1.0) * ease_out(prog(t - s["start"], s["p"].get("grade_at", 0.0), 0.5)))
    # transition from previous scene
    if idx > 0:
        ps, pobj = B[idx - 1]
        lt = t - s["start"]
        if s["trans"] == "burst" and lt < 0.45:    # comic speed-line accent on a shocking reveal
            f = speed_lines(f, t, 1 - lt / 0.45, seed=idx)
        elif s["trans"] == "flash" and lt < 0.35:  # white flash (time skip)
            f = cv2.addWeighted(f, lt / 0.35, np.full_like(f, 255), 1 - lt / 0.35, 0)
        elif s["trans"] == "slide":
            d = 0.32
            if lt < d:
                k = ease_in_out(lt / d)
                prev = pobj.render(t - ps["start"], fi)
                off = int(W * k)
                out = np.empty_like(f)
                out[:, :W - off] = prev[:, off:]
                out[:, W - off:] = f[:, :off]
                f = out
        else:
            d = 0.18
            if lt < d:
                k = lt / d
                prev = pobj.render(t - ps["start"], fi)
                f = cv2.addWeighted(f, k, prev, 1 - k, 0)
    # global fade in / fade out
    if t < 0.25: f = (f * (t / 0.25)).astype(np.uint8)
    if t > plan.TOTAL - 0.6: f = (f * max(0, (plan.TOTAL - t) / 0.6)).astype(np.uint8)
    overlays(f, t, fi)
    return add_grain(f, fi)

def render_chunk(args):
    i0, i1, fps, scale, path = args
    w, h = int(W * scale) // 2 * 2, int(H * scale) // 2 * 2
    p = subprocess.Popen(["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "rgb24", "-s", f"{w}x{h}",
                          "-r", str(fps), "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "16",
                          "-pix_fmt", "yuv420p", path], stdin=subprocess.PIPE)
    for i in range(i0, i1):
        t = i / fps
        f = frame_at(t, int(t * 30))
        if scale != 1: f = cv2.resize(f, (w, h), interpolation=cv2.INTER_AREA)
        p.stdin.write(f.tobytes())
    p.stdin.close(); p.wait()
    return path

def main():
    mode = sys.argv[1]
    if mode == "stills":
        out = Path(sys.argv[2]); out.mkdir(parents=True, exist_ok=True)
        for ts in sys.argv[3:]:
            t = float(ts); f = frame_at(t, int(t * 30))
            cv2.imwrite(str(out / f"still_{t:07.2f}.jpg"), cv2.cvtColor(f, cv2.COLOR_RGB2BGR), [cv2.IMWRITE_JPEG_QUALITY, 88])
        return
    outp = sys.argv[2]
    args = sys.argv[3:]
    opt = lambda k, d: type(d)(args[args.index(k) + 1]) if k in args else d
    workers, scale, fps = opt("--workers", 4), opt("--scale", 1.0), opt("--fps", 30)
    t0, t1 = opt("--from", 0.0), opt("--to", plan.TOTAL)
    n0, n1 = int(t0 * fps), int(t1 * fps)
    nchunks = workers * 6
    edges = np.linspace(n0, n1, nchunks + 1).astype(int)
    tmp = Path(outp).resolve().parent / (Path(outp).stem + "_chunks"); tmp.mkdir(exist_ok=True)
    jobs = [(edges[i], edges[i + 1], fps, scale, str(tmp / f"c{i:03d}.mp4")) for i in range(nchunks)]
    st = time.time()
    with Pool(workers) as pool:
        for k, _ in enumerate(pool.imap(render_chunk, jobs)):
            print(f"chunk {k + 1}/{nchunks}  {time.time() - st:.0f}s", flush=True)
    lst = tmp / "list.txt"; lst.write_text("".join(f"file '{j[4]}'\n" for j in jobs))
    subprocess.run(["ffmpeg", "-y", "-loglevel", "error", "-f", "concat", "-safe", "0", "-i", str(lst), "-c", "copy", outp], check=True)
    print("done", outp, f"{time.time() - st:.0f}s")

if __name__ == "__main__":
    main()
