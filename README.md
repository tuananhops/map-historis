# map-historis: gói kiến thức cho bot làm video "Lịch sử thế giới qua bản đồ"

Quy trình, quy tắc đã học, ví dụ và script để một AI agent mới làm video ngắn 9:16 về lịch sử qua bản đồ (phong cách Hinton Media) mà không cần dạy lại.

## Giao cho bot mới
1. Clone repo về máy của bot.
2. Bảo bot: **"Đọc AGENTS.md và làm theo."** (Claude Code tự đọc CLAUDE.md, bản sao của AGENTS.md.)
3. Bot cần: Linux, ffmpeg (libass), Python 3.11+, git; chạy `bash scripts/setup.sh`.

## Cấu trúc
```
AGENTS.md / CLAUDE.md            hướng dẫn cho AI agent
rules.md                         phong cách, thông số, quy tắc, bài học
skills/history-map-video/        SKILL.md: quy trình chi tiết
scripts/                         CLI pipeline (make_video.sh, run_next.sh, registry.py, TTS daemon...)
scripts/toolkit/                 engine render (từ editor-skill-1, texture vệ tinh tải bằng fetch_assets.sh)
examples/                        topic JSON từ video đã làm (Midway 1942, Manzikert 1071)
```
Không chứa video/audio, mật khẩu, token hay thông tin tài khoản.
