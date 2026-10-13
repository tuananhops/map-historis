#!/usr/bin/env bash
# Tải texture vệ tinh (toolkit/assets/sat, ~50MB) từ repo gốc editor-skill-1. Idempotent.
set -euo pipefail
B="$(cd "$(dirname "$0")" && pwd)"; DST="${TOOLKIT:-$B/toolkit}/assets/sat"; mkdir -p "$DST"
if ls "$DST"/bm_*.{jpg,png} >/dev/null 2>&1; then echo "sat tiles đã có ($DST)"; exit 0; fi
T=$(mktemp -d); trap 'rm -rf "$T"' EXIT
git clone -q --depth 1 --filter=blob:none --sparse https://github.com/tuananhops/editor-skill-1 "$T/r"
git -C "$T/r" sparse-checkout set toolkit/assets/sat
cp -n "$T/r/toolkit/assets/sat/"* "$DST/"; echo "OK: $(ls "$DST" | wc -l) file -> $DST"
