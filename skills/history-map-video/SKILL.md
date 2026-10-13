---
name: history-map-video
description: Dựng video ngắn 9:16 "lịch sử thế giới qua bản đồ" (50-60s) từ topic JSON: chọn chủ đề không trùng, viết kịch bản đã kiểm chứng, TTS MMS tiếng Việt, render bằng toolkit, QA, upload.
---
# Quy trình history-map-video

## 0. Chuẩn bị (mỗi phiên)
`bash scripts/setup.sh` (idempotent). Đặt `WORK_DIR` cố định (VD `~/hinton-work`) để registry và hàng đợi không mất.

## 1. Chọn chủ đề
- Đọc registry: `python3 scripts/registry.py` không đối số in hướng dẫn; file `$WORK_DIR/topics_done.json` (`done`, `in_progress`).
- Chọn sự kiện CHƯA làm (so theo sự kiện, không theo tên), luân phiên Châu Âu → Thế giới → Việt Nam.
- Có hàng đợi sẵn: `scripts/run_next.sh` lấy topic cũ nhất.

## 2. Kịch bản (150–180 chữ)
- Hook "Bạn có biết? …" → 3–5 nhịp diễn biến (năm, địa điểm, quân, kết cục) → chi tiết "Trớ trêu," / "Bằng chứng?" → outro "Lịch sử thế giới qua bản đồ…".
- Chỉ dữ kiện đã công nhận rộng rãi; soát năm, hướng, con số.
- Viết `topic.json` (mẫu: `examples/`). `start` mỗi scene = cụm từ nguyên văn trong `text`. Thêm `spell` cho tên nước ngoài.
- Có Biển Đông trong khung → `hs_ts: true`.
- ⛔ Nếu chủ nhân yêu cầu duyệt kịch bản: dừng chờ.

## 3. Ảnh
Chỉ PD/CC (Wikimedia Commons), lưu vào `media_dir`, ghi credit trong caption. Video map-only không cần ảnh.

## 4. Dựng
```
N=$(python3 scripts/registry.py reserve "<title>")
scripts/make_video.sh --dry-run topic.json
scripts/make_video.sh topic.json $WORK_DIR/out/${N}_Ten.mp4
```
Các bước: prep → TTS daemon (MMS vie) → timeline/subs → render song song → audio (nhạc epic + SFX, ducking) → assemble (-14 LUFS, CRF18, 30fps) → QA.

## 5. QA
Exit 3 = trượt (xem `jobs/<job>/qa/check.json`). Sửa: thời lượng → chỉnh số chữ; khung đen/đứng → chỉnh cam/scene. Xem contact sheet `*_contact.png`.

## 6. Upload & báo cáo
- Upload mp4 lên thư mục Drive chủ nhân chỉ định (ID lấy từ cấu hình/chủ nhân, không ghi vào repo).
- `python3 scripts/registry.py done "<title>" "<link>"`; lỗi: `registry.py fail "<title>"`.
- Báo cáo: tên, số, thời lượng, link, nguồn ảnh, chủ đề tiếp theo dự kiến.
