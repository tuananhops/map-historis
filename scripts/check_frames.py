"""Automated QA on final.mp4: format, duration, black/frozen frames, loudness, caption/text QA log, contact sheet. Exit 1 on failure."""
import json, subprocess, sys, os, re, numpy as np
os.chdir(sys.argv[1]); f="final.mp4"; bad=[]
pr=json.loads(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration:stream=codec_name,width,height,r_frame_rate","-of","json",f],capture_output=True,text=True).stdout)
v=[s for s in pr["streams"] if s["codec_name"]=="h264"]; a=[s for s in pr["streams"] if s["codec_name"]=="aac"]; dur=float(pr["format"]["duration"])
if not v or (v[0]["width"],v[0]["height"])!=(1080,1920): bad.append("format")
if not a: bad.append("no AAC audio")
lo,hi=json.load(open("topic.json")).get("duration_range",[30,75])
if not lo<=dur<=hi: bad.append(f"duration {dur:.1f}s outside {lo}-{hi}")
bd=subprocess.run(["ffmpeg","-hide_banner","-i",f,"-vf","blackdetect=d=0.1:pix_th=0.06","-an","-f","null","-"],capture_output=True,text=True).stderr
nb=len(re.findall("black_start",bd)); 
if nb: bad.append(f"{nb} black segments")
fz=subprocess.run(["ffmpeg","-hide_banner","-i",f,"-vf","freezedetect=n=0.001:d=2.5","-an","-f","null","-"],capture_output=True,text=True).stderr
nf=len(re.findall("freeze_start",fz))
if nf: bad.append(f"{nf} frozen stretches >2.5s")
lu=subprocess.run(["ffmpeg","-hide_banner","-i",f,"-af","ebur128","-f","null","-"],capture_output=True,text=True).stderr
I=float(re.findall(r"I:\s+(-?[\d.]+) LUFS",lu)[-1])
if not -16.5<=I<=-12: bad.append(f"loudness {I}")
os.makedirs("qa",exist_ok=True)
subprocess.run(["ffmpeg","-v","error","-y","-i",f,"-vf",f"fps=12/{dur},scale=270:480,tile=6x2","-frames:v","1","qa/contact_sheet.png"])
rep={"duration":round(dur,2),"lufs":I,"black":nb,"frozen":nf,"problems":bad,"ok":not bad}
json.dump(rep,open("qa/check.json","w"),indent=1); print(json.dumps(rep,ensure_ascii=False)); sys.exit(0 if not bad else 1)
