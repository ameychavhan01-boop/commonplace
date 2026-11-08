#!/usr/bin/env python3
"""
Turn the supplied JSR logo (black disc on a white background) into a clean
circular asset with a transparent outside:

    python3 prepare_logo.py <source image>  ->  assets/jsr_logo.png

The disc is rebuilt as a perfect anti-aliased circle in pure black, and the
lettering is kept from the source's brightness (levels-cleaned) in white.
"""
import os
import sys

import numpy as np
from PIL import Image, ImageDraw, ImageFilter

HERE = os.path.dirname(os.path.abspath(__file__))
OUT_SIZE = 1200


def main(src_path):
    g = np.asarray(Image.open(src_path).convert("L")).astype(np.float32)
    dark = g < 100
    ys, xs = np.nonzero(dark)
    cx, cy = (xs.min() + xs.max()) / 2, (ys.min() + ys.max()) / 2
    r = ((xs.max() - xs.min()) + (ys.max() - ys.min())) / 4

    # lettering: bright pixels well inside the disc, levels-cleaned
    yy, xx = np.mgrid[0:g.shape[0], 0:g.shape[1]]
    inside = np.hypot(xx - cx, yy - cy) < r * 0.92
    letters = np.clip((g - 45) / (205 - 45), 0, 1) * inside

    # crop a square around the disc and scale to the output size
    box = (int(round(cx - r)), int(round(cy - r)), int(round(cx + r)), int(round(cy + r)))
    L = Image.fromarray((letters * 255).astype(np.uint8)).crop(box)
    L = L.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS).filter(ImageFilter.GaussianBlur(0.6))
    L = Image.fromarray((np.clip((np.asarray(L) / 255.0 - 0.5) * 1.6 + 0.5, 0, 1) * 255).astype(np.uint8))

    # perfect anti-aliased disc
    S = 4
    disc = Image.new("L", (OUT_SIZE * S, OUT_SIZE * S), 0)
    ImageDraw.Draw(disc).ellipse((0, 0, OUT_SIZE * S - 1, OUT_SIZE * S - 1), fill=255)
    disc = disc.resize((OUT_SIZE, OUT_SIZE), Image.LANCZOS)

    rgb = np.zeros((OUT_SIZE, OUT_SIZE, 3), np.float32)
    rgb += (np.asarray(L, np.float32)[..., None] / 255.0) * 255
    out = Image.fromarray(np.clip(rgb, 0, 255).astype(np.uint8), "RGB").convert("RGBA")
    out.putalpha(disc)
    dst = os.path.join(HERE, "assets", "jsr_logo.png")
    os.makedirs(os.path.dirname(dst), exist_ok=True)
    out.save(dst)
    print("centre=(%.1f, %.1f) radius=%.1f -> %s" % (cx, cy, r, dst))


if __name__ == "__main__":
    main(sys.argv[1])
