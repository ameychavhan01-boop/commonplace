#!/usr/bin/env bash
# Build every deliverable. Run from the project folder (which holds these scripts plus
# narration.py, plan.py, doodle_scenes.py). Optional AI art: illustrations/imgNN.png.
#   VOICE=am_michael SPEED=0.97 PAUSE=0.6 ./build_all.sh
#   THUMB_TOP / THUMB_BIG / THUMB_TAG set the thumbnail words.
set -euo pipefail
cd "$(dirname "$0")"
WK=work; OUT=${OUT:-deliverables}; mkdir -p "$WK" "$OUT"
VOICE=${VOICE:-am_michael}; SPEED=${SPEED:-0.97}; PAUSE=${PAUSE:-0.6}
# 1. narration (skip if already made; delete work/voice to redo)
if [ ! -f "$WK/voice/narration.wav" ]; then python3 make_voice.py "$VOICE" "$SPEED" "$WK/voice" "$PAUSE"; cp "$WK/voice/timings.json" timings.json; fi
TOTAL=$(python3 -c "import plan; print(plan.TOTAL)")
# 2. original score (follows the story) + sound effects
python3 audio_gen.py "$WK/audio" "$(python3 -c 'import plan; print(plan.VO)')" "$TOTAL"
# 3. mix: music 11 LU under the voice; master + voice-only at -15 LUFS / -2 dBTP
python3 mix.py "$WK/voice/narration.wav" "$WK/audio" "$WK/mix.wav" "$WK/voice_only.wav"
# 4. picture (about 2x real time on 4 cores)
python3 render.py video "$WK/video_noaudio.mp4" --workers "${WORKERS:-4}"
# 5. encodes: 1080p ~3.3 Mbps and 720p ~2.1 Mbps stay small enough to send in chat (<250 MB for ~9 min)
ffmpeg -y -loglevel error -i "$WK/video_noaudio.mp4" -i "$WK/mix.wav" -map 0:v -map 1:a -c:v libx264 -preset faster \
  -b:v 3.3M -maxrate 4M -bufsize 8M -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000 -movflags +faststart -shortest "$OUT/final_video_1080p.mp4"
ffmpeg -y -loglevel error -i "$WK/video_noaudio.mp4" -i "$WK/mix.wav" -map 0:v -map 1:a -vf scale=1280:720:flags=lanczos \
  -c:v libx264 -preset faster -b:v 2.1M -maxrate 2.6M -bufsize 5M -pix_fmt yuv420p -r 30 -c:a aac -b:a 160k -ar 48000 \
  -movflags +faststart -shortest "$OUT/final_video_720p.mp4"
ffmpeg -y -loglevel error -i "$OUT/final_video_1080p.mp4" -i "$WK/voice_only.wav" -map 0:v -map 1:a -c:v copy -c:a aac -b:a 160k \
  -ar 48000 -movflags +faststart -shortest "$OUT/final_video_voice_only.mp4"
# 6. thumbnail + subtitles
TB=(); [ -f illustrations/thumb_base.png ] && TB=(illustrations/thumb_base.png)
python3 make_thumb.py "$OUT/thumbnail.jpg" "${TB[@]}" --top "${THUMB_TOP:-NVIDIA}" --big "${THUMB_BIG:-GONE?}" --tag "${THUMB_TAG:-WHAT IF...}"
python3 make_subs.py "$OUT/subtitles.srt"
# 7. integrity: every file must decode with zero errors
for f in "$OUT"/*.mp4; do e=$(ffmpeg -v error -i "$f" -f null - 2>&1 | head -1); [ -z "$e" ] || { echo "DECODE ERROR in $f: $e"; exit 1; }; done
ls -la "$OUT"; echo "ALL DONE"
