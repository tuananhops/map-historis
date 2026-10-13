#!/usr/bin/env bash
# Cài đặt idempotent (chạy lại an toàn — box có thể bị khôi phục về trạng thái cũ, mất .venv/out).
# Tuỳ chọn: PIP_CERT=/etc/ssl/certs/ca-certificates.crt nếu pip lỗi SSL; SKIP_APT=1; SKIP_REMBG=1
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; CERT=()
[ -n "${PIP_CERT:-}" ] && CERT=(--cert "$PIP_CERT")
echo "== toolkit (render venv)"; PIP_CERT="${PIP_CERT:-}" bash "$B/toolkit/setup.sh" || echo "!! toolkit setup báo lỗi, xem log ở trên"
echo "== sat tiles"; bash "$B/fetch_assets.sh"
echo "== TTS venv ($B/.venv-tts)"
[ -x "$B/.venv-tts/bin/python" ] || python3 -m venv "$B/.venv-tts"
"$B/.venv-tts/bin/pip" install -q "${CERT[@]}" -r "$B/requirements.txt"
mkdir -p "${WORK_DIR:-$B/work}"/{topics/queue,out,jobs,run}
echo "OK. Thử: $B/make_video.sh --dry-run $B/../examples/map-only/topic.json"
