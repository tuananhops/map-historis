# scenekit — shared scene helpers (timeline/word timing, credits, cut-outs, stamps, scrims, HS/TS labels, map callouts)
# + NEW effects from docs/effects_study.md (fx section below). Use in a project's scenes.py:  from scenekit import *
import re
from textkit import *
TLJ=json.load(open("assets/timeline.json")); TL={n:(a,b,s) for a,b,n,s in TLJ}
WORDS=json.load(open("assets/disp.json"))
def _norm(x): return re.sub(r"[^\w%.,]","",x).strip(".,").lower()
def WT(word,after,n=1):
    k=0; word=_norm(word)
    for w in WORDS:
        toks=[_norm(t) for t in w["d"].split()]+[_norm(w["d"])]
        if word in toks and w["t0"]>=after-0.13:
            k+=1
            if k==n: return w["t0"]
    raise KeyError(word)
SCENES=[]
def mk_credit(text):
    f=fnt(18,"Medium"); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=int(d.textlength(text,font=f))
    im=Image.new("RGBA",(tw+24,28),(0,0,0,0)); dd=ImageDraw.Draw(im); dd.rounded_rectangle([0,0,tw+23,27],8,fill=(0,0,0,110)); dd.text((12,14),text,font=f,fill=(235,235,235),anchor="lm")
    return pil2spr(im)
CR_SAT=mk_credit("Ảnh vệ tinh: NASA Blue Marble · Sentinel-2 cloudless 2016 © EOX (CC BY 4.0)")
CR_NE=mk_credit("Bản đồ: Natural Earth")
def new(name,bg,kind,credit=None,brand=True):
    a,b,sub=TL[name]; sc=Scene(name,a,b,bg,brand=brand,credit=credit); sc.kind=kind; sc.sub=bool(sub); SCENES.append(sc)
    sc.w=lambda word,n=1: WT(word,sc.t0g,n)-sc.t0g
    return sc
_par=[1]
def drift(src,**k):
    _par[0]*=-1; d=dict(zin=_par[0]>0,pan=(_par[0],0.45*-_par[0])); d.update(k); return DriftBg(src,**d)
def log_lerp(a,b,u): return math.exp(lerp(math.log(a),math.log(b),u))
def dark_bg(seed=3):
    yy,xx=np.mgrid[0:SH,0:SW]; r=np.sqrt(((xx-SW/2)/SW)**2+((yy-SH*0.4)/SH)**2)
    base=np.stack([14+0*r,32+0*r,46+0*r],-1)*(1-0.6*np.clip(r/0.8,0,1))[...,None]+np.random.default_rng(seed).normal(0,1.6,(SH,SW,1))
    return np.clip(base,0,255).astype(np.uint8)
def place(sp,X,Y): return X-((sp.ink[0]+sp.ink[2])/2-sp.w/2), Y-((sp.ink[1]+sp.ink[3])/2-sp.h/2)
MOT_CUT=(2.4,9,2.8,1.0); MOT_GLOW=(1.4,5,3.3,0.3)
def cutout(sc,name,x,y,at,maxw=380,maxh=380,kind="drop",glow=True,mot=MOT_CUT,gsize=None,rot=0.0):
    if glow: sc.add(Item(glow_spr(gsize or int(max(maxw,maxh)*1.45)),x,y,at-0.05,"pop",MOT_GLOW))
    sc.add(Item(cut_spr(name,maxw,maxh),x,y,at,kind,mot,rot=rot),"swish" if kind!="pop" else "pop",at,0.6)
def stamp(sc,text,x,y,at,size=56,color=RD,rot=-10):
    f=fnt(size,"ExtraBold"); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=d.textlength(text,font=f); w,h=int(tw+56),int(size*1.5)
    im=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); dd=ImageDraw.Draw(im); dd.rounded_rectangle([10,10,10+w,10+h],14,outline=color+(235,),width=8)
    dd.text((10+w/2,10+h/2),text,font=f,fill=color+(235,),anchor="mm"); sp=pil2spr(im)
    x=min(max(x,SAFE[0]+w/2),SAFE[2]-w/2); sc.add(Item(sp,x,y,at,"snap",None,rot=rot),"boom",at,0.5); log(sc,text,"label",(x-w/2,y-h/2,x+w/2,y+h/2),at)
def scrim(sc,y0,y1,a=0.55,fade=160):
    """darken a band behind keyword text over busy maps (no box)"""
    ys=np.arange(H,dtype=np.float32); m=np.clip(np.minimum(ys-y0+fade,y1+fade-ys)/fade,0,1)*a; m=(1-m)[:,None,None]
    def f(fr,t,cam): fr*=m
    sc.add(Fn(f))
def hsts(sc,bg,at=0.0,size=22,short=False,col=(230,238,240)):
    """Hoàng Sa & Trường Sa (Việt Nam): dots + labels, labels clamped inside the safe zone"""
    sc.add(Fn(lambda fr,t,cam: hs_ts(fr,bg.cam,t,at)))
    for txt_,a,d in [("Hoàng Sa (VN)" if short else "QĐ. Hoàng Sa (Việt Nam)",(112.0,16.4),-26),("Trường Sa (VN)" if short else "QĐ. Trường Sa (Việt Nam)",(113.8,9.9),30)]:
        spr=text_spr(txt_,size,col,"SemiBold",3)
        def pf(t,a=a,d=d,spr=spr):
            P=P1(bg,*a); return (min(max(P[0],SAFE[0]+spr.w/2-10),SAFE[2]-spr.w/2+10),P[1]+d)
        sc.add(Item(spr,0,0,at+0.1,"fade",posfn=pf))
def sat_hsts(sc,bg,t0,t1):
    def lay(fr,t,cam):
        if not(t0<=t<=t1): return
        st=bg.state
        if st[2]>2500: return
        a=cl((t-t0)/0.3)*cl((t1-t)/0.3)
        P=bg.proj(np.array([p[0] for p in HS+TS]),np.array([p[1] for p in HS+TS])); vis=bg.vis
        m=np.zeros((H,W),np.uint8)
        for q,v in zip(P,vis):
            if v: cv2.circle(m,(int(q[0]*16),int(q[1]*16)),int(max(2,st[2]/260)*16),255,-1,cv2.LINE_AA,4)
        blend_mask(fr,m,(0.97,0.95,0.85),a)
    sc.add(Fn(lay))
    for txt_,anc,d in [("Hoàng Sa (VN)",(112.0,16.4),-22),("Trường Sa (VN)",(113.8,9.9),24)]:
        spr=text_spr(txt_,20,(240,240,236),"SemiBold",3)
        def pf(t,anc=anc,d=d):
            if not(t0<=t<=t1) or bg.state[2]>2500: return (-900,-900)
            P=bg.proj(*anc)[0]; return (P[0],P[1]+d) if bg.vis[0] else (-900,-900)
        sc.add(Item(spr,0,0,t0,"fade",posfn=pf))
def kcall(sc,bg,lon,lat,at,dx,dy,rows,w=400):
    """map callout: leader line + dark card; rows=(text|ctr-dict, role, color, at[, size]); card clamped to safe zone"""
    L=Leader(bg,lon,lat,at,dx,dy,WH); sc.add(L); sc.ev(at,"swish",0.4)
    sizes=[(r[4] if len(r)>4 else ROLE[r[1]][0]) for r in rows]; hh=sum(s*1.12 for s in sizes)+56; side=1 if dx>=0 else -1
    def cc(t):
        e=L.end(t); x=min(max(e[0]+side*w/2,SAFE[0]+w/2),SAFE[2]-w/2); y=min(max(e[1],SAFE[1]+hh/2),SAFE[3]-hh/2); return x,y
    L.endfn=lambda t:(lambda c:np.array([c[0]-side*w/2,c[1]]))(cc(t))
    ca=at+0.3; sc.add(Item(card2(w,int(hh),True),0,0,ca,"pop",posfn=cc)); sc.ev(ca,"pop",0.6)
    y=-hh/2+28; labs=[]
    for r,s in zip(rows,sizes):
        text,role,color,ra=r[:4]; ra=max(ra,ca+0.08); yc=y+s*0.56
        if isinstance(text,dict):
            c=text; f=fnt(s,ROLE[role][1])
            pc=PCounter(lambda t,yc=yc,s=s:(cc(t)[0]+6,cc(t)[1]+yc+s*0.36),ra,c.get("dur",0.7),0,c["v1"],c.get("dec",0),s,color,c.get("pre",""),caps(c.get("suf","")),ROLE[role][1],"bounce",None,0)
            pc.q=c.get("q",10**-c.get("dec",0) if c.get("dec",0) else 1); sc.add(pc); sc.ev(ra,"pop",0.5); [sc.ev(ra+k*0.07,"tick",0.4) for k in range(9)]
            labs.append(pc.fmt(c["v1"]))
        else:
            sp=txt(text,role,color,False,size=s if len(r)>4 else None); labs.append(sp.text)
            sc.add(Item(sp,0,0,ra,"bounce",posfn=lambda t,sp=sp,yc=yc:place(sp,cc(t)[0]+6,cc(t)[1]+yc))); sc.ev(ra,"pop",0.4)
        y+=s*1.12
    sc.post.append(lambda fr,t:fr)
    if hasattr(bg,"at"): bg.at(sc.T-0.01)
    X,Y=cc(sc.T); log(sc,"[callout] "+" / ".join(labs),"card",(X-w/2,Y-hh/2,X+w/2,Y+hh/2),at)
VEQ=vec_equi(("Vietnam",))
# =====================================================================================================
# EFFECTS (docs/effects_study.md) — A zoom/motion, B glow/extrude text (textkit fx=), C transitions, E photo
# =====================================================================================================
def e_expo_io(x):
    x=cl(x)
    if x==0 or x==1: return x
    return 2**(20*x-10)/2 if x<0.5 else (2-2**(-20*x+10))/2
def e_expo_v(x):     # normalised speed of e_expo_io (peak 1 at x=0.5) — drives blur strength
    x=cl(x); return min(1.0,(2**(-abs(20*x-10)))*1.0*7) if 0<x<1 else 0.0
def radial_blur(fr,k,cx=540,cy=820,n=7):
    """zoom blur: average n copies scaled 1..1+k around (cx,cy)"""
    if k<0.004: return fr
    acc=fr.copy()
    for i in range(1,n+1):
        z=1+k*i/n; M=np.float32([[z,0,(1-z)*cx],[0,z,(1-z)*cy]])
        acc+=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
    return acc/(n+1)
def dir_blur(fr,L,vertical=False):
    L=int(L)
    if L<3: return fr
    return cv2.blur(fr,(1,L) if vertical else (L,1),borderType=cv2.BORDER_REFLECT)
def snap_zoom(sc,t0,frames=18,strength=0.22,cx=540,cy=820,sfx=True):
    """A1 snap zoom: pair with a camera path that uses e_expo_io(…(t-t0)/(frames/FPS)) — adds radial motion blur
    proportional to the expo speed + whoosh. Returns the easing fn u(t) for the camera path."""
    d=frames/FPS
    def post(fr,t):
        u=(t-t0)/d
        if 0<u<1: return radial_blur(fr,strength*e_expo_v(u),cx,cy)
        return fr
    sc.post.append(post)
    if sfx: sc.ev(max(0,t0-0.05),"whoosh",1.0)
    return lambda t: e_expo_io((t-t0)/d)
def transition(a,b,kind="whip",frames=12,direction=1):
    """C: whip pan (directional blur) or zoom-through (radial blur) between two GRAPHIC scenes.
    Half the frames at the end of a, half at the start of b. Do NOT use into/out of subtitle scenes (hard cut)."""
    if a.sub or b.sub: return False
    n=frames//2; a.tout=(kind,n,direction); b.tin=(kind,n,direction)
    b.ev(0.0,"whoosh",0.9 if kind=="whip" else 1.1); return True
def _apply_trans(sc,fr,f):
    tin=getattr(sc,"tin",None); tout=getattr(sc,"tout",None); k=f-sc.f0; r=sc.f1-1-f
    if tin and k<tin[1]:
        kind,n,dr=tin; p=(k+1)/(n+1)
        if kind=="whip":
            off=dr*W*0.55*(1-e_out(p))**1.5; M=np.float32([[1,0,off],[0,1,0]])
            fr=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT); fr=dir_blur(fr,220*(1-p)**1.3)
        else:
            z=1+0.9*(1-e_out(p))**2; M=np.float32([[z,0,(1-z)*540],[0,z,(1-z)*900]])
            fr=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT); fr=radial_blur(fr,0.35*(1-p),540,900)
    if tout and r<tout[1]:
        kind,n,dr=tout; p=(tout[1]-r)/(n+1)
        if kind=="whip":
            off=-dr*W*0.55*p**3; M=np.float32([[1,0,off],[0,1,0]])
            fr=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT); fr=dir_blur(fr,220*p**1.3)
        else:
            z=1+1.6*p**2; M=np.float32([[z,0,(1-z)*540],[0,z,(1-z)*900]])
            fr=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT); fr=radial_blur(fr,0.35*p,540,900)
        fr=fr*(1+0.25*p**2)   # light flash at the cut
    return fr
_orig_render=Scene.render
def _render_fx(s,f):
    out=_orig_render(s,f)
    if getattr(s,"tin",None) or getattr(s,"tout",None):
        fr=out.astype(np.float32)*(1/255.0); fr=_apply_trans(s,fr,f); out=(fr*255+0.5).clip(0,255).astype(np.uint8)
    return out
Scene.render=_render_fx
def auto_transitions(scenes,kinds=("whip","zoom"),skip=("end",)):
    """whip/zoom-through between consecutive graphic scenes; hard cuts kept around subtitle scenes"""
    i=0; used=[]
    for a,b in zip(scenes,scenes[1:]):
        if a.name in skip or b.name in skip or getattr(b,"no_tin",False): continue
        if transition(a,b,kinds[i%len(kinds)],12,1 if i%4<2 else -1): used.append((round(b.t0g,2),a.name,b.name,kinds[i%len(kinds)])); i+=1
    return used
class RackFocus:
    """A4 rack focus: blur everything drawn BEFORE this layer from s0 to s1 (gaussian sigma px) over [at,at+dur]"""
    def __init__(s,at,dur=1.0,s0=0.0,s1=9.0): s.at,s.dur,s.s0,s.s1=at,dur,s0,s1
    def draw(s,fr,t,cam):
        sg=lerp(s.s0,s.s1,e_io((t-s.at)/s.dur)) if t>=s.at else s.s0
        if sg<0.3: return
        sm=cv2.resize(fr,(W//2,H//2),interpolation=cv2.INTER_AREA); sm=cv2.GaussianBlur(sm,(0,0),sg/2)
        fr[:]=cv2.resize(sm,(W,H),interpolation=cv2.INTER_LINEAR)
class NeonOutline:
    """B6 dashed neon outline running around a cut-out (same name/size/pos as cutout()); draws on in 0.5 s"""
    def __init__(s,name,x,y,at,maxw=380,maxh=380,color=OR,dash=26,gap=18,speed=140,off=12,width=5,mot=None):
        sp=cut_spr(name,maxw,maxh); a=(sp.a[...,3]*255).astype(np.uint8)
        a=cv2.dilate((a>40).astype(np.uint8)*255,cv2.getStructuringElement(cv2.MORPH_ELLIPSE,(2*off+1,2*off+1)))
        cs,_=cv2.findContours(a,cv2.RETR_EXTERNAL,cv2.CHAIN_APPROX_NONE); c=max(cs,key=cv2.contourArea)[:,0,:].astype(np.float32)
        c=cv2.approxPolyDP(c,1.5,True)[:,0,:].astype(np.float32); c=np.vstack([c,c[:1]])
        seg=np.sqrt(((c[1:]-c[:-1])**2).sum(1)); L=np.concatenate([[0],np.cumsum(seg)])
        s.n=int(L[-1]/3); u=np.linspace(0,L[-1],s.n); s.P=np.stack([np.interp(u,L,c[:,0]),np.interp(u,L,c[:,1])],1)-np.float32([sp.w/2,sp.h/2])
        s.L=L[-1]; s.x,s.y,s.at,s.col,s.dash,s.gap,s.speed,s.width,s.mot=x,y,at,np.float32(color)/255,dash,gap,speed,width,mot
    def draw(s,fr,t,cam):
        if t<s.at: return
        ox,oy=moff(s.mot,t,cam); P=s.P+np.float32([s.x+ox,s.y+oy]); reveal=e_out((t-s.at)/0.5)
        per=s.dash+s.gap; ph=(t-s.at)*s.speed; step=s.L/s.n
        m=np.zeros((H,W),np.uint8); nmax=int(s.n*reveal)
        idx=np.arange(nmax); on=((idx*step+ph)%per)<s.dash
        # split into runs
        runs=np.split(idx[on],np.where(np.diff(idx[on])!=1)[0]+1) if on.any() else []
        pts=[np.round(P[r]*16).astype(np.int32) for r in runs if len(r)>1]
        if pts: cv2.polylines(m,pts,False,255,s.width,cv2.LINE_AA,4)
        glow_mask(fr,m,s.col,1.3,10); blend_mask(fr,m,np.minimum(s.col*1.2+0.15,1),1.0)
def bw_photo(path,w,h=None,border=16,grain=0.035,sepia=0.08,contrast=1.15,rot=0.0,shadow=True):
    """E: archival treatment — B&W + slight sepia + grain + vignette, printed with white border; returns Spr"""
    im=Image.open(path).convert("RGB"); h=h or int(w*im.height/im.width); im=cover(im,w,h)
    g=np.asarray(ImageOps.grayscale(im)).astype(np.float32)/255; g=np.clip((g-0.5)*contrast+0.5,0,1)
    yy,xx=np.mgrid[0:h,0:w]; r=np.sqrt(((xx-w/2)/(w/2))**2+((yy-h/2)/(h/2))**2); g*=1-0.28*np.clip(r-0.5,0,1)
    g=np.clip(g+np.random.default_rng(3).normal(0,grain,g.shape),0,1)
    rgb=np.stack([g*(1+sepia*0.6),g*(1+sepia*0.15),g*(1-sepia*0.5)],-1); rgb=np.clip(rgb*255,0,255).astype(np.uint8)
    card=Image.new("RGBA",(w+2*border,h+2*border),(246,244,238,255)); card.paste(Image.fromarray(rgb),(border,border))
    pad=60; c=Image.new("RGBA",(card.width+2*pad,card.height+2*pad),(0,0,0,0))
    if shadow:
        sh=Image.new("RGBA",c.size,(0,0,0,0)); ImageDraw.Draw(sh).rectangle([pad+8,pad+16,pad+card.width+8,pad+card.height+16],fill=(0,0,0,110)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    c.alpha_composite(card,(pad,pad))
    if rot: c=c.rotate(rot,Image.BICUBIC,expand=True)
    return pil2spr(c)
def photo_bright(path,w,h,border=0,rot=0.0,sat=1.08,bright=1.04):
    """color photo card (bright, no black background) for sparing reference photos"""
    im=cover(Image.open(path).convert("RGB"),w,h); im=ImageEnhance.Color(im).enhance(sat); im=ImageEnhance.Brightness(im).enhance(bright)
    pad=60; card=Image.new("RGBA",(w+2*border,h+2*border),(250,250,248,255)); card.paste(im,(border,border))
    c=Image.new("RGBA",(card.width+2*pad,card.height+2*pad),(0,0,0,0)); sh=Image.new("RGBA",c.size,(0,0,0,0))
    ImageDraw.Draw(sh).rectangle([pad+8,pad+16,pad+card.width+8,pad+card.height+16],fill=(0,0,0,100)); c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14))); c.alpha_composite(card,(pad,pad))
    if rot: c=c.rotate(rot,Image.BICUBIC,expand=True)
    return pil2spr(c)
def KX(sc,text,role,color,x,y,at,fx="extrude",**k):
    """dramatic keyword: 3D extrude (boom) or glow (pop); same placement/log rules as K()"""
    b=K(sc,text,role,color,x,y,at,fx=fx,sfx=None,**k)
    sc.ev(at,"boom" if fx.startswith("extrude") else "pop",0.9 if fx.startswith("extrude") else 0.5); return b
def chaching(sc,at,g=1.0): sc.ev(at,"chaching",g)
