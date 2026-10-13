"""Spec → timeline.json (cảnh theo câu mở đầu) + subs.ass (phụ đề CHỈ ở cảnh sub=true).
python3 tools/subs.py spec.json   (chạy trong thư mục project, sau tts.py)"""
import json, subprocess, re, sys, os
sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","engine")); from subkit import make_cues, write_ass
FPS=30; spec=json.load(open(sys.argv[1] if len(sys.argv)>1 else "spec.json"))
words=json.load(open("assets/words.json")); disp=[dict(w) for w in words]
script=open(spec.get("script","script.txt")).read().split(); k=0
for w in disp:   # map TTS words -> display tokens (giữ dấu câu, số kiểu VN)
    target=re.sub(r"[^\w%]","",w["w"]); acc=""; toks=[]
    while k<len(script) and len(re.sub(r"[^\w%]","",acc))<len(target):
        toks.append(script[k]); acc+=script[k]; k+=1
    w["d"]=" ".join(toks) if toks else w["w"]
json.dump(disp,open("assets/disp.json","w"),ensure_ascii=False)
dur=float(subprocess.run(["ffprobe","-v","error","-show_entries","format=duration","-of","csv=p=0","assets/vo_raw.mp3"],capture_output=True,text=True).stdout)
total=dur+spec.get("tail",2.6)
plan=[(s["start"],s["name"],1 if s.get("sub") else 0) for s in spec["scenes"]]
toks=[w["d"] for w in disp]
def find(ph,after):
    for i in range(after,len(toks)):
        if " ".join(toks[i:i+6]).startswith(ph): return i
    raise KeyError(f"không tìm thấy câu mở cảnh: {ph!r}")
idx=[]; p=0
for ph,_,_ in plan: p=find(ph,p); idx.append(p); p+=1
starts=[0.0]+[disp[i]["t0"]-0.12 for i in idx[1:]]
tl=[]; cues=[]; subT=0
for n,(ph,name,sub) in enumerate(plan):
    t0=starts[n]; t1=starts[n+1] if n+1<len(plan) else total
    tl.append([round(t0*FPS),round(t1*FPS),name,sub])
    if sub:
        a=idx[n]; b=idx[n+1] if n+1<len(plan) else len(disp)
        cs=make_cues(disp[a:b],round(t1*FPS)/FPS); cues+=cs; subT+=sum(c["t1"]-c["t0"] for c in cs)
json.dump(tl,open("assets/timeline.json","w"))
for a,b,c,s in tl: print(f"{a/FPS:7.2f} {(b-a)/FPS:5.2f}s {'SUB' if s else '   '} {c}")
write_ass(cues,"subs.ass"); open("assets/total.txt","w").write(str(total))
json.dump(cues,open("assets/cues.json","w"),ensure_ascii=False,indent=0)
st=sum((b-a)/FPS for a,b,c,s in tl if s)
print(f"total {total:.2f}s  subtitle scenes {st:.1f}s ({st/total*100:.0f}%), on-screen subtitle {subT:.1f}s ({subT/total*100:.0f}%)")
