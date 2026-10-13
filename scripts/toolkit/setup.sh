#!/usr/bin/env bash
# Hinton Media toolkit — cài đặt (idempotent). Chạy:  bash setup.sh   (tuỳ chọn: SKIP_APT=1, SKIP_REMBG=1, VENV=.venv)
set -euo pipefail
TK="$(cd "$(dirname "$0")" && pwd)"; cd "$TK"; VENV="${VENV:-$TK/.venv}"
echo "== 1. Gói hệ thống (ffmpeg có libass, python3-venv, fontconfig)"
if [ -z "${SKIP_APT:-}" ]; then
  need=(); command -v ffmpeg >/dev/null || need+=(ffmpeg); command -v fc-cache >/dev/null || need+=(fontconfig)
  python3 -c "import venv,ensurepip" 2>/dev/null || need+=(python3-venv)
  if [ ${#need[@]} -gt 0 ]; then
    if command -v apt-get >/dev/null; then SUDO=$([ "$(id -u)" = 0 ] && echo "" || echo sudo); $SUDO apt-get update -qq && $SUDO apt-get install -y -qq "${need[@]}" fonts-noto-cjk || true
    elif command -v brew >/dev/null; then brew install ffmpeg python3
    else echo "!! Hãy tự cài: ${need[*]}"; fi
  fi
fi
FL="$(ffmpeg -hide_banner -filters 2>/dev/null || true)"; echo "$FL" | grep -q " ass " || echo "!! ffmpeg thiếu filter 'ass' (libass) — phụ đề sẽ không burn được"
echo "== 2. Font (Be Vietnam Pro, Tinos) → ~/.local/share/fonts"
mkdir -p ~/.local/share/fonts/hinton && cp -n assets/fonts/*.ttf ~/.local/share/fonts/hinton/ && (fc-cache -f >/dev/null 2>&1 || true)
echo "== 3. Python venv: $VENV"
[ -x "$VENV/bin/python" ] || python3 -m venv "$VENV"
"$VENV/bin/pip" install -q --upgrade pip
if [ -n "${SKIP_REMBG:-}" ]; then grep -vE "rembg|onnxruntime" requirements.txt > /tmp/req_norembg.txt; "$VENV/bin/pip" install -q -r /tmp/req_norembg.txt
else "$VENV/bin/pip" install -q -r requirements.txt; fi
echo "== 4. Dữ liệu"
[ -s assets/countries50.geojson ] || curl -fsSL -o assets/countries50.geojson https://raw.githubusercontent.com/nvkelso/natural-earth-vector/master/geojson/ne_50m_admin_0_countries.geojson
[ -s assets/sat/bm_5400.jpg ] || curl -fsSL -o assets/sat/bm_5400.jpg "https://eoimages.gsfc.nasa.gov/images/imagerecords/74000/74142/world.topo.200412.3x5400x2700.jpg"
if [ -z "${SKIP_REMBG:-}" ] && [ ! -s ~/.u2net/u2netp.onnx ]; then
  mkdir -p ~/.u2net && curl -fsSL -o ~/.u2net/u2netp.onnx https://github.com/danielgatis/rembg/releases/download/v0.0.0/u2netp.onnx || echo "!! không tải được u2netp (rembg sẽ tự tải khi dùng)"
fi
echo "== 5. Kiểm tra"
"$VENV/bin/python" - <<'PY'
import numpy, cv2, PIL, edge_tts, requests; print("python deps OK", numpy.__version__, cv2.__version__, PIL.__version__)
PY
echo "OK. Dùng:  $VENV/bin/python make_video.py examples/video03/spec.json --until 20"
