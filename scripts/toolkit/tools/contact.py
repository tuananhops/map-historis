"""contact.py video.mp4 out.png [n=20] [cols=5] — lưới n khung hình đều nhau để QA"""
import sys, subprocess, tempfile, os
v,out=sys.argv[1],sys.argv[2]; n=int(sys.argv[3]) if len(sys.argv)>3 else 20; cols=int(sys.argv[4]) if len(sys.argv)>4 else 5
d=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0",v],capture_output=True,text=True).stdout)
tmp=tempfile.mkdtemp()
for i in range(n):
    t=min(d-0.1,1.0+i*(d-2)/max(1,n-1))
    subprocess.run(["ffmpeg","-loglevel","error","-y","-ss",f"{t:.2f}","-i",v,"-frames:v","1","-vf","scale=270:480",f"{tmp}/c{i:02d}.png"])
subprocess.run(["ffmpeg","-loglevel","error","-y","-i",f"{tmp}/c%02d.png","-vf",f"tile={cols}x{(n+cols-1)//cols}",out]); print(out)
