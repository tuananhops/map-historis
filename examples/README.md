# Ví dụ manifest (topic JSON) từ video đã hoàn thành
- `midway-1942/topic.json`: video đầy đủ (bản đồ + tranh Ken Burns + ảnh Polaroid). Cần thư mục ảnh PD/CC: đặt `media_dir` trỏ tới thư mục chứa các file ảnh mà các cảnh `image`/`photo` tham chiếu (trường `img`). Không kèm ảnh trong repo.
- `map-only/topic.json`: video chỉ dùng bản đồ (Manzikert 1071), không cần ảnh, chạy được ngay.

Chạy thử: `scripts/make_video.sh --dry-run examples/map-only/topic.json`
