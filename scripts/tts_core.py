"""Shared TTS logic (MMS-TTS vie + optional faster-whisper word timing). Path-based, no chdir -> safe in a threaded daemon."""
import re, json, os, subprocess, numpy as np, torch, soundfile as sf
PITCH=0.92
DG="không một hai ba bốn năm sáu bảy tám chín".split()
def n2w(n):
    n=int(n)
    if n<10: return DG[n]
    if n<20: return "mười"+("" if n==10 else " lăm" if n%10==5 else " "+DG[n%10])
    if n<100: t,u=divmod(n,10); return DG[t]+" mươi"+("" if u==0 else " mốt" if u==1 else " tư" if u==4 else " lăm" if u==5 else " "+DG[u])
    if n<1000:
        h,r=divmod(n,100); return DG[h]+" trăm"+("" if r==0 else " linh "+DG[r] if r<10 else " "+n2w(r))
    if n<1000000:
        k,r=divmod(n,1000); s=n2w(k)+" nghìn"
        if r==0: return s
        if r<100: return s+" không trăm "+(("linh "+DG[r]) if r<10 else n2w(r))
        return s+" "+n2w(r)
    m,r=divmod(n,1000000); return n2w(m)+" triệu"+("" if r==0 else " "+n2w(r))
M={}
def load(whisper="small"):
    if "m" not in M:
        from transformers import VitsModel, AutoTokenizer
        M["m"]=VitsModel.from_pretrained("facebook/mms-tts-vie"); M["m"].noise_scale=0.75
        M["tk"]=AutoTokenizer.from_pretrained("facebook/mms-tts-vie")
    if whisper!="none" and ("w",whisper) not in M:
        from faster_whisper import WhisperModel
        M[("w",whisper)]=WhisperModel(whisper,device="cpu",compute_type="int8",cpu_threads=int(os.environ.get("WTHREADS","3")))
def run(job,tempo=1.32,whisper="small"):
    load(whisper); m,tk=M["m"],M["tk"]; wm=M.get(("w",whisper))
    P=lambda *a: os.path.join(job,*a)
    EXTRA=json.load(open(P("spell.json"))) if os.path.exists(P("spell.json")) else {}
    def spoken(tok):
        c=re.sub(r"[^\w.%]","",tok).strip(".")
        if c in EXTRA: return EXTRA[c].split()
        if re.fullmatch(r"\d{1,3}(\.\d{3})+",c): c=c.replace(".","")
        if c.isdigit(): return n2w(c).split()
        if c.endswith("%") and c[:-1].isdigit(): return (n2w(c[:-1])+" phần trăm").split()
        return [re.sub(r"[^\w]","",tok)] if re.sub(r"[^\w]","",tok) else []
    D=[p.strip() for p in re.findall(r"[^,.:?!]+[,.:?!]?",open(P("script.txt")).read()) if p.strip()]
    os.makedirs(P("assets","tts"),exist_ok=True); out=[]; words=[]; cur=0.0; hits=0
    for i,dd in enumerate(D):
        dt=dd.split(); spk=[spoken(t) or ["ờ"] for t in dt]; text=" ".join(" ".join(s) for s in spk).lower()
        g=torch.Generator().manual_seed(7); torch.manual_seed(7)
        with torch.no_grad(): y=m(**tk(text,return_tensors="pt")).waveform[0].numpy()
        sf.write(P("assets","tts",f"{i:02d}.wav"),y,16000)
        subprocess.run(["ffmpeg","-y","-v","error","-i",P("assets","tts",f"{i:02d}.wav"),"-af",
          f"silenceremove=start_periods=1:start_threshold=-42dB,areverse,silenceremove=start_periods=1:start_threshold=-42dB,areverse,asetrate=16000*{PITCH},aresample=16000,atempo={tempo/PITCH:.4f}",
          "-ar","48000",P("assets","tts",f"p{i:02d}.wav")],check=True)
        z,_=sf.read(P("assets","tts",f"p{i:02d}.wav"),dtype="float32"); d=len(z)/48000
        # syllable-proportional default (Vietnamese tokens ~= syllables), weighted by letters
        flat=[w for s in spk for w in s]; wt=np.array([0.6+0.08*len(w) for w in flat]); c=np.concatenate([[0],np.cumsum(wt)])/wt.sum()*d
        st=[(c[k],c[k+1]) for k in range(len(flat))]
        if wm is not None:
            z16=np.interp(np.arange(0,len(z),3),np.arange(len(z)),z).astype(np.float32)
            segs,_=wm.transcribe(z16,language="vi",word_timestamps=True,beam_size=1,vad_filter=False,condition_on_previous_text=False)
            ww=[w for s in segs for w in s.words]
            if len(ww)==len(flat): st=[(w.start,w.end) for w in ww]; hits+=1
        k=0
        for t,s in zip(dt,spk):
            a,b=st[k][0],st[k+len(s)-1][1]; k+=len(s); words.append({"t0":round(cur+a,3),"t1":round(cur+b,3),"w":re.sub(r"[,.:?!]","",t)})
        gap=0.05 if dd[-1] in ",:" else 0.12; out+=[z,np.zeros(int(gap*48000),np.float32)]; cur+=d+gap
    sf.write(P("assets","vo.wav"),np.concatenate(out),48000)
    subprocess.run(["ffmpeg","-y","-v","error","-i",P("assets","vo.wav"),"-af","highpass=f=80,equalizer=f=160:t=q:w=1:g=3,equalizer=f=3000:t=q:w=1:g=2,acompressor=threshold=-20dB:ratio=3:attack=5:release=60","-c:a","libmp3lame","-b:a","256k",P("assets","vo_raw.mp3")],check=True)
    json.dump(words,open(P("assets","words.json"),"w"),ensure_ascii=False)
    return f"voice {cur:.2f}s, {len(D)} phrases, whisper-aligned {hits} ({whisper})"
