#!/usr/bin/env bash
# One-command history-map video:  ./make_video.sh topics/<topic>.json [out.mp4]
# Fast path defaults: persistent TTS daemon (run/tts.sock), no Whisper (syllable timing), adaptive WORKERS, x264 preset faster.
# Env: WORKERS (render procs; default nproc/active_jobs, 2..6), TEMPO (1.32), WHISPER (none|tiny|base|small), PRESET (faster), KEEP=1
set -euo pipefail
usage(){ cat <<'U'
Usage: make_video.sh [--dry-run] <topic.json> [out.mp4]
  Render one 9:16 history-map video from a topic manifest (see ../examples/).
  --dry-run   validate manifest + tools, print plan, render nothing
Env: WORK_DIR (default scripts/work), TOOLKIT (default scripts/toolkit), TOOLKIT_PY, TTS_PY,
     WORKERS, TEMPO (1.32), WHISPER (none|tiny|base|small), PRESET (faster), KEEP=1
Exit: 0 ok, 2 TTS failed, 3 QA failed (*.FAILED.mp4 kept), other = step error
U
}
DRY=""; case "${1:-}" in -h|--help|"") usage; exit 0;; --dry-run) DRY=1; shift;; esac
B="$(cd "$(dirname "$0")" && pwd)"; TK="${TOOLKIT:-$B/toolkit}"; PY="${TOOLKIT_PY:-$TK/.venv/bin/python}"; TPY="${TTS_PY:-$B/.venv-tts/bin/python}"; WD="${WORK_DIR:-$B/work}"
TOPIC="$(realpath "$1")"; SLUG=$(basename "$TOPIC" .json); OUT="${2:-$WD/out/$SLUG.mp4}"; [[ "$OUT" != /* ]] && OUT="$PWD/$OUT"; OUT="$(mkdir -p "$(dirname "$OUT")" && realpath -m "$OUT")"; 
[ -z "$DRY" ] && mkdir -p "$WD/out" "$WD/jobs" "$WD/run/active"
if [ -n "$DRY" ]; then
  python3 - "$TOPIC" <<'P' || exit 1
import json,sys
T=json.load(open(sys.argv[1])); sc=T["scenes"]; w=sum(len(s["text"].split()) for s in sc)
bad=[s["name"] for s in sc if s.get("start") and s["start"] not in " ".join(x["text"] for x in sc)]
print(f"topic: {T['title']} | scenes: {len(sc)} | VO words: {w} (target 150-180)")
if bad: print("WARN start phrase not found verbatim in script:",bad)
P
  for t in ffmpeg ffprobe; do command -v $t >/dev/null && echo "ok $t" || echo "MISSING $t"; done
  [ -x "$PY" ] && echo "ok toolkit python $PY" || echo "MISSING toolkit venv ($PY) -> run setup.sh"
  [ -x "$TPY" ] && echo "ok tts python $TPY" || echo "MISSING tts venv ($TPY) -> run setup.sh"
  [ -f "$TK/make_video.py" ] && echo "ok toolkit $TK" || echo "MISSING toolkit $TK"
  ls "$TK"/assets/sat/*.jpg >/dev/null 2>&1 && echo "ok sat tiles" || echo "MISSING sat tiles -> run fetch_assets.sh"
  echo "plan: prep -> tts -> timeline -> render -> audio -> assemble -> QA -> $OUT"; exit 0
fi
J="$WD/jobs/$SLUG-$(date +%Y%m%d-%H%M%S)-$$"; mkdir -p "$J"; cd "$J"; T0=$(date +%s)
echo "$J" > "$WD/run/active/$$"; trap 'rm -f "$WD/run/active/$$"' EXIT
log(){ echo "[$(( $(date +%s)-T0 ))s] $*"; }
cp "$TOPIC" topic.json; cp "$B/scenes_from_topic.py" scenes.py
MD=$(python3 -c "import json;print(json.load(open('topic.json')).get('media_dir',''))"); [ -n "$MD" ] && ln -s "$MD" media
for f in "$WD"/run/active/*; do kill -0 "$(basename "$f")" 2>/dev/null || rm -f "$f"; done
ACT=$(ps -eo pid=,ppid=,args= | awk '$3 ~ /bash$/ && $0 ~ /make_video\.sh/ {p[$1]=$2} END{n=0; for (k in p) if (!(p[k] in p)) n++; print n}'); [ "${ACT:-0}" -lt 1 ] && ACT=1
W=${WORKERS:-$(( $(nproc)/ACT )) }; [ $W -lt 2 ] && W=2; [ $W -gt 6 ] && W=6
export WORK_DIR="$WD" WHISPER=${WHISPER:-none}
log "prep";   python3 "$B/prep.py" "$J"
log "tts";    $TPY "$B/tts.py" "$J" 2>&1 | grep -E "^voice|fallback" || { echo "TTS failed"; exit 2; }
export HINTON_PROJECT="$J" PYTHONPATH="$TK/engine:$J"
log "timeline"; $PY "$TK/make_video.py" spec.json --steps init,subs | grep -E "total|SUB|^ +[0-9]" | tail -1
log "render ($W workers, $ACT active jobs)"; $PY "$TK/engine/render.py" full $W | tail -1
log "audio";  $PY "$B/audio.py" | tail -1
log "assemble"; bash "$B/assemble_fast.sh" "$J" > assemble.log 2>&1
log "check";  $PY "$B/check_frames.py" "$J" || { echo "QA FAILED (see $J/qa/check.json)"; cp final.mp4 "${OUT%.mp4}.FAILED.mp4"; exit 3; }
cp final.mp4 "$OUT"; cp qa/contact_sheet.png "${OUT%.mp4}_contact.png"
log "done -> $OUT"
[ -n "${KEEP:-}" ] || rm -rf seg assets/tts assets/video.mp4 assets/mix_raw.wav assets/mix_norm.wav
