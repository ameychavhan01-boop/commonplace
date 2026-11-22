#!/usr/bin/env bash
# Rebuild every deliverable. Illustrations go in $S/illustrations/img01.png ... img51.png
# (missing ones fall back to placeholder cards); thumbnail art in $S/illustrations/thumb_base.png.
set -euo pipefail
cd "$(dirname "$0")"
S=/tmp/claude-0/-home-user-commonplace/b86ce5d7-0153-5b98-a71a-4c4535dda987/scratchpad
OUT=..
# 1. voice: Kokoro am_michael, speed 0.97, US English, chunk by chunk (pauses at 60%)
[ -f "$S/voice_michael/narration.wav" ] || { python3 make_voice.py am_michael 0.97 "$S/voice_michael" 0.6; cp "$S/voice_michael/timings.json" timings.json; }
TOTAL=$(python3 -c "import plan; print(plan.TOTAL)")
# 2. music (original lo-fi, 76 BPM) + SFX
python3 music.py "$S/audio/music.wav" "$TOTAL"
python3 -c "import audio_gen, soundfile as sf; [sf.write('$S/audio/sfx_'+k+'.wav', f(), 48000) for k, f in audio_gen.SFX.items()]"
# 3. mix: music ~11 dB under voice; master + voice-only at -15 LUFS, ~-2 dBTP
python3 mix.py "$S/voice_michael/narration.wav" "$S/audio" "$S/mix.wav" "$S/voice_only.wav"
# 4. picture
python3 render.py video "$S/video_noaudio.mp4" --workers 4
# 5. final encodes (YouTube-friendly bitrate)
ENC="-c:v libx264 -preset slow -crf 19 -maxrate 14M -bufsize 28M -pix_fmt yuv420p -r 30"
ffmpeg -y -loglevel error -i "$S/video_noaudio.mp4" -i "$S/mix.wav" -map 0:v -map 1:a $ENC \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT/final_video.mp4"
ffmpeg -y -loglevel error -i "$OUT/final_video.mp4" -i "$S/voice_only.wav" -map 0:v -map 1:a -c:v copy \
  -c:a aac -b:a 256k -ar 48000 -movflags +faststart -shortest "$OUT/final_video_voice_only.mp4"
if [ -f "$S/illustrations/thumb_base.png" ]; then
  python3 make_thumb.py "$OUT/thumbnail.jpg" "$S/illustrations/thumb_base.png"
else
  python3 make_thumb.py "$OUT/thumbnail.jpg"
fi
python3 make_subs.py "$OUT/subtitles.srt"
echo "ALL DONE"
