#!/usr/bin/env python3
"""ref_images.py — tìm & tải ảnh THAM KHẢO cho video Hinton Media.

  python3 tools/ref_images.py "cà phê Tây Nguyên" -n 20 --out refs/caphe
  python3 tools/ref_images.py "trà sữa" -n 12 --out refs/trasua --cutout 1,3,5      # tách nền (rembg u2netp)
  python3 tools/ref_images.py "cảng Cát Lái" --sources commons,openverse            # chỉ nguồn có giấy phép rõ

Thứ tự nguồn mặc định:  google_cse → serpapi → google → bing → openverse → commons → ddg
  google_cse : Google Programmable Search JSON API (cần GOOGLE_CSE_KEY + GOOGLE_CSE_CX, searchType=image)
  serpapi    : SerpAPI engine=google_images (cần SERPAPI_KEY)  — trả kết quả Google Images thật
  google     : HTML google.com udm=2 — hiện Google bắt JavaScript/captcha → tự phát hiện và bỏ qua
  bing       : Bing Images (endpoint images/async, HTML có murl/purl) — KHÔNG cần key, hoạt động
  openverse  : api.openverse.org (ảnh CC, có licence + tác giả) — không cần key
  commons    : Wikimedia Commons API (licence rõ ràng) — không cần key
  ddg        : DuckDuckGo i.js — hiện trả 403 (cần token JS), giữ lại để thử
Ảnh chỉ dùng THAM KHẢO / cut-out tiết chế. manifest.json giữ URL ảnh + trang nguồn + domain (+licence nếu có)
để người dùng tự đánh giá bản quyền.
"""
import argparse, hashlib, html, io, json, os, re, sys, time, urllib.parse
import requests
from PIL import Image, ImageDraw, ImageFont, ImageOps

UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/128.0 Safari/537.36"
S = requests.Session(); S.headers.update({"User-Agent": UA, "Accept-Language": "vi,en;q=0.8"})
TO = 15

def log(*a): print(*a, file=sys.stderr, flush=True)
def dom(u):
    try: return urllib.parse.urlparse(u).netloc.lower().removeprefix("www.")
    except Exception: return ""
def C(img_url, page, title="", prov="", **kw):
    return dict(image_url=img_url, source_page=page or "", domain=dom(page or img_url), title=title or "", provider=prov, **kw)

# ---------------------------------------------------------------- providers
def p_google_cse(q, n):
    key, cx = os.environ.get("GOOGLE_CSE_KEY"), os.environ.get("GOOGLE_CSE_CX")
    if not (key and cx): raise RuntimeError("thiếu GOOGLE_CSE_KEY/GOOGLE_CSE_CX")
    out = []
    for start in range(1, min(n, 100) + 1, 10):
        r = S.get("https://www.googleapis.com/customsearch/v1", timeout=TO, params=dict(
            key=key, cx=cx, q=q, searchType="image", num=10, start=start, hl="vi", gl="vn", safe="active"))
        r.raise_for_status(); items = r.json().get("items", [])
        out += [C(i["link"], i.get("image", {}).get("contextLink"), i.get("title"), "google_cse") for i in items]
        if len(items) < 10: break
    return out

def p_serpapi(q, n):
    key = os.environ.get("SERPAPI_KEY")
    if not key: raise RuntimeError("thiếu SERPAPI_KEY")
    r = S.get("https://serpapi.com/search.json", timeout=30, params=dict(engine="google_images", q=q, hl="vi", gl="vn", api_key=key))
    r.raise_for_status()
    return [C(i["original"], i.get("link"), i.get("title"), "serpapi") for i in r.json().get("images_results", []) if i.get("original")]

def p_google(q, n):
    r = S.get("https://www.google.com/search", timeout=TO, params=dict(q=q, udm=2, hl="vi"))
    t = r.text
    if "/sorry/" in r.url or "captcha" in t.lower() or "enablejs" in t or "unusual traffic" in t:
        raise RuntimeError("Google trả trang yêu cầu JavaScript/captcha (chặn truy cập tự động)")
    out = []
    for m in re.finditer(r'\["(https?://[^"]+?)",(\d+),(\d+)\]', t):
        u = m.group(1).encode().decode("unicode_escape")
        if "gstatic.com" in u or "google." in dom(u): continue
        out.append(C(u, "", "", "google", w=int(m.group(3)), h=int(m.group(2))))
    if not out: raise RuntimeError("không parse được kết quả Google")
    return out

def p_bing(q, n):
    out, seen = [], set()
    for first in range(0, max(n, 35) * 2, 35):
        r = S.get("https://www.bing.com/images/async", timeout=TO, params=dict(q=q, first=first, count=35, mmasync=1, setlang="vi", cc="VN"))
        got = 0
        for m in re.finditer(r'\bm="(\{[^"]+\})"', r.text):
            try: d = json.loads(html.unescape(m.group(1)))
            except Exception: continue
            u = d.get("murl")
            if not u or u in seen: continue
            seen.add(u); got += 1; out.append(C(u, d.get("purl"), d.get("t"), "bing"))
        if not got or len(out) >= n * 3: break
    return out

def p_ddg(q, n):
    r = S.get("https://duckduckgo.com/", timeout=TO, params=dict(q=q, iax="images", ia="images"))
    v = re.search(r'vqd=["\']?([\d-]+)', r.text)
    if not v: raise RuntimeError("không lấy được vqd")
    r = S.get("https://duckduckgo.com/i.js", timeout=TO, headers={"Referer": "https://duckduckgo.com/"},
              params=dict(l="vn-vi", o="json", q=q, vqd=v.group(1), f=",,,,,", p="1"))
    if r.status_code != 200: raise RuntimeError(f"DDG i.js HTTP {r.status_code}")
    return [C(i["image"], i.get("url"), i.get("title"), "ddg", w=i.get("width"), h=i.get("height")) for i in r.json().get("results", [])]

def p_openverse(q, n):
    r = requests.get("https://api.openverse.org/v1/images/", timeout=TO, headers={"User-Agent": "HintonMediaRefTool/1.0"}, params=dict(q=q, page_size=min(50, n * 3)))
    r.raise_for_status()
    return [C(i["url"], i.get("foreign_landing_url"), i.get("title"), "openverse", license=f'{i.get("license","")} {i.get("license_version","")}'.strip(),
              creator=i.get("creator") or "", w=i.get("width"), h=i.get("height")) for i in r.json().get("results", [])]

def p_commons(q, n):
    r = S.get("https://commons.wikimedia.org/w/api.php", timeout=TO, headers={"User-Agent": "HintonMediaRefTool/1.0 (reference research)"},
              params=dict(action="query", format="json", generator="search", gsrnamespace=6, gsrsearch=f"{q} filetype:bitmap",
                          gsrlimit=min(50, n * 3), prop="imageinfo", iiprop="url|size|extmetadata", iiurlwidth=1600))
    r.raise_for_status(); out = []
    for p in sorted(r.json().get("query", {}).get("pages", {}).values(), key=lambda p: p.get("index", 0)):
        ii = (p.get("imageinfo") or [{}])[0]; md = ii.get("extmetadata", {})
        g = lambda k: re.sub("<[^>]+>", "", md.get(k, {}).get("value", ""))[:120]
        out.append(C(ii.get("thumburl") or ii.get("url"), ii.get("descriptionurl"), p.get("title"), "commons",
                     license=g("LicenseShortName"), creator=g("Artist"), w=ii.get("width"), h=ii.get("height")))
    return out

PROVIDERS = dict(google_cse=p_google_cse, serpapi=p_serpapi, google=p_google, bing=p_bing, openverse=p_openverse, commons=p_commons, ddg=p_ddg)
DEFAULT = "google_cse,serpapi,google,bing,openverse,commons,ddg"

# ---------------------------------------------------------------- download / dedupe
def dhash(im, k=8):
    g = ImageOps.grayscale(im).resize((k + 1, k), Image.LANCZOS); px = list(g.tobytes())
    return sum(1 << i for i in range(k * k) if px[(i // k) * (k + 1) + i % k] > px[(i // k) * (k + 1) + i % k + 1])
def ham(a, b): return bin(a ^ b).count("1")

def fetch(c, minside):
    r = S.get(c["image_url"], timeout=TO, headers={"Referer": c["source_page"] or ""}, stream=True)
    r.raise_for_status()
    data = r.raw.read(25_000_000, decode_content=True)
    im = Image.open(io.BytesIO(data)); im.load(); im = ImageOps.exif_transpose(im)
    if min(im.size) < minside: raise ValueError(f"nhỏ {im.size}")
    return data, im

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("query"); ap.add_argument("-n", type=int, default=20); ap.add_argument("--out", default=None)
    ap.add_argument("--sources", default=DEFAULT, help="thứ tự nguồn, phân tách bằng dấu phẩy")
    ap.add_argument("--min", type=int, default=500, help="cạnh ngắn tối thiểu (px)")
    ap.add_argument("--mix", action="store_true", help="lấy từ TẤT CẢ nguồn chạy được (không dừng khi đủ n)")
    ap.add_argument("--cutout", default=None, help='chỉ số ảnh cần tách nền, vd "1,4,7" hoặc "all" (rembg u2netp)')
    a = ap.parse_args()
    out = a.out or os.path.join("refs", re.sub(r"\W+", "_", a.query.lower()).strip("_"))
    os.makedirs(out, exist_ok=True)
    mpath = os.path.join(out, "manifest.json")
    man = json.load(open(mpath)) if os.path.exists(mpath) else dict(query=a.query, items=[], providers={})
    if a.cutout and man["items"] and not a.n:  # chỉ cutout
        pass
    status, cands = man.get("providers", {}), []
    for name in [s.strip() for s in a.sources.split(",") if s.strip()]:
        if len(cands) >= a.n * 3 and not a.mix: break
        try:
            got = PROVIDERS[name](a.query, a.n); status[name] = f"ok ({len(got)} kết quả)"; cands += got
        except Exception as e:
            status[name] = f"lỗi: {str(e)[:120]}"
        log(f"[{name}] {status[name]}")
    items = man["items"]; hashes = [(i["sha1"], i["dhash"]) for i in items]; seen_url = {i["image_url"] for i in items}
    k = len(items)
    for c in cands:
        if k >= a.n: break
        if c["image_url"] in seen_url: continue
        seen_url.add(c["image_url"])
        try: data, im = fetch(c, a.min)
        except Exception as e: log("  bỏ", c["domain"], str(e)[:60]); continue
        sha = hashlib.sha1(data).hexdigest(); dh = dhash(im)
        if any(sha == s or ham(dh, d) <= 6 for s, d in hashes): log("  trùng", c["domain"]); continue
        hashes.append((sha, dh)); k += 1
        fn = f"{k:02d}_{re.sub(r'[^a-z0-9.]+','-',c['domain'])[:40]}.jpg"
        im.convert("RGB").save(os.path.join(out, fn), quality=92)
        c.update(file=fn, w=im.size[0], h=im.size[1], sha1=sha, dhash=dh, index=k, fetched=time.strftime("%Y-%m-%d %H:%M"))
        items.append(c); log(f"  {k:02d} {im.size[0]}x{im.size[1]} {c['provider']:9s} {c['domain']}")
    man.update(query=a.query, providers=status, items=items,
               note="Ảnh tham khảo. Kiểm tra quyền sử dụng tại source_page trước khi dùng trong video; ưu tiên licence CC (openverse/commons).")
    if a.cutout and items:
        from rembg import new_session, remove
        sess = new_session("u2netp")
        sel = range(1, len(items) + 1) if a.cutout == "all" else [int(x) for x in a.cutout.split(",")]
        for i in sel:
            it = items[i - 1]; src = os.path.join(out, it["file"])
            cut = remove(Image.open(src).convert("RGB"), session=sess)
            bb = cut.getchannel("A").point(lambda v: 255 if v > 20 else 0).getbbox()
            if bb: cut = cut.crop(bb)
            it["cutout"] = it["file"].replace(".jpg", "_cut.png"); cut.save(os.path.join(out, it["cutout"]))
            log(f"  cutout {it['cutout']} {cut.size}")
    json.dump(man, open(mpath, "w"), ensure_ascii=False, indent=1)
    sheet(items, out, a.query)
    print(json.dumps(dict(out=out, images=len(items), providers=status), ensure_ascii=False, indent=1))

def sheet(items, out, q, cw=270, ch=270, cols=5):
    if not items: return
    rows = (len(items) + cols - 1) // cols
    sh = Image.new("RGB", (cols * cw, rows * (ch + 30) + 50), (22, 26, 30)); d = ImageDraw.Draw(sh)
    fp = [p for p in [
                      os.path.join(os.path.dirname(__file__), "..", "assets", "fonts", "BeVietnamPro-SemiBold.ttf")] if os.path.exists(p)]
    f = ImageFont.truetype(fp[0], 16) if fp else ImageFont.load_default(); fb = ImageFont.truetype(fp[0], 22) if fp else f
    d.text((10, 12), f"{q} — {len(items)} ảnh tham khảo", font=fb, fill=(236, 160, 53))
    for j, it in enumerate(items):
        im = Image.open(os.path.join(out, it.get("cutout") or it["file"])).convert("RGBA")
        bg = Image.new("RGBA", im.size, (60, 66, 72, 255)); im = Image.alpha_composite(bg, im).convert("RGB")
        im = ImageOps.fit(im, (cw - 6, ch - 6)); x, y = (j % cols) * cw, 50 + (j // cols) * (ch + 30)
        sh.paste(im, (x + 3, y + 3))
        d.text((x + 6, y + ch + 4), f"{it['index']:02d} {it['domain'][:22]} · {it['provider']}", font=f, fill=(230, 230, 230))
    sh.save(os.path.join(out, "contact.jpg"), quality=88)

if __name__ == "__main__": main()
