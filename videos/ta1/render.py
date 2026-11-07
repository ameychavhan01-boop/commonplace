"""Render scenes. Usage:
  python render.py BUILD preview  [ids...] [--t=end|SECONDS]   -> PNG previews
  python render.py BUILD video    [ids...] [--workers=3]        -> per-scene MP4s
"""
import os, sys, subprocess, time, math
from multiprocessing import Pool
import cairocffi as cairo
from engine import *
import timeline
from script_p1 import CHAPTERS, SHORT
import scenes  # registers all scene draw functions
from scenes import REG

def chrome_and_content(c, t, m, b):
    draw_bg(c, t)
    sid = m["id"]
    fn = REG.get(sid)
    if 1 <= m["ch"] <= 8:
        if m["first"]:
            tc_a = 1 - P(t, b[1] - .45, .7)
            if tc_a > 0:
                with xf(c, W / 2, H / 2, 1 + .04 * (1 - tc_a)):
                    title_card(c, t, m["ch"], CHAPTERS[m["ch"]], 8, tc_a, 0.15)
            hdr_a = P(t, b[1] - .3, .7)
        else:
            hdr_a = P(t, .1, .6)
        header(c, f"CHAPTER {m['ch']}  ·  {SHORT[m['ch']]}", m["title"], m["count"], m["idx"], hdr_a)
        if fn: fn(c, t, b)
        banner(c, m["key"], P(t, b.key_t, .8))
    else:
        if fn: fn(c, t, b)
        if m.get("key") and sid not in ("hook", "outro", "recap"):
            banner(c, m["key"], P(t, b.key_t, .8))
    # scene fade in / out through the paper
    fa = max(1 - P(t, 0, .4, lambda x: x), P(t, b.end - .45, .45, lambda x: x))
    if sid == "hook": fa = max(0, fa if t > .2 else 0)
    if fa > 0.001:
        c.set_source_surface(background(), 0, 0); c.paint_with_alpha(fa)

def frame_surface():
    s = cairo.ImageSurface(cairo.FORMAT_RGB24, W, H)
    c = cairo.Context(s); c.set_antialias(cairo.ANTIALIAS_BEST)
    fo = cairo.FontOptions(); fo.set_antialias(cairo.ANTIALIAS_GRAY); fo.set_hint_style(cairo.HINT_STYLE_NONE); fo.set_hint_metrics(cairo.HINT_METRICS_OFF)
    c.set_font_options(fo)
    return s, c

def preview(args):
    build, m, b, t, out = args
    import traceback
    try:
        s, c = frame_surface()
        chrome_and_content(c, t, m, b)
        s.write_to_png(out)
        return out
    except Exception:
        return 'ERROR ' + out + '\n' + traceback.format_exc(limit=-3)

def render_video(args):
    build, m, b = args
    out = f"{build}/scenes/{m['id']}.mp4"
    tmp = out + ".part.mp4"
    n = int(round(b.end * FPS))
    cmd = ["ffmpeg", "-y", "-loglevel", "error", "-f", "rawvideo", "-pix_fmt", "bgr0", "-s", f"{W}x{H}", "-r", str(FPS),
           "-i", "-", "-c:v", "libx264", "-preset", "medium", "-crf", "19", "-tune", "animation", "-pix_fmt", "yuv420p",
           "-g", "60", "-threads", "2", "-an", "-movflags", "+faststart", tmp]
    p = subprocess.Popen(cmd, stdin=subprocess.PIPE)
    s, c = frame_surface()
    t0 = time.time()
    for f in range(n):
        c.save(); chrome_and_content(c, f / FPS, m, b); c.restore()
        s.flush(); p.stdin.write(bytes(s.get_data()))
    p.stdin.close(); p.wait()
    os.replace(tmp, out)
    return f"{m['id']}: {n} frames in {time.time()-t0:.0f}s"

def main():
    build, mode = sys.argv[1], sys.argv[2]
    ids = [a for a in sys.argv[3:] if not a.startswith("--")]
    opts = dict(a[2:].split("=") for a in sys.argv[3:] if a.startswith("--"))
    tl = timeline.load(build)
    sel = [(m, b) for (m, b, T) in tl if not ids or m["id"] in ids]
    if mode == "preview":
        os.makedirs(f"{build}/preview", exist_ok=True)
        tt = opts.get("t", "end")
        jobs = []
        for m, b in sel:
            for spec in tt.split(","):
                if spec == "end": t = b.end - .6
                elif spec.startswith("b"): t = b[int(spec[1:])] + .9
                else: t = float(spec)
                jobs.append((build, m, b, t, f"{build}/preview/{m['id']}_{spec}.png"))
        with Pool(int(opts.get("workers", 4))) as pool:
            for r in pool.imap_unordered(preview, jobs): print(r, flush=True)
    else:
        os.makedirs(f"{build}/scenes", exist_ok=True)
        sel.sort(key=lambda mb: -mb[1].end)
        with Pool(int(opts.get("workers", 3))) as pool:
            for r in pool.imap_unordered(render_video, [(build, m, b) for m, b in sel]): print(r, flush=True)

if __name__ == "__main__":
    main()
