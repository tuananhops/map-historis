# Nghiên cứu hiệu ứng kênh @nqs.kinhte (zoom, chữ sáng, chuyển cảnh, SFX)

## A. Zoom / chuyển động
- Snap zoom: 1x→20–50x trong 15–20 frame, EaseInOutExpo, radial motion blur toàn khung (vd. Trái Đất → bệnh viện Tokyo 0:00; bản đồ VN → phố Hà Nội).
- Slow drift: 1x→1.1–1.15x trong ~240 frame, linear, không blur, cả nền và tiền cảnh.
- Parallax 3D: tiền cảnh dịch nhanh hơn nền ~1.5x; tilt 3D kiểu Google Earth (top-down → ~45°).
- Rack focus: đẩy qua cửa sổ, tiền cảnh blur ksize 0→21, chủ thể 21→0 trong ~30 frame.

## B. Chữ sáng
- Outer glow số liệu chính: cam #FF9900, blur ~15px, font Black 900 + bóng tối phía sau (vd "7.000 VND").
- Số tiêu cực: đỏ #FF3333, glow ~20px (vd "204,4%").
- Extrude 3D: lặp 10 lần offset +1,+1 màu #333333, không blur (vd "CHỈ 7.000 ĐỒNG?").
- Từ khóa kịch tính: đỏ #FF0000 + drop shadow đen 5px blur 5px.
- Thanh dọc cam #FFB800 rộng 10px cho phụ đề.
- Viền neon nét đứt cam chạy quanh vật thể (Canny trên mask + blur + dịch dash).

## C. Chuyển cảnh
- Hard cut: giữa "chế độ bằng chứng" (đồ họa) và "chế độ giải thích" (người dẫn/phụ đề).
- Whip pan / zoom-through có motion blur 10–15 frame: nối giữa các cảnh đồ họa khác nhau (map→map, phố→map).
- Slide/push: giấy xám trượt từ dưới lên ~10 frame EaseOut cho tài liệu.
- Match cut: giữ vật thể ở tâm khung (540,960), cắt cứng đổi size/giá.

## D. Âm thanh
- Whoosh trầm cho bay địa lý lớn, whoosh lên nhanh cho chữ bay vào (~-5 dB so với giọng).
- Boom sub-bass khi hiện chữ đỏ lớn (~-2 dB, rất rõ).
- Pop/bubble khi ghim lên bản đồ; "cha-ching" máy tính tiền khi hiện giá.
- Nhạc nền: chủ đề nghiêm túc = cinematic synth/string căng ~90 BPM; chủ đề đời thường = lo-fi hip-hop vui. Duck xuống ~-15 dB khi có giọng, lên ~-8 dB ở đoạn chuyển/b-roll.

## E. Ảnh
- Ít ảnh. Ảnh thật được tách nền làm sticker (bóng đổ, vòng tròn cam phía sau) trên nền giấy.
- Ảnh tư liệu cũ chuyển đen trắng; ảnh cửa hàng blur viền/tilt-shift để mắt dồn vào chữ ở giữa.
- Vật thể tách nền có thể được keyframe chạy ngang ảnh nền (vd xe tải).

## Thứ tự lớp
Nền giấy → Bản đồ → Ảnh tách nền → Chữ → Vignette/Blur.
