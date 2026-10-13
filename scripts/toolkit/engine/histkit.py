# histkit — reusable HISTORY-MAP templates for the Hinton toolkit (built for "Mông Cổ vs Đại Việt").
#   from tpl import *; from histkit import *
# Territory spread (EmpireFX/RegionFX), Đại Việt glow, eased camera paths, darkened satellite Mercator basemap (SatMapBg),
# word-synced 1–3-word captions (Montserrat), army dot clusters, top-down ships, Ken Burns paintings, Polaroid photos, Earth intro/outro.
from tpl import *
from PIL import ImageOps
RD2=(206,36,40); GOLD=(255,200,70)
KAR=(102.8,47.2)                      # Karakorum
CITY={"onon":(109.0,48.5),"bk":(116.4,39.9),"sam":(66.97,39.65),"kiev":(30.52,50.45),"bag":(44.4,33.3),
      "tl":(105.85,21.03),"bd":(106.75,20.92),"kunming":(102.7,25.0),"nanning":(108.3,22.8),"qz":(110.3,21.3)}
CR_MAP=mk_credit("Bản đồ: Natural Earth · ranh giới lịch sử minh hoạ, gần đúng")
# ---------------- approximate historical extents (lon,lat); clipped to land and minus EXCL countries ----------------
P_1206=["Mongolia",[(98,50),(98,53.5),(110,53.5),(117,50),(105,48)]]
P_1215=[(98,43.5),(105,46),(118,48),(124,47),(126,42.5),(122,40.5),(121.5,39),(119,37.5),(117,36.5),(112,37.2),(106,38.5),(101,40)]
P_1220=[(52,45),(56,49),(62,53),(70,55),(85,54),(95,52.5),(99,48),(99,46),(98,42),(92,39),(80,36.5),(73,36.8),(70,34.5),(62,34.5),(57,37.5),(53,40)]
P_RUS=[(26,48.5),(27,53),(32,56),(40,57.5),(50,58),(58,56.5),(62,52),(60,48),(54,45),(49,43.5),(46,41.8),(40,43.5),(37.5,45),(33,44.5),(30,46)]
P_JIN=[(101,40),(106,38.5),(112,37.2),(117,36.5),(119,37.5),(121,37.5),(122.5,37),(120,34.5),(119,33),(114,32.5),(108,33),(104,32.5),(102.5,34),(100.5,37)]
P_MAN=[(118,48),(124,53.5),(135,53),(135,48),(131,43),(126,42.5),(124,47)]
P_1258=[(39,42),(46,43.5),(50,44),(54,42),(57,38.5),(62,35.5),(63,31),(61.5,25.2),(57.5,25.6),(56.2,27.1),(52,27.6),(50,30),(48,30),(46.5,31),
        (44,32.5),(41.5,34.5),(38.5,36.8),(36.3,37.0),(33,38),(31.5,40),(32.5,41.8),(36,41.8)]
P_YUN=[(78,36),(80,32),(84,29),(88,27.5),(92,27.2),(96,27),(97,24),(99,21),(102,21),(104.5,21.8),(106,25),(105,29),(104.5,32.8),(102,35.5),(99,38.5),(92,39.5),(85,37.5)]
P_SONG=[(104,32.5),(108,33),(114,32.5),(119,33),(120,34.5),(122,31.5),(121.5,28),(119.5,25.5),(117,23.3),(114,22.2),(111.5,18),(108.5,17.5),(104,21.5),(102.5,22.0),
        (106,25),(105,29),(104.5,32.8)]
P_KOR=[(124.5,40),(129,42.5),(130.7,42.3),(129.6,35.1),(126.3,34.3),(125,37.5)]
EXCL={"Vietnam","Laos","Myanmar","Thailand","India","Nepal","Bhutan","Bangladesh","Pakistan","Japan","Syria","Saudi Arabia","Kuwait",
      "Jordan","Israel","Lebanon","Poland","Hungary","Taiwan","Philippines","Cambodia","Oman","United Arab Emirates","Qatar","Bahrain","Palestine"}
ST_1240=[P_RUS,P_JIN,P_MAN]
ALL=P_1206+[P_1215,P_1220,P_RUS,P_JIN,P_MAN,P_1258,P_YUN,P_SONG,P_KOR]
def hav(lon,lat,a=KAR):
    l1,p1,l2,p2=[np.radians(v) for v in (lon,lat,a[0],a[1])]
    return 2*6371*np.arcsin(np.sqrt(np.sin((p2-p1)/2)**2+np.cos(p1)*np.cos(p2)*np.sin((l2-l1)/2)**2))
def drange(polys):
    lo,la=np.meshgrid(np.arange(-20,150,0.5),np.arange(0,70,0.5)); ds=[]
    for P in polys:
        if isinstance(P,str): P=[tuple(x) for x in np.stack(merc_inv(biggest(P)[0]),-1)[::5]]
        c=np.array(P,np.float32); ins=np.array([cv2.pointPolygonTest(c,(float(x),float(y)),False)>=0 for x,y in zip(lo.ravel(),la.ravel())])
        ds.append(hav(lo.ravel()[ins],la.ravel()[ins]))
    d=np.concatenate(ds); return float(d.min()),float(d.max())
def wobble(Q,a=0.55):
    x,y=Q[:,0],Q[:,1]
    dx=a*(np.sin(x*0.61+y*0.37)+0.5*np.sin(x*1.7-y*1.3+2.1)); dy=a*(np.cos(x*0.43-y*0.71+0.7)+0.5*np.sin(x*1.4+y*1.9))
    return np.stack([x+dx,y+dy],-1)
def poly_px(cm,P,step=0.4):
    if isinstance(P,str): return [np.round(cm.mp(r)*16).astype(np.int32) for r in COUNTRIES[P] if len(r)>20]
    P=np.array(list(P)+[P[0]],float); Q=[]
    for i in range(len(P)-1):
        n=max(2,int(np.linalg.norm(P[i+1]-P[i])/step)); Q.append(np.linspace(P[i],P[i+1],n,endpoint=False))
    Q=wobble(np.concatenate(Q)); return [np.round(cm.proj(Q[:,0],Q[:,1])*16).astype(np.int32)]
class EmpireFX:
    """growing empire: stages [(polys, t0, dur)] — each stage spreads as a wave (distance from Karakorum) over its region;
    deep red fill + glowing border + bright advancing front."""
    def __init__(s,bg,stages,alpha=0.62):
        s.bg=bg; s.alpha=alpha; s.st=[(P,t0,du)+drange(P) for P,t0,du in stages]
    def draw(s,fr,t,cam):
        cm=s.bg.cam; q=4; h,w=H//q,W//q
        xs=(np.arange(w)*q+q/2-cm.sx)/cm.S; ys=-(np.arange(h)*q+q/2-cm.sy)/cm.S
        M=np.stack(np.meshgrid(xs+cm.c[0],ys+cm.c[1]),-1); lon,lat=merc_inv(M); D=hav(lon,lat)
        tot=np.zeros((h,w),np.float32); front=np.zeros((h,w),np.float32)
        for P,t0,du,d0,d1 in s.st:
            if t<t0: continue
            u=e_out((t-t0)/du); r=lerp(d0-300,d1+300,u)
            pm=np.zeros((H,W),np.uint8)
            for p in P:
                for q in poly_px(cm,p): cv2.fillPoly(pm,[q],255,cv2.LINE_AA,4)
            pm=cv2.resize(pm,(w,h),interpolation=cv2.INTER_AREA).astype(np.float32)/255
            wave=np.clip((r-D)/180,0,1); tot=np.maximum(tot,pm*wave)
            if u<1: front=np.maximum(front,pm*np.exp(-((D-r)/140)**2)*(1-u**4))
        if tot.max()<=0: return
        land=poly_mask(W,H,cm,s.bg.rs,True).astype(np.float32)/255
        ex=[x for x in s.bg.rs if x[0] in EXCL]
        if ex: land*=1-poly_mask(W,H,cm,ex,True).astype(np.float32)/255
        T=cv2.resize(tot,(W,H),interpolation=cv2.INTER_LINEAR)*land
        a=(s.alpha*(0.94+0.06*math.sin(t*4)))*T
        fr*=1-a[...,None]; fr+=a[...,None]*np.float32(RD2)/255
        b=(T>0.5).astype(np.uint8)*255; edge=cv2.morphologyEx(b,cv2.MORPH_GRADIENT,np.ones((5,5),np.uint8))
        glow_mask(fr,edge,np.float32((255,90,60))/255,1.0,10); blend_mask(fr,edge,np.float32((255,150,110))/255,0.95)
        if front.max()>0:
            F=cv2.GaussianBlur(cv2.resize(front,(W,H),interpolation=cv2.INTER_LINEAR),(0,0),6)*land
            fr+=F[...,None]*np.float32((1.0,0.62,0.3))*0.9
class DaiVietFX:
    """Đại Việt (thế kỷ XIII, phía bắc ~vĩ tuyến 17): gold fill + glow + pulsing border"""
    def __init__(s,bg,at,dur=0.6,alpha=0.85): s.bg,s.at,s.dur,s.alpha=bg,at,dur,alpha
    def draw(s,fr,t,cam):
        if t<s.at: return
        cm=s.bg.cam; rs=[x for x in s.bg.rs if x[0]=="Vietnam"]
        if not rs: return
        m=poly_mask(W,H,cm,rs,True); y=int(cm.proj(np.array([106.0]),np.array([16.95]))[0][1]); m[max(0,y):]=0
        a=e_out((t-s.at)/s.dur)*s.alpha
        glow_mask(fr,m,np.float32(GOLD)/255,0.9*a*(0.75+0.25*math.sin(t*5)),16); blend_mask(fr,m,np.float32(GOLD)/255,a)
        e=cv2.morphologyEx(m,cv2.MORPH_GRADIENT,np.ones((4,4),np.uint8)); blend_mask(fr,e,(1,0.97,0.85),a)
def cam_path(keys):
    """keys: [(t, lon, lat, k)] — eased (e_io) moves between consecutive keyframes"""
    def f(t):
        if t<=keys[0][0]: return keys[0][1:]
        for (ta,*A),(tb,*B) in zip(keys,keys[1:]):
            if t<tb:
                u=e_io((t-ta)/(tb-ta)); return (lerp(A[0],B[0],u),lerp(A[1],B[1],u),log_lerp(A[2],B[2],u))
        return keys[-1][1:]
    return f
def mapscene(name,keys,sy=900,drift=0.04,dark=0.92):
    d=dur_of(name); cp=cam_path(keys)
    def p(t):
        lon,lat,k=cp(t); return lon,lat,k*(1+drift*e_sine(t/d)),0,sy
    bg=VecBg(p,dark); sc=new(name,bg,"map",credit=CR_MAP); return sc,bg
def pin_label(sc,bg,text,ll,at,dx=0,dy=-58,col=WH,until=1e9):
    sp=text_spr(caps(text),36,col,"ExtraBold",5)
    def pf(t):
        P=P1(bg,*ll); x=min(max(P[0]+dx,SAFE[0]+sp.w/2-20),SAFE[2]-sp.w/2+20); y=min(max(P[1]+dy,560),1290); return x,y
    sc.add(TItem(sp,0,0,at,"bounce",posfn=pf,until=until,exit="fade"))
def hud(sc,rows,y=330,y2=470,col=OR):
    """big year + caption at the top, each pair replaced by the next (exit up)"""
    for i,(yr,cap,at) in enumerate(rows):
        nxt=rows[i+1][2] if i+1<len(rows) else 1e9
        for txt_,role,yy,c,fx in ((yr,"hero",y,col,"glow"),(cap,"label",y2,WH,None)):
            sz=ROLE[role][0]; sp=txt(txt_,role,c,True,fx=fx)
            while sp.ink[2]-sp.ink[0]>SAFE[2]-SAFE[0]-20 and sz>34: sz-=2; sp=txt(txt_,role,c,True,size=sz,fx=fx)
            cx=540-((sp.ink[0]+sp.ink[2])/2-sp.w/2); cy=yy-((sp.ink[1]+sp.ink[3])/2-sp.h/2); cx,cy=clamp_xy(sp,cx,cy)
            sc.add(TItem(sp,cx,cy,at if role=="hero" else at+0.12,"bounce",until=nxt-0.12,exit="up")); log(sc,sp.text,role,ink_box(sp,cx,cy),at)
        sc.ev(at,"boom" if i==0 else "pop",0.7)
Y0,Y1=1206,1288; TX0,TX1,TY=180,875,1330
def timeline(sc,keys,ticks=(1206,1240,1288),until=1e9):
    """bottom history timeline 1206→1288: keys [(t, year)] — orange fill eases to each year"""
    def yr(t):
        v=keys[0][1]
        for (ta,ya),(tb,yb) in zip(keys,keys[1:]):
            if t>=tb: v=yb
            elif t>=ta: return lerp(ya,yb,e_io((t-ta)/max(0.01,min(0.6,tb-ta)))) if False else v
        return v
    st={"v":None}
    def f(fr,t,cam):
        al=1-e_io((t-until)/0.4)
        if al<=0: return
        if al<1: tmp=fr.copy(); g(tmp,t); fr[...]=fr*(1-al)+tmp*al
        else: g(fr,t)
    def g(fr,t):
        tgt=keys[0][1]; ta=0
        for tk,yk in keys:
            if t>=tk: tgt,ta=yk,tk
        prev=[y for tk,y in keys if tk<ta]; y0=prev[-1] if prev else tgt
        v=lerp(y0,tgt,e_io((t-ta)/0.6)); x=TX0+(v-Y0)/(Y1-Y0)*(TX1-TX0)
        m=np.zeros((H,W),np.uint8); cv2.line(m,(TX0*16,TY*16),(TX1*16,TY*16),255,4,cv2.LINE_AA,4); blend_mask(fr,m,(0.75,0.8,0.82),0.45)
        m=np.zeros((H,W),np.uint8); cv2.line(m,(TX0*16,TY*16),(int(x*16),TY*16),255,8,cv2.LINE_AA,4); glow_mask(fr,m,ORf,0.8,8); blend_mask(fr,m,ORf,1)
        for yk in sorted({y for _,y in keys}):
            if yk<=v+0.01: xx=TX0+(yk-Y0)/(Y1-Y0)*(TX1-TX0); m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(xx*16),TY*16),9*16,255,-1,cv2.LINE_AA,4); blend_mask(fr,m,WHf,1)
        blit(fr,glow_spr(90,OR,230),x,TY); m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(x*16),TY*16),13*16,255,-1,cv2.LINE_AA,4); blend_mask(fr,m,WHf,1)
    sc.add(Fn(f))
    for y in ticks:
        sp=txt(str(y),"axis",(225,232,235),True); x=TX0+(y-Y0)/(Y1-Y0)*(TX1-TX0); cy=TY+45-((sp.ink[1]+sp.ink[3])/2-sp.h/2); cx=x-((sp.ink[0]+sp.ink[2])/2-sp.w/2)
        sc.add(TItem(sp,cx,cy,0.0,"fade",until=until,exit="fade")); log(sc,str(y),"axis",ink_box(sp,cx,cy),0.0)
class Attack:
    """invasion arrow (red) that is repelled: draws in, impact burst at target, then fades/retreats"""
    def __init__(s,bg,a,b,at,hit,bend=0.2): s.R=Route(bg,a,b,at,hit-at,bend,RD,7,flow=False); s.bg,s.b,s.at,s.hit=bg,b,at,hit
    def draw(s,fr,t,cam):
        if t<s.at: return
        if t<s.hit+0.7:
            tmp=fr.copy(); s.R.draw(tmp,t,cam); al=1-e_io((t-s.hit-0.15)/0.55); fr[...]=fr*(1-al)+tmp*al
        if t>=s.hit:
            u=(t-s.hit)/0.7
            if u<1:
                P=P1(s.bg,*s.b); m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(P[0]*16),int(P[1]*16)),int((20+190*e_out(u))*16),255,6,cv2.LINE_AA,4)
                glow_mask(fr,m,np.float32(GOLD)/255,1.2*(1-u),8); blend_mask(fr,m,np.float32((255,236,180))/255,1-u)
                blit(fr,glow_spr(360,GOLD,230),P[0],P[1],1.0,0,1-u)


from PIL import ImageOps
def polaroid(path,w,rot):
    im=Image.open(path).convert("RGB"); im=ImageOps.fit(im,(w,int(w*0.82)),Image.LANCZOS); b=int(w*0.05)
    P=Image.new("RGB",(w+2*b,int(w*0.82)+b+int(w*0.16)),(250,250,247)); P.paste(im,(b,b))
    pad=60; C=Image.new("RGBA",(P.width+2*pad,P.height+2*pad),(0,0,0,0)); sh=Image.new("RGBA",C.size,(0,0,0,0))
    ImageDraw.Draw(sh).rectangle([pad+8,pad+18,pad+P.width+8,pad+P.height+18],fill=(0,0,0,140)); C.alpha_composite(sh.filter(ImageFilter.GaussianBlur(18)))
    C.paste(P,(pad,pad)); return pil2spr(C.rotate(rot,Image.BICUBIC,expand=True))
class KB:
    """Ken Burns background: slow zoom/pan over a painting, cover-cropped, darkened edges"""
    def __init__(s,path,z=(1.0,1.18),fx=(0.5,0.5),fy=(0.5,0.45),dur=3):
        im=np.asarray(Image.open(path).convert("RGB")).astype(np.float32)/255; s.im=im; s.z,s.fx,s.fy,s.d=z,fx,fy,dur
        yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/W)**2+((yy-H/2)/H)**2); s.vig=(1-0.55*np.clip(r-0.25,0,1)**1.2)[...,None].astype(np.float32)
    def __call__(s,u,t):
        h,w=s.im.shape[:2]; base=max(W/w,H/h); z=base*lerp(s.z[0],s.z[1],e_sine(t/s.d))
        cx=lerp(*s.fx,e_sine(t/s.d))*w; cy=lerp(*s.fy,e_sine(t/s.d))*h
        cx=min(max(cx,W/2/z),w-W/2/z); cy=min(max(cy,H/2/z),h-H/2/z)
        M=np.float32([[z,0,W/2-cx*z],[0,z,H/2-cy*z]]); fr=cv2.warpAffine(s.im,M,(W,H),flags=cv2.INTER_AREA if z<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        return (np.clip(fr*s.vig,0,1)*255).astype(np.uint8),(0.0,0.0)
def title(sc,t,col=OR,y=330,at=0.0): K(sc,t,"key",col,540,y,at,fx="glow",size=96)
# ======================= v3 additions =======================
from sat import _tex
MONT=os.environ.get("HIST_FONT_DIR",os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))),"assets","fonts"))+"/"
def mfont(size,w="Black"): return ImageFont.truetype(MONT+f"Montserrat-{w}.ttf",size)
class SatMapBg:
    """darkened, contrasty satellite basemap in Mercator (Blue Marble + optional EOX Sentinel-2 Mercator mosaics).
    path(t)->(lon,lat,k,rot,sy) like VecBg; exposes .cam/.rs so EmpireFX/DaiVietFX/hsts work on top."""
    def __init__(s,path,layers=(),dark=0.68,contrast=1.18,sat=1.05):
        s.path,s.dark,s.contrast,s.sat=path,dark,contrast,sat; s.layers=[(k,_tex(k)) for k in layers if _tex(k) is not None]
        yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/W)**2+((yy-H/2)/H)**2); s.vig=(1-0.6*np.clip(r-0.22,0,1)**1.3)[...,None].astype(np.float32)
    def at(s,t):
        v=s.path(t); s.cam=Cam(v[0],v[1],v[2],0,sy=v[4] if len(v)>4 else 820); return s
    def proj(s,lon,lat):
        if not hasattr(s,"cam"): s.at(0)
        return s.cam.proj(np.atleast_1d(lon),np.atleast_1d(lat))
    def __call__(s,u,t):
        s.at(t); cm=s.cam
        xs=(np.arange(W)+0.5-cm.sx)/cm.S+cm.c[0]; ys=-(np.arange(H)+0.5-cm.sy)/cm.S+cm.c[1]
        lon1=((xs/D2R+180)%360-180).astype(np.float32); lat1=((2*np.arctan(np.exp(ys))-math.pi/2)/D2R).astype(np.float32)
        lon=np.broadcast_to(lon1[None,:],(H,W)); lat=np.broadcast_to(lat1[:,None],(H,W))
        bm=_tex("BM"); mx,my=bm.coords(lon,lat); img=cv2.remap(bm.img,mx,my,cv2.INTER_CUBIC,borderMode=cv2.BORDER_WRAP).astype(np.float32)/255
        k=cm.S*D2R
        for key,tex in s.layers:
            need=tex.res*0.05
            if k<need: continue
            mx,my=tex.coords(lon,lat); ins=(mx>=0)&(my>=0)&(mx<tex.w-1)&(my<tex.h-1)
            if not ins.any(): continue
            col=cv2.remap(tex.img,mx,my,cv2.INTER_AREA if k<tex.res else cv2.INTER_CUBIC,borderMode=cv2.BORDER_REPLICATE).astype(np.float32)/255
            f=np.clip(np.minimum(np.minimum(mx,tex.w-1-mx)/(0.06*tex.w),np.minimum(my,tex.h-1-my)/(0.06*tex.h)),0,1)*ins*cl((k-need)/need)
            img=img*(1-f[...,None])+col*f[...,None]
        g=img.mean(2,keepdims=True); img=g+(img-g)*s.sat; img=np.clip((img-0.45)*s.contrast+0.45,0,1)*s.dark*s.vig
        s.rs=rings_in_view(cm,W,H)
        return (np.clip(img,0,1)*255).astype(np.uint8),(0.0,0.0)
def satscene(name,keys,layers=("vnn8",),sy=900,drift=0.04,credit=None):
    d=dur_of(name); cp=cam_path(keys)
    def p(t): lon,lat,k=cp(t); return lon,lat,k*(1+drift*e_sine(t/d)),0,sy
    bg=SatMapBg(p,layers); sc=new(name,bg,"map",credit=credit or CR_SAT); return sc,bg
# ---------- word-synced captions (1–3 words, ALL CAPS, Montserrat Black, spring pop) ----------
CAP_RED={"MÔNG","CỔ","NGUYÊN","HỐT","TẤT","LIỆT","THẤT","BẠI","THUA","VỠ","TAN","GIẶC","KỴ","BINH","MẮC","CỌC"}
CAP_YEL={"ĐẠI","VIỆT","TRẦN","HƯNG","ĐẠO","BẠCH","ĐẰNG","HINTON","MEDIA","THĂNG","LONG","BẰNG","CHỨNG?","BẪY","TRIỀU","QUẢNG","NINH","NHỎ","BA"}
def cap_groups(words,maxw=3,maxc=15):
    G=[]; cur=[]
    for w in words:
        cur.append(w); txt_=" ".join(x["d"] for x in cur)
        if w["d"][-1] in ",.?!:" or len(cur)>=maxw or len(txt_)>=maxc: G.append(cur); cur=[]
    if cur: G.append(cur)
    return G
@functools.lru_cache(None)
def cap_spr(text,size=88):
    toks=text.upper().split(); f=mfont(size); d=ImageDraw.Draw(Image.new("L",(1,1)))
    cols=[]
    for t in toks:
        c=re.sub(r"[,.:!]","",t)
        cols.append((255,214,64) if (re.search(r"\d",c) or c in CAP_YEL) else (240,62,52) if c in CAP_RED else (255,255,255))
    sw=d.textlength(" ",font=f); ws=[d.textlength(t,font=f) for t in toks]; tw=sum(ws)+sw*(len(toks)-1)
    while tw>880 and size>56: return cap_spr(text,size-6)
    asc,desc=f.getmetrics(); pad=40; im=Image.new("RGBA",(int(tw)+2*pad,asc+desc+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ds=ImageDraw.Draw(sh); x=pad
    for t,w_ in zip(toks,ws): ds.text((x,pad+6),t,font=f,fill=(0,0,0,200),stroke_width=6,stroke_fill=(0,0,0,200)); x+=w_+sw
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(9))); dd=ImageDraw.Draw(im); x=pad
    for t,w_,c in zip(toks,ws,cols): dd.text((x,pad),t,font=f,fill=c,stroke_width=2,stroke_fill=(0,0,0)); x+=w_+sw
    return pil2spr(im)
def add_captions(y=1240):
    G=cap_groups(WORDS); items=[]
    for i,g in enumerate(G):
        t0=g[0]["t0"]-0.04; t1=(G[i+1][0]["t0"]-0.04) if i+1<len(G) else g[-1]["t1"]+0.6
        items.append((t0,t1," ".join(x["d"] for x in g)))
    for sc in SCENES:
        mine=[(a,b,tx) for a,b,tx in items if a<sc.f1/FPS and b>sc.f0/FPS]
        def f(fr,t,cam,mine=mine,sc=sc):
            T=sc.t0g+t
            for a,b,tx in mine:
                if a<=T<b:
                    u=(T-a)*FPS; s_=0.55+0.45*e_back(u/7,2.2) if u<7 else 1.0
                    blit(fr,cap_spr(tx),540,y,s_,0,cl(u/2))
        sc.add(Fn(f))
        for a,b,tx in mine:
            if sc.f0/FPS<=a<sc.f1/FPS: sc.ev(a-sc.t0g,"pop",0.25)
# ---------- armies, ships, photos, paintings ----------
class ArmyDots:
    """cluster of small glowing blocks marching along a curved path a→b (lon,lat)"""
    def __init__(s,bg,a,b,at,dur,n=36,color=RD2,bend=0.15,spread=46,size=9,seed=1,stop=1.0):
        s.__dict__.update(locals()); del s.__dict__["s"]; r=np.random.default_rng(seed)
        s.off=np.stack([r.normal(0,spread,n),r.normal(0,spread*0.6,n)],-1); s.lag=r.uniform(0,0.12,n)
    def draw(s,fr,t,cam):
        if t<s.at: return
        A=P1(s.bg,*s.a); B=P1(s.bg,*s.b); dv=B-A; nn=np.array([dv[1],-dv[0]]); C=(A+B)/2+nn*s.bend
        m=np.zeros((H,W),np.uint8)
        for (ox,oy),lg in zip(s.off,s.lag):
            u=min(s.stop,e_io((t-s.at-lg)/s.dur)); P=(1-u)**2*A+2*(1-u)*u*C+u**2*B
            x,y=P[0]+ox,P[1]+oy; q=s.size*8
            cv2.rectangle(m,(int(x*16-q),int(y*16-q)),(int(x*16+q),int(y*16+q)),255,-1,cv2.LINE_AA,4)
        glow_mask(fr,m,np.float32(s.color)/255,1.1,8); blend_mask(fr,m,np.minimum(np.float32(s.color)/255*1.25,1),1)
@functools.lru_cache(None)
def ship_spr(color=RD2,L=90):
    S=4; w,h=L*S,int(L*0.36)*S; im=Image.new("RGBA",(w+40,h+40),(0,0,0,0)); d=ImageDraw.Draw(im); o=20
    hull=[(o,o+h*0.2),(o+w*0.72,o),(o+w,o+h/2),(o+w*0.72,o+h),(o,o+h*0.8)]
    d.polygon(hull,fill=tuple(color)+(255,),outline=(30,12,8,255)); d.line([(o+w*0.08,o+h/2),(o+w*0.86,o+h/2)],fill=(60,24,14,255),width=S*2)
    for k in range(1,6): x=o+w*k/7; d.line([(x,o+h*0.15),(x,o+h*0.85)],fill=(0,0,0,70),width=S)
    d.rectangle([o+w*0.38,o+h*0.08,o+w*0.44,o+h*0.92],fill=(235,225,200,255))
    im=im.resize(((w+40)//S,(h+40)//S),Image.LANCZOS); return pil2spr(im)
def polaroid(path,w,rot,crop=None):
    im=Image.open(path).convert("RGB")
    if crop: W0,H0=im.size; im=im.crop((int(crop[0]*W0),int(crop[1]*H0),int(crop[2]*W0),int(crop[3]*H0)))
    hh=int(w*im.height/im.width) if im.height/im.width<1.25 else int(w*1.25); im=ImageOps.fit(im,(w,hh),Image.LANCZOS); b=int(w*0.045)
    P=Image.new("RGB",(w+2*b,hh+b+int(w*0.14)),(250,250,247)); P.paste(im,(b,b))
    pad=70; C=Image.new("RGBA",(P.width+2*pad,P.height+2*pad),(0,0,0,0)); sh=Image.new("RGBA",C.size,(0,0,0,0))
    ImageDraw.Draw(sh).rectangle([pad+10,pad+22,pad+P.width+10,pad+P.height+22],fill=(0,0,0,150)); C.alpha_composite(sh.filter(ImageFilter.GaussianBlur(20)))
    C.paste(P,(pad,pad)); return pil2spr(C.rotate(rot,Image.BICUBIC,expand=True))
class KB:
    """Ken Burns over an image (cover fit) with vignette; blur=True → blurred dark backdrop version"""
    def __init__(s,path,z=(1.0,1.18),fx=(0.5,0.5),fy=(0.5,0.45),dur=3,blur=0,dark=1.0):
        im=np.asarray(Image.open(path).convert("RGB")).astype(np.float32)/255
        if blur: im=cv2.GaussianBlur(im,(0,0),blur)
        s.im=im*dark; s.z,s.fx,s.fy,s.d=z,fx,fy,dur
        yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-W/2)/W)**2+((yy-H/2)/H)**2); s.vig=(1-0.55*np.clip(r-0.25,0,1)**1.2)[...,None].astype(np.float32)
    def __call__(s,u,t):
        h,w=s.im.shape[:2]; base=max(W/w,H/h); e=e_sine(t/s.d); z=base*lerp(s.z[0],s.z[1],e)
        cx=min(max(lerp(*s.fx,e)*w,W/2/z),w-W/2/z); cy=min(max(lerp(*s.fy,e)*h,H/2/z),h-H/2/z)
        M=np.float32([[z,0,W/2-cx*z],[0,z,H/2-cy*z]]); fr=cv2.warpAffine(s.im,M,(W,H),flags=cv2.INTER_AREA if z<1 else cv2.INTER_CUBIC,borderMode=cv2.BORDER_REFLECT)
        return (np.clip(fr*s.vig,0,1)*255).astype(np.uint8),(0.0,0.0)
def title(sc,t,col=OR,y=330,at=0.0,size=96,fx="glow"): return K(sc,t,"key",col,540,y,at,fx=fx,size=size)
def xstamp(sc,x,y,at,size=150):
    m=Image.new("RGBA",(size+60,size+60),(0,0,0,0)); d=ImageDraw.Draw(m); o=30
    d.line([(o,o),(o+size,o+size)],fill=(235,40,40,255),width=size//6); d.line([(o+size,o),(o,o+size)],fill=(235,40,40,255),width=size//6)
    g=Image.new("RGBA",m.size,(0,0,0,0)); g.alpha_composite(m.filter(ImageFilter.GaussianBlur(10))); g.alpha_composite(m)
    sc.add(Item(pil2spr(g),x,y,at,"snap")); sc.ev(at,"boom",0.8)
def earth_intro(name,to,R1=5200,start=(20,25),zoom_at=0.45):
    d=dur_of(name)
    def gp(t):
        u=e_expo_io((t-d*zoom_at)/max(0.5,d*(1-zoom_at)-0.1)); return lerp(start[0]+6*t,to[0],u),lerp(start[1],to[1],u),log_lerp(440,R1,u),0,0,900
    sc=new(name,SatCam(gp,"globe"),"map",credit=CR_SAT); sc.ev(0,"whoosh",1.0)
    sc.post.append(lambda fr,t:radial_blur(fr,0.25*e_expo_v((t-d*zoom_at)/max(0.5,d*(1-zoom_at)-0.1)),540,900)); return sc
def earth_outro(name,frm,title1="Lịch sử thế giới",title2="qua bản đồ",brand="HINTON MEDIA"):
    d=dur_of(name)
    def op(t): u=e_out(t/1.0); return frm[0]-22*t/d,lerp(frm[1],22,u),log_lerp(9000,470,u),0,0,1260
    sc=new(name,SatCam(op,"globe"),"end",credit=CR_SAT); sc.zblur=True; sc.ev(0,"whoosh",1.0)
    K(sc,title1,"title",WH,540,370,0.15,size=84); K(sc,title2,"title",OR,540,470,0.35,fx="glow",size=84)
    sc.add(Item(txt(brand,"key",OR,fx="glow",size=96),540,640,0.6,"bounce")); sc.ev(0.6,"boom",0.7)
    sc.add(Item(pill_spr("+  THEO DÕI",54,OR,DK),540,790,0.9,"bounce",pulse=0.05)); sc.ev(0.9,"pop",0.8)
    return sc
