# Quy tắc làm việc (bắt buộc)

## 1. Phong cách video
- Dọc **9:16** (1080x1920), **50–60 giây**; lời đọc 150–180 chữ.
- **Hook**: chữ "BẠN CÓ BIẾT?" + zoom từ Trái Đất vào khu vực sự kiện.
- **Bản đồ**: ảnh vệ tinh tông tối, lãnh thổ phát sáng neon, mũi tên tự vẽ, đàn chấm (army dots) cho quân đội.
- **Tư liệu**: tranh cổ chuyển động Ken Burns; ảnh Polaroid "bằng chứng" với tiêu đề "Bằng chứng?" / "Trớ trêu,".
- **Phụ đề**: IN HOA, đậm, 1–3 từ/lần, hiệu ứng nảy; trắng, từ khóa vàng hoặc đỏ.
- **Âm thanh**: giọng nam tiếng Việt nhịp nhanh, nhạc epic, SFX dày (whoosh, trống, boom).
- **Outro**: zoom ra quả địa cầu, "LỊCH SỬ THẾ GIỚI QUA BẢN ĐỒ" + tên kênh + "+ THEO DÕI".

## 2. Thông số bắt buộc
- x264 preset `faster`, CRF 18, 30fps, yuv420p, AAC 192k 48kHz; loudnorm **-14 LUFS** (TP -1.5).
- QA: thời lượng **48–66s**, không khung đen, không đứng hình >2.5s, LUFS trong -16.5..-12. Trượt QA = không upload.

## 3. Nội dung
- **Không bao giờ lặp chủ đề.** Kiểm tra registry trước khi chọn; khử trùng theo **sự kiện**, không theo tên (VD: Huế 1968 ≈ Tết Mậu Thân; Inchon = Incheon; San Jacinto gần như cùng chiến dịch Alamo).
- Luân phiên khu vực: Châu Âu → Thế giới → Việt Nam.
- Chỉ dùng sự kiện, số liệu **đã được công nhận rộng rãi**; kiểm chứng trước khi viết. Không chắc thì bỏ chi tiết.
- Khi Biển Đông hiện trên bản đồ: luôn có nhãn **"Hoàng Sa (Việt Nam)"** và **"Trường Sa (Việt Nam)"** (`hs_ts: true`).
- Chỉ ảnh public-domain / CC (Wikimedia Commons), ghi nguồn (credit) trong caption; ảnh vệ tinh ghi credit NASA/EOX.

## 4. Bài học từ lỗi
- **edge-tts trả 403** trên loại box này → dùng **MMS-TTS `facebook/mms-tts-vie`** chạy **daemon thường trú** (tts_server.py), khỏi nạp model mỗi lần.
- pip lỗi SSL → `--cert /etc/ssl/certs/ca-certificates.crt` (hoặc `export PIP_CERT=...`).
- Box có thể **khôi phục về trạng thái cũ**, mất out/ và .venv → setup phải **idempotent** (`scripts/setup.sh` chạy lại an toàn); upload sớm, đừng giữ thành phẩm chỉ trên box.
- Cụm `start` của mỗi scene phải **khớp nguyên văn** lời đọc (kể cả dấu câu) — lệch dấu câu đã làm hỏng render. Dùng `--dry-run` để soát.
- Thiếu khóa màu `green` từng làm sập render → chỉ dùng màu trong bảng (red, gold, orange, white, blue, green) hoặc [r,g,b].
- Kịch bản quá ngắn/dài → trượt QA thời lượng → chỉnh số chữ (150–180), không chỉnh tốc độ đọc quá tay.
- Lỗi sự thật đã bắt được: Midway "một buổi sáng" → "một ngày"; hướng tiến quân trận Salsu; số thương vong Balaclava. Luôn soát lại năm, hướng, con số.
- Chủ đề trùng (xem mục 3) → khử trùng theo sự kiện.
- Không làm phiền job đang render: copy chứ không move file trong thư mục làm việc.
