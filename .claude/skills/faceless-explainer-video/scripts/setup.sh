#!/usr/bin/env bash
# One-time setup: Python packages + free assets (all commercial-use licences).
#   Kokoro-82M TTS weights (Apache-2.0) via kokoro-onnx GitHub release (MIT)
#   Fonts: Anton, Poppins, Patrick Hand (SIL Open Font Licence)
#   Natural Earth map data (public domain), India uses the official "India point of view" borders
# Assets go to $VIDEO_ASSETS (default ~/.video_assets). Safe to re-run.
set -euo pipefail
A="${VIDEO_ASSETS:-$HOME/.video_assets}"; mkdir -p "$A/models" "$A/fonts" "$A/geo"
pip install --break-system-packages -q kokoro-onnx soundfile pyloudnorm scipy numpy pillow opencv-python-headless pyshp fonttools librosa 2>&1 | grep -v -i warning || true
cd "$A/models"
for f in kokoro-v1.0.onnx voices-v1.0.bin; do
  [ -s "$f" ] || curl -sSfL -O "https://github.com/thewh1teagle/kokoro-onnx/releases/download/model-files-v1.0/$f"
done
cd "$A/fonts"
for f in ofl/anton/Anton-Regular.ttf ofl/poppins/Poppins-ExtraBold.ttf ofl/poppins/Poppins-Bold.ttf \
         ofl/poppins/Poppins-SemiBold.ttf ofl/poppins/Poppins-Black.ttf ofl/patrickhand/PatrickHand-Regular.ttf \
         apache/permanentmarker/PermanentMarker-Regular.ttf ofl/kalam/Kalam-Bold.ttf; do
  [ -s "$(basename $f)" ] || curl -sSfL -O "https://raw.githubusercontent.com/google/fonts/main/$f"
done
[ -s Caveat-VF.ttf ] || curl -sSfL -o Caveat-VF.ttf "https://raw.githubusercontent.com/google/fonts/main/ofl/caveat/Caveat%5Bwght%5D.ttf"
cd "$A/geo"
for f in ne_10m_admin_0_countries_ind ne_110m_land; do
  d=$([ $f = ne_110m_land ] && echo 110m_physical || echo 10m_cultural)
  for e in shp shx dbf; do [ -s "$f.$e" ] || curl -sSfL -o "$f.$e" "https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/$d/$f.$e"; done
done
python3 - <<'PY'
import shapefile, json, numpy as np
r = shapefile.Reader('ne_10m_admin_0_countries_ind'); fields = [x.name for x in r.fields[1:]]
for sr in r.iterShapeRecords():
    if dict(zip(fields, sr.record))['ADM0_A3'] == 'IND':
        pts = np.array(sr.shape.points); parts = list(sr.shape.parts) + [len(pts)]
        polys = sorted([pts[parts[i]:parts[i+1]] for i in range(len(parts)-1)], key=len, reverse=True)
        json.dump([p[::3].tolist() for p in polys if len(p) > 40], open('india.json', 'w'))
L = []
for s in shapefile.Reader('ne_110m_land').shapes():
    parts = list(s.parts) + [len(s.points)]
    L += [s.points[parts[i]:parts[i+1]] for i in range(len(parts)-1)]
json.dump(L, open('land.json', 'w'))
PY
echo "assets ready in $A"
