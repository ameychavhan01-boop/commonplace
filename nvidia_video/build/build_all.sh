#!/usr/bin/env bash
# Rebuild every deliverable. Illustrations go in $S/illustrations/img01.png ... img51.png
# (missing ones fall back to placeholder cards), thumbnail art in $S/illustrations/thumb_base.png.
set -euo pipefail
cd "$(dirname "$0")"
S=/tmp/claude-0/-home-user-commonplace/b86ce5d7-0153-5b98-a71a-4c4535dda987/scratchpad
OUT=..
TOTAL=$(python3 -c "import plan; print(plan.TOTAL)")

[ -f "$S/voice13/narration.wav" ] || python3 make_voice.py bm_fable 1.3 "$S/voice13" 0.85
python3 audio_gen.py "$S/audio" 0.4 "$TOTAL"
python3 mix.py "$S/voice13/narration.wav" "$S/audio" "$S/mix.wav"
python3 render.py video "$S/video_noaudio.mp4" --workers 4
ffmpeg -y -loglevel error -i "$S/video_noaudio.mp4" -i "$S/mix.wav" -map 0:v -map 1:a \
  -c:v copy -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT/final_video.mp4"
if [ -f "$S/illustrations/thumb_base.png" ]; then
  python3 make_thumb.py "$OUT/thumbnail.jpg" "$S/illustrations/thumb_base.png"
else
  python3 make_thumb.py "$OUT/thumbnail.jpg"
fi
python3 make_subs.py "$OUT/subtitles.srt"
echo "ALL DONE"
