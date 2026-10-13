import numpy as np, json, subprocess, os
os.chdir(os.environ.get("HINTON_PROJECT",os.getcwd()))
SR=48000; TOTAL=float(open("assets/total.txt").read()); N=int(TOTAL*SR)+SR
rng=np.random.default_rng(7)
raw=subprocess.run(["ffmpeg","-v","error","-i","assets/vo_raw.mp3","-f","f32le","-ac","2","-ar",str(SR),"-"],capture_output=True).stdout
vo=np.frombuffer(raw,np.float32).reshape(-1,2).copy(); voice=np.zeros((N,2),np.float32); voice[:len(vo)]=vo
def movavg(x,k):
    """O(N) centred moving average (np.convolve with long windows is O(N*k) = minutes)"""
    c=np.concatenate([[0.0],np.cumsum(x,dtype=np.float64)]); h=k//2; i=np.arange(len(x)); a=np.clip(i-h,0,len(x)); b=np.clip(i-h+k,0,len(x))
    return ((c[b]-c[a])/k).astype(np.float32)
def env_follow(x,win=0.05):
    m=np.abs(x).mean(1); return movavg(m,int(win*SR))
venv=env_follow(voice); active=venv>venv.max()*0.08; vr=np.sqrt((voice[active]**2).mean())
def stft_noise(dur,f_of_t,bw_of_t):
    n=int(dur*SR); hop=256; win=1024; x=rng.normal(0,1,n+win); out=np.zeros(n+win); w=np.hanning(win); fr=np.fft.rfftfreq(win,1/SR)
    for i in range(0,n,hop):
        t=i/SR; X=np.fft.rfft(x[i:i+win]*w); fc=f_of_t(t); bw=bw_of_t(t)
        X*=np.exp(-0.5*((np.log2(np.maximum(fr,20))-np.log2(fc))/bw)**2); out[i:i+win]+=np.fft.irfft(X)*w
    o=out[:n]; return o/np.abs(o).max()
def adsr(n,a,r):
    t=np.arange(n)/SR; e=np.minimum(1,t/a)*np.exp(-np.maximum(0,t-a)/r); return e
def whoosh(dur=0.55,lo=250,hi=4200):
    n=int(dur*SR); t=np.arange(n)/SR; x=stft_noise(dur,lambda t:lo*(hi/lo)**np.sin(np.pi*min(t/dur,1)) ,lambda t:0.9)
    e=np.sin(np.pi*np.clip(t/dur,0,1))**1.6; return x*e
def pop():
    n=int(0.12*SR); t=np.arange(n)/SR; f=350+600*np.exp(-t/0.02); ph=2*np.pi*np.cumsum(f)/SR
    return (np.sin(ph)*np.exp(-t/0.035)+0.25*rng.normal(0,1,n)*np.exp(-t/0.003))*0.9
def tick():
    n=int(0.03*SR); t=np.arange(n)/SR; return (np.sin(2*np.pi*3200*t)*np.exp(-t/0.004)+0.4*rng.normal(0,1,n)*np.exp(-t/0.0015))
def boom():
    n=int(0.7*SR); t=np.arange(n)/SR; f=48+60*np.exp(-t/0.05); ph=2*np.pi*np.cumsum(f)/SR
    thump=np.sin(ph)*np.exp(-t/0.22); air=np.concatenate([whoosh(0.3,150,1500)*0.35,np.zeros(n-int(0.3*SR))]); return thump+air
def chaching():
    """cash register: two FM bell strikes + drawer thunk + coin shimmer (synth, no samples)"""
    n=int(0.9*SR); t=np.arange(n)/SR; out=np.zeros(n)
    for t0,fc,g in [(0.0,2093.0,1.0),(0.085,2637.0,0.9)]:
        i=int(t0*SR); tt=t[:n-i]; mod=np.sin(2*np.pi*fc*1.41*tt)*3.2*np.exp(-tt/0.12)
        out[i:]+=g*np.sin(2*np.pi*fc*tt+mod)*np.exp(-tt/0.32)
    i=int(0.17*SR); tt=t[:n-i]; out[i:]+=0.55*np.sin(2*np.pi*(90+80*np.exp(-tt/0.03))*tt)*np.exp(-tt/0.06)
    out[i:]+=0.25*rng.normal(0,1,n-i)*np.exp(-tt/0.012)
    for k in range(9):
        j=int((0.2+0.05*k+0.02*rng.random())*SR); f=rng.uniform(3500,7000); tt=t[:n-j]
        out[j:]+=0.18*np.sin(2*np.pi*f*tt)*np.exp(-tt/0.04)
    return out/np.abs(out).max()
def drum():
    n=int(0.6*SR); t=np.arange(n)/SR; f=62+70*np.exp(-t/0.04); x=np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-t/0.25)+0.3*rng.normal(0,1,n)*np.exp(-t/0.02); return x/np.abs(x).max()
def horse():
    out=np.zeros(int(1.6*SR))
    for k in range(12):
        for j,dt in enumerate((0,0.07,0.15)):
            i=int((k*0.13+dt)*SR); n=int(0.05*SR); t=np.arange(n)/SR
            if i+n<len(out): out[i:i+n]+=(np.sin(2*np.pi*(140+40*j)*t)*np.exp(-t/0.012)+0.6*rng.normal(0,1,n)*np.exp(-t/0.006))*(0.6+0.4*np.sin(k/12*np.pi))
    return out/np.abs(out).max()
def splash():
    d=0.9; x=stft_noise(d,lambda t:3500*np.exp(-t*2.2)+300,lambda t:1.3); t=np.arange(len(x))/SR; return x*np.exp(-t/0.28)*np.minimum(1,t/0.01)
def crash():
    n=int(0.9*SR); t=np.arange(n)/SR; x=rng.normal(0,1,n)*np.exp(-t/0.09)
    for k in range(10):
        i=int(rng.uniform(0,0.35)*SR); f=rng.uniform(180,900); tt=t[:n-i]; x[i:]+=0.9*np.sin(2*np.pi*f*tt)*np.exp(-tt/0.05)
    x+=0.8*np.sin(2*np.pi*(55+30*np.exp(-t/0.05))*t)*np.exp(-t/0.2); return x/np.abs(x).max()
def clash():
    n=int(0.7*SR); t=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*t+rng.uniform(0,6))*np.exp(-t/(0.08+0.3*rng.random())) for f in (2210,3170,4620,5840,7300))+0.5*rng.normal(0,1,n)*np.exp(-t/0.01); return x/np.abs(x).max()
LIB={"drum":drum(),"horse":horse(),"splash":splash(),"crash":crash(),"clash":clash(),"chaching":chaching(),"pop":pop(),"tick":tick(),"boom":boom(),"whoosh":whoosh(0.55),"swish":whoosh(0.28,600,6000)}
LVL={"drum":1.0,"horse":0.55,"splash":0.8,"crash":0.95,"clash":0.5,"chaching":0.85,"pop":0.55,"tick":0.22,"boom":0.95,"whoosh":0.6,"swish":0.38}   # x voice RMS
OFF={"whoosh":-0.22,"swish":-0.08}   # whoosh peaks centre on the cut/fly-in
sfx=np.zeros((N,2),np.float32); ev=json.load(open("assets/events.json")); last={}
for t,k,g in ev:
    if k=="tick" and t-last.get("tick",-1)<0.055: continue
    if k=="pop" and t-last.get("pop",-1)<0.06: continue
    last[k]=t; s=LIB[k]*LVL[k]*g*vr*(0.9+0.2*rng.random()); i=int(max(0,(t+OFF.get(k,0)))*SR); j=min(N,i+len(s))
    pan=rng.uniform(-0.35,0.35) if k in("pop","tick","swish") else 0
    sfx[i:j,0]+=s[:j-i]*(1-pan); sfx[i:j,1]+=s[:j-i]*(1+pan)
# ---- synthesized music bed (no third-party music) ----
# MUSIC env/spec: "tense" (~90 BPM pulse: kick, 8th-note bass, off-beat hat, string pad) | "lofi" (~84 BPM swing beat, rhodes, crackle) | "pad"
spec=json.load(open("spec.json")) if os.path.exists("spec.json") else {}
STYLE=os.environ.get("HINTON_MUSIC") or spec.get("music","pad")
t=np.arange(N)/SR
def mtof(m): return 440*2**((m-69)/12)
def pad_bed(chords,CL,lvl=1.0,oct_=-12):
    p=np.zeros(N)
    for ci in range(int(TOTAL/CL)+2):
        ch=chords[ci%len(chords)]; t0=ci*CL; seg=(t>=t0-1.5)&(t<t0+CL+1.5); tt=t[seg]-t0
        e=np.clip((tt+1.5)/1.5,0,1)*np.clip((CL+1.5-tt)/1.5,0,1)
        for m in ch:
            for det in (-0.07,0.0,0.06):
                f=mtof(m+oct_)*2**(det/12); p[seg]+=np.sin(2*np.pi*f*t[seg]+rng.uniform(0,6.28))*e/12
                p[seg]+=0.25*np.sin(2*np.pi*2*f*t[seg])*e/12
    return p*lvl
def hit(buf,pos,x,g=1.0):
    i=int(pos*SR); j=min(N,i+len(x))
    if i<N: buf[i:j]+=x[:j-i]*g
def kick():
    n=int(0.35*SR); tt=np.arange(n)/SR; f=45+90*np.exp(-tt/0.035); return np.sin(2*np.pi*np.cumsum(f)/SR)*np.exp(-tt/0.16)
def hat(dec=0.025):
    n=int(0.08*SR); tt=np.arange(n)/SR; x=rng.normal(0,1,n); x=np.diff(np.concatenate([[0],x])); return x*np.exp(-tt/dec)*0.5
def snare():
    n=int(0.25*SR); tt=np.arange(n)/SR; return (0.6*rng.normal(0,1,n)*np.exp(-tt/0.07)+0.5*np.sin(2*np.pi*190*tt)*np.exp(-tt/0.05))
def pluck(f,dur,bright=6):
    n=int(dur*SR); tt=np.arange(n)/SR; x=sum(np.sin(2*np.pi*f*k*tt)/k**1.2*np.exp(-tt*k/bright/dur*3) for k in range(1,7)); return x*np.exp(-tt/(dur*0.6))
if STYLE=="epic":
    BPM=100; b=60/BPM; D_=drum(); chords=[[45,52,57],[41,48,53],[43,50,55],[40,47,52]]   # Am F G Em, low strings
    build=np.clip(t/TOTAL,0,1)
    music=pad_bed([[c+12 for c in ch] for ch in chords],4*b*2,0.7,oct_=0)
    sub=np.zeros(N)
    for i in range(int(TOTAL/b)+1):
        x=i*b; lvl=0.55+0.45*min(1,x/(TOTAL*0.7))
        hit(sub,x,D_,0.9*lvl if i%2==0 else 0.5*lvl)
        if x>TOTAL*0.25 and i%4==3: hit(sub,x+b/2,D_,0.6*lvl)
        if x>TOTAL*0.45: hit(sub,x+b/2,hat(0.03),0.25*lvl)
        if i%8==0:   # brass-like stab: stacked saw-ish partials
            ch=chords[(i//8)%4]; n=int(1.2*b*SR); tt=np.arange(n)/SR
            st=sum(np.sin(2*np.pi*mtof(m)*k*tt)/k for m in ch for k in range(1,6))*np.exp(-tt/0.35)*np.minimum(1,tt/0.03)
            hit(sub,x,st/np.abs(st).max(),0.35*lvl)
        for h in (0,0.5): hit(sub,x+h*b,pluck(mtof(chords[(i//8)%4][0]-12),b*0.45,4),0.4*lvl)
    music=music*(0.6+0.6*build)+sub
elif STYLE=="tense":
    BPM=90; b=60/BPM; chords=[[57,60,64],[53,57,60],[50,53,57],[52,56,59]]   # Am F Dm E (tense minor)
    music=pad_bed([[c+12 for c in ch] for ch in chords],4*b*2,0.55)
    K_,H_=kick(),hat()
    for i in range(int(TOTAL/b)+1):
        hit(music,i*b,K_,0.9 if i%4==0 else 0.6); hit(music,i*b+b/2,H_,0.35)
        root=chords[(i//8)%4][0]-24
        for h in (0,0.5): hit(music,i*b+h*b,pluck(mtof(root),b*0.45,4),0.45)
elif STYLE=="lofi":
    BPM=84; b=60/BPM; sw=0.58; chords=[[53,57,60,64],[52,55,59,62],[50,53,57,60],[48,52,55,59]]  # Fmaj7 Em7 Dm7 Cmaj7
    music=np.zeros(N); K_,S_,H_=kick(),snare(),hat(0.02)
    for i in range(int(TOTAL/b)+1):
        if i%4 in(0,2): hit(music,i*b,K_,0.8)
        if i%4 in(1,3): hit(music,i*b,S_,0.45)
        hit(music,i*b,H_,0.25); hit(music,i*b+sw*b,H_,0.18)
        if i%4==0:
            for m in chords[(i//4)%4]: hit(music,i*b+0.02*rng.random(),pluck(mtof(m),4*b,10)*(1+0.1*np.sin(2*np.pi*5*np.arange(int(4*b*SR))/SR)),0.16)
    music+=np.where(rng.random(N)<0.0006,rng.normal(0,0.6,N),0)   # vinyl crackle
else:
    music=pad_bed([[57,60,64,69],[53,57,60,65],[48,55,60,64],[55,59,62,67]],6.0)
    air=stft_noise(TOTAL+1,lambda x:1800,lambda x:1.2)[:N]; music[:len(air)]+=air*0.05
fade=np.clip(t/1.5,0,1)*np.clip((TOTAL-t)/2.5,0,1); music*=fade
music=music/np.sqrt((music[fade>0.5]**2).mean()+1e-9)
# ducking: ~-15 dB under voice, ~-8 dB in gaps/transitions (relative to voice RMS), smooth 250 ms
act=movavg((venv>venv.max()*0.08).astype(np.float32),int(0.25*SR))
gain=vr*(10**(-15/20)*act+10**(-8/20)*(1-act))
pad=music*gain
mix=voice+sfx+np.stack([pad,pad*0.97],1).astype(np.float32)
mix=mix[:int(TOTAL*SR)]
mix.astype(np.float32).tofile("assets/mix.f32")
subprocess.run(["ffmpeg","-y","-v","error","-f","f32le","-ar",str(SR),"-ac","2","-i","assets/mix.f32","assets/mix_raw.wav"],check=True)
os.remove("assets/mix.f32"); print("voice rms",vr,"events",len(ev),"peak",np.abs(mix).max())
