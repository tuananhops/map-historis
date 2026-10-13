import sys, time, subprocess, json, os
from scenes import *
import multiprocessing as mp
def scene_at(f):
    for s in SCENES:
        if s.f0<=f<s.f1: return s
def frame(f): return scene_at(f).render(f)
def render_scene(i):
    s=SCENES[i]; out=f"seg/{i:03d}.mp4"; t=time.time()
    p=subprocess.Popen(["ffmpeg","-y","-loglevel","error","-f","rawvideo","-pix_fmt","rgb24","-s",f"{W}x{H}","-r",str(FPS),"-i","-",
        "-c:v","libx264","-preset","fast","-crf","14","-pix_fmt","yuv420p","-threads","2","-r",str(FPS),out],stdin=subprocess.PIPE)
    for f in range(s.f0,s.f1): p.stdin.write(s.render(f).tobytes())
    p.stdin.close(); p.wait(); return i,s.name,s.f1-s.f0,time.time()-t
if __name__=="__main__":
    if sys.argv[1]=="preview":
        from PIL import Image
        os.makedirs("preview",exist_ok=True); ims=[]
        for ts in sys.argv[2:]:
            f=int(round(float(ts)*FPS)); t=time.time(); im=frame(f); dt=time.time()-t
            Image.fromarray(im).save(f"preview/{ts}.png"); ims.append((ts,im)); print(ts,scene_at(f).name,f"{dt*1000:.0f}ms")
        n=len(ims); sheet=Image.new("RGB",(360*n,640))
        for k,(ts,im) in enumerate(ims): sheet.paste(Image.fromarray(im).resize((360,640)),(360*k,0))
        sheet.save("preview/sheet.jpg",quality=88)
    else:
        os.makedirs("seg",exist_ok=True)
        ev=[e for s in SCENES for e in s.events]; json.dump(sorted(ev),open("assets/events.json","w"))
        t0=time.time(); order=sorted(range(len(SCENES)),key=lambda i:-(SCENES[i].f1-SCENES[i].f0))
        if len(sys.argv)>3 and sys.argv[3]: order=[i for i in order if SCENES[i].name in sys.argv[3].split(',')]
        UNTIL=float(os.environ.get("HINTON_UNTIL","0") or 0)
        if UNTIL: order=[i for i in order if SCENES[i].f0<UNTIL*FPS]
        with mp.get_context("fork").Pool(int(sys.argv[2]) if len(sys.argv)>2 else 6) as pool:
            for i,name,n,dt in pool.imap_unordered(render_scene,order): print(f"{i:03d} {name:12s} {n:4d}f {dt:6.1f}s {n/dt:5.1f}fps",flush=True)
        open("seg/list.txt","w").write("".join(f"file '{i:03d}.mp4'\n" for i in range(len(SCENES)) if not UNTIL or SCENES[i].f0<UNTIL*FPS))
        print("render wall time %.1fs"%(time.time()-t0))
