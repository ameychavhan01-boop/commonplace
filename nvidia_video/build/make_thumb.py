"""thumbnail.jpg (1280x720). usage: python make_thumb.py OUT.jpg [BASE_IMAGE]
BASE_IMAGE = the ElevenLabs cartoon (character on the right, cracking chip on the left).
Without it, a code-drawn cracked chip is used as a stand-in."""
import sys, math
import numpy as np, cv2
from PIL import Image
import gfx
from gfx import *

TW, TH = 1280, 720
out = sys.argv[1]
base_p = sys.argv[2] if len(sys.argv) > 2 else None

if base_p:
    im = cv2.cvtColor(cv2.imread(base_p), cv2.COLOR_BGR2RGB)
    h, w = im.shape[:2]; tgt = 16 / 9
    if w / h > tgt: nw = int(h * tgt); im = im[:, (w - nw) // 2:(w - nw) // 2 + nw]
    else: nh = int(w / tgt); im = im[(h - nh) // 2:(h - nh) // 2 + nh]
    f = cv2.resize(im, (W, H), interpolation=cv2.INTER_LANCZOS4)
    # darken left side so the words pop
    grad = np.clip(1 - np.linspace(0, 1, W)[None, :, None] * 1.6, 0, 1) * 0.55
    f = (f * (1 - grad)).astype(np.uint8)
else:
    f = dark_bg()
    glow(f, 1400, 560, 700, RED, 0.35)
    chip(f, 1400, 560, 260, 0, 1.0, seed=2)
    r = np.random.default_rng(3)
    for k in range(7):   # cracks
        x, y = 1400, 560; pts = [(x, y)]
        a = r.uniform(0, 2 * math.pi)
        for s in range(6):
            a += r.uniform(-0.6, 0.6); x += math.cos(a) * 60; y += math.sin(a) * 60; pts.append((x, y))
        poly(f, pts, (255, 240, 200), None, 9, 0, 0, k, closed=False)
    for k in range(160):   # flying pixels
        x, y = 1400 + r.normal(0, 340), 560 + r.normal(0, 260)
        s = int(r.uniform(8, 26)); c = LIME if r.random() < 0.6 else YELLOW
        cv2.rectangle(f, (int(x), int(y)), (int(x) + s, int(y) + s), c, -1)

# --- words: big, few, high contrast (readable on a phone)
put_text(f, "NVIDIA", 540, 300, "anton", 250, WHITE, stroke=14, stroke_fill=DARK, shadow=10)
put_text(f, "GONE?", 540, 610, "anton", 380, YELLOW, stroke=16, stroke_fill=DARK, shadow=12)
# red accent tag
L = text_layer("WHAT IF...", "anton", 96, WHITE)
tag = np.zeros((L.shape[0] + 30, L.shape[1] + 60, 4), np.uint8); tag[:, :, :3] = RED; tag[:, :, 3] = 255
blit(f, tag, 300, 110, rot=-4); blit(f, L, 300, 110, rot=-4)
t = cv2.resize(f, (TW, TH), interpolation=cv2.INTER_AREA)
Image.fromarray(t).save(out, quality=92, optimize=True)
print("saved", out)
