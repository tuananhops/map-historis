#!/usr/bin/env bash
# assemble.sh <project_dir> [seconds]  — concat segments, loudnorm -14 LUFS (2 pass), burn subs, H.264 crf18 + AAC
set -e
TK="$(cd "$(dirname "$0")/.." && pwd)"; cd "$1"
TOTAL=${2:-$(cat assets/total.txt)}
ffmpeg -y -loglevel error -f concat -safe 0 -i seg/list.txt -c copy assets/video.mp4
J=$(ffmpeg -hide_banner -i assets/mix_raw.wav -af loudnorm=I=-14:TP=-1.5:LRA=11:print_format=json -f null - 2>&1 | sed -n '/^{/,/^}/p')
MI=$(echo "$J" | python3 -c "import json,sys;d=json.load(sys.stdin);print(d['input_i'],d['input_tp'],d['input_lra'],d['input_thresh'],d['target_offset'])")
set -- $MI
ffmpeg -y -loglevel error -i assets/mix_raw.wav -af "loudnorm=I=-14:TP=-1.5:LRA=11:measured_I=$1:measured_TP=$2:measured_LRA=$3:measured_thresh=$4:offset=$5:linear=true" -ar 48000 assets/mix_norm.wav
ffmpeg -y -loglevel error -i assets/video.mp4 -i assets/mix_norm.wav \
 -vf "ass=subs.ass:fontsdir='$TK/assets/fonts'" \
 -map 0:v -map 1:a -c:v libx264 -preset slow -crf 18 -pix_fmt yuv420p -r 30 -profile:v high -c:a aac -b:a 192k -ar 48000 -movflags +faststart -t $TOTAL final.mp4
ffprobe -v error -show_entries format=duration,bit_rate:stream=codec_name,width,height,r_frame_rate -of compact final.mp4
ffmpeg -hide_banner -i final.mp4 -af ebur128=peak=true -f null - 2>&1 | grep -E "^\s+(I:|Peak:)" || true
