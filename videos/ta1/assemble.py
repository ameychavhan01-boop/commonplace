"""Join rendered scenes and mux audio. Usage: python assemble.py BUILD OUTDIR"""
import sys, subprocess, json
import timeline

build, out = sys.argv[1], sys.argv[2]
tl = timeline.load(build)
lst = f'{build}/concat.txt'
with open(lst, 'w') as f:
    for m, b, T in tl:
        f.write(f"file '{build}/scenes/{m['id']}.mp4'\n")
def probe_frames(p):
    r = subprocess.run(['ffprobe', '-v', 'error', '-select_streams', 'v:0', '-count_packets', '-show_entries', 'stream=nb_read_packets', '-of', 'csv=p=0', p], capture_output=True, text=True)
    return int(r.stdout.strip())
bad = []
for m, b, T in (tl if '--check' in sys.argv else []):
    exp = int(round(b.end * 30)); got = probe_frames(f"{build}/scenes/{m['id']}.mp4")
    if exp != got: bad.append((m['id'], exp, got))
print('frame check:', 'OK' if not bad else bad)
subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-f', 'concat', '-safe', '0', '-i', lst, '-c', 'copy', f'{build}/video_only.mp4'], check=True)
for name, wav in (('final_video.mp4', 'final_audio.wav'), ('voice_only_video.mp4', 'voice_only_audio.wav')):
    subprocess.run(['ffmpeg', '-y', '-loglevel', 'error', '-i', f'{build}/video_only.mp4', '-i', f'{out}/{wav}', '-map', '0:v', '-map', '1:a',
                    '-c:v', 'copy', '-c:a', 'aac', '-b:a', '192k', '-ar', '48000', '-shortest', '-movflags', '+faststart', f'{out}/{name}'], check=True)
    r = subprocess.run(['ffprobe', '-v', 'error', '-show_entries', 'format=duration,size:stream=codec_name,width,height,r_frame_rate', '-of', 'json', f'{out}/{name}'], capture_output=True, text=True)
    info = json.loads(r.stdout)
    lo = subprocess.run(['ffmpeg', '-hide_banner', '-nostats', '-i', f'{out}/{name}', '-map', '0:a', '-af', 'ebur128=peak=true', '-f', 'null', '-'], capture_output=True, text=True).stderr
    I = [l for l in lo.splitlines() if 'I:' in l][-1].strip(); P = [l for l in lo.splitlines() if 'Peak:' in l][-1].strip()
    print(name, f"{float(info['format']['duration'])/60:.2f} min", f"{int(info['format']['size'])/1e6:.0f} MB",
          [(s['codec_name'], s.get('width'), s.get('height'), s.get('r_frame_rate')) for s in info['streams']], I, P)
