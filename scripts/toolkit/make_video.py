#!/usr/bin/env python3
"""Hinton Media — dựng video end-to-end từ spec.

  python3 make_video.py examples/video03/spec.json                # toàn bộ: tts → subs → render → audio → assemble → QA → contact
  python3 make_video.py examples/video03/spec.json --until 20     # chỉ 20 s đầu (kiểm tra nhanh)
  python3 make_video.py spec.json --steps render,audio,assemble   # chạy lại vài bước
  python3 make_video.py spec.json --preview 3.5,12,40             # ảnh tĩnh preview/sheet.jpg
  python3 make_video.py spec.json --workers 3

Thư mục project = thư mục chứa spec.json; cần: spec.json, script.txt, script_tts.txt, scenes.py (code cảnh, dùng engine/).
"""
import argparse, json, os, subprocess, sys, shutil, time
TK = os.path.dirname(os.path.abspath(__file__))
STEPS = ["init", "tts", "subs", "gfx", "render", "audio", "assemble", "qa", "contact"]

def run(cmd, cwd, env=None):
    print("▶", " ".join(cmd), flush=True); t = time.time()
    r = subprocess.run(cmd, cwd=cwd, env=env)
    if r.returncode: sys.exit(f"✗ lỗi ở bước: {' '.join(cmd)}")
    print(f"  ({time.time()-t:.1f}s)")

def link(src, dst):
    if os.path.lexists(dst): return
    os.makedirs(os.path.dirname(dst), exist_ok=True); os.symlink(src, dst)

def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("spec"); ap.add_argument("--until", type=float, default=0); ap.add_argument("--workers", type=int, default=max(1, min(6, (os.cpu_count() or 2) - 1)))
    ap.add_argument("--steps", default=",".join(STEPS)); ap.add_argument("--preview", default=None)
    a = ap.parse_args()
    spec_path = os.path.abspath(a.spec); P = os.path.dirname(spec_path); spec = json.load(open(spec_path))
    env = dict(os.environ, HINTON_PROJECT=P, PYTHONPATH=os.pathsep.join([os.path.join(TK, "engine"), P]), HINTON_UNTIL=str(a.until or ""))
    py = sys.executable; steps = a.steps.split(",")
    if a.preview:
        steps = ["init"]; 
    if "init" in steps:   # tài nguyên dùng chung → project/assets (symlink, không copy file lớn)
        os.makedirs(os.path.join(P, "assets", "cut"), exist_ok=True); os.makedirs(os.path.join(P, "seg"), exist_ok=True)
        link(os.path.join(TK, "assets", "countries50.geojson"), os.path.join(P, "assets", "countries50.geojson"))
        for f in os.listdir(os.path.join(TK, "assets", "sat")):
            link(os.path.join(TK, "assets", "sat", f), os.path.join(P, "assets", "sat", f))
        for f in os.listdir(os.path.join(TK, "assets", "cut")):
            if not os.path.exists(os.path.join(P, "assets", "cut", f)): shutil.copy(os.path.join(TK, "assets", "cut", f), os.path.join(P, "assets", "cut", f))
        miss = [f for f in ["countries50.geojson", "sat/bm_5400.jpg"] if not os.path.exists(os.path.join(P, "assets", f))]
        if miss: sys.exit(f"thiếu dữ liệu {miss} — chạy setup.sh trước")
    if a.preview:
        run([py, os.path.join(TK, "engine", "render.py"), "preview", *a.preview.split(",")], P, env); print(os.path.join(P, "preview", "sheet.jpg")); return
    if "tts" in steps and not (os.path.exists(os.path.join(P, "assets", "words.json")) and spec.get("reuse_tts", True)):
        run([py, os.path.join(TK, "tools", "tts.py"), spec.get("voice", "vi-VN-HoaiMyNeural"), spec.get("rate", "+15%")], P, env)
    if "subs" in steps: run([py, os.path.join(TK, "tools", "subs.py"), spec_path], P, env)
    if "gfx" in steps and spec.get("gfx_sets"):
        for g in spec["gfx_sets"]: run([py, os.path.join(TK, "engine", "gfx.py"), g], P, env)
    if "render" in steps:
        if not a.until:
            for f in os.listdir(os.path.join(P, "seg")): os.remove(os.path.join(P, "seg", f))
        run([py, os.path.join(TK, "engine", "render.py"), "full", str(a.workers)], P, env)
    if "audio" in steps: run([py, os.path.join(TK, "engine", "audio.py")], P, env)
    if "assemble" in steps:
        cmd = ["bash", os.path.join(TK, "tools", "assemble.sh"), P]
        if a.until:   # cắt đúng điểm cuối của các cảnh đã render
            tl = json.load(open(os.path.join(P, "assets", "timeline.json")))
            cmd.append(str(max(b for f0, b, n, s in tl if f0 < a.until * 30) / 30))
        run(cmd, P, env)
    if "qa" in steps: run([py, os.path.join(TK, "tools", "qa_text.py")], P, env)
    if "contact" in steps and os.path.exists(os.path.join(P, "final.mp4")):
        run([py, os.path.join(TK, "tools", "contact.py"), os.path.join(P, "final.mp4"), os.path.join(P, "contact.png"), "20"], P, env)
    print("✓ xong:", os.path.join(P, "final.mp4"))

if __name__ == "__main__": main()
