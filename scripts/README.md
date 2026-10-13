# scripts/ — pipeline dựng video bản đồ lịch sử 9:16

## Cài đặt
```bash
sudo apt-get install -y ffmpeg fontconfig python3-venv git   # ffmpeg cần libass
export PIP_CERT=/etc/ssl/certs/ca-certificates.crt          # chỉ khi pip lỗi SSL (pip tự đọc biến này)
bash scripts/setup.sh                                        # idempotent: toolkit venv + sat tiles + TTS venv
scripts/make_video.sh --dry-run examples/map-only/topic.json # kiểm tra
```
Texture vệ tinh (~50MB) không nằm trong repo; `fetch_assets.sh` tải từ https://github.com/tuananhops/editor-skill-1 (toolkit/assets/sat).

## CLI
| Lệnh | Việc |
|---|---|
| `make_video.sh [--dry-run] <topic.json> [out.mp4]` | dựng 1 video: prep → TTS → timeline → render → audio → assemble → QA |
| `run_next.sh [out.mp4]` | lấy topic cũ nhất trong `$WORK_DIR/topics/queue/` (claim nguyên tử), dựng. Exit 4 = hết hàng đợi |
| `run_job.sh` | như run_next + đặt số thứ tự trong registry + ghi marker `run/ready_upload/*.json` để bước upload xử lý |
| `registry.py reserve\|done\|fail "<title>" [link]` | registry chủ đề chống trùng (`$REGISTRY` hoặc `$WORK_DIR/topics_done.json`) |
| `gen_queue.py` | sinh topic map-only từ dữ liệu đã kiểm chứng trong file vào hàng đợi (bỏ qua chủ đề đã làm) |
| `tts_server.py` / `tts.py` | daemon MMS-TTS (socket `$WORK_DIR/run/tts.sock`), tts.py tự khởi động daemon, fallback chạy trong tiến trình |
| `check_frames.py <jobdir>` | QA: thời lượng, khung đen, đứng hình >2.5s, LUFS, contact sheet |

Biến môi trường: `WORK_DIR` (mặc định `scripts/work`), `TOOLKIT`, `TOOLKIT_PY`, `TTS_PY`, `WORKERS`, `TEMPO` (1.32), `WHISPER` (none), `PRESET` (faster), `KEEP=1`.
Exit code make_video: 0 ok, 2 TTS lỗi, 3 QA trượt (giữ `*.FAILED.mp4`).

## Topic JSON
Khóa: title, music, duration_range, media_dir, exclude_countries, sat_regions, map_credit, spell {từ: cách đọc}, scenes[].
Mỗi scene: name, type (intro|map|image|photo|outro), text (lời đọc tiếng Việt), start (cụm từ ĐÚNG NGUYÊN VĂN trong text) + trường theo loại
(map: cam, layers, territories, armies, pins, hud, counter, xstamps, hs_ts, sfx; image: img + Ken Burns; photo: img, caption). Xem `../examples/`.
Màu hợp lệ: red, gold, orange, white, blue, green hoặc [r,g,b].
