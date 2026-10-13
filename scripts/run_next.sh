#!/usr/bin/env bash
# Fast path for scheduled runs: atomically pop the oldest topic from topics/queue/, render it.
# Usage: ./run_next.sh [out.mp4]   -> prints "TOPIC <path>" first, then make_video output. Exit 4 = queue empty.
# The popped JSON lands in topics/claimed/ (hard-link claim is atomic: two runs can never get the same file). On failure it is
# moved to topics/failed/ for inspection (not re-queued automatically).
set -uo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; WD="${WORK_DIR:-$B/work}"; export WORK_DIR="$WD"; mkdir -p "$WD/topics/claimed" "$WD/topics/failed"
T=""
for f in $(ls "$WD"/topics/queue/*.json 2>/dev/null | sort); do
  n=$(basename "$f"); if ln "$f" "$WD/topics/claimed/$n" 2>/dev/null; then rm -f "$f"; T="$WD/topics/claimed/$n"; break; fi
done
[ -z "$T" ] && { echo "QUEUE EMPTY"; exit 4; }
echo "TOPIC $T"; echo "TITLE $(python3 -c "import json,sys;print(json.load(open(sys.argv[1]))['title'])" "$T")"
"$B/make_video.sh" "$T" "$@"; rc=$?
[ $rc -ne 0 ] && mv "$T" "$WD/topics/failed/" 
exit $rc
