# Hinton Media Toolkit — dựng video kinh tế dọc 9:16 (1080x1920) trên Linux, CPU-only

Bộ công cụ đã dùng để làm video01–03 cho Hinton Media (phong cách tham chiếu: TikTok @nqs.kinhte).
Gồm: engine motion-graphics (bản đồ, vệ tinh bay vào, quả địa cầu, bộ đếm số, chữ nảy, list, thẻ câu hỏi, biểu đồ, giấy/collage,
thẻ tài liệu + highlight, SFX tổng hợp + nhạc pad + chuẩn hoá -14 LUFS), giọng đọc edge-tts có mốc thời gian từng từ,
phụ đề ASS tự ngắt theo cụm từ tiếng Việt, QA chữ tự động, công cụ tìm ảnh tham khảo.

Tài liệu đi kèm:
- [docs/style_guide.md](docs/style_guide.md) — style guide đầy đủ (gồm **§9 Quy tắc chữ**).
- [docs/effects_study.md](docs/effects_study.md) — nghiên cứu hiệu ứng zoom / chữ sáng / chuyển cảnh / SFX của kênh tham chiếu
  (bảng "đã có / TODO" ở cuối README).

## 1. Cài đặt (máy mới)

```bash
tar xzf hinton_toolkit.tar.gz && cd toolkit
bash setup.sh                 # apt: ffmpeg(libass) python3-venv fontconfig; font → ~/.local/share/fonts; venv .venv; pip -r requirements.txt;
                              # tải dữ liệu nếu thiếu (Natural Earth, Blue Marble, model rembg u2netp). Chạy lại nhiều lần không sao.
# tuỳ chọn: SKIP_APT=1 (không dùng apt), SKIP_REMBG=1 (bỏ rembg/onnxruntime), VENV=/đường/dẫn
.venv/bin/python make_video.py examples/video03/spec.json --until 20    # kiểm tra nhanh 20 s đầu
.venv/bin/python make_video.py examples/video03/spec.json               # dựng lại toàn bộ video03 (~10 phút với 3 worker)
```
Yêu cầu: Python 3.11–3.13, ffmpeg có libass, ~4 GB RAM / worker render (`--workers`). Mạng chỉ cần cho edge-tts, tải tile vệ tinh, tìm ảnh.

## 2. Cây thư mục

```
toolkit/
  make_video.py          CLI end-to-end: init → tts → subs → gfx → render → audio → assemble → qa → contact
  setup.sh  requirements.txt  README.md
  engine/
    engine.py            lõi compositing (Spr, blit, Item: snap/pop/drop/up/fade/bounce/slide, Counter, Scene, DriftBg, paper_bg, Highlight, glow)
    maps.py              Mercator vector (Natural Earth), globe vector, Hoàng Sa/Trường Sa luôn là của Việt Nam
    sat.py               quả địa cầu vệ tinh (Blue Marble) + fly-in nhiều tầng Sentinel-2 (EOX), nghiêng phối cảnh
    mlayers.py           VecBg, CountryFX, GlowPin, Route (tuyến cong phát sáng), Leader+callout, Bar3D, LineChart, BottomGlobe, DocCard
    textkit.py           PRESET CHỮ (§9): ROLE (hero/key/title/label/cap/item/axis/src), K(), KC() bộ đếm lượng tử hoá,
                         listing() (tiêu đề + số cam + item trượt), qcard() thẻ câu hỏi, src() nguồn, vùng an toàn, TEXTLOG
    subkit.py            ngắt phụ đề tiếng Việt (quy hoạch động, không mồ côi 1 từ, không tách từ ghép/số+đơn vị), xuất ASS
    gfx.py               vẽ cut-out vector (bao cà phê, túi rang xay, tiền, mũi tên, chồng tiền…): `python engine/gfx.py coffee`
    audio.py             SFX tổng hợp (pop, tick, boom, whoosh, swish, cha-ching) theo events + nhạc nền tense/lofi/pad, duck −15/−8 dB
    render.py            render song song theo cảnh → seg/NNN.mp4 ; `preview t1 t2…`
  tools/
    tts.py               edge-tts vi-VN-HoaiMyNeural (+15%) + WordBoundary → assets/words.json
    subs.py              spec → timeline.json (cảnh bắt đầu ở câu nào) + subs.ass (chỉ cảnh sub=true)
    assemble.sh          ghép, loudnorm 2-pass -14 LUFS / TP -1.5, burn phụ đề, H.264 crf18 + AAC 192k
    qa_text.py           QA chữ: vùng an toàn, phụ đề ⟂ chữ đồ hoạ, định dạng số VN, CAPS, phụ đề không vượt cắt cảnh/không mồ côi
    contact.py           contact sheet n khung
    ref_images.py        tìm + tải ảnh tham khảo (Google API/SerpAPI nếu có key → Bing → Openverse → Commons), manifest, --cutout
    sat_tiles.py         tải mosaic Sentinel-2 cloudless cho vùng mới
  engine/scenekit.py     hiệu ứng: snap_zoom, transitions, RackFocus, NeonOutline, bw_photo, KX, chaching, scrim, cutout…
  engine/tpl.py          template cảnh: T_map, T_satfly, T_sathold, T_globe, T_zoomout, T_paper, T_question, T_openq, T_end, map_bar, bar_rows, tag, neon_cut, finish
  templates/             code cảnh của video02 (nợ công Nhật) và video03 (cà phê) để chép/sửa
  examples/video04..08/  5 video làm bằng tpl.py (spec, script, scenes.py, sources, caption, contact.png)
  examples/video03/      spec.json, script.txt, script_tts.txt, scenes.py, text_plan.md, sources.md, caption.txt, assets (giọng, tile vệ tinh)
  assets/                fonts (Be Vietnam Pro, Tinos), countries50.geojson, sat/bm_*.jpg|png, cut/*.png
  docs/                  style_guide.md, effects_study.md
```

## 3. Quy trình: chủ đề → video

1. **Chủ đề**: chuyện đời thường/kinh tế có **một con số gây sốc + một nghịch lý** (vd "bán nhiều hơn mà thu ít hơn"). Có địa lý để làm bản đồ.
2. **Nghiên cứu**: chỉ dùng số liệu thật, có nguồn (bộ ngành, hải quan, USDA, IMF, báo lớn). Ghi ngay vào `sources.md` (nguồn, ngày, link).
3. **Kịch bản** `script.txt` (2:00–3:00, ~420–500 từ): hook số + lật ngược → thẻ câu hỏi trung tâm (15–30 s) → 2–4 lý do → twist →
   tóm tắt + câu hỏi mở → CTA **"Theo dõi Hinton Media để hiểu kinh tế mỗi ngày."** Số viết kiểu VN (7.000; 43,1%).
   `script_tts.txt` = bản cho TTS (có thể viết số thành chữ nếu TTS đọc sai).
4. **text_plan.md** (BẮT BUỘC trước khi render): mỗi câu → PHỤ ĐỀ hoặc TỪ KHOÁ (ghi rõ từ khoá 1–5 chữ, vai trò cỡ chữ, màu).
5. **spec.json**: danh sách cảnh theo thứ tự, mỗi cảnh: `name`, `start` (vài chữ đầu của câu mở cảnh, khớp script),
   `sub` (true = cảnh "thay người dẫn": phụ đề, KHÔNG chữ đồ hoạ), `type`, `keywords`, `map`. Xem `examples/video03/spec.json`.
6. **scenes.py**: code từng cảnh bằng engine (chép từ `templates/` hoặc `examples/video03/scenes.py`), mỗi chữ dùng preset textkit
   `K(sc,"…","key",OR,x,y,sc.w("từ được đọc"))` → chữ nảy vào đúng lúc từ đó được đọc.
7. **Render**: chạy `qa_text.py` trước (nhanh, không render) → render thẳng toàn bộ `make_video.py spec.json --workers 6`
   (tuỳ chọn `--preview 3,12,40` ảnh tĩnh / `--until 20` khi thử nghiệm). Sửa cảnh lẻ: `engine/render.py full 2 tên1,tên2` rồi `tools/assemble.sh`.
8. **QA**: `qa_text.py` phải "ALL TEXT RULES PASS"; xem `contact.png` + trích ≥30 khung full-size (chữ chồng, số dở dang, nửa khung trống,
   phụ đề 1 từ, HS/TS khi thấy Việt Nam).
9. **caption.txt**: caption TikTok + hashtag + nguồn ngắn.

## 4. Style guide (tóm tắt — bản đầy đủ: docs/style_guide.md)

**Format**: 1080x1920, 30 fps, H.264 crf18, AAC, -14 LUFS. Thời lượng 2:00–3:00. Giọng vi-VN-HoaiMyNeural +15%.
**Màu**: nền tối xanh-than / bản đồ teal tối / giấy sáng; cam `#ECA035` nhấn; trắng nền chữ; **đỏ chỉ cho số âm/tiêu cực**; tối đa 2 màu/khối chữ.
**Bản đồ ≥40% thời lượng** (video03: 62%): vệ tinh bay vào, globe xoay, quốc gia phát sáng, ghim, tuyến cong, cột 3D trên bản đồ.

### Quy tắc chữ (§9)
- **Phụ đề và chữ đồ hoạ loại trừ nhau.** Phụ đề CHỈ ở cảnh thay người dẫn (vệ tinh, globe, tuyến) ~25–35% thời lượng.
- Chữ đồ hoạ **tóm tắt 1–5 chữ**, không chép lời. Không đoạn văn (trừ thẻ tài liệu).
- Phân cấp: hero 140–200 px > key 90–120 > title 70–90 > label/item 40–56 > caption 30–40 > axis 26–30 > nguồn 22.
  Tiêu đề/nhãn/câu hỏi **IN HOA**; item list, trục: viết thường câu. Font Be Vietnam Pro đậm. Bóng đổ 40%/5 px/blur 10 trên bản đồ.
- Vùng an toàn x 80–920, y 200–1400. Chữ vào bằng **nảy 80→105→100% trong 0,3 s đúng lúc đọc từ đó**, đứng yên, cắt cứng theo cảnh.
- List: tiêu đề in hoa, **số thứ tự cam**, item trượt từ trái khi được đọc.
- Phụ đề: trái, trắng đậm ~45 px, cao dòng 1,3, ≤30 ký tự/dòng, 1–2 dòng, ngắt theo cụm, đáy y≈1500, thanh cam 10 px cách 20 px, không hộp,
  không animation, **không dòng 1 chữ**.
- Số: kiểu VN (7.000; 43,1%), đơn vị in hoa; bộ đếm chỉ hiện giá trị "tròn" (lượng tử hoá), kết thúc đúng giá trị thật.
- Nguồn: 22 px IN HOA trắng 70% ngay dưới số liệu. Thẻ câu hỏi: giữa khung, 70–90 px, in hoa, xen kẽ trắng/cam, từng cụm nảy vào.

## 5. Bài học từ phản hồi của người dùng (BẮT BUỘC)
1. **Không lạm dụng nền đen** trong video có ảnh — v1 bị chê "nhiều nền đen"; dùng bản đồ teal, giấy sáng, ảnh vệ tinh.
2. **Ít ảnh, nhiều bản đồ** — kênh tham chiếu dùng rất ít ảnh; ảnh thật chỉ làm sticker tách nền, tiết chế.
3. **"Sơ sài" = thiếu chuyển động** — mỗi cảnh phải có chuyển động camera (drift/zoom/bay) + chữ/đồ hoạ vào theo nhịp lời.
4. **Không phụ đề đè lên đồ hoạ**; chữ là **từ khoá**, không chép nguyên câu.
5. CTA cuối luôn: **"Theo dõi Hinton Media để hiểu kinh tế mỗi ngày"**.
6. **Hoàng Sa, Trường Sa luôn là của Việt Nam** — bất cứ khi nào thấy Việt Nam trên bản đồ/globe: chấm đảo màu Việt Nam + nhãn
   "QĐ. Hoàng Sa (Việt Nam)" / "QĐ. Trường Sa (Việt Nam)" (`hsts()`, `sat_hsts()`, `vec_equi(("Vietnam",))`). Ngoại lệ hợp lệ duy nhất
   cho quy tắc "cảnh phụ đề không có chữ đồ hoạ".
7. **Chỉ số liệu thật có nguồn**; ghi nguồn trên màn hình và trong sources.md; ước tính/dự báo phải nói rõ.
8. Không để nửa khung trống, không để bộ đếm/biểu đồ dừng ở giá trị lẻ dở dang, không dòng phụ đề 1 chữ.
9. Video được đánh giá "tạm được" khi đạt các điều trên; bước tiếp theo là hiệu ứng (xem bảng dưới).

## 6. Ảnh tham khảo: tools/ref_images.py

```bash
.venv/bin/python tools/ref_images.py "cà phê Tây Nguyên" -n 20 --out refs/caphe              # tải, khử trùng lặp, lọc ảnh nhỏ, contact.jpg, manifest.json
.venv/bin/python tools/ref_images.py "cà phê Tây Nguyên" --out refs/caphe -n 20 --cutout 2,5  # tách nền (rembg u2netp) → NN_cut.png
.venv/bin/python tools/ref_images.py "cảng Cát Lái" --sources commons,openverse               # chỉ nguồn có licence rõ
```
- **Google**: trang google.com (cả `udm=2`, `tbm=isch`) nay bắt JavaScript và captcha với truy cập tự động → công cụ tự phát hiện và bỏ qua
  (không vượt captcha). Muốn kết quả Google thật: đặt **`SERPAPI_KEY`** (serpapi.com, engine google_images) hoặc
  **`GOOGLE_CSE_KEY` + `GOOGLE_CSE_CX`** (Programmable Search JSON API, bật "Image search"; Google đã đóng API này với khách hàng mới, chỉ
  dùng được nếu tài khoản đã có).
- **Bing Images** (không key): hoạt động, là nguồn chính hiện tại. **Openverse**, **Wikimedia Commons**: hoạt động, có licence + tác giả.
  **DuckDuckGo**: trả 403 (cần token JS) — giữ trong danh sách thử cuối.
- `manifest.json`: image_url, source_page, domain, title, provider, licence/creator (nếu có), kích thước, sha1, dhash.
  Ảnh chỉ để **tham khảo / cut-out tiết chế**; kiểm tra quyền ở source_page trước khi dùng, ưu tiên CC.

## 7. Hiệu ứng (docs/effects_study.md): đã có

| Mục | Trạng thái / cách dùng |
|---|---|
| Slow drift nền 1→1,1x | ĐÃ CÓ (DriftBg, VecBg path) |
| Fly-in vệ tinh nhiều tầng + nghiêng 3D | ĐÃ CÓ (`T_satfly`, `T_sathold`, `T_zoomout`, `T_globe` trong engine/tpl.py) |
| Snap zoom EaseInOutExpo 15–20 frame + radial blur + whoosh | ĐÃ CÓ (`snap_zoom()`; `T_satfly(...,snap=True)`, `T_map(...,snap_at=0.2)`) |
| Whip pan / zoom-through có directional blur (12 frame) | ĐÃ CÓ, TỰ ĐỘNG giữa 2 cảnh đồ hoạ khác loại (`finish()` → `auto_transitions`); cắt cứng vào/ra cảnh phụ đề |
| Rack focus | ĐÃ CÓ (`RackFocus(t,dur,blur_from,blur_to)`) |
| Outer glow chữ số (cam ~15 px, đỏ ~20 px) + bóng tối, Black 900 | ĐÃ CÓ (`fx="glow"` / `"glow_red"` trong K/KC/KX) — dùng trên nền tối/bản đồ |
| Chữ extrude 3D 10 lớp (#333 / nâu) | ĐÃ CÓ (`fx="extrude"` / `"extrude_brown"`; `KX()` tự thêm boom/pop) — dùng trên nền giấy |
| Viền neon nét đứt chạy quanh cut-out | ĐÃ CÓ (`neon_cut(sc,"tên",x,y,t,w,h)`, `NeonOutline`) |
| Ảnh cũ đen trắng (sepia, grain, vignette, viền in) | ĐÃ CÓ (`bw_photo(path,w,h,rot=)`) |
| SFX whoosh / boom / pop / tick / swish / **cha-ching** | ĐÃ CÓ (tổng hợp; `chaching(sc,t)`, `tag(...)` tự kêu) |
| Nhạc nền theo chủ đề | ĐÃ CÓ: spec `"music": "tense"` (90 BPM) / `"lofi"` (84 BPM) / `"pad"`; duck −15 dB dưới giọng, −8 dB ở khoảng lặng |
| Thanh cam 10 px cho phụ đề; hard cut đồ hoạ ↔ phụ đề | ĐÃ CÓ |
| Giấy trượt lên / vật thể chạy ngang | MỘT PHẦN (DocCard, Item mot/posfn) |
| Tilt-shift ảnh cửa hàng | chưa (ít dùng) |

### Viết cảnh nhanh bằng templates (engine/tpl.py) — ~80 dòng/video
```python
from tpl import *
sc,bg=T_map("hook",(107,20),26,dark=0.8,fly=((110,15),9,1.2),glow=[("Vietnam",0.2)],routes=[(A,B,0.6,0.2,OR,7)],hs=True)
scrim(sc,220,700,0.55); KC(sc,"hero",OR,540,530,sc.w("30"),30,fx="glow")
T_satfly("truck",(108.05,12.69),"vn",60000,True)          # cảnh phụ đề (spec sub=true)
sc,bg=T_paper("value","grey"); bar_rows(sc,[...],430); KX(sc,"rẻ hơn ~15%","key",RD,540,1000,sc.w("15%"),fx="glow"); chaching(sc,sc.w("15%"))
T_question("question",[("Vì sao",("sao")),...]); T_openq(...); T_end("end"); USED=finish()
```
- Vùng vệ tinh mới: `python tools/sat_tiles.py <dir> <key> <z> lon0 lon1 lat0 lat1` (z8/z11/z14) rồi `region("hn",["BMV","vnn8","hn11","hn14"])`.
  Nên để tile ở một thư mục chung (sat_cache) và symlink vào `project/assets/sat/` để các video dùng lại.
- `map_bar` trên bản đồ thế giới (k≈3) chỉ ~3 px/độ — đặt các cột cách nhau ≥ 250 px, nếu không dùng `bar_rows` trên nền giấy.
- Ví dụ đầy đủ: `examples/video04` … `examples/video08` (sầu riêng, vàng, xăng, du lịch, gạo).

## 8. Hạn chế đã biết
- Nội dung hình ảnh của từng cảnh vẫn viết bằng Python (`scenes.py`); `spec.json` điều khiển thời điểm cảnh, phụ đề, từ khoá/bản đồ để
  lập kế hoạch & QA — chưa sinh cảnh tự động thuần từ spec.
- Ảnh vệ tinh z14 (Sentinel-2, 10 m) hơi mờ khi zoom sát. Tile EOX cần mạng (credit "Sentinel-2 cloudless © EOX, CC BY 4.0").
- edge-tts cần mạng; ví dụ video03 kèm sẵn `vo_raw.mp3` + `words.json` để tái tạo chính xác (đặt `"reuse_tts": false` để đọc lại).
- RAM: mỗi worker render ~0,7–1 GB (cảnh vệ tinh). Máy 16 GB dùng chung: `--workers 3`. (Đã sửa rò bộ nhớ starfield/ocean_img khi
  nghiêng camera — trước đây cảnh fly-in dài có thể ăn >6 GB và bị OOM-kill làm render treo.)
- Font Be Vietnam Pro **không có mũi tên "→"**; dấu "~" nhỏ dễ đọc nhầm thành dấu trừ — viết "gần/khoảng". `qa_text.py` báo MISSING GLYPH.
- Tile vệ tinh kèm sẵn trong assets/sat: Tây Nguyên (vn8/dl11/dl14), TP.HCM (hcm11/cl14), Hà Nội (vnn8/hn11/hn14), ĐBSCL (mk11/mk14).
