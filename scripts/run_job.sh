#!/usr/bin/env bash
# One background job: pop queue topic, reserve num, render, leave upload marker.
set -uo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; WD="${WORK_DIR:-$B/work}"; export WORK_DIR="$WD"
mkdir -p "$WD/run/ready_upload" "$WD/run/job_logs" "$WD/topics/claimed" "$WD/topics/failed"
LOG="$WD/run/job_logs/job-$$-$(date +%Y%m%d-%H%M%S).log"
exec > >(tee -a "$LOG") 2>&1
echo "JOB start $$ $(date -Iseconds)"

# Atomic claim
T=""
for f in $(ls "$WD"/topics/queue/*.json 2>/dev/null | sort); do
  n=$(basename "$f")
  if ln "$f" "$WD/topics/claimed/$n" 2>/dev/null; then rm -f "$f"; T="$WD/topics/claimed/$n"; break; fi
done
if [ -z "$T" ]; then echo "QUEUE EMPTY"; exit 4; fi
TITLE=$(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['title'])" "$T")
echo "TOPIC $T"
echo "TITLE $TITLE"

N=$(python3 "$B/registry.py" reserve "$TITLE")
# Build output name from title slug
SLUG=$(python3 -c "
import json,sys,re,unicodedata
t=json.load(open(sys.argv[1]))
title=t['title']
# ascii-ish filename
s=unicodedata.normalize('NFKD', title.replace('đ','d').replace('Đ','D'))
s=''.join(c for c in s if not unicodedata.combining(c))
s=re.sub(r'[^A-Za-z0-9]+','_', s).strip('_')
# prefer year at end if present
print(s[:60])
" "$T")
OUT="$WD/out/${N}_${SLUG}.mp4"
echo "OUT $OUT NUM $N"

"$B/make_video.sh" "$T" "$OUT"
rc=$?
if [ $rc -ne 0 ]; then
  echo "FAIL rc=$rc"
  python3 "$B/registry.py" fail "$TITLE"
  mv "$T" "$WD/topics/failed/" 2>/dev/null || true
  exit $rc
fi

# Success: marker for routine to upload
MARK="$WD/run/ready_upload/${N}_$(basename "$OUT" .mp4).json"
python3 -c "
import json,sys
json.dump({'num':int(sys.argv[1]),'title':sys.argv[2],'path':sys.argv[3],'topic_json':sys.argv[4]}, open(sys.argv[5],'w'), ensure_ascii=False, indent=1)
" "$N" "$TITLE" "$OUT" "$T" "$MARK"
echo "READY $MARK"
echo "JOB done $$ $(date -Iseconds)"
exit 0
