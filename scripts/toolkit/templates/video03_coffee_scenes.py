# VIDEO 03 — Cà phê: bán nhiều hơn, thu ít hơn. Text follows text_plan.md / style_guide §9 (textkit presets).
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
BMT=(108.05,12.69); CL=(106.80,10.765); HH=(9.95,53.53)
VEQ=vec_equi(("Vietnam",))
# ===================== 1 FLY (SUB) =====================
def p_fly(t):
    c=e_out((t-0.3)/3.2); lon=lerp(100,BMT[0],c); lat=lerp(5,BMT[1],c)
    R=lerp(330,360,t/0.4) if t<0.4 else log_lerp(360,60000,e_io((t-0.4)/3.57))
    return lon,lat,R,-8*e_sine(t/4),0.55*e_io((t-2.5)/1.47)
bg=SatCam(p_fly); sc=new("fly",bg,"map",credit=CR_SAT); sc.ev(0.0,"whoosh",0.8); sc.ev(1.2,"whoosh",1.0); sc.ev(2.8,"whoosh",0.7)
sat_hsts(sc,bg,0.0,2.4)
# ===================== 2 HOOK =====================
T=TL["hook"]; dur=(T[1]-T[0])/FPS
def p_hook(t): u=e_sine(t/dur); return BMT[0]+0.01*u,BMT[1]-0.006*u,log_lerp(60000,150000,u),-8+6*u,0.55
bg=SatCam(p_hook,dim=lambda t:1-0.5*e_out(t/0.35)); sc=new("hook",bg,"map",credit=CR_SAT)
K(sc,"9 tháng đầu năm 2026","cap",OR,540,310,sc.w("chín"))
K(sc,"Lượng xuất khẩu","cap",WH,540,400,sc.w("1,4"))
KC(sc,"hero",WH,540,535,sc.w("1,4"),1.4,dec=1,dur=0.6)
K(sc,"triệu tấn","label",WH,540,660,sc.w("triệu"))
K(sc,"+15,4%","key",OR,540,790,sc.w("tăng")); sc.hit(sc.w("tăng")+0.05,False)
sc.add(Item(Spr(np.dstack([np.full((3,600,3),255,np.uint8),np.full((3,600,1),110,np.uint8)])),540,878,sc.w("nhưng"),"fade"))
K(sc,"Tiền thu về","cap",WH,540,950,sc.w("tiền"))
K(sc,"−7,3%","key",RD,540,1080,sc.w("giảm")); sc.hit(sc.w("giảm")+0.05)
K(sc,"còn 6,54 tỷ USD","label",WH,540,1215,sc.w("chỉ"))
src(sc,"Nguồn: Bộ Nông nghiệp & Môi trường · 10/2026",540,1290,sc.w("6,54")+0.4)
# ===================== 3 FLIP: Vietnam map =====================
T=TL["flip"]; dur=(T[1]-T[0])/FPS
bg=VecBg(lambda t:(108.0,15.6,44*(1+0.06*e_sine(t/dur)),0,880),0.9); sc=new("flip",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.8)
sc.add(CountryFX(bg,["Vietnam"],stroke=(0.05,1.0),fill=(0.9,1.3),alpha=0.75,pulse=0.15,nstroke=3))
hsts(sc,bg,0.6)
scrim(sc,230,440,0.5)
K(sc,"Bán nhiều hơn","title",WH,465,290,sc.w("bán")); cutout(sc,"arr_up_or",880,290,sc.w("bán")+0.1,60,90,kind="up",glow=False,mot=None)
K(sc,"Thu ít hơn","title",RD,465,395,sc.w("thu")); cutout(sc,"arr_dn",880,395,sc.w("thu")+0.1,60,90,kind="drop",glow=False,mot=None); sc.hit(sc.w("ít")+0.05,False)
sc.add(GlowPin(bg,*BMT,sc.w("mỗi"),OR,14))
kcall(sc,bg,*BMT,sc.w("mỗi")+0.1,230,-420,[("Giá mỗi tấn","cap",GREY,sc.w("tấn")),(dict(v1=4537,dur=0.8,q=100),"key",OR,sc.w("4.537"),96),("USD","cap",WH,sc.w("4.537")+0.3),
   ("−19,7%","label",RD,sc.w("thấp")),("so với 9T/2025 · Bộ NN&MT","src",SRC_W,sc.w("so"),20)],w=340)
# ===================== 4 RANK (SUB): red-soil highlands =====================
T=TL["rank"]; dur=(T[1]-T[0])/FPS
def p_rank(t): u=e_sine(t/dur); return 108.0+0.08*u,12.85-0.05*u,log_lerp(62000,80000,u),25-10*u,0.5
bg=SatCam(p_rank); sc=new("rank",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.6)
# ===================== 5 QUESTION CARD =====================
bg=drift(dark_bg(5),z=(1.0,1.05)); sc=new("question",bg,"kinetic"); sc.zblur=True; sc.ev(0,"whoosh",0.9)
sc.add(BottomGlobe(VEQ,2140,900,-35,5,10,0.0,0.6))
qcard(sc,[("Vì sao",sc.w("tại")),("bán nhiều hơn",sc.w("bán")),("mà thu ít hơn?",sc.w("thu")),("ai hưởng",sc.w("ai")),("phần còn lại?",sc.w("còn"))],cy=760,size=88,alt=(WH,OR))
sc.hit(sc.w("ít")+0.05,False)
# ===================== 6 BACK (SUB): globe rewinds =====================
def p_back(t): u=e_io(t/3.5); return 106-120*u,12+6*u,lerp(470,440,u),18*u,0,820
bg=SatCam(p_back,"globe"); sc=new("back",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.9); sc.ev(1.2,"whoosh",0.6)
sat_hsts(sc,bg,0.0,3.6)
# ===================== 7 RECORD: bars over dark map =====================
T=TL["record"]; dur=(T[1]-T[0])/FPS
bg=VecBg(lambda t:(2,28,6.0*(1+0.06*e_sine(t/dur)),0,900),0.42); sc=new("record",bg,"chart",credit=CR_NE); sc.ev(0,"whoosh",0.7)
K(sc,"2025: thế giới thiếu cà phê","cap",OR,540,300,sc.w("thiếu"))
K(sc,"Giá xuất khẩu bình quân","cap",WH,540,390,sc.w("giá"))
KC(sc,"key",OR,540,500,sc.w("5.604"),5604,dur=0.8,q=100)
K(sc,"USD/tấn","cap",WH,540,595,sc.w("5.604")+0.35)
BX=[260,540,820]; BASE=1250; VAL=[5.62,8.92,6.54]; SCL=42; LAB=["2024","2025","9T/2026"]
TB=[0.5,sc.w("8,92"),sc.w("nhất")+0.3]; COL=[(196,150,90),OR,(140,150,158)]
K(sc,"Kim ngạch · tỷ USD","cap",GREY,80,700,0.5,align="l")
for i in range(3):
    b=Bar3D(lambda t,i=i:(BX[i],BASE),TB[i],VAL[i]*SCL,0.7,150,COL[i]); sc.add(b); sc.ev(TB[i],"swish",0.5)
    top=BASE-VAL[i]*SCL-48
    if i==1: KC(sc,"key",OR,BX[i]+20,top-30,TB[i],8.92,dec=2,dur=0.7)
    else: K(sc,vn(VAL[i],2),"label",WH if i==0 else GREY,BX[i]+20,top,TB[i]+0.2)
    K(sc,LAB[i],"axis",GREY,BX[i],BASE+40,TB[i],sfx=None)
stamp(sc,"KỶ LỤC",540,1070,sc.w("cao"),44,WH,-8); sc.hit(sc.w("cao")+0.05,False)
src(sc,"Hải quan Việt Nam · Bộ NN&MT",540,BASE+95,0.8)
# ===================== 8 GLOBE (SUB): Vietnam -> Brazil =====================
def p_globe(t): u=e_io(t/5.6); return lerp(106,-50,u),lerp(12,-12,u),470,0,0,820
bg=SatCam(p_globe,"globe"); sc=new("globe",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.7); sc.ev(2.4,"whoosh",0.6)
sat_hsts(sc,bg,0.0,5.7)
# ===================== 9 BRAZIL =====================
T=TL["brazil"]; dur=(T[1]-T[0])/FPS
def p_br(t): e=e_io(t/1.4); return lerp(-40,-49,e),lerp(-2,-15,e),log_lerp(4.5,12.5,e)*(1+0.05*e_sine((t-1.4)/(dur-1.4))),0,760
bg=VecBg(p_br,0.92); sc=new("brazil",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.9)
sc.add(CountryFX(bg,["Brazil"],stroke=(0.3,1.4),fill=(1.2,1.7),alpha=0.8,pulse=0.15,nstroke=3))
scrim(sc,230,430,0.45)
K(sc,"Lý do 1","cap",OR,540,290,0.13)
K(sc,"Brazil được mùa","title",WH,540,375,sc.w("brazil"))
K(sc,"#1 thế giới","label",WH,470,640,sc.w("số"))
MG_=(-44.5,-18.6); ES_=(-40.6,-19.6)
sc.add(GlowPin(bg,*MG_,sc.w("vụ"),WH,12)); sc.add(GlowPin(bg,*ES_,sc.w("vụ")+0.2,WH,12))
stamp(sc,"VỤ MÙA KỶ LỤC",700,520,sc.w("lịch"),44,OR,-8); sc.hit(sc.w("lịch")+0.05,False)
kcall(sc,bg,*MG_,sc.w("dự")-0.4,-330,330,[("Dự báo vụ 2026/27","cap",GREY,sc.w("dự")),(dict(v1=71.9,dec=1,dur=0.8),"key",OR,sc.w("71,9")),("triệu bao 60 kg","cap",WH,sc.w("triệu")),("+14%","label",OR,sc.w("14%")),("USDA · 7/2026","src",SRC_W,sc.w("14%")+0.3)],w=420)
# ===================== 10 BARS: Brazil vs Vietnam =====================
bg=VecBg(lambda t:(28,2,3.6*(1+0.04*e_sine(t/3.2)),0,880),0.9); sc=new("bars",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Brazil"],fill=(0,0.3),alpha=0.85,glow=0.4)); sc.add(CountryFX(bg,["Vietnam"],fill=(0.15,0.45),alpha=0.9,glow=0.4))
BRA=(-50,-11); VNM=(104.0,20.5)
for i,(anc,v,nm,at) in enumerate([(BRA,71.9,"Brazil",0.15),(VNM,32.5,"Việt Nam",0.35)]):
    b=Bar3D(lambda t,anc=anc,bg=bg:tuple(P1(bg,*anc)),at,v*5.4,0.7,64,OR); sc.add(b); sc.ev(at,"swish",0.5)
    P=P1(bg.at(1.0),*anc)
    K(sc,vn(v,1),"label",WH,P[0]+10,P[1]-v*5.4-60,at+0.25)
    K(sc,nm,"map",WH,P[0]-(175 if i else 0),P[1]+(10 if i else 44),at+0.1,sfx=None)
hsts(sc,bg,0.1,18,True)
K(sc,"Sản lượng 2026/27 · triệu bao","cap",GREY,540,300,0.1)
K(sc,"Gấp 2,2 lần","title",OR,540,1230,sc.w("gấp")); sc.hit(sc.w("gấp")+0.05,False)
src(sc,"USDA · 7/2026",540,1310,sc.w("gấp")+0.3)
# ===================== 11 SHIPS (SUB): routes out of Brazil =====================
bg=VecBg(lambda t:(28,2,3.6*(1.04+0.03*e_sine(t/2.8)),0,880),0.75); sc=new("ships",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.6)
sc.add(CountryFX(bg,["Brazil"],fill=(0,0.01),alpha=0.85,glow=0.4)); hsts(sc,bg,0.0,18,True)
SANTOS=(-46.3,-23.9)
for i,(dst,bend) in enumerate([((10,53.5),-0.25),((4.4,51.2),-0.2),((-74,40.7),0.2),((8.9,44.4),-0.15),((139.7,35.7),-0.35),((121.5,31.2),-0.3),((3,36.7),-0.1),((-81,32),0.25)]):
    sc.add(Route(bg,SANTOS,dst,0.05+i*0.12,0.9,bend,OR,4)); sc.ev(0.05+i*0.12,"swish",0.3)
sc.add(GlowPin(bg,*SANTOS,0.0,OR,12))
# ===================== 12 FARM (SUB): close satellite of coffee farms =====================
T=TL["farm"]; dur=(T[1]-T[0])/FPS
def p_farm(t): u=e_sine(t/dur); return BMT[0]-0.01+0.02*u,BMT[1]+0.01-0.01*u,log_lerp(330000,430000,u),32-12*u,0.6
bg=SatCam(p_farm); sc=new("farm",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.7)
# ===================== 13 PRICE: collage =====================
bg=drift(paper_bg("grey",21)); sc=new("price",bg,"collage")
K(sc,"Giá cà phê nhân · Tây Nguyên","cap",MG,540,300,sc.w("giá"),shadow=False)
cutout(sc,"sack",820,560,0.15,300,330,kind="drop",gsize=440); cutout(sc,"beans",815,890,0.35,330,200,kind="drop",glow=False)
t1=sc.w("135.000"); t2=sc.w("93.000"); t3=sc.w("mất")
sc.add(Item(cut_spr("tag",600,220),400,540,t1-0.1,"right",(0.5,2,3.5,0))); sc.ev(t1-0.1,"swish",0.5)
K(sc,"5/3/2025 · đỉnh","cap",MG,420,470,sc.w("tháng 3 năm 2025"),shadow=False)
K(sc,"135.000","key",DK,420,560,t1,shadow=False)
K(sc,"VNĐ/kg","cap",MG,420,632,t1+0.3,shadow=False)
sc.add(Strike(220,640,560,sc.w("đầu"),0.3,RD,14),"swish",sc.w("đầu"),0.6)
sc.add(Item(cut_spr("tag",600,220),400,880,sc.w("đầu")+0.1,"right",(0.5,2,3.5,1))); sc.ev(sc.w("đầu")+0.1,"swish",0.5)
K(sc,"Đầu tháng 10/2026","cap",MG,420,810,sc.w("tháng 10"),shadow=False)
KC(sc,"key",RD,420,900,t2,93000,dur=0.7,q=1000,v0=135000,shadow=False)
K(sc,"VNĐ/kg","cap",MG,420,972,t2+0.3,shadow=False)
cutout(sc,"arr_dn",820,1170,t3,120,180,kind="drop",glow=False)
K(sc,"−31%","hero",RD,420,1150,t3,shadow=False); sc.hit(t3+0.05)
K(sc,"gần 1/3","label",DK,420,1285,sc.w("phần"),shadow=False)
src(sc,"Giá thu mua · Dân Việt 6/3/2025 · giacaphe.com 8/10/2026",540,1372,t3+0.4,dark=False)
# ===================== 14 PORT (SUB): Cát Lái =====================
T=TL["port"]; dur=(T[1]-T[0])/FPS
def p_port(t): u=e_sine(t/dur); return CL[0]-0.005+0.01*u,CL[1]+0.004-0.004*u,log_lerp(240000,320000,u),-22+10*u,0.55
bg=SatCam(p_port,"hcm"); sc=new("port",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.7)
# ===================== 15 MARKETS: routes + ranked list =====================
T=TL["markets"]; dur=(T[1]-T[0])/FPS
bg=VecBg(lambda t:(60,30,5.6*(1+0.05*e_sine(t/dur)),0,1110),0.85); sc=new("markets",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.8)
scrim(sc,200,880,0.6,180)
sc.add(CountryFX(bg,["Vietnam"],fill=(0,0.3),alpha=0.9,glow=0.4)); hsts(sc,bg,0.1,18,True)
VNP=(106.7,10.8); sc.add(GlowPin(bg,*VNP,0.1,OR,11))
mk=[("Đức 13,7%","Germany",(10,53.5),sc.w("đức"),-0.25),("Ý 7,8%","Italy",(12.5,42),sc.w("ý"),-0.2),("Tây Ban Nha 7,1%","Spain",(-3.7,40.4),sc.w("tây"),-0.18),
    ("Nhật Bản 6,9%","Japan",(139.7,35.7),sc.w("nhật"),0.25),("Mỹ 5,7%","United States of America",(240,38),sc.w("mỹ"),0.2)]
for i,(lab,cn,dst,at,bend) in enumerate(mk):
    sc.add(Route(bg,VNP,dst,at-0.1,0.7,bend,OR if i==0 else (236,200,140),5 if i==0 else 4)); sc.ev(at-0.1,"swish",0.4)
    if cn!="United States of America": sc.add(CountryFX(bg,[cn],fill=(at+0.5,at+0.8),alpha=0.85 if i==0 else 0.55,glow=0.3))
listing(sc,"Ai mua cà phê Việt?",[(m[0],m[3]) for m in mk],90,300,0.13,step=100,isize=62)
K(sc,"% kim ngạch năm 2025","cap",GREY,90,388,sc.w("2025")+0.2,align="l")
src(sc,"Hải quan Việt Nam · 2025",540,1385,sc.w("mỹ")+0.4)
# ===================== 16 HAMBURG (SUB): fly into the port =====================
def p_hh(t):
    e=e_out(t/3.0); return lerp(10.6,HH[0],e),lerp(51.8,HH[1],e),log_lerp(2600,260000,e_io(t/3.9)),-6*e_sine(t/3.9),0.5*e_io((t-1.8)/2.0)
bg=SatCam(p_hh,"hh"); sc=new("hamburg",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.8); sc.ev(1.6,"whoosh",0.8)
# ===================== 17 STONEX: document card =====================
bg=drift(paper_bg("grey",22)); sc=new("stonex",bg,"document"); sc.post.append(edge_blur(0.8,(540,620)))
body=("In 2024, Germany imported over 1.1 million metric tons of green coffee. This reflected its ongoing role as a global processing and re-export hub, "
      "channeling large volumes of raw beans into Europe's coffee-consuming markets. […] In 2024, Germany re-exported over 250,000 metric tons of roasted coffee, "
      "highlighting its role as a value-adding transformation hub within Europe.")
DocCard(sc,"COFFEENETWORK · STONEX","Germany's Green Coffee Imports in 2024–2025 and How the EUDR Will Reshape the Market (21/1/2026)",body,
  [("imported over 1.1 million metric tons of green coffee.",sc.w("nhập"),0.8),("re-exported over 250,000 metric tons of roasted coffee,",sc.w("bán"),0.9)],
  0.05,y=600,size=34,w=960,src_line="Trích nguyên văn · StoneX CoffeeNetwork, 21/1/2026",logo=("StoneX",(18,56,104)),kind="up",rot=(-1.0,0.4))
sc.add(Item(card_spr(940,300,accent=True,r=26),540,1185,sc.w("nhập")-0.1,"up",None)); sc.ev(sc.w("nhập")-0.1,"swish",0.5)
K(sc,"Nhập","cap",MG,220,1095,sc.w("nhập"),shadow=False); K(sc,"1,1","key",DK,220,1190,sc.w("1,1"),shadow=False); K(sc,"triệu tấn nhân","cap",DK,220,1280,sc.w("triệu"),shadow=False)
sc.add(Route(None,(330,1200),(550,1200),sc.w("rang"),0.6,0.0,OR,6,flow=False)); sc.ev(sc.w("rang"),"swish",0.5)
K(sc,"rang · đóng gói","cap",OR,440,1150,sc.w("đóng"),shadow=False,size=26)
K(sc,"Bán lại","cap",MG,770,1095,sc.w("bán"),shadow=False); K(sc,"250.000","key",OR,780,1190,sc.w("250.000"),shadow=False,size=70); K(sc,"tấn đã rang","cap",DK,770,1280,sc.w("250.000")+0.3,shadow=False)
sc.hit(sc.w("250.000")+0.05,False)
# ===================== 18 RAWSAT (SUB) =====================
T=TL["rawsat"]; dur=(T[1]-T[0])/FPS
def p_rs(t): u=e_sine(t/dur); return 107.95+0.03*u,12.95-0.02*u,log_lerp(120000,150000,u),48-8*u,0.45
bg=SatCam(p_rs); sc=new("rawsat",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.6)
# ===================== 19 RAW: processed share =====================
bg=drift(paper_bg("grey",23)); sc=new("raw",bg,"collage")
K(sc,"Năm 2025","cap",MG,540,290,0.13,shadow=False)
K(sc,"Cà phê chế biến","title",DK,540,380,sc.w("rang"),shadow=False)
cutout(sc,"sack",300,640,0.2,280,300,kind="drop",gsize=380); K(sc,"Hạt thô","cap",MG,300,835,0.5,shadow=False)
cutout(sc,"pouch",780,640,sc.w("rang"),220,300,kind="drop",gsize=380); K(sc,"Rang xay, hòa tan","cap",OR,780,835,sc.w("hòa"),shadow=False)
def bar_row(y,frac,at,col):
    def f(fr,t,cam):
        fr[int(y-16):int(y+16),90:910]=fr[int(y-16):int(y+16),90:910]*0.8+0.2*np.float32((150,150,156))/255
        if t<at: return
        p=e_out((t-at)/0.7); fr[int(y-16):int(y+16),90:int(90+820*frac*p)]=np.float32(col)/255
    sc.add(Fn(f))
K(sc,"Khối lượng","cap",MG,90,950,sc.w("chiếm"),align="l",shadow=False); K(sc,"9%","key",DK,910,940,sc.w("9%"),align="r",shadow=False); bar_row(1030,0.09,sc.w("9%"),DK)
K(sc,"Giá trị","cap",MG,90,1135,sc.w("mang"),align="l",shadow=False); K(sc,"15,9%","key",OR,910,1125,sc.w("16%"),align="r",shadow=False); bar_row(1215,0.159,sc.w("16%"),OR)
sc.hit(sc.w("16%")+0.05,False)
src(sc,"Hải quan Việt Nam · tổng hợp: Nhà Bè Agri",540,1300,sc.w("16%")+0.4,dark=False)
# ===================== 20 SUMMARY: list over dark world map =====================
T=TL["summary"]; dur=(T[1]-T[0])/FPS
bg=VecBg(lambda t:(-38+4*e_sine(t/dur),8,4.2,0,880),0.36); sc=new("summary",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Brazil"],fill=(sc.w("brazil"),sc.w("brazil")+0.4),alpha=0.5,glow=0.3))
listing(sc,"Vì sao thu ít hơn?",[("Brazil được mùa kỷ lục",sc.w("brazil")),("Giá thế giới đi xuống",sc.w("giá")),("Vẫn bán chủ yếu hạt thô",sc.w("mình"))],90,320,0.13,step=118)
K(sc,"Bán nhiều hơn","title",WH,540,1060,sc.w("bán")); K(sc,"không giữ được giá","title",RD,540,1170,sc.w("không"),size=74); sc.hit(sc.w("không")+0.05)
# ===================== 21 ZOOMOUT (SUB) =====================
def p_zo(t):
    if t<4.0: u=e_io(t/4.0); return lerp(BMT[0],108,u),lerp(BMT[1],14,u),log_lerp(300000,470,u),-10*(1-u),0.5*(1-e_out(t/1.4)),820
    return 108-4*(t-4.0),14,470,0,0,820
bg=SatCam(p_zo); sc=new("zoomout",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.9); sc.ev(2.4,"whoosh",0.6)
sat_hsts(sc,bg,1.8,5.3)
# ===================== 22 OPEN QUESTION =====================
bg=drift(dark_bg(6),z=(1.0,1.05)); sc=new("openq",bg,"kinetic"); sc.zblur=True; sc.ev(0,"whoosh",0.9)
qcard(sc,[("Nếu là bạn:",sc.w("nếu")),("bán nhiều hạt thô",sc.w("bán")),("hay bán ít hơn",sc.w("hay")),("có thương hiệu?",sc.w("thương"))],cy=600,size=86)
cutout(sc,"sack",300,1130,sc.w("hạt"),260,280,kind="drop",gsize=380); cutout(sc,"pouch",780,1130,sc.w("thương"),210,290,kind="drop",gsize=380)
# ===================== 23 END =====================
sc=new("end",drift(dark_bg(7),z=(1.0,1.06)),"end",brand=False); sc.zblur=True; sc.ev(0,"whoosh",0.8)
sc.add(BottomGlobe(VEQ,2120,900,100,5,14,0.0,0.8))
sc.add(Item(glow_spr(900,OR,60),540,560,0.0,"pop",(0,10,4,0)))
sc.add(Strike(450,630,336,0.05,0.3,OR,12))
sc.add(Item(tsp("HINTON",160,WH),540,470,sc.w("hinton")-0.1,"bounce")); sc.ev(sc.w("hinton")-0.1,"pop",0.7)
sc.add(Item(tsp("MEDIA",160,OR),540,630,sc.w("media")-0.1,"bounce")); sc.ev(sc.w("media")-0.1,"pop",0.7)
sc.add(Item(pill_spr("+  THEO DÕI",52,OR,DK),540,841,sc.w("để")-0.25,"bounce",pulse=0.045)); sc.ev(sc.w("để")-0.25,"boom",0.6)
sc.add(Item(tsp("để hiểu kinh tế mỗi ngày",46,(176,176,180),"Bold"),540,975,sc.w("hiểu"),"bounce")); sc.ev(sc.w("hiểu"),"swish",0.4)
for t_,r_,b_ in [("HINTON","hero",(540-300,470-60,540+300,470+60)),("MEDIA","hero",(540-260,630-60,540+260,630+60)),("+ THEO DÕI","label",(380,800,700,880)),("để hiểu kinh tế mỗi ngày","item",(290,950,790,1000))]: log(sc,t_,r_,b_,0)
SCENES.sort(key=lambda s:s.f0)
for a,b in zip(SCENES,SCENES[1:]): assert a.f1==b.f0,(a.name,b.name,a.f1,b.f0)
assert SCENES[0].f0==0
