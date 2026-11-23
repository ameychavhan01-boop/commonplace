"""Scene types. Each scene: render(t, fi) -> RGB uint8 frame, t = seconds since
scene start, fi = global frame index. `cues` are scene-local seconds at which
words are spoken (computed by plan.py)."""
import json, math, os
from functools import lru_cache
from pathlib import Path
import numpy as np
import cv2
from gfx import *

ILLUS_DIR = Path(os.environ.get("VIDEO_ILLUS", "illustrations"))   # optional AI art: imgNN.png
GEO = SCRATCH / "geo"

class Scene:
    def __init__(self, **kw):
        self.p = kw
        self.dur = 1.0
        self.cues = {}
    def cue(self, key, default=0.0):
        return self.cues.get(key, default)
    def render(self, t, fi):
        raise NotImplementedError

# ------------------------------------------------------------------ overlays shared by scenes
def kw_overlay(frame, t, items, fi):
    """items: list of dict(text, at, y, size, color, sub, style, x, rot, font)"""
    for it in items:
        at = it.get("t", 0.0)
        if t < at: continue
        s = pop_scale(t, at, 0.4)
        x = it.get("x", W / 2); y = it.get("y", H * 0.8)
        style = it.get("style", "stroke")
        size = it.get("size", 120)
        col = it.get("color", YELLOW)
        rot = it.get("rot", 0.0)
        fn = it.get("font", "marker")
        if style == "plate":
            tw, th = text_size(it["text"], fn, size)
            pw, ph = tw + 70, th + 34
            plate = np.zeros((int(ph), int(pw), 4), np.uint8)
            cv2.rectangle(plate, (0, 0), (int(pw) - 1, int(ph) - 1), (*it.get("plate", DARK), 235), -1)
            blit(frame, plate, x + 10 * s, y + 10 * s, s, 0.35, rot)
            blit(frame, plate, x, y, s, 1.0, rot)
            put_text(frame, it["text"], x, y, fn, size, col, scale=s, rot=rot)
        else:
            put_text(frame, it["text"], x, y, fn, size, col, stroke=it.get("stroke", 9), stroke_fill=it.get("sf", DARK),
                     shadow=6, scale=s, rot=rot)
        if it.get("sub"):
            st = at + 0.25
            if t >= st:
                put_text(frame, it["sub"], x, y + size * 0.78 + 18, it.get("subfont", "semi"), it.get("subsize", 40),
                         it.get("subcolor", WHITE), stroke=5, stroke_fill=DARK, alpha=ease_out(prog(t, st, 0.3)))

# ------------------------------------------------------------------ illustration (Ken Burns)
@lru_cache(maxsize=24)
def load_illus(img_id):
    p = ILLUS_DIR / f"{img_id}.png"
    if p.exists():
        im = cv2.cvtColor(cv2.imread(str(p), cv2.IMREAD_COLOR), cv2.COLOR_BGR2RGB)
        # fill to 16:9 then upscale so zooms stay sharp
        h, w = im.shape[:2]; tgt = 16 / 9
        if w / h > tgt: nw = int(h * tgt); im = im[:, (w - nw) // 2:(w - nw) // 2 + nw]
        else: nh = int(w / tgt); im = im[(h - nh) // 2:(h - nh) // 2 + nh]
        return cv2.resize(im, (2880, 1620), interpolation=cv2.INTER_LANCZOS4)
    return placeholder(img_id)

@lru_cache(maxsize=60)
def placeholder(img_id):
    from images import IMAGES
    desc = IMAGES.get(img_id, ("", ""))[0]
    f = cv2.resize(paper_bg(PAPER2, 11), (2880, 1620))
    import textwrap
    pts = rect_pts(140, 120, 2740, 1500, 10)
    poly(f, pts, (170, 150, 120), None, 8, 0, 3, hash(img_id) % 100)
    small = np.ascontiguousarray(f[::1, ::1])
    lines = textwrap.wrap(desc, 46)[:6]
    canvas = small
    L = text_layer(f"ILLUSTRATION {img_id[3:]}", "anton", 150, (190, 120, 80))
    # draw onto a 1920 scale copy then upscale (simple path: draw at 1.5x positions)
    def bl(layer, cx, cy):
        h, w = layer.shape[:2]; x0, y0 = int(cx - w / 2), int(cy - h / 2)
        a = layer[:, :, 3:4] / 255.0
        canvas[y0:y0 + h, x0:x0 + w] = (layer[:, :, :3] * a + canvas[y0:y0 + h, x0:x0 + w] * (1 - a)).astype(np.uint8)
    bl(L, 1440, 520)
    for i, ln in enumerate(lines):
        bl(text_layer(ln, "hand", 80, (110, 90, 70)), 1440, 760 + i * 100)
    bl(text_layer("(placeholder — final cartoon art comes from ElevenLabs)", "semi", 44, (160, 140, 120)), 1440, 1400)
    return canvas

def doodle_kw():
    try:
        import doodle_scenes
        return getattr(doodle_scenes, "DOODLE_KW", {})
    except ImportError:
        return {}

def has_art(img_id):
    return (ILLUS_DIR / f"{img_id}.png").exists()

class Illus(Scene):
    """p: img, move=(x0,y0,z0)->(x1,y1,z1) where x,y in 0..1 centre, z = zoom (1 = full frame)."""
    def render(self, t, fi):
        if not has_art(self.p["img"]):
            return self.render_doodle(t, fi)
        im = load_illus(self.p["img"])
        a = self.p.get("a", (0.5, 0.5, 1.0)); b = self.p.get("b", (0.5, 0.5, 1.12))
        k = ease_in_out(t / max(self.dur, 0.01)) if self.p.get("ease", True) else t / max(self.dur, 0.01)
        cx, cy, z = [lerp(a[i], b[i], k) for i in range(3)]
        Hs, Ws = im.shape[:2]
        cw, ch = Ws / z, Hs / z
        x0 = clamp(cx * Ws - cw / 2, 0, Ws - cw); y0 = clamp(cy * Hs - ch / 2, 0, Hs - ch)
        sx, sy = self.p.get("shake_at"), 0
        M = np.array([[W / cw, 0, -x0 * W / cw], [0, H / ch, -y0 * H / ch]], np.float32)
        if sx is not None:
            dx, dy = shake(t, sx, 0.6, 16); M[0, 2] += dx; M[1, 2] += dy
        f = cv2.warpAffine(im, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.p.get("tint"):
            col, amt = self.p["tint"]
            amt = amt * ease_out(prog(t, self.p.get("tint_at", 0), 0.6))
            f = (f * (1 - amt) + np.array(col) * amt).astype(np.uint8)
        if self.p.get("dark_bottom", True) and self.p.get("kw"):
            grad = np.linspace(0, 1, H)[:, None, None] ** 3 * 0.55
            f = (f * (1 - grad)).astype(np.uint8)
        kw_overlay(f, t, self.resolve(self.p.get("kw", [])), fi)
        return f
    def render_doodle(self, t, fi):
        from doodles import render_doodle
        base = render_doodle(self.p["img"], t, fi)
        a = self.p.get("a", (0.5, 0.5, 1.0)); b = self.p.get("b", (0.5, 0.5, 1.12))
        k = ease_in_out(t / max(self.dur, 0.01))
        # gentle camera on code-drawn art: small zoom + drift in the same direction as planned
        push = self.p.get("push", 0.16)            # pro reference: ~15% push over a 4 s shot
        z = 1.0 + push * k if b[2] >= a[2] else 1.0 + push * (1 - k)
        dx = (b[0] - a[0]) * 260 * k; dy = (b[1] - a[1]) * 160 * k
        M = np.array([[z, 0, (1 - z) * W / 2 - dx], [0, z, (1 - z) * H / 2 - dy]], np.float32)
        if self.p.get("shake_at") is not None:
            sx, sy = shake(t, self.p["shake_at"], 0.6, 16); M[0, 2] += sx; M[1, 2] += sy
        f = cv2.warpAffine(base, M, (W, H), flags=cv2.INTER_LINEAR, borderMode=cv2.BORDER_REFLECT)
        if self.p.get("tint"):
            col, amt = self.p["tint"]
            amt = amt * ease_out(prog(t, self.p.get("tint_at", 0), 0.6))
            f = (f * (1 - amt) + np.array(col) * amt).astype(np.uint8)
        kws = self.resolve(self.p.get("kw", []))
        if not kws and self.p["img"] in doodle_kw():
            kws = [dict(text=doodle_kw()[self.p["img"]], t=0.15, size=120, y=H * 0.87, style="plate", color=YELLOW)]
        kw_overlay(f, t, kws, fi)
        return f

    def resolve(self, items):
        out = []
        for it in items:
            it = dict(it)
            if isinstance(it.get("t"), str): it["t"] = self.cue(it["t"])
            out.append(it)
        return out

# ------------------------------------------------------------------ big text card
class BigText(Scene):
    """p: lines=[(text, font, size, color)], bg, style (pop/glitch/stamp/type), sub, icon"""
    def render(self, t, fi):
        kind = self.p.get("bg", "dark")
        f = bg(kind) if kind in ("dark", "paper") else bg(kind)
        style = self.p.get("style", "pop")
        lines = self.p["lines"]
        total_h = sum(s * 1.08 for _, _, s, _ in lines)
        y = H / 2 - total_h / 2 + self.p.get("dy", 0)
        dx, dy = (shake(t, 0.0, 0.5, 18) if style in ("glitch", "stamp") else (0, 0))
        for i, (txt, fn, size, col) in enumerate(lines):
            at = self.p.get("stagger", 0.12) * i + self.p.get("delay", 0.0)
            if isinstance(self.p.get("line_at"), list): at = self.cue(self.p["line_at"][i], at)
            cy = y + size * 0.54
            if t >= at:
                if style == "stamp":
                    p = prog(t, at, 0.22); s = lerp(2.2, 1.0, ease_out(p)); a = clamp(p * 2)
                    put_text(f, txt, W / 2 + dx, cy + dy, fn, size, col, stroke=0, scale=s, alpha=a,
                             rot=self.p.get("rot", -4))
                elif style == "glitch":
                    s = pop_scale(t, at, 0.3)
                    if (fi // 2) % 5 == 0 and t - at < 0.8:
                        put_text(f, txt, W / 2 + dx - 14, cy + dy, fn, size, (0, 220, 255), scale=s, alpha=0.6)
                        put_text(f, txt, W / 2 + dx + 14, cy + dy, fn, size, RED, scale=s, alpha=0.6)
                    put_text(f, txt, W / 2 + dx, cy + dy, fn, size, col, scale=s)
                    if (fi // 3) % 4 == 0 and t - at < 1.0:
                        yy = int(cy + np.random.default_rng(fi).uniform(-size / 2, size / 2))
                        f[max(0, yy):yy + 12] = np.roll(f[max(0, yy):yy + 12], 40, axis=1)
                elif style == "type":
                    n = int(len(txt) * prog(t, at, max(0.3, len(txt) * 0.05)))
                    shown = txt[:n] + ("|" if (fi // 8) % 2 == 0 and n < len(txt) else "")
                    if shown:
                        L = text_layer(txt, fn, size, col)
                        put_text(f, shown, W / 2 - L.shape[1] / 2, cy, fn, size, col, anchor="left")
                else:
                    put_text(f, txt, W / 2, cy, fn, size, col, stroke=self.p.get("stroke", 0),
                             stroke_fill=self.p.get("sf", INK), scale=pop_scale(t, at, 0.4))
            y += size * 1.08
        if self.p.get("underline") and t > 0.4:
            k = ease_out(prog(t, 0.4, 0.5)); uy = y + 10 + self.p.get("dy", 0)
            uw = self.p["underline"]
            pts = [(W / 2 - uw / 2 + uw * i / 20 * k, uy + 6 * math.sin(i)) for i in range(21)]
            poly(f, pts, self.p.get("ucolor", YELLOW), None, 10, fi, 1.5, 3, closed=False)
        if self.p.get("note"):
            nt = self.p.get("note_at", 0.6)
            if isinstance(nt, str): nt = self.cue(nt)
            if t >= nt:
                put_text(f, self.p["note"], W / 2 + self.p.get("note_dx", 0), H - 170, "hand", 64,
                         self.p.get("note_color", (200, 200, 210) if kind == "dark" else (110, 95, 80)),
                         alpha=ease_out(prog(t, nt, 0.4)), rot=-2)
        return f

# ------------------------------------------------------------------ number counter
class Counter(Scene):
    """p: value, start_value, prefix, suffix, decimals, label, sub, at(cue), color, bg, icon"""
    def render(self, t, fi):
        f = bg(self.p.get("bg", "dark"))
        at = self.cue("num", self.p.get("delay", 0.2))
        dur = self.p.get("count_dur", 1.4)
        v0, v1 = self.p.get("from", 0), self.p["value"]
        k = ease_out(prog(t, at, dur))
        v = lerp(v0, v1, k)
        txt = self.p.get("prefix", "") + fmt_num(v, self.p.get("decimals", 0)) + self.p.get("suffix", "")
        if k >= 1 and self.p.get("final"): txt = self.p["final"]
        size = self.p.get("size", 230)
        col = self.p.get("color", YELLOW)
        s = 1.0 + 0.08 * math.sin(clamp((t - at - dur) / 0.25) * math.pi) if t > at + dur else 1.0
        cy = self.p.get("y", H / 2 - 40)
        if t >= at:
            glow(f, W / 2, cy, 700, col, 0.12 * (1 if t > at + dur else k))
            put_text(f, txt, W / 2, cy, "anton", size, col, scale=s * ease_back(prog(t, at, 0.3), 1.5))
        if self.p.get("label"):
            la = self.cue("label", at + 0.3)
            if t >= la:
                put_text(f, self.p["label"], W / 2, cy + size * 0.62 + 30, "xbold", self.p.get("label_size", 58),
                         self.p.get("label_color", WHITE), scale=pop_scale(t, la, 0.35))
        if self.p.get("sub") and t >= at + 0.6:
            put_text(f, self.p["sub"], W / 2, cy + size * 0.62 + 115, "hand", 52, (190, 195, 210),
                     alpha=ease_out(prog(t, at + 0.6, 0.4)))
        if self.p.get("stamp"):
            st = self.cue("stamp", at + dur + 0.6)
            if t >= st:
                p = prog(t, st, 0.2)
                L = text_layer(self.p["stamp"], "anton", 150, RED)
                box_l = np.zeros((L.shape[0] + 50, L.shape[1] + 70, 4), np.uint8)
                cv2.rectangle(box_l, (6, 6), (box_l.shape[1] - 7, box_l.shape[0] - 7), (*RED, 255), 12)
                blit(f, box_l, W / 2, cy, lerp(2, 1, ease_out(p)), clamp(p * 2), -10)
                blit(f, L, W / 2, cy, lerp(2, 1, ease_out(p)), clamp(p * 2), -10)
        if self.p.get("grid"):
            self.grid(f, t, at, fi)
        return f
    def grid(self, f, t, at, fi):
        g = self.p["grid"]  # dict(n, cols, color, y0)
        n, cols = g["n"], g["cols"]; rows = math.ceil(n / cols)
        cell = g.get("cell", 18); gx0 = W / 2 - cols * cell / 2; gy0 = g.get("y0", 120)
        shown = int(n * ease_out(prog(t, at, self.p.get("count_dur", 1.4))))
        for i in range(shown):
            r, c = divmod(i, cols)
            x, y = int(gx0 + c * cell), int(gy0 + r * cell)
            cv2.rectangle(f, (x, y), (x + cell - 5, y + cell - 5), g.get("color", LIME), -1)

# ------------------------------------------------------------------ comparison bars
class Bars(Scene):
    """p: items=[(label, value, color, valtext)], title, unit_note, max"""
    def render(self, t, fi):
        f = bg(self.p.get("bg", "paper"))
        dark = self.p.get("bg", "paper") == "dark"
        ink = WHITE if dark else INK
        if self.p.get("title"):
            put_text(f, self.p["title"], W / 2, 150, "xbold", 64, ink, scale=pop_scale(t, 0, 0.35))
        items = self.p["items"]; mx = self.p.get("max", max(v for _, v, _, _ in items))
        x0 = 520; x1 = 1700; bh = 120; gap = 70
        y = H / 2 - (len(items) * (bh + gap) - gap) / 2 + 40
        for i, (lab, v, col, vt) in enumerate(items):
            at = self.cue(f"bar{i}", 0.3 + i * 0.6)
            k = ease_out(prog(t, at, 1.0))
            put_text(f, lab, x0 - 30, y + bh / 2, "xbold", 50, ink, anchor="right", alpha=clamp(k * 3))
            if k > 0:
                xe = x0 + (x1 - x0) * v / mx * k
                box(f, x0, y, max(x0 + 30, xe), y + bh, col, INK, 5, fi, r=14, seed=i, shadow=True)
                if k > 0.6:
                    put_text(f, vt, xe + 24, y + bh / 2, "anton", 84, ink, anchor="left", alpha=clamp((k - 0.6) * 3))
            y += bh + gap
        if self.p.get("note"):
            put_text(f, self.p["note"], W / 2, H - 110, "hand", 46, (200, 200, 210) if dark else (110, 95, 80),
                     alpha=ease_out(prog(t, 1.2, 0.5)))
        if self.p.get("callout"):
            ct = self.cue("callout", 1.8)
            if t >= ct:
                put_text(f, self.p["callout"], W / 2, H - 200, "anton", 90, self.p.get("callout_color", RED),
                         scale=pop_scale(t, ct, 0.4))
        return f

# ------------------------------------------------------------------ pie / donut
class Pie(Scene):
    """p: share (0..1), label, big, color, note, remove_at(cue), title"""
    def render(self, t, fi):
        f = bg(self.p.get("bg", "paper"))
        dark = self.p.get("bg", "paper") == "dark"
        ink = WHITE if dark else INK
        cx, cy, r = self.p.get("cx", 560), H / 2 + 40, 300
        share = self.p["share"]
        k = ease_out(prog(t, 0.15, 1.1))
        rest = self.p.get("rest_color", (190, 200, 210) if not dark else (70, 80, 100))
        poly(f, circle_pts(cx, cy, r, 80), INK, fill=rest, thick=6, fi=fi, wob=1.2, seed=1)
        a1 = -90 + 360 * share * k
        off = 0
        rm = self.cue("remove", 999)
        if t >= rm:
            q = ease_in_out(prog(t, rm, 0.9)); off = q
        if k > 0.01 and off < 1:
            mid = math.radians(-90 + 180 * share)
            ox, oy = math.cos(mid) * (40 + 900 * off), math.sin(mid) * (40 + 900 * off) + 300 * off ** 2
            pts = [(cx + ox, cy + oy)] + circle_pts(cx + ox, cy + oy, r, 30, -90, a1)
            poly(f, pts, INK, fill=self.p.get("color", LIME), thick=6, fi=fi, wob=1.2, seed=2)
        if self.p.get("hole", True):
            poly(f, circle_pts(cx, cy, r * 0.5, 50), INK, fill=PAPER if not dark else DARK, thick=6, fi=fi, wob=1, seed=3)
        tx = self.p.get("tx", 1320)
        if t > 0.5:
            put_text(f, self.p["big"], tx, cy - 90, "anton", 190, self.p.get("big_color", self.p.get("color", LIME)) if not dark else YELLOW,
                     stroke=6 if not dark else 0, stroke_fill=INK, scale=pop_scale(t, 0.5, 0.4))
        if t > 0.8:
            put_text(f, self.p["label"], tx, cy + 70, "xbold", 46, ink, scale=pop_scale(t, 0.8, 0.35))
        if self.p.get("note") and t > 1.2:
            put_text(f, self.p["note"], tx, cy + 150, "hand", 40, (110, 95, 80) if not dark else (190, 195, 210),
                     alpha=ease_out(prog(t, 1.2, 0.4)))
        if self.p.get("title"):
            put_text(f, self.p["title"], W / 2, 110, "xbold", 58, ink)
        if t >= rm and self.p.get("remove_text"):
            put_text(f, self.p["remove_text"], tx, cy + 250, "anton", 110, RED, scale=pop_scale(t, rm + 0.5, 0.4))
        return f

# ------------------------------------------------------------------ line chart (real data)
class LineChart(Scene):
    """p: points=[(label, value)], unit fmt, reveal from cue 'start' to 'end', annotations"""
    def render(self, t, fi):
        f = bg("dark")
        pts = self.p["points"]; vals = [v for _, v in pts]
        vmin, vmax = self.p.get("ymin", 0), self.p.get("ymax", max(vals) * 1.1)
        x0, x1, y0, y1 = 220, 1700, 880, 260
        # axes + grid
        for gv in self.p.get("grid", []):
            gy = lerp(y0, y1, (gv - vmin) / (vmax - vmin))
            cv2.line(f, (x0, int(gy)), (x1, int(gy)), (55, 62, 82), 2, cv2.LINE_AA)
            put_text(f, f"${gv:.0f}T", x0 - 30, gy, "semi", 34, (150, 155, 175), anchor="right")
        poly(f, [(x0, y1 - 20), (x0, y0), (x1 + 20, y0)], (150, 155, 175), None, 4, fi, 0.8, 5, closed=False)
        a = self.cue("draw0", 0.2); b = self.cue("draw1", self.dur * 0.8)
        k = lerp(self.p.get("kmin", 0.0), self.p.get("kmax", 1.0), ease_in_out(prog(t, a, b - a)))
        n = len(pts); m = max(2, int(round(1 + (n - 1) * k)))
        xy = [(lerp(x0, x1, i / (n - 1)), lerp(y0, y1, (v - vmin) / (vmax - vmin))) for i, (_, v) in enumerate(pts)]
        # area fill
        shown = xy[:m]
        if len(shown) >= 2:
            area = shown + [(shown[-1][0], y0), (shown[0][0], y0)]
            ov = f.copy(); cv2.fillPoly(ov, [np.int32(area)], (120, 40, 50)); f[:] = cv2.addWeighted(ov, 0.35, f, 0.65, 0)
            poly(f, shown, RED, None, 9, fi, 0.6, 9, closed=False)
            ex, ey = shown[-1]; glow(f, ex, ey, 60, RED, 0.8)
            cv2.circle(f, (int(ex), int(ey)), 12, WHITE, -1, cv2.LINE_AA)
            put_text(f, f"${pts[m-1][1]:.1f}T", ex + 20, ey - 50, "anton", 64, WHITE, anchor="left", stroke=5, stroke_fill=DARK)
        # x labels
        for i in self.p.get("xticks", []):
            put_text(f, pts[i][0], xy[i][0], y0 + 40, "semi", 34, (170, 175, 195))
        for ann in self.p.get("ann", []):
            at = self.cue(ann["t"], 0) if isinstance(ann["t"], str) else ann["t"]
            if t >= at:
                put_text(f, ann["text"], ann["x"], ann["y"], ann.get("font", "anton"), ann.get("size", 80),
                         ann.get("color", YELLOW), stroke=6, stroke_fill=DARK, scale=pop_scale(t, at, 0.4))
        put_text(f, self.p.get("title", ""), W / 2, 150, "xbold", 52, WHITE)
        put_text(f, self.p.get("source", ""), W - 60, H - 40, "semi", 26, (130, 135, 155), anchor="right")
        return f

# ------------------------------------------------------------------ maps
@lru_cache(None)
def india_poly():
    polys = json.load(open(GEO / "india.json"))
    return [np.array(p, np.float32) for p in polys]

@lru_cache(None)
def land_polys():
    return [np.array(p, np.float32) for p in json.load(open(GEO / "land.json"))]

def proj_india(lon, lat, cx=960, cy=560, scale=27.0):
    # simple equirectangular with cos(lat) correction around 22N
    return cx + (lon - 82.5) * scale * math.cos(math.radians(22)), cy - (lat - 22.0) * scale

CITIES = {"Bengaluru": (77.59, 12.97), "Hyderabad": (78.49, 17.39), "Pune": (73.86, 18.52),
          "Gurugram": (77.03, 28.46), "Jamnagar": (70.06, 22.47), "Mumbai": (72.88, 19.08)}

class IndiaMap(Scene):
    """p: pins=[(city, label, cue)], wires(bool), title, note, glow, mode('draw')"""
    def render(self, t, fi):
        f = bg(self.p.get("bg", "dark"))
        sc = self.p.get("scale", 27.0); cx = self.p.get("cx", 960); cy = self.p.get("cy", 600)
        k = ease_out(prog(t, 0, 1.2)) if self.p.get("draw", False) else 1.0
        col = self.p.get("fill", (58, 70, 98))
        for i, pl in enumerate(india_poly()):
            pts = [proj_india(lon, lat, cx, cy, sc) for lon, lat in pl]
            if i == 0 and k < 1:
                m = max(2, int(len(pts) * k))
                poly(f, pts[:m], SAFFRON, None, 5, fi, 0, 0, closed=False)
            else:
                poly(f, pts, (235, 225, 205), fill=col, thick=4 if i == 0 else 1, fi=fi, wob=0, seed=i)
        if self.p.get("glow") and k >= 1:
            glow(f, cx, cy, 600, SAFFRON, 0.15 + 0.05 * math.sin(t * 3))
        if self.p.get("chip"):
            ct = self.cue("chip", 0.5)
            if t >= ct:
                chx, chy = self.p["chip"]
                chip(f, chx, chy, 90, fi, lit=self.p.get("chip_lit", 1.0), seed=4)
                for j, c in enumerate(["Bengaluru", "Hyderabad", "Pune", "Gurugram", "Mumbai"]):
                    px, py = proj_india(*CITIES[c], cx, cy, sc)
                    pk = ease_out(prog(t, ct + 0.15 * j, 0.6))
                    arrow(f, px, py, lerp(px, chx - 100, pk), lerp(py, chy, pk), LIME, 4, 0, fi, 20 + j, p=1.0)
        for city, label, cue in self.p.get("pins", []):
            at = self.cue(cue, 0.5) if isinstance(cue, str) else cue
            if t < at: continue
            px, py = proj_india(*CITIES[city], cx, cy, sc)
            s = pop_scale(t, at, 0.35)
            glow(f, px, py, 50 * s, YELLOW, 0.8)
            cv2.circle(f, (int(px), int(py)), int(14 * s), RED, -1, cv2.LINE_AA)
            cv2.circle(f, (int(px), int(py)), int(14 * s), WHITE, 3, cv2.LINE_AA)
            dxl = -1 if city in ("Pune", "Mumbai") else 1
            put_text(f, label, px + dxl * 30, py, "xbold", 40, WHITE, stroke=6, stroke_fill=DARK,
                     anchor="left" if dxl > 0 else "right", scale=s)
        if self.p.get("title"):
            put_text(f, self.p["title"], self.p.get("title_x", W / 2), self.p.get("title_y", 150), "anton", self.p.get("title_size", 96), YELLOW,
                     stroke=6, stroke_fill=DARK, scale=pop_scale(t, self.cue("title", 0.3), 0.4))
        if self.p.get("note"):
            nt = self.cue("note", 1.0)
            if t >= nt:
                put_text(f, self.p["note"], self.p.get("note_x", W / 2), self.p.get("note_y", H - 80), "hand", 54, WHITE,
                         alpha=ease_out(prog(t, nt, 0.4)))
        for card in self.p.get("cards", []):
            at = self.cue(card["t"], 1.0)
            if t >= at:
                s = pop_scale(t, at, 0.35)
                x0, y0 = card["x"], card["y"]
                L1 = text_layer(card["title"], "anton", 64, YELLOW); L2 = text_layer(card["text"], "semi", 36, WHITE)
                bw = max(L1.shape[1], L2.shape[1]) + 60; bh = L1.shape[0] + L2.shape[0] + 50
                pl = np.zeros((bh, bw, 4), np.uint8); cv2.rectangle(pl, (0, 0), (bw - 1, bh - 1), (*DARK2, 240), -1)
                cv2.rectangle(pl, (0, 0), (bw - 1, bh - 1), (*YELLOW, 255), 4)
                blit(f, pl, x0, y0, s)
                blit(f, L1, x0, y0 - L2.shape[0] / 2 - 4, s); blit(f, L2, x0, y0 + L1.shape[0] / 2 + 4, s)
        return f

def proj_world(lon, lat):
    return 960 + lon * 4.9, 560 - lat * 4.9

@lru_cache(None)
def world_dots():
    mask = np.zeros((H, W), np.uint8)
    for pl in land_polys():
        cv2.fillPoly(mask, [np.int32([proj_world(lo, la) for lo, la in pl])], 255)
    # paint India (IND point of view outline) so it is complete
    for pl in india_poly():
        cv2.fillPoly(mask, [np.int32([proj_world(lo, la) for lo, la in pl])], 255)
    dots = [(x, y) for y in range(40, H - 40, 18) for x in range(20, W - 20, 18) if mask[y, x]]
    return np.array(dots)

class WorldMap(Scene):
    """p: mode: 'pulses' (markets), 'darkwave' (chips going dark), 'flows' (money out of India), 'zoom_india'"""
    def render(self, t, fi):
        f = bg("dark"); mode = self.p.get("mode", "pulses")
        dots = world_dots()
        zoom = 1.0; zx, zy = 960, 560
        if mode == "zoom_india":
            k = ease_in_out(prog(t, 0.3, 2.2)); zoom = lerp(1, 3.2, k)
            ix, iy = proj_world(80, 22); zx, zy = lerp(960, ix, k), lerp(560, iy, k)
        for x, y in dots:
            X = (x - zx) * zoom + 960; Y = (y - zy) * zoom + 560
            if -20 < X < W + 20 and -20 < Y < H + 20:
                c = (70, 82, 110)
                if mode == "darkwave":
                    wave = (t - 0.3) * 900 - (x * 0.9)
                    c = LIME if wave < 0 else (50, 56, 72)
                if mode == "zoom_india":
                    lon = (x - 960) / 4.9; lat = (560 - y) / 4.9
                    if 68 < lon < 97.5 and 6.5 < lat < 37.1: c = SAFFRON
                cv2.circle(f, (int(X), int(Y)), max(2, int(4 * zoom ** 0.5)), c, -1, cv2.LINE_AA)
        if mode == "pulses":
            for i, (lon, lat, name) in enumerate([(-74, 40.7, "NEW YORK"), (-0.1, 51.5, "LONDON"), (8.7, 50.1, "FRANKFURT"),
                                                  (72.9, 19.1, "MUMBAI"), (139.7, 35.7, "TOKYO"), (114.2, 22.3, "HONG KONG"),
                                                  (151.2, -33.9, "SYDNEY")]):
                at = 0.2 + i * 0.35
                if t < at: continue
                x, y = proj_world(lon, lat)
                ph = ((t - at) % 1.2) / 1.2
                cv2.circle(f, (int(x), int(y)), int(10 + 60 * ph), RED, 3, cv2.LINE_AA)
                cv2.circle(f, (int(x), int(y)), 11, RED, -1, cv2.LINE_AA)
                put_text(f, name + " ▼" if False else name, x, y - 36, "xbold", 26, WHITE, stroke=4, stroke_fill=DARK)
        if mode == "flows":
            ix, iy = proj_world(77, 21)
            for j, (lon, lat) in enumerate([(-80, 38), (-2, 50), (10, 52)]):
                tx, ty = proj_world(lon, lat)
                for q in range(3):
                    ph = ((t * 0.6 + q / 3 + j * 0.1) % 1.0)
                    px, py = lerp(ix, tx, ph), lerp(iy, ty, ph) - math.sin(ph * math.pi) * 120
                    put_text(f, "$", px, py, "anton", 44, YELLOW, alpha=1 - abs(ph - 0.5) * 1.6)
            cv2.circle(f, (int(ix), int(iy)), 14, SAFFRON, -1, cv2.LINE_AA)
        if self.p.get("title"):
            put_text(f, self.p["title"], W / 2, self.p.get("title_y", 150), "anton", self.p.get("size", 96),
                     self.p.get("color", YELLOW), stroke=6, stroke_fill=DARK, scale=pop_scale(t, self.cue("title", 0.4), 0.4))
        if self.p.get("note"):
            put_text(f, self.p["note"], W / 2, H - 80, "hand", 50, (200, 205, 220), alpha=ease_out(prog(t, 1.0, 0.5)))
        return f

# ------------------------------------------------------------------ GPU explainer graphics
class ChipScene(Scene):
    """p: mode: 'gpu' (chip pops with label), 'parallel' (grid of cores all working), 'engine', 'dissolve', 'price'"""
    def render(self, t, fi):
        mode = self.p.get("mode", "gpu")
        f = bg(self.p.get("bg", "dark"))
        if mode == "gpu":
            s = ease_back(prog(t, 0.1, 0.5), 1.8)
            if s > 0: chip(f, W / 2, H / 2 - 40, 230 * s, fi, 1.0, seed=1, label="GPU" if s > 0.8 else None)
            if t > 0.8: put_text(f, self.p.get("caption", "GRAPHICS PROCESSING UNIT"), W / 2, H - 140, "xbold", 48, WHITE,
                                 scale=pop_scale(t, 0.8))
        elif mode == "parallel":
            cols, rows = 48, 20; cs = 26; gx = W / 2 - cols * cs / 2; gy = 250
            for r in range(rows):
                for c in range(cols):
                    ph = (math.sin(t * 9 + (r * 7 + c * 13) % 17) + 1) / 2
                    on = t > 0.4 + ((r * cols + c) % 37) * 0.012
                    col = tuple(int(lerp(a, b, ph)) for a, b in zip((40, 90, 50), LIME)) if on else (45, 50, 66)
                    cv2.rectangle(f, (int(gx + c * cs), int(gy + r * cs)), (int(gx + c * cs + cs - 6), int(gy + r * cs + cs - 6)), col, -1)
            put_text(f, self.p.get("title", "BILLIONS OF TINY MATHS PROBLEMS"), W / 2, 160, "anton", 88, WHITE, scale=pop_scale(t, 0.1))
            at = self.cue("big", 1.4)
            if t >= at:
                put_text(f, "ALL AT ONCE", W / 2, H - 140, "anton", 120, YELLOW, stroke=8, stroke_fill=DARK, scale=pop_scale(t, at))
        elif mode == "engine":
            chip(f, 620, H / 2, 190, fi, 1.0, seed=2, label="GPU")
            arrow(f, 870, H / 2, 1080, H / 2, WHITE, 9, 34, fi, 3, p=ease_out(prog(t, 0.3, 0.5)))
            if t > 0.6:
                put_text(f, "THE ENGINE\nOF AI", 1420, H / 2, "anton", 150, YELLOW, scale=pop_scale(t, 0.6))
        elif mode == "dissolve":
            # the word NVIDIA (plain text, not a logo) breaking into particles
            L = text_layer(self.p.get("word", "GONE"), "anton", 260, WHITE)
            p = ease_in_out(prog(t, self.cue("go", 0.6), 1.6))
            if p <= 0:
                blit(f, L, W / 2, H / 2)
            else:
                h, w = L.shape[:2]; r = np.random.default_rng(5)
                ys, xs = np.where(L[:, :, 3] > 128)
                idx = r.choice(len(ys), min(5000, len(ys)), replace=False)
                vx = r.uniform(-1, 1, len(idx)) * 700; vy = r.uniform(-1.3, 0.3, len(idx)) * 600
                X = (W / 2 - w / 2 + xs[idx] + vx * p ** 1.5).astype(int); Y = (H / 2 - h / 2 + ys[idx] + vy * p ** 1.5).astype(int)
                ok = (X >= 0) & (X < W - 3) & (Y >= 0) & (Y < H - 3)
                a = 1 - p
                for x, y in zip(X[ok], Y[ok]):
                    f[y:y + 3, x:x + 3] = (f[y:y + 3, x:x + 3] * (1 - a) + np.array(WHITE) * a).astype(np.uint8)
            if t > self.cue("label", 1.2):
                put_text(f, self.p.get("label", "GONE."), W / 2, H - 170, "anton", 110, RED, scale=pop_scale(t, self.cue("label", 1.2)))
        elif mode == "darkchips":
            n = 9
            for i in range(n):
                cx = 260 + (i % 5) * 350 + (175 if i >= 5 else 0); cy = 380 if i < 5 else 720
                off = self.cue("off", 0.6) + i * 0.12
                lit = 1 - ease_out(prog(t, off, 0.3))
                if lit > 0.05 and (fi % 4 < 2) and t > off - 0.2: lit *= 0.6
                chip(f, cx, cy, 95, fi, lit, seed=10 + i)
        elif mode == "price":
            chip(f, 560, H / 2 + 20, 170, fi, 1.0, seed=3)
            k = ease_out(prog(t, 0.4, 1.6))
            v = lerp(1, 9, k)
            put_text(f, "PRICE", 1250, 330, "xbold", 60, WHITE)
            for j in range(3):
                arrow(f, 1100 + j * 130, 820, 1100 + j * 130, lerp(820, 450, k), RED, 14, 40, fi, 30 + j, p=1)
            put_text(f, self.p.get("label", "SHOOTS UP"), 1250, 940, "anton", 110, RED, scale=pop_scale(t, 0.8))
        if self.p.get("kw"):
            kw_overlay(f, t, [dict(it, t=self.cue(it["t"]) if isinstance(it.get("t"), str) else it.get("t", 0)) for it in self.p["kw"]], fi)
        return f

# ------------------------------------------------------------------ cards (names, reasons, rivals)
class Cards(Scene):
    """p: cards=[dict(title, text, color, t(cue), icon)], title, layout('row'|'col'), stamp"""
    def render(self, t, fi):
        f = bg(self.p.get("bg", "paper"))
        dark = self.p.get("bg", "paper") == "dark"
        cards = self.p["cards"]; n = len(cards)
        if self.p.get("title"):
            put_text(f, self.p["title"], W / 2, 140, "anton", 96, WHITE if dark else INK, scale=pop_scale(t, 0.05))
        cw = min(400, (W - 200) / n - 40); chh = self.p.get("card_h", 360)
        total = n * cw + (n - 1) * 40; x = W / 2 - total / 2
        for i, c in enumerate(cards):
            at = self.cue(c.get("t", f"c{i}"), 0.25 + i * 0.3) if isinstance(c.get("t", None), str) or c.get("t") is None else c["t"]
            if t >= at:
                s = ease_back(prog(t, at, 0.35), 1.8)
                y0 = H / 2 - chh / 2 + 50 + (1 - s) * 80
                dim = self.p.get("dim") and i in self.p["dim"] and t > self.cue("dim", 99)
                fill = c.get("color", WHITE)
                if dim: fill = (120, 120, 125)
                box(f, x, y0, x + cw, y0 + chh, fill, INK, 6, fi, 26, seed=i * 3)
                put_text(f, c["title"], x + cw / 2, y0 + chh * 0.36, "anton", c.get("size", 74), INK)
                if c.get("text"):
                    put_text(f, c["text"], x + cw / 2, y0 + chh * 0.72, "semi", 32, INK, align="center")
                if c.get("icon") == "hourglass":
                    k = (t * 0.7) % 1
                    put_text(f, "⏳" if False else "...", x + cw / 2, y0 + chh * 0.72, "anton", 60, (110, 110, 120))
            x += cw + 40
        if self.p.get("stamp"):
            st = self.cue("stamp", 1.5)
            if t >= st:
                p = prog(t, st, 0.2)
                put_text(f, self.p["stamp"], W / 2, H / 2 + 60, "anton", 170, RED, scale=lerp(2, 1, ease_out(p)),
                         alpha=clamp(p * 2), rot=-8, stroke=10, stroke_fill=WHITE)
        if self.p.get("note"):
            nt = self.cue("note", 1.2)
            if t >= nt:
                put_text(f, self.p["note"], W / 2, H - 110, "hand", 50, (200, 205, 220) if dark else (110, 95, 80),
                         alpha=ease_out(prog(t, nt, 0.4)))
        return f

# ------------------------------------------------------------------ timeline roadmap
class Timeline(Scene):
    STEPS = ["HOUR 1", "DAY 1", "WEEK 1", "MONTH 6", "YEAR 1"]
    def render(self, t, fi):
        steps = self.p.get("steps", self.STEPS)
        f = bg("dark")
        x0, x1, y = 230, 1690, 600
        cur = self.p.get("cur", -1)
        k = ease_out(prog(t, 0.1, 1.0))
        poly(f, [(x0, y), (lerp(x0, x1, k), y)], (110, 118, 140), None, 8, fi, 1.0, 1, closed=False)
        for i, s in enumerate(steps):
            x = lerp(x0, x1, i / max(1, len(steps) - 1))
            at = 0.2 + i * 0.18
            if t < at: continue
            sc = pop_scale(t, at, 0.3)
            done = i < cur; active = i == cur
            col = YELLOW if active else (LIME if done else (90, 98, 122))
            cv2.circle(f, (int(x), y), int(30 * sc), col, -1, cv2.LINE_AA)
            cv2.circle(f, (int(x), y), int(30 * sc), WHITE, 4, cv2.LINE_AA)
            put_text(f, s, x, y + 90, "anton", 64 if active else 50, col if active else WHITE, scale=sc)
            if active: glow(f, x, y, 140, YELLOW, 0.3 + 0.1 * math.sin(t * 5))
        put_text(f, self.p.get("title", "THE TIMELINE"), W / 2, 260, "anton", 110, WHITE, scale=pop_scale(t, 0))
        return f

# ------------------------------------------------------------------ code editor that stops
class CodeEditor(Scene):
    CODE = ["def answer(question):", "    model = load_model()", "    tokens = tokenize(question)",
            "    for step in range(1000):", "        tokens = model.next(tokens)", "    return decode(tok"]
    def render(self, t, fi):
        f = bg("paper")
        box(f, 260, 170, 1660, 900, (32, 36, 50), INK, 6, fi, 24, 2)
        for i, c in enumerate([(255, 95, 86), (255, 189, 46), (39, 201, 63)]):
            cv2.circle(f, (310 + i * 40, 215), 12, c, -1, cv2.LINE_AA)
        stop = self.cue("stop", self.dur * 0.55)
        chars = int(min(t, stop) * 32)
        y = 300; shown = 0
        for ln in self.CODE:
            take = max(0, min(len(ln), chars - shown)); shown += len(ln)
            if take > 0:
                put_text(f, ln[:take], 320, y, "semi", 40, (210, 220, 235) if not ln.startswith("def") else (130, 200, 255), anchor="left")
            y += 80
            if take < len(ln): break
        if t > stop:
            if (fi // 10) % 2 == 0:
                put_text(f, "▌" if False else "|", 320 + 20 * 0, y - 80, "semi", 40, WHITE, anchor="left", alpha=0)
            put_text(f, "CONNECTION LOST", W / 2, 960, "anton", 90, RED, scale=pop_scale(t, stop + 0.2))
        return f

# ------------------------------------------------------------------ service tiles going dark
class Tiles(Scene):
    def render(self, t, fi):
        f = bg("dark")
        cols, rows = 10, 5; tw, th = 150, 120; gx = W / 2 - cols * (tw + 16) / 2; gy = 260
        survivors = {7, 23, 41}
        off_at = self.cue("off", 0.6)
        for r in range(rows):
            for c in range(cols):
                i = r * cols + c
                o = off_at + ((i * 37) % 50) * 0.025
                lit = 1.0 if (i in survivors or t < o) else 0.0
                col = (LIME if i not in survivors else (90, 170, 255)) if lit else (48, 54, 70)
                x, y = int(gx + c * (tw + 16)), int(gy + r * (th + 16))
                cv2.rectangle(f, (x, y), (x + tw, y + th), col, -1)
                cv2.rectangle(f, (x, y), (x + tw, y + th), (20, 22, 30), 3)
        put_text(f, self.p.get("title", "AI SERVICES"), W / 2, 150, "anton", 96, WHITE)
        if self.p.get("note") and t > off_at + 1.2:
            put_text(f, self.p["note"], W / 2, H - 120, "xbold", 52, (90, 170, 255), scale=pop_scale(t, off_at + 1.2))
        return f

# ------------------------------------------------------------------ progress bar slowing to stop
class Progress(Scene):
    def render(self, t, fi):
        f = bg("dark")
        k = 1 - math.exp(-t * 1.2)
        v = min(0.62, k * 0.62)
        box(f, 360, 480, 1560, 600, (45, 52, 70), WHITE, 5, fi, 30, 1, shadow=False)
        if v > 0.01: box(f, 372, 492, 372 + 1176 * v, 588, LIME if t < self.cue("stop", 1.5) else RED, None, 0, fi, 24, 2, shadow=False)
        put_text(f, "SLOWING DOWN..." if t < self.cue("stop", 1.5) else "STOPPED.", W / 2, 360, "anton", 110,
                 WHITE if t < self.cue("stop", 1.5) else RED, scale=1.0)
        return f

# ------------------------------------------------------------------ single point of failure network / chain
class Network(Scene):
    def render(self, t, fi):
        f = bg("dark")
        mode = self.p.get("mode", "spof")
        if mode == "spof":
            cx, cy = W / 2, H / 2 + 30
            n = 22
            for i in range(n):
                a = 2 * math.pi * i / n; R = 380 + 40 * (i % 3)
                x, y = cx + R * math.cos(a), cy + R * 0.72 * math.sin(a)
                k = ease_out(prog(t, 0.1 + i * 0.03, 0.4))
                arrow(f, x, y, lerp(x, cx, 0.8 * k), lerp(y, cy, 0.8 * k), (120, 130, 160), 3, 0, fi, i, p=1)
                cv2.circle(f, (int(x), int(y)), 18, (120, 180, 255), -1, cv2.LINE_AA)
            red = t > self.cue("fail", 1.6) and (fi // 6) % 2 == 0
            chip(f, cx, cy, 90, fi, 1.0, color=RED if red else LIME, seed=7)
            if t > self.cue("fail", 1.6):
                put_text(f, "SINGLE POINT\nOF FAILURE", W / 2, 140, "anton", 92, RED, stroke=6, stroke_fill=DARK,
                         scale=pop_scale(t, self.cue("fail", 1.6)))
        else:  # chain WORLD -> NVIDIA -> TSMC
            labels = [(lab, col) for lab, col in zip(self.p.get("chain", ["THE WORLD", "COMPANY", "SUPPLIER"]), [BLUE, LIME, ORANGE])]
            xs = [380, 960, 1540]
            for i, (lab, col) in enumerate(labels):
                at = 0.2 + i * 0.7
                if t < at: continue
                s = pop_scale(t, at)
                box(f, xs[i] - 220 * s, H / 2 - 110 * s, xs[i] + 220 * s, H / 2 + 110 * s, col, WHITE, 6, fi, 26, i)
                put_text(f, lab, xs[i], H / 2, "anton", 80, DARK, scale=s)
                if i:
                    arrow(f, xs[i - 1] + 230, H / 2, xs[i] - 235, H / 2, WHITE, 8, 30, fi, 9 + i, p=ease_out(prog(t, at - 0.3, 0.4)))
            put_text(f, "DEPENDS ON", 670, H / 2 - 160, "hand", 54, WHITE, alpha=ease_out(prog(t, 0.6, 0.3)))
            put_text(f, "DEPENDS ON", 1250, H / 2 - 160, "hand", 54, WHITE, alpha=ease_out(prog(t, 1.3, 0.3)))
        return f

# ------------------------------------------------------------------ towers: one giant -> six
class Towers(Scene):
    def render(self, t, fi):
        f = bg("dark")
        base = 900
        sp = self.cue("split", 0.9)
        k = ease_in_out(prog(t, sp, 1.2))
        if k < 1:
            hgt = 620 * (1 - k)
            box(f, W / 2 - 140, base - hgt, W / 2 + 140, base, LIME, WHITE, 6, fi, 12, 1, shadow=False)
        cols = [LIME, BLUE, ORANGE, TEAL, YELLOW, RED]
        for i in range(6):
            x = 360 + i * 240; hgt = 380 * k * (0.85 + 0.15 * ((i * 7) % 3) / 2)
            if hgt > 5:
                box(f, x - 80, base - hgt, x + 80, base, cols[i], WHITE, 5, fi, 12, 3 + i, shadow=False)
        cv2.line(f, (150, base), (W - 150, base), (150, 155, 175), 4, cv2.LINE_AA)
        put_text(f, self.p.get("before", "1 GIANT") if k < 0.5 else self.p.get("after", "MANY PLAYERS"), W / 2, 150, "anton", 110, YELLOW, scale=1.0)
        return f

# ------------------------------------------------------------------ title card & end screen
class Title(Scene):
    def render(self, t, fi):
        f = Illus(img=self.p.get("img", "img06"), a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.1)); f.dur = self.dur
        fr = f.render(t, fi)
        fr = (fr * 0.55).astype(np.uint8)
        lines = self.p.get("lines", [("WHAT IF", WHITE, 150), ("THE TITLE GOES HERE", YELLOW, 210), ("TOMORROW?", WHITE, 170)])
        ys = {1: [540], 2: [430, 650], 3: [330, 520, 730]}[len(lines)]
        for i, ((txt, col, size), y) in enumerate(zip(lines, ys)):
            put_text(fr, txt, W / 2, y, "anton", size, col, stroke=9, stroke_fill=DARK, scale=pop_scale(t, 0.2 + 0.35 * i))
        return fr

class EndScreen(Scene):
    def render(self, t, fi):
        f = Illus(img=self.p.get("img", "img51"), a=(0.5, 0.5, 1.0), b=(0.5, 0.5, 1.06)); f.dur = self.dur
        fr = (f.render(t, fi) * 0.45).astype(np.uint8)
        l1, l2 = self.p.get("lines", ("SUBSCRIBE FOR MORE", "'WHAT IF' STORIES"))
        put_text(fr, l1, W / 2, 150, "anton", 110, WHITE, stroke=6, stroke_fill=DARK, scale=pop_scale(t, 0.2))
        put_text(fr, l2, W / 2, 285, "anton", 130, YELLOW, stroke=8, stroke_fill=DARK, scale=pop_scale(t, 0.45))
        # empty frames where YouTube end-screen elements (2 videos + subscribe) will sit
        for i, x in enumerate((560, 1360)):
            k = ease_out(prog(t, 0.8 + i * 0.2, 0.4))
            if k > 0:
                pts = rrect_pts(x - 330, 470, x + 330, 842, 20)
                poly(fr, pts, (230, 230, 235), None, 4, fi, 1.0, 40 + i)
                put_text(fr, "WATCH NEXT" if i == 0 else "MORE VIDEOS", x, 656, "xbold", 40, (220, 220, 230), alpha=0.6 * k)
        cv2.circle(fr, (W // 2, 960), int(70 * ease_back(prog(t, 1.3, 0.4))), RED, -1, cv2.LINE_AA)
        if t > 1.3:
            put_text(fr, "SUBSCRIBE", W / 2, 960, "xbold", 30, WHITE, scale=ease_back(prog(t, 1.3, 0.4)))
        return fr

# ------------------------------------------------------------------ black text card (pro signature beat)
class TextCard(Scene):
    """Black card, white handwritten text typed on letter by letter (the reference video uses one
    about every 17 s, ~2.7 s long, for punchlines, questions and chapter titles).
    p: text, size (90), cps (typing speed, 26), chapter (bool: bigger, centred, no typing), color"""
    def render(self, t, fi):
        f = np.zeros((H, W, 3), np.uint8); f[:] = (8, 8, 10)
        txt = self.p["text"]; chapter = self.p.get("chapter", False)
        size = self.p.get("size", 128 if chapter else 92)
        col = self.p.get("color", WHITE)
        import textwrap
        lines = textwrap.wrap(txt, 30 if not chapter else 22)
        full = "\n".join(lines)
        if chapter:
            shown = full; a = ease_out(prog(t, 0.05, 0.35))
        else:
            n = int(prog(t, 0.08, max(0.25, len(txt) / self.p.get("cps", 26))) * len(full) + 0.999)
            shown = full[:n]; a = 1.0
        if shown.strip():
            L = text_layer(full, "script", size, col, align="left" if not chapter else "center")
            sub = text_layer(shown, "script", size, col, align="left" if not chapter else "center")
            s = 1.0 + 0.025 * ease_in_out(t / max(self.dur, 0.1))
            x0 = W / 2 - L.shape[1] * s / 2
            blit(f, sub, x0 if not chapter else W / 2, H / 2 - (L.shape[0] - sub.shape[0]) * s / 2, s, a,
                 anchor="left" if not chapter else "center")
        return f

TYPES = dict(text=TextCard, illus=Illus, big=BigText, counter=Counter, bars=Bars, pie=Pie, line=LineChart, india=IndiaMap,
             world=WorldMap, chip=ChipScene, cards=Cards, timeline=Timeline, code=CodeEditor, tiles=Tiles,
             progress=Progress, network=Network, towers=Towers, title=Title, end=EndScreen)
