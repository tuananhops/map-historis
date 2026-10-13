from mlayers import *
TL={n:(a,b) for a,b,n in json.load(open("assets/timeline.json"))}
WORDS=json.load(open("assets/disp.json"))
def WT(word,after,n=1):
    k=0
    for w in WORDS:
        if w["w"]==word and w["t0"]>=after-0.05:
            k+=1
            if k==n: return w["t0"]
    raise KeyError(word)
SCENES=[]
def mk_credit(text):
    f=fnt(20,"Regular"); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=int(d.textlength(text,font=f))
    im=Image.new("RGBA",(tw+24,30),(0,0,0,0)); dd=ImageDraw.Draw(im); dd.rounded_rectangle([0,0,tw+23,29],8,fill=(0,0,0,120)); dd.text((12,15),text,font=f,fill=(235,235,235),anchor="lm")
    return pil2spr(im)
CR_SAT=mk_credit("Ảnh vệ tinh: NASA Blue Marble (PD) · Sentinel-2 cloudless 2016 © EOX (CC BY 4.0)")
CR_NE=mk_credit("Bản đồ: Natural Earth (phạm vi công cộng)")
def new(name,bg,kind,credit=None,brand=True):
    a,b=TL[name]; sc=Scene(name,a,b,bg,brand=brand,credit=credit); sc.kind=kind; SCENES.append(sc)
    sc.w=lambda word,n=1: WT(word,sc.t0g,n)-sc.t0g
    return sc
_par=[1]
def drift(src,**k):
    _par[0]*=-1; d=dict(zin=_par[0]>0,pan=(_par[0],0.45*-_par[0])); d.update(k); return DriftBg(src,**d)
def R(t,s,c,**k): d=dict(t=t,s=s,c=c); d.update(k); return d
MOT_CARD=(-0.9,3,3.6,0.0); MOT_TXT=(-0.4,0,3,0); MOT_CUT=(2.4,9,2.8,1.0); MOT_GLOW=(1.4,5,3.3,0.3)
def rows_block(sc,rows,y0,t_card=0.0,mot=MOT_CARD,x0=90,w=900,pad=46,card=True,shadow=0,cardkw=None,minat=0.12):
    cx=x0+w/2; y=y0+pad; laid=[]
    for r in rows:
        if "t" not in r: y+=r.get("gap",0); continue
        s=r["s"]; low=r.get("low",any(ch.islower() for ch in r["t"]))
        base=y+s*r.get("asc",0.93); laid.append((r,base,low)); y+=s*(r.get("asc",0.93)+(0.25 if low else 0.08))+s*0.12+r.get("after",0)
    h=int(y-y0+pad-laid[-1][0]["s"]*0.12)
    if card: sc.add(Item(card_spr(w,h,**(cardkw or {})),cx,y0+h/2,t_card,"pop",mot),"pop",t_card,0.6)
    out=[]
    for r,base,low in laid:
        s=r["s"]; at=max(r.get("at",t_card+0.15),t_card+(minat if card else 0)); kind=r.get("kind","pop"); wt=r.get("w","Bold")
        if "ctr" in r:
            c=r["ctr"]; L=Counter(cx,base,at,c.get("dur",0.7),c.get("v0",0),c["v1"],c.get("dec",0),s,r["c"],c.get("pre",""),c.get("suf",""),wt,kind,mot,shadow)
            cw=L.cw; parts=[L]; dd=c.get("dur",0.7); step=max(0.07,dd/12)
            for k in range(int(dd/step)): sc.ev(at+k*step,"tick",0.5)
            sc.ev(at,"pop",0.5)
        elif r.get("words"):
            words=r["t"].split(); f=fnt(s,wt); sp=f.getlength(" "); sps=[tsp(x,s,r["c"],wt,shadow) for x in words]
            ws=[f.getlength(x) for x in words]; cw=sum(ws)+sp*(len(words)-1); xl=cx-cw/2; parts=[]
            times=list(r["words"]) if isinstance(r["words"],list) else [at+i*0.11 for i in range(len(words))]
            while len(times)<len(words): times.append(times[-1]+0.1)
            for i,(spr,wd) in enumerate(zip(sps,ws)):
                ti=max(times[i],t_card+(minat if card else 0)); x,yy=at_base(spr,xl+wd/2,base); parts.append(Item(spr,x,yy,ti,kind,mot)); sc.ev(ti,"pop",0.35); xl+=wd+sp
        else:
            spr=tsp(r["t"],s,r["c"],wt,shadow); x,yy=at_base(spr,cx,base); cw=spr.cw; parts=[Item(spr,x,yy,at,kind,mot,pulse=r.get("pulse",0))]
            sc.ev(at,"swish" if kind in("up","right","left","drop") else "pop",0.45)
        rect=(cx-cw/2-18,base-s*0.86,cx+cw/2+18,base+s*(0.27 if low else 0.13))
        if "hl" in r: sc.add(Highlight(rect,r["hl"],0.35,r.get("hlc",YEL),mot=mot),"swish",r["hl"],0.35)
        for p in parts: sc.add(p)
        if "strike" in r: sc.add(Strike(rect[0]+10,rect[2]-10,base-s*0.36,r["strike"],0.25,RD,max(8,s//9),mot),"swish",r["strike"],0.5)
        out.append(dict(rect=rect,base=base,at=at))
    return out,h
def cutout(sc,name,x,y,at,maxw=380,maxh=380,kind="drop",glow=True,mot=MOT_CUT,gsize=None,rot=0.0,until=None,exit="fade"):
    if glow: sc.add(TItem(glow_spr(gsize or int(max(maxw,maxh)*1.45)),x,y,at-0.05,"pop",MOT_GLOW,until=until or 1e9,exit="fade"))
    it=TItem(cut_spr(name,maxw,maxh),x,y,at,kind,mot,rot=rot,until=until or 1e9,exit=exit); sc.add(it,"swish" if kind!="pop" else "pop",at,0.6)
    if until: sc.ev(until,"swish",0.5)
    return it
def pill(sc,text,y,at,size=36,fill=OR,fg=DK,kind="pop",mot=MOT_TXT,x=540,pulse=0,rot=0.0):
    sc.add(Item(pill_spr(text,size,fill,fg),x,y,at,kind,mot,rot=rot,pulse=pulse),"pop",at,0.6)
def snapbox(sc,rect,at,color=OR,width=6):
    x0,y0,x1,y1=rect; sc.add(Item(box_spr(int(x1-x0),int(y1-y0),color,width),(x0+x1)/2,(y0+y1)/2,at,"snap"),"pop",at,0.5)
def stamp(sc,text,x,y,at,size=64,color=RD,rot=-10):
    f=fnt(size); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=d.textlength(text,font=f); w,h=int(tw+60),int(size*1.5)
    im=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); dd=ImageDraw.Draw(im); dd.rounded_rectangle([10,10,10+w,10+h],14,outline=color+(235,),width=8)
    dd.text((10+w/2,10+h/2),text,font=f,fill=color+(235,),anchor="mm"); sc.add(Item(pil2spr(im),x,y,at,"snap",MOT_TXT,rot=rot),"boom",at,0.5)
def hsts(sc,bg,at=0.0,size=24,dy=(-34,40)):
    sc.add(Fn(lambda fr,t,cam: hs_ts(fr,bg.cam,t,at)))
    for txt,a,d in [("QĐ. Hoàng Sa (Việt Nam)",(112.0,16.4),dy[0]),("QĐ. Trường Sa (Việt Nam)",(113.8,9.9),dy[1])]:
        spr=text_spr(txt,size,(225,236,238),"SemiBold",3)
        sc.add(Item(spr,0,0,at+0.1,"fade",posfn=(lambda a=a,d=d:(lambda t:tuple(P1(bg,*a)+np.array([0,d]))))()))
def map_label(sc,bg,text,lon,lat,at,size=30,color=WH,dx=0,dy=0,kind="pop"):
    spr=text_spr(text,size,color); sc.add(Item(spr,0,0,at,kind,posfn=lambda t:tuple(P1(bg,lon,lat)+np.array([dx,dy])))); sc.ev(at,"pop",0.35)
def dark_bg(seed=3):
    yy,xx=np.mgrid[0:SH,0:SW]; r=np.sqrt(((xx-SW/2)/SW)**2+((yy-SH*0.4)/SH)**2)
    base=np.stack([14+0*r,32+0*r,46+0*r],-1)*(1-0.6*np.clip(r/0.8,0,1))[...,None]+np.random.default_rng(seed).normal(0,1.6,(SH,SW,1))
    return np.clip(base,0,255).astype(np.uint8)
def log_lerp(a,b,u): return math.exp(lerp(math.log(a),math.log(b),u))
def sat_hsts(sc,bg,t0,t1):
    """HS/TS (Vietnam) dots + labels on satellite globe whenever that hemisphere faces camera and globe is small enough to show them"""
    def lay(fr,t,cam):
        if not(t0<=t<=t1): return
        st=bg.state; 
        if st[2]>2500: return
        a=cl((t-t0)/0.3)*cl((t1-t)/0.3)
        P=bg.proj(np.array([p[0] for p in HS+TS]),np.array([p[1] for p in HS+TS])); vis=bg.vis
        m=np.zeros((H,W),np.uint8)
        for q,v in zip(P,vis):
            if v: cv2.circle(m,(int(q[0]*16),int(q[1]*16)),int(max(2,st[2]/260)*16),255,-1,cv2.LINE_AA,4)
        blend_mask(fr,m,(0.97,0.95,0.85),a)
    sc.add(Fn(lay))
    for txt,anc,d in [("Hoàng Sa (VN)",(112.0,16.4),-22),("Trường Sa (VN)",(113.8,9.9),24)]:
        spr=text_spr(txt,20,(240,240,236),"SemiBold",3)
        def pf(t,anc=anc,d=d):
            if not(t0<=t<=t1) or bg.state[2]>2500: return (-900,-900)
            P=bg.proj(*anc)[0]; return (P[0],P[1]+d) if bg.vis[0] else (-900,-900)
        sc.add(Item(spr,0,0,t0,"fade",posfn=pf))
TOK=(139.767,35.681); BOJ=(139.7714,35.6866)
VEQ=vec_equi(("Japan",))
# ===================== 0 FLY: space -> Tokyo satellite =====================
def p_fly(t):
    c=e_out((t-0.5)/2.9); lon=lerp(112,TOK[0],c); lat=lerp(24,TOK[1],c)
    if t<0.7: R=lerp(330,380,t/0.7)
    elif t<5.4: R=log_lerp(380,300000,e_io((t-0.7)/4.7))
    else: R=log_lerp(300000,420000,e_sine((t-5.4)/2.0))
    return lon,lat,R,-11*e_sine((t-2.5)/4.9),0.85*e_io((t-3.7)/2.4)
bg=SatCam(p_fly); sc=new("fly",bg,"map",credit=CR_SAT); sc.ev(0.0,"whoosh",0.8); sc.ev(1.0,"whoosh",1.0); sc.ev(3.6,"whoosh",0.7)
sat_hsts(sc,bg,0.0,1.6)
pill(sc,"NHẬT BẢN · 2026",330,0.15,40,DK,OR)
cutout(sc,"baby",270,560,sc.w("bé"),300,300,kind="pop",gsize=480)
sc.add(Item(pill_spr("MỖI EM BÉ",34,WH,DK),270,760,sc.w("chào"),"up",MOT_TXT)); sc.ev(sc.w("chào"),"swish",0.5)
cutout(sc,"coin",820,600,sc.w("gánh"),230,230,kind="drop",gsize=360)
rows_block(sc,[R("GÁNH SẴN",40,(200,206,210),at=sc.w("gánh")),R("≈ 11 TRIỆU ¥",104,OR,ctr=dict(v1=11,suf=" TRIỆU ¥",pre="≈ ",dur=0.6),at=sc.w("11"),asc=0.82),
  R("≈ 1,8 tỷ đồng / người",52,WH,at=sc.w("1,8 tỷ đồng"),kind="up",hl=sc.w("1,8 tỷ đồng")+0.4,hlc=(255,150,120))],930,sc.w("gánh")-0.1,cardkw=dict(fill=(16,26,34),alpha=232,accent=True))
sc.hit(sc.w("11")+0.35)
sc.add(GlowPin(bg,*TOK,4.3,OR,16)); 
tk=text_spr("TOKYO",44,WH); sc.add(Item(tk,0,0,4.5,"pop",posfn=lambda t,bg=bg:tuple(bg.proj(*TOK)[0]+np.array([0,-70])))); sc.ev(4.5,"pop",0.6)
pill(sc,"CHƯA TỪNG VAY 1 ĐỒNG",820,sc.w("vay"),32,RD,WH,x=290)
# ===================== 1 EA: zoom-out reveal, Japan stroke + fill, callouts =====================
def p_ea(t):
    u=e_io(t/1.6); return lerp(TOK[0],124,u),lerp(TOK[1],30,u),log_lerp(260,24,u)*(1-0.06*e_sine((t-1.7)/2.7)),2*(1-u)
bg=VecBg(p_ea); sc=new("ea",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.9)
sc.add(CountryFX(bg,["Japan"],stroke=(0.5,1.6),fill=(1.4,1.9),pulse=0.25,nstroke=4))
sc.add(CountryFX(bg,["Vietnam"],fill=(1.0,1.5),alpha=0.35,color=(120,190,196),glow=0))
hsts(sc,bg,1.2,22)
map_label(sc,bg,"VIỆT NAM",105.5,17.5,1.3,26,(200,230,232),dx=-20)
map_label(sc,bg,"TRUNG QUỐC",108,33,1.5,30,(170,200,205)); map_label(sc,bg,"HÀN QUỐC",128,36.3,1.7,24,(170,200,205),dx=-40,dy=10)
callout(sc,bg,139.7,35.7,sc.w("122"),-120,420,[dict(t="DÂN SỐ NHẬT",s=28,c=(190,206,210)),dict(ctr=(100,122.65,2,"","",0.6),s=62,c=OR),dict(t="triệu người · 9/2026",s=26,c=WH,w="SemiBold")],w=380)
callout(sc,bg,130.6,32.8,sc.w("chia")+0.1,-250,-260,[dict(t="CHIA ĐỀU NỢ",s=28,c=(190,206,210)),dict(t="÷ MỖI NGƯỜI",s=46,c=WH)],w=330)
# ===================== 2 TOTAL =====================
bg=VecBg(lambda t:(137.6,37.6+0.3*e_sine(t/7.3),58*(1+0.12*e_sine(t/7.3)),-3+3*e_sine(t/7.3)),0.92); sc=new("total",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Japan"],fill=(0.0,0.3),alpha=0.9,pulse=0.18))
for i,(nm,lo,la) in enumerate([("",*TOK),("Osaka",135.5,34.69),("Nagoya",136.9,35.18),("Sapporo",141.35,43.06),("Fukuoka",130.4,33.59),("Sendai",140.87,38.27)]):
    sc.add(GlowPin(bg,lo,la,0.2+i*0.18 if i else 0.15,WH if i else RD,12 if i else 16,rings=i==0)); sc.ev(0.2+i*0.18,"pop",0.3)
pill(sc,"CUỐI THÁNG 6/2026",330,sc.w("tháng 6 năm 2026"),38,DK,OR)
callout(sc,bg,*TOK,sc.w("khoản")-0.2,-40,380,[dict(t="NỢ CỦA NHÀ NƯỚC NHẬT",s=30,c=(190,206,210)),dict(ctr=(0,1346,0,"","",1.0),s=96,c=OR,at=sc.w("1.346")),dict(t="NGHÌN TỶ YÊN",s=48,c=WH,at=sc.w("nghìn")),dict(t="Bộ Tài chính Nhật · 国債及び借入金",s=22,c=(170,186,190),w="Regular")],w=560)
sc.hit(sc.w("1.346")+1.0)
stamp(sc,"KỶ LỤC",800,780,sc.w("cao"),70)
# ===================== 3 LINE: debt/GDP over darkened map =====================
bg=VecBg(lambda t:(136,36.5,40*(1+0.10*e_sine(t/14.7)),0),0.42); sc=new("line",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Japan"],fill=(0,0.4),alpha=0.35,glow=0.3))
pill(sc,"NỢ CÔNG / GDP CỦA NHẬT",330,0.1,40,OR,DK)
yrs=[1980,1990,1995,2000,2005,2010,2015,2019,2020,2021,2022,2023,2024,2025]; vals=[41.4,54.8,80.7,118.5,153.4,178.6,200.1,206.3,228.8,222.7,227.8,220.3,214.5,206.5]
t0=sc.w("IMF"); t1=sc.w("206%")+0.2
LC=LineChart(sc,(170,470,930,1090),yrs,vals,(1980,2026),(0,250),t0,t1,OR,True,yticks=[0,50,100,150,200,250],xticks=[(1980,"1980"),(1990,"1990"),(2000,"2000"),(2010,"2010"),(2025,"2025")],head_fmt=lambda v:vn(v,0)+"%")
sc.add(Item(text_spr("Nguồn: IMF World Economic Outlook, 4/2026",24,(190,200,205),"Regular",2),540,1180,t0,"fade"))
sc.hit(t1)
sc.add(Item(pill_spr("206% GDP",56,OR,DK),330,430,t1+0.1,"popr",MOT_TXT)); sc.ev(t1+0.1,"pop",0.7)
t90=sc.w("1990"); x90,y90=LC.X(1990),LC.Y(54.8)
sc.add(Item(glow_spr(130,RD,230),x90,y90,t90,"pop")); sc.add(Item(text_spr("55%",50,(255,190,170)),x90,y90-60,t90+0.05,"popr")); sc.ev(t90,"pop",0.7)
def dash(fr,t,cam):
    if t<t90+0.5: return
    p=e_out((t-t90-0.5)/0.6); xe=x90+(LC.X(2025)-x90)*p; m=np.zeros((H,W),np.uint8)
    for x in np.arange(x90,xe,26): cv2.line(m,(int(x*16),int(y90*16)),(int(min(x+14,xe)*16),int(y90*16)),255,3,cv2.LINE_AA,4)
    blend_mask(fr,m,(1,0.75,0.68),0.9)
sc.add(Fn(dash))
tg=sc.w("gấp"); xa=LC.X(2025)+38
sc.add(Route(None,(xa,y90),(xa,LC.Y(206.5)+10),tg-0.3,0.6,0.0,RD,7,flow=False)); sc.ev(tg-0.3,"swish",0.6)
sc.add(Item(pill_spr("≈ ×3,8",54,RD,WH),xa-150,(y90+LC.Y(206.5))/2,sc.w("bốn"),"popr",MOT_TXT)); sc.ev(sc.w("bốn"),"pop",0.8); sc.hit(sc.w("bốn")+0.05,False)
sc.add(Item(text_spr("35 NĂM",40,WH),xa-150,(y90+LC.Y(206.5))/2-80,sc.w("35"),"pop",MOT_TXT)); sc.ev(sc.w("35"),"pop",0.5)
x20=LC.X(2020); sc.add(Item(text_spr("đỉnh 2020: 228,8%",26,(230,236,238),"SemiBold"),x20-40,LC.Y(228.8)-50,t1+0.6,"fade"))
# ===================== 4 CMP: 2x2 choropleth panels + 3D bars =====================
ANCH={"Greece":(22.0,39.4),"Italy":(12.9,42.6),"United States of America":(-98.0,38.6),"Japan":(138.6,36.4)}
class MapPanel:
    def __init__(s,sc,rect,lon,lat,k,country,name,val,at,tval,col):
        s.__dict__.update(locals()); del s.__dict__["s"]; x0,y0,x1,y1=rect; s.pw,s.ph=x1-x0,y1-y0
        s.frame=card_spr(s.pw,s.ph,fill=(16,28,38),alpha=255,r=10,accent=False,outline=(90,140,150),ow=2)
        s.lab=pill_spr(name,30,DK,OR)
    def cam(s,t): return Cam(s.lon,s.lat,s.k*(1+0.06*e_sine(t/10)),0,s.pw/2,s.ph/2)
    def base_pt(s,t):
        c=s.cam(t); P=c.proj(*ANCH[s.country])[0]; x0,y0,_,_=s.rect; dy=s.dy(t); return x0+P[0],y0+P[1]+dy
    def dy(s,t): return 900*(1-e_back((t-s.at)*FPS/14)) if t<s.at+1 else 0
    def draw(s,fr,t,cam):
        if t<s.at: return
        x0,y0,x1,y1=s.rect; dy=s.dy(t); c=s.cam(t)
        img,rs=draw_vecmap(s.pw,s.ph,c,0.95,True)
        if t>=s.tval:
            m=poly_mask(s.pw,s.ph,c,[r for r in rs if r[0]==s.country]); a=e_out((t-s.tval)/0.4)
            glow_mask(img,m,np.float32(s.col)/255,0.6*a,8); blend_mask(img,m,np.float32(s.col)/255,0.92*a)
        blit(fr,s.frame,(x0+x1)/2,(y0+y1)/2+dy)
        ya,yb=int(y0+dy),int(y1+dy); ca,cb=max(0,ya),min(H,yb)
        if cb>ca: fr[ca:cb,x0:x1]=img[ca-ya:cb-ya]
        m2=np.zeros((H,W),np.uint8); cv2.rectangle(m2,(x0,int(y0+dy)),(x1-1,int(y1+dy)),255,2); blend_mask(fr,m2,(0.45,0.65,0.7),1)
        blit(fr,s.lab,x0+s.lab.w/2-14,y1+dy-36)
bg=drift(dark_bg(4)); sc=new("cmp",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
data=[((40,350,520,760),23.6,38.8,62,"Greece","HY LẠP",145.7,"Hy",(240,192,120)),((560,350,1040,760),12.6,42.2,36,"Italy","Ý",137.1,"Ý",(236,186,110)),
      ((40,790,520,1200),-97,39,8.6,"United States of America","MỸ",123.9,"Mỹ",(230,180,104)),((560,790,1040,1200),137.5,37.6,22,"Japan","NHẬT BẢN",206.5,"Nhật",OR)]
panels=[]
for i,(rect,lo,la,k,cn,nm,v,wd,col) in enumerate(data):
    tv=sc.w(wd) if wd!="Nhật" else sc.w("Nhật")
    p=MapPanel(sc,rect,lo,la,k,cn,nm,v,0.15+i*0.22,tv,col); sc.add(p); sc.ev(0.15+i*0.22,"swish",0.5); panels.append(p)
for p in panels:
    hpx=p.val/206.5*200; b=Bar3D(lambda t,p=p:p.base_pt(t),p.tval+0.1,hpx,0.8,54,p.col if p.name!="NHẬT BẢN" else OR); sc.add(b)
    sc.add(PCounter(lambda t,p=p,b=b:(p.base_pt(t)[0]+8,p.base_pt(t)[1]-b.cur(t)-26),p.tval+0.1,0.8,0,p.val,1,46 if p.name=="NHẬT BẢN" else 38,WH,"","%",kind="pop",shadow=3))
    [sc.ev(p.tval+0.1+k*0.07,"tick",0.45) for k in range(11)]
pill(sc,"NỢ CÔNG / GDP 2025 · IMF",268,0.1,34,OR,DK)
tj=sc.w("Nhật"); snapbox(sc,(552,782,1048,1208),sc.w("đứng"),RD,8); sc.add(Item(pill_spr("#1",56,RD,WH),975,1150,sc.w("đầu"),"popr")); sc.ev(sc.w("đầu"),"boom",0.7); sc.hit(sc.w("đầu")+0.05)
# ===================== 5 TITLE =====================
bg=drift(dark_bg(5),z=(1.0,1.06)); sc=new("title",bg,"kinetic"); sc.zblur=True; sc.ev(0,"whoosh",0.9)
sc.add(BottomGlobe(VEQ,2080,880,150,6,22,0.0,0.6))
rows_block(sc,[R("VÌ SAO",72,(220,228,232),words=[sc.w("Vậy"),sc.w("tại")]),R("NỢ NHIỀU NHƯ VẬY",80,WH,words=[sc.w("nợ"),sc.w("nhiều"),sc.w("như"),sc.w("vậy")]),
  R("NHẬT VẪN",96,WH,words=[sc.w("vẫn"),sc.w("vẫn")+0.1]),R("CHƯA SỤP ĐỔ?",130,OR,words=[sc.w("chưa"),sc.w("sụp"),sc.w("đổ")],kind="popr",asc=0.88)],300,card=False,shadow=4)
sc.hit(sc.w("sụp")+0.05)
# ===================== 6 HOLDERS: notepad -> table =====================
bg=drift(paper_bg("grey",11)); sc=new("holders",bg,"collage")
tex=sc.w("Theo")
cutout(sc,"notepad",540,700,0.1,520,640,kind="drop",glow=False,until=tex,exit="shrink")
sc.add(TItem(tsp("AI ĐANG",64,DK),540,620,0.35,"pop",MOT_CUT,until=tex,exit="shrink")); sc.add(TItem(tsp("CẦM GIẤY NỢ?",64,RD),540,720,sc.w("cầm"),"pop",MOT_CUT,until=tex,exit="shrink")); sc.ev(0.35,"pop",0.5); sc.ev(sc.w("cầm"),"pop",0.5)
cutout(sc,"coin",830,980,sc.w("nợ"),200,200,kind="drop",until=tex)
TB=(60,290,1020,1200)
class Expand:
    def __init__(s,at): s.at=at
    def draw(s,fr,t,cam):
        if t<s.at: return
        u=e_back((t-s.at)*FPS/13,1.2); a=(300,400,780,1020); b=TB; r=[lerp(a[i],b[i],u) for i in range(4)]
        m=np.zeros((H,W),np.uint8); cv2.rectangle(m,(int(r[0]+8),int(r[1]+16)),(int(r[2]+8),int(r[3]+16)),255,-1); m=cv2.GaussianBlur(m,(0,0),14); blend_mask(fr,m,(0,0,0),0.3)
        m=np.zeros((H,W),np.uint8); cv2.rectangle(m,(int(r[0]),int(r[1])),(int(r[2]),int(r[3])),255,-1); blend_mask(fr,m,(0.99,0.985,0.97),1)
        m=np.zeros((H,W),np.uint8); cv2.rectangle(m,(int(r[0]),int(r[1])),(int(r[2]),int(r[1]+14)),255,-1); blend_mask(fr,m,ORf,1)
sc.add(Expand(tex)); sc.ev(tex,"whoosh",0.8)
sc.add(Item(tsp("AI NẮM TRÁI PHIẾU CHÍNH PHỦ NHẬT?",38,DK),570,370,tex+0.25,"fade")); sc.add(Item(tsp("Tỷ trọng nắm giữ JGB · 6/2026 (sơ bộ) · Bộ Tài chính Nhật, dữ liệu dòng vốn BOJ",20,MG,"SemiBold"),540,418,tex+0.35,"fade"))
pill(sc,"THÁNG 6/2026",296,sc.w("tháng 6 năm 2026"),26,DK,OR,x=900)
rows=[("NH Trung ương Nhật (BOJ)",46.7,sc.w("Ngân"),sc.w("46,7%"),RD),("Ngân hàng thương mại",15.6,sc.w("ngân"),sc.w("15,6%"),DOR),("Công ty bảo hiểm",15.1,sc.w("công",1),sc.w("15,1%"),DOR),
      ("Nhà đầu tư nước ngoài",7.9,13.9,14.05,(40,110,170)),("Quỹ hưu trí công",7.6,14.15,14.3,MG),("Khác (hộ gia đình, quỹ…)",7.1,14.4,14.55,MG)]
y=540
for i,(nm,v,ta,tv,col) in enumerate(rows):
    cy=y+i*112; mot=(-0.3,1.5,3.5,i)
    if i==0: sc.add(Highlight((80,cy-50,1000,cy+50),tv+0.2,0.45,(255,170,160),0.75,mot),"swish",tv+0.2,0.5)
    if i==3: sc.add(Highlight((80,cy-50,1000,cy+50),14.6,0.4,YEL,0.6,mot))
    ta=min(ta,tex+0.6+i*0.14); s1=tsp(nm,34,DK); sc.add(Item(s1,110+s1.cw/2,*at_base(s1,0,cy+12)[1:],at=ta,kind="right",mot=mot)); sc.ev(ta,"swish",0.4)
    def bar(fr,t,cam,cy=cy,v=v,tv=tv,col=col):
        if t<tv: return
        p=e_out((t-tv)/0.7); x0=560; x1=x0+v/46.7*280*p; fr[int(cy-14):int(cy+14),x0:int(x1)]=np.float32(col)/255
    sc.add(Fn(bar))
    sc.add(Counter(930,cy+16,tv,0.7,0,v,1,44,col if i else RD,suffix="%",mot=mot)); [sc.ev(tv+k*0.07,"tick",0.4) for k in range(10)]
    if i<5: sc.add(Item(Spr(np.dstack([np.full((2,880,3),180,np.uint8),np.full((2,880,1),120,np.uint8)])),540,cy+56,ta,"fade"))
snapbox(sc,(70,540-56,1010,540+56),sc.w("46,7%")+0.1,RD,7)
cutout(sc,"bank",120,330,sc.w("Ngân")+0.2,150,130,kind="drop",gsize=220)
stamp(sc,"GẦN 1/2",690,545,sc.w("46,7%")+0.8,34,RD,-8); sc.hit(sc.w("46,7%")+0.05,False)
# ===================== 7 FOREIGN: arrows into Japan =====================
bg=VecBg(lambda t:(35,28,4.5*(1+0.08*e_sine(t/3.3)),0),0.95); sc=new("foreign",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Japan"],fill=(0,0.3),pulse=0.2)); hsts(sc,bg,0.0,18,(-24,28))
for i,(nm,lo,la) in enumerate([("New York",-74,40.7),("London",-0.1,51.5),("Dubai",55.3,25.2)]):
    sc.add(GlowPin(bg,lo,la,0.05+i*0.2,(120,200,255),9)); sc.add(Route(bg,(lo,la),TOK,0.15+i*0.25,1.0,-0.22 if i<2 else -0.15,(120,200,255),5)); sc.ev(0.15+i*0.25,"swish",0.5)
    map_label(sc,bg,nm,lo,la,0.2+i*0.2,24,(200,225,240),dy=-30)
rows_block(sc,[R("NHÀ ĐẦU TƯ NƯỚC NGOÀI",34,(200,206,210),at=0.1),R("CHỈ NẮM 7,9%",84,OR,at=sc.w("7,9%"),kind="popr"),R("trái phiếu chính phủ Nhật (JGB)",30,WH,w="SemiBold",at=sc.w("7,9%")+0.3,kind="fade")],930,0.05,cardkw=dict(fill=(16,26,34),alpha=232))
sc.hit(sc.w("7,9%")+0.1,False)
# ===================== 8 INSIDE: Japan silhouette, people, yen note =====================
bg=drift(paper_bg("grey",12)); sc=new("inside",bg,"collage")
pill(sc,"NỢ TRONG NHÀ",330,0.1,44,DK,OR)
cutout(sc,"japan_sil",540,700,0.15,560,600,kind="drop",gsize=700)
cutout(sc,"pers_d",200,950,sc.w("người"),150,300,kind="up",glow=False); cutout(sc,"pers_o",880,950,sc.w("người",2),150,300,kind="up",glow=False)
sc.add(Item(tsp("NGƯỜI NHẬT",30,DK),200,1130,sc.w("người")+0.1,"pop")); sc.add(Item(tsp("NGƯỜI NHẬT",30,DOR),880,1130,sc.w("người",2)+0.1,"pop"))
sc.add(Route(None,(880,880),(220,880),sc.w("nợ",2),0.6,0.25,RD,6,flow=True)); sc.ev(sc.w("nợ",2),"swish",0.6)
sc.add(Item(pill_spr("NỢ",30,RD,WH),540,760,sc.w("nợ",2)+0.4,"pop"))
cutout(sc,"yen_note",540,700,sc.w("yên"),680,400,kind="pop",gsize=760,mot=(1.0,6,3,0.5)); sc.hit(sc.w("yên")+0.05)
sc.add(Item(pill_spr("BẰNG ĐỒNG YÊN DO NHẬT PHÁT HÀNH",34,DK,WH),540,1180,sc.w("phát"),"right",MOT_TXT)); sc.ev(sc.w("phát"),"whoosh",0.5)
# ===================== 9 UST: Japan -> US Treasuries =====================
def p_ust(t):
    u=e_io(t/1.5); return lerp(TOK[0],211,u),lerp(TOK[1],36,u),log_lerp(70,5.5,u)*(1+0.04*e_sine((t-1.5)/5.5)),0
bg=VecBg(p_ust); sc=new("ust",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.9)
sc.add(CountryFX(bg,["Japan"],fill=(0,0.3),pulse=0.2)); sc.add(CountryFX(bg,["United States of America"],stroke=(0.9,1.9),fill=(1.7,2.2),alpha=0.5,color=(110,180,200),glow=0.3,nstroke=2))
sc.add(GlowPin(bg,*TOK,0.3,OR,14))
WDC=(283.0,38.9); tr=sc.w("chủ")
sc.add(Route(bg,TOK,WDC,tr,1.4,-0.28,OR,7)); sc.ev(tr,"whoosh",0.7); sc.add(GlowPin(bg,*WDC,tr+1.3,(120,200,255),14))
map_label(sc,bg,"NHẬT BẢN",*TOK,0.5,30,OR,dy=46); map_label(sc,bg,"MỸ",*WDC,tr+1.3,34,(150,215,235),dx=-40,dy=50)
pill(sc,"CHỦ NỢ NƯỚC NGOÀI LỚN NHẤT CỦA MỸ",330,sc.w("lớn"),32,OR,DK)
rows_block(sc,[R("TRÁI PHIẾU KHO BẠC MỸ NHẬT NẮM",30,(200,206,210),at=sc.w("nắm")),R("1.104 TỶ USD",96,OR,ctr=dict(v1=1104,suf=" TỶ USD",dur=0.9),at=sc.w("1.104"),asc=0.82),R("7/2026 · Bộ Tài chính Mỹ (TIC)",26,WH,w="SemiBold",at=sc.w("1.104")+0.5,kind="fade")],930,sc.w("nắm")-0.1,cardkw=dict(fill=(16,26,34),alpha=232))
cutout(sc,"coin_usd",900,880,sc.w("1.104")-0.2,170,170,kind="drop",gsize=260); sc.hit(sc.w("1.104")+0.95)
# ===================== 10 IMF1: document card =====================
bg=drift(paper_bg("grey",13)); sc=new("imf1",bg,"document"); sc.post.append(edge_blur(0.9))
body=("While the debt level is elevated, the overall risk of sovereign debt distress is assessed as moderate, reflecting a favorable maturity structure "
      "and the mitigating roles of the deep domestic investor base, the yen's reserve currency status, and the large stock of public sector financial assets.")
DocCard(sc,"INTERNATIONAL MONETARY FUND","Japan: 2026 Article IV Consultation — Staff Report (IMF Country Report No. 26/75)",body,
  [("the overall risk of sovereign debt distress is assessed as moderate",sc.w("trung"),0.9),("deep domestic investor base",sc.w("lực"),0.6),("the yen's reserve currency status",sc.w("đồng"),0.6),("large stock of public sector financial assets",sc.w("khối"),0.7)],
  0.05,y=660,size=40,w=960,src_line="Trích nguyên văn · IMF, 4/2026")
pill(sc,"IMF: RỦI RO VỠ NỢ Ở MỨC “TRUNG BÌNH”",300,sc.w("trung")+0.3,32,RD,WH)
for i,(txt,wd) in enumerate([("NĐT trong nước\nđông đảo","lực"),("Yên: tiền tệ\ndự trữ","đồng"),("Tài sản tài chính\ncông lớn","khối")]):
    x=200+i*340; at=sc.w(wd)+0.1; sc.add(Item(card_spr(300,130,accent=True,r=20),x,1130,at,"up",MOT_CARD)); sc.ev(at,"swish",0.5)
    for j,ln in enumerate(txt.split("\n")): sc.add(Item(tsp(ln,30,DK if j==0 else DOR),x,1110+j*42,at+0.08,"up",MOT_CARD))
# ===================== 11 TURN: bottom globe, rates ~0 vanishing =====================
bg=drift(dark_bg(6),z=(1.0,1.05)); sc=new("turn",bg,"map"); sc.zblur=True; sc.ev(0,"whoosh",0.9)
sc.add(BottomGlobe(VEQ,2100,960,160,7,24,0.0,0.7))
pill(sc,"CHỖ DỰA QUAN TRỌNG NHẤT",350,0.15,36,OR,DK)
o,_=rows_block(sc,[R("LÃI SUẤT",80,WH,at=sc.w("lãi")),R("≈ 0%",230,OR,at=sc.w("gần"),kind="popr",asc=0.8)],430,card=False,shadow=4)
r=o[1]["rect"]; sc.add(Strike(r[0]+10,r[2]-10,(r[1]+r[3])/2,sc.w("biến"),0.3,RD,22),"swish",sc.w("biến"),0.6); sc.hit(sc.w("biến")+0.1)
sc.add(Item(pill_spr("ĐANG BIẾN MẤT",44,RD,WH),540,1010,sc.w("mất"),"popr")); sc.ev(sc.w("mất"),"pop",0.7)
cutout(sc,"arr_up",880,820,sc.w("biến"),150,230,kind="up",gsize=300)
# ===================== 12 BOJ: tilted satellite Tokyo + pin =====================
def p_boj(t): u=e_sine(t/8.23); return BOJ[0]-0.004*(1-u),BOJ[1]-0.003*(1-u),log_lerp(560000,700000,u),-14+8*u,0.6
bg=SatCam(p_boj); sc=new("boj",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.8)
pill(sc,"18/9/2026",330,0.1,42,DK,OR)
sc.add(GlowPin(bg,*BOJ,0.4,RD,16))
lb=pill_spr("NGÂN HÀNG TRUNG ƯƠNG NHẬT BẢN",28,WH,DK); sc.add(Item(lb,0,0,sc.w("Ngân"),"pop",posfn=lambda t,bg=bg:tuple(bg.proj(*BOJ)[0]+np.array([0,-80])))); sc.ev(sc.w("Ngân"),"pop",0.6)
rows_block(sc,[R("LÃI SUẤT ĐIỀU HÀNH",34,(200,206,210),at=sc.w("nâng")),R("1,25%",150,OR,ctr=dict(v1=1.25,dec=2,suf="%",dur=0.8),at=sc.w("1,25%"),asc=0.8),
  R("cao nhất kể từ năm 1995",46,WH,w="SemiBold",at=sc.w("năm 1995")-0.3,kind="up",hl=sc.w("năm 1995")+0.1,hlc=(255,140,110))],880,sc.w("nâng")-0.1,cardkw=dict(fill=(16,26,34),alpha=235))
sc.hit(sc.w("1,25%")+0.8)
cutout(sc,"arr_up_or",900,700,sc.w("1,25%"),120,180,kind="up",gsize=220)
# ===================== 13 YIELD: line over darkened map =====================
bg=VecBg(lambda t:(137,37,30*(1+0.08*e_sine(t/7.6)),2*e_sine(t/7.6)),0.38); sc=new("yield",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Japan"],fill=(0,0.4),alpha=0.3,glow=0.2))
pill(sc,"LỢI SUẤT TRÁI PHIẾU NHẬT 10 NĂM",330,0.1,34,OR,DK)
xs=[2020,2021,2022,2023,2024,2025,2025.75]; ys=[0.035,0.089,0.454,0.647,1.111,2.066,3.092]
t0=0.5; t1=sc.w("3,09%")+0.15
LC=LineChart(sc,(180,470,900,1040),xs,ys,(2019.8,2026.0),(0,3.6),t0,t1,RD,True,yfmt=lambda v:vn(v,0)+"%",yticks=[0,1,2,3],xticks=[(2020,"2020"),(2021,"2021"),(2022,"2022"),(2023,"2023"),(2024,"2024"),(2025,"2025"),(2025.75,"10/26")],head_fmt=lambda v:vn(v,2)+"%")
y3=LC.Y(3.0); t3=sc.w("3%")
def d3(fr,t,cam):
    if t<t3: return
    p=e_out((t-t3)/0.5); xe=180+(900-180)*p; m=np.zeros((H,W),np.uint8)
    for x in np.arange(180,xe,26): cv2.line(m,(int(x*16),int(y3*16)),(int(min(x+14,xe)*16),int(y3*16)),255,3,cv2.LINE_AA,4)
    blend_mask(fr,m,(1,0.85,0.5),0.95)
sc.add(Fn(d3)); sc.add(Item(pill_spr("MỐC 3%",28,YEL,DK),300,y3-40,t3+0.2,"pop")); sc.ev(t3,"swish",0.5)
sc.add(Item(pill_spr("3,09%",60,RD,WH),720,400,t1+0.05,"popr")); sc.ev(t1,"boom",0.7); sc.hit(t1+0.05,False)
sc.add(Item(pill_spr("CAO NHẤT KỂ TỪ 1996",38,WH,RD),540,1185,sc.w("năm 1996")-0.2,"up")); sc.ev(sc.w("năm 1996")-0.2,"swish",0.5)
sc.add(Item(text_spr("Lợi suất cuối năm; 1/10/2026 · Nguồn: Bộ Tài chính Nhật",22,(190,200,205),"Regular",2),540,1122,0.6,"fade"))
# ===================== 14 SWAP: bond refinancing =====================
bg=drift(paper_bg("grey",14)); sc=new("swap",bg,"collage")
td=sc.w("đáo"); tn=sc.w("mới")
sc.add(Item(cut_spr("bond_old",560,360),330,520,0.05,"drop",(0.8,3,3,0),rot=8)); sc.add(Item(cut_spr("bond_old",560,360),760,560,0.12,"drop",(0.8,3,3,1),rot=-6))
cutout(sc,"bond_old",540,720,0.25,760,480,kind="drop",glow=False,until=td+0.35,exit="left")
stamp(sc,"ĐÁO HẠN",540,720,td,80,(60,110,90),-12)
cutout(sc,"bond_new",540,720,tn,780,500,kind="drop",gsize=900)
sc.hit(tn+0.3)
rows_block(sc,[R("TỪ 0,1% LÊN ~3%",84,DK,words=[sc.w("lãi"),sc.w("lãi")+0.1,tn,tn+0.25]),R("vay mới để trả nợ cũ, với lãi cao hơn nhiều",34,DOR,w="SemiBold",at=sc.w("cao"),kind="up",hl=sc.w("nhiều"))],1030,sc.w("lãi")-0.1)
# ===================== 15 MATUR: IMF doc 2 =====================
bg=drift(paper_bg("grey",15)); sc=new("matur",bg,"document"); sc.post.append(edge_blur(0.9,(540,700)))
body="Interest rates are projected to continue rising gradually, but a favorable maturity structure (average residual maturity of 9.5 years) will slow the pass-through to government interest payments."
DocCard(sc,"INTERNATIONAL MONETARY FUND","Japan: 2026 Article IV Consultation — Staff Report (IMF Country Report No. 26/75)",body,
  [("average residual maturity of 9.5 years",sc.w("9,5")-0.2,0.6),("slow the pass-through to government interest payments",sc.w("thấm"),0.8)],0.0,y=640,size=38,src_line="Trích nguyên văn · IMF, 4/2026",kind="up",rot=(1.2,-0.4))
sc.add(Item(card_spr(380,150,accent=True,r=24),280,1130,sc.w("9,5"),"popr",MOT_CARD)); sc.add(Counter(280,1150,sc.w("9,5"),0.6,0,9.5,1,74,DK,suffix=" NĂM",mot=MOT_CARD)); sc.add(Item(tsp("kỳ hạn còn lại bình quân",24,MG,"SemiBold"),280,1185,sc.w("9,5")+0.2,"fade",MOT_CARD))
[sc.ev(sc.w("9,5")+k*0.07,"tick",0.4) for k in range(8)]
sc.add(Item(pill_spr("NHƯNG KHÔNG CHẶN ĐƯỢC MÃI",28,RD,WH),760,1130,sc.w("chặn"),"popr",MOT_TXT)); sc.ev(sc.w("chặn"),"pop",0.7); sc.hit(sc.w("chặn")+0.05,False)
# ===================== 16 BUDGET: dual-axis chart over blurred satellite =====================
def sat_blur():
    im=cv2.cvtColor(cv2.imread("assets/sat/eox_z11.jpg"),cv2.COLOR_BGR2RGB); h,w=im.shape[:2]; c=im[h//2-1700:h//2+1700,w//2-960:w//2+960]
    c=cv2.resize(c,(SW,SH)); c=cv2.GaussianBlur(c,(0,0),9).astype(np.float32)*0.42; c[...,2]*=1.12; return finish_bg(c,0.3)
bg=drift(sat_blur()); sc=new("budget",bg,"chart",credit=CR_SAT); sc.ev(0,"whoosh",0.7)
sc.add(Item(card2(940,860,True,None),540,740,0.0,"pop")); sc.ev(0,"pop",0.6)
sc.add(Item(tsp("CHI TRẢ NỢ TRONG NGÂN SÁCH NHẬT",36,WH),540,370,0.1,"fade"))
sc.add(Item(tsp("Chi trả nợ gốc + lãi (nghìn tỷ ¥)",24,OR,"SemiBold"),330,420,0.2,"fade")); sc.add(Item(tsp("Lợi suất 10 năm (%)",24,(255,120,100),"SemiBold"),790,420,0.2,"fade"))
fy=["NTC 2023","NTC 2024","NTC 2025","NTC 2026"]; bv=[25.3,27.0,28.2,31.3]; yv=[0.647,1.111,2.066,3.092]
bx=[230+i*205 for i in range(4)]; base=1080; top=520
def bars(fr,t,cam):
    for i,v in enumerate(bv):
        p=e_out((t-0.3-i*0.18)/0.6)
        if p<=0: continue
        hh=v/34*(base-top)*p; col=np.float32(OR if i==3 else (196,150,90))/255; fr[int(base-hh):base,bx[i]-62:bx[i]+62]=col
sc.add(Fn(bars))
for i,v in enumerate(bv):
    at=0.3+i*0.18 if i<3 else sc.w("31,3")-0.3
    sc.add(Counter(bx[i],base-v/34*(base-top)-16,at,0.6,0,v,1,40 if i<3 else 54,WH if i<3 else OR,shadow=2)); sc.ev(at,"tick",0.5)
    sc.add(Item(tsp(fy[i],26,(200,210,214),"SemiBold"),bx[i],base+36,0.2,"fade"))
LC=LineChart(sc,(bx[0],top,bx[3],base),[0,1,2,3],yv,(0,3),(0,3.6),1.6,3.3,(255,90,70),True,yticks=None,xticks=None,head_fmt=None,width=7)
for i,v in enumerate(yv):
    tt=1.6+(3.3-1.6)*[0,0.37,0.63,1.0][i]; sc.add(Item(text_spr(vn(v,2)+"%",30 if i<3 else 40,(255,170,150) if i<3 else (255,120,100),"Bold",3),bx[i]+(0 if i<3 else -20),LC.Y(v)-44,tt,"pop")); sc.ev(tt,"pop",0.4)
sc.add(Item(text_spr("lợi suất cuối năm (NTC 2026: 1/10/2026)",20,(220,200,196),"SemiBold",2),790,452,1.8,"fade"))
sc.add(Item(pill_spr("≈ 1/4 TỔNG CHI NGÂN SÁCH",36,RD,WH),540,1205,sc.w("phần"),"popr")); sc.ev(sc.w("phần"),"pop",0.7); sc.hit(sc.w("phần")+0.05,False)
sc.add(Item(text_spr("NTC = năm tài khóa (ngân sách ban đầu) · Bộ Tài chính Nhật",20,(190,200,205),"Regular",2),540,1146,0.5,"fade"))
# ===================== 17 INTEREST: invoices stacking + coins =====================
bg=drift(paper_bg("grey",16)); sc=new("interest",bg,"collage")
for i in range(5):
    at=0.05+i*0.32; sc.add(Item(cut_spr(f"inv{i}",360,470),470+(-1)**i*60+i*8,650-i*14,at,"drop",(0.6,3,3,i),rot=(-1)**i*(5+i*2))); sc.ev(at,"swish",0.5)
rows_block(sc,[R("RIÊNG TIỀN LÃI",34,MG,at=0.1),R("13 NGHÌN TỶ ¥",104,RD,ctr=dict(v1=13,suf=" NGHÌN TỶ ¥",dur=0.6),at=sc.w("13"),asc=0.82),R("ngân sách năm tài khóa 2026",30,DK,w="SemiBold",at=sc.w("13")+0.4,kind="fade")],930,0.0)
cutout(sc,"stack10",880,640,sc.w("tăng"),200,330,kind="up",gsize=320); cutout(sc,"arr_up",880,380,sc.w("24%"),120,180,kind="up",gsize=200)
sc.add(Item(pill_spr("+24%",54,RD,WH),720,300,sc.w("24%")+0.1,"popr")); sc.ev(sc.w("24%")+0.1,"pop",0.8); sc.hit(sc.w("24%")+0.1)
# ===================== 18 AGING: Japan map, pins, callout, people =====================
bg=VecBg(lambda t:(137.2,37.8,52*(1+0.10*e_sine(t/7.3)),-2+3*e_sine(t/7.3)),0.85); sc=new("aging",bg,"map",credit=CR_NE); sc.ev(0,"whoosh",0.7)
sc.add(CountryFX(bg,["Japan"],stroke=(0.1,1.0),fill=(0.8,1.3),alpha=0.55,pulse=0.15,nstroke=4))
pill(sc,"ÁP LỰC THỨ 3: DÂN SỐ",330,0.1,40,OR,DK)
for i,(lo,la) in enumerate([TOK,(135.5,34.69),(136.9,35.18),(141.35,43.06),(130.4,33.59),(140.87,38.27),(132.46,34.39),(139.02,37.9)]):
    sc.add(GlowPin(bg,lo,la,0.6+i*0.15,WH,10,rings=False)); sc.ev(0.6+i*0.15,"pop",0.3)
callout(sc,bg,140.1,39.7,sc.w("65")-0.3,-260,-140,[dict(t="NGƯỜI TỪ 65 TUỔI",s=28,c=(190,206,210)),dict(ctr=(0,29.6,1,"","%",0.8),s=80,c=OR,at=sc.w("29,6%")),dict(t="36,24 triệu người · 9/2026",s=24,c=WH,w="SemiBold")],w=380)
for k in range(10):
    x=135+k*90; sc.add(Item(cut_spr("pers_g",60,120),x,1110,1.5+k*0.05,"up")); 
    if k<3: sc.add(Item(cut_spr("pers_o",60,120),x,1110,sc.w("29,6%")+0.2+k*0.15,"pop")); sc.ev(sc.w("29,6%")+0.2+k*0.15,"pop",0.5)
sc.ev(1.5,"swish",0.4)
stamp(sc,"KỶ LỤC",820,900,sc.w("kỷ"),62)
# ===================== 19 BIRTHS =====================
bg=drift(paper_bg("grey",17)); sc=new("births",bg,"collage")
sc.add(Item(cut_spr("japan_or",600,640),540,600,0.0,"fade",(0.5,2,4,0)))
cutout(sc,"baby",540,560,0.1,360,360,kind="drop",gsize=560)
rows_block(sc,[R("TRẺ SINH RA Ở NHẬT NĂM 2025",34,MG,words=True,at=0.2),R("671.270",150,DK,ctr=dict(v1=671270,dur=1.0),at=sc.w("671"),asc=0.8),R("thấp nhất từ trước đến nay",48,RD,w="SemiBold",at=sc.w("thấp"),kind="up",hl=sc.w("thấp")+0.3,hlc=(255,190,180)),R("giảm 10 năm liên tiếp · Bộ Y tế, Lao động & Phúc lợi Nhật",24,MG,w="SemiBold",at=sc.w("thấp")+0.6,kind="fade")],800,0.05)
cutout(sc,"arr_dn",880,520,sc.w("thấp"),130,200,kind="drop",gsize=220); sc.hit(sc.w("thấp")+0.05)
# ===================== 20 PENSION: coin stacks with arrows =====================
bg=drift(paper_bg("grey",18)); sc=new("pension",bg,"collage")
tl=sc.w("Ít"); td=sc.w("đóng"); tr=sc.w("lương"); tg=sc.w("lớn")
sc.add(Item(tsp("ĐI LÀM, ĐÓNG THUẾ",42,DK),290,340,tl,"pop")); sc.ev(tl,"pop",0.5)
cutout(sc,"stack9g",290,700,tl+0.1,260,480,kind="up",glow=False,until=td+0.3,exit="shrink"); cutout(sc,"stack4",290,790,td+0.45,260,300,kind="pop",glow=False)
cutout(sc,"arr_dn",290,520,td+0.4,110,170,kind="drop",glow=False)
sc.add(Item(tsp("LƯƠNG HƯU, Y TẾ",42,RD),790,340,tr,"pop")); sc.ev(tr,"pop",0.5)
cutout(sc,"stack6",790,760,tr+0.1,260,380,kind="up",glow=False,until=tg-0.1,exit="shrink"); cutout(sc,"stack14",790,690,tg+0.1,260,560,kind="pop",gsize=420)
cutout(sc,"arr_up",985,520,tg+0.25,90,140,kind="up",glow=False); sc.hit(tg+0.2)
sc.add(Item(Spr(np.dstack([np.full((520,4,3),120,np.uint8),np.full((520,4,1),110,np.uint8)])),540,700,0.0,"fade"))
rows_block(sc,[R("TỶ LỆ PHỤ THUỘC NGƯỜI GIÀ",30,MG,at=tg-0.6),R("49,7 LÊN 53,1",80,RD,words=[tg-0.5,tg-0.3,tg-0.1]),R("người 65+ / 100 người tuổi lao động · 2025 đến 2031 (IMF dự báo)",22,MG,w="SemiBold",at=tg,kind="fade")],975,tg-0.7)
# ===================== 21 IMF2: press release doc =====================
bg=drift(paper_bg("grey",19)); sc=new("imf2",bg,"document"); sc.post.append(edge_blur(0.9,(540,700)))
body=("Recent fiscal performance has exceeded expectations, but: The deficit is expected to widen in 2026. Spending on interest and health and long-term care for the aging population "
      "will continue to rise, eventually leading to an increase in the debt-to-GDP ratio from 2035.")
DocCard(sc,"INTERNATIONAL MONETARY FUND","Press Release No. 26/105 — IMF Executive Board Concludes 2026 Article IV Consultation with Japan",body,
  [("Spending on interest and health and long-term care for the aging population",sc.w("chi"),1.0),("an increase in the debt-to-GDP ratio from 2035.",sc.w("tăng"),0.8)],0.05,y=660,size=38,src_line="Trích nguyên văn · IMF, 3/4/2026",kind="left",rot=(-1.0,0.6))
sc.add(Item(card_spr(300,150,accent=True,r=24),300,1140,sc.w("năm 2035")-0.3,"popr",MOT_CARD)); sc.add(Item(tsp("2035",90,RD),300,1150,sc.w("năm 2035")-0.25,"popr",MOT_CARD)); sc.ev(sc.w("năm 2035")-0.3,"boom",0.6)
sc.add(Item(pill_spr("NỢ/GDP TĂNG TRỞ LẠI",34,DK,OR),730,1140,sc.w("trở"),"right",MOT_TXT)); sc.ev(sc.w("trở"),"whoosh",0.5)
# ===================== 22 MEAN: satellite zoom-out reveal -> globe sinks to bottom =====================
def p_mean(t):
    if t<3.4:
        u=e_io(t/3.4); return lerp(TOK[0],150,e_io(t/3.4)**2),lerp(TOK[1],28,e_io(t/3.4)**2),log_lerp(300000,430,u),-8*(1-u),0.5*(1-e_out(t/1.2)),820
    u=e_io((t-3.4)/1.6); return 150+5*(t-3.4),lerp(28,22,u),lerp(430,950,u),0,0,lerp(820,2120,u)
bg=SatCam(p_mean); sc=new("mean",bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.9); sc.ev(3.4,"whoosh",0.6)
sat_hsts(sc,bg,2.0,9.0)
pill(sc,"VẬY ĐIỀU NÀY NÓI LÊN GÌ?",330,0.1,38,OR,DK)
rows_block(sc,[R("SỐNG CHUNG VỚI NỢ",84,WH,words=[sc.w("sống"),sc.w("chung"),sc.w("với"),sc.w("nợ")]),{"gap":20},R("khi chủ nợ là người trong nhà",44,(220,228,232),w="SemiBold",at=sc.w("chủ"),kind="up"),
   R("và tiền vay ≈ miễn phí",54,OR,at=sc.w("miễn"),kind="up",hl=sc.w("miễn")+0.3,hlc=(255,220,150))],480,card=False,shadow=4)
sc.hit(sc.w("sống")+0.05,False)
# ===================== 23 BILL =====================
bg=drift(paper_bg("grey",20)); sc=new("bill",bg,"collage")
rows_block(sc,[R("KHI LÃI SUẤT QUAY LẠI",44,MG,words=[0.05,sc.w("lãi"),sc.w("suất"),sc.w("quay"),sc.w("lại")]),R("MỖI 1%",120,DK,at=sc.w("mỗi"),kind="popr",asc=0.84),R("= MỘT HÓA ĐƠN THẬT",62,RD,words=[sc.w("trở"),sc.w("một"),sc.w("hóa"),sc.w("thật")])],270,0.0)
for i in range(4):
    at=sc.w("hóa")+i*0.25; sc.add(Item(cut_spr(f"inv{i+1}",300,400),300+i*14,880-i*12,at,"drop",(0.6,3,3,i),rot=(-1)**i*(6+i*2))); sc.ev(at,"swish",0.45)
cutout(sc,"baby",800,860,sc.w("em"),300,300,kind="drop",gsize=460); sc.hit(sc.w("em")+0.1,False)
sc.add(Item(pill_spr("NGƯỜI TRẢ HÓA ĐƠN",32,DK,OR),800,1090,sc.w("trả"),"popr")); sc.ev(sc.w("trả"),"pop",0.7)
sc.add(Route(None,(430,1150),(690,1100),sc.w("trả")+0.2,0.5,-0.3,RD,6,flow=False))
# ===================== 24 END =====================
sc=new("end",drift(dark_bg(7),z=(1.0,1.06)),"end",brand=False); sc.zblur=True; sc.ev(0,"whoosh",0.8)
sc.add(BottomGlobe(VEQ,2120,900,155,5,22,0.0,0.8))
sc.add(Item(glow_spr(900,OR,60),540,560,0.0,"pop",(0,10,4,0)))
sc.add(Strike(450,630,336,0.05,0.3,OR,12))
sc.add(Item(tsp("HINTON",160,WH),540,470,sc.w("Hinton")-0.1,"popr")); sc.ev(sc.w("Hinton")-0.1,"pop",0.7)
sc.add(Item(tsp("MEDIA",160,OR),540,630,sc.w("Media")-0.1,"popr")); sc.ev(sc.w("Media")-0.1,"pop",0.7)
sc.add(Item(pill_spr("+  THEO DÕI",52,OR,DK),540,800+41,sc.w("để")-0.25,"pop",pulse=0.045)); sc.ev(sc.w("để")-0.25,"boom",0.6)
sc.add(Item(tsp("để hiểu kinh tế mỗi ngày",46,(176,176,180),"Bold"),540,975,sc.w("hiểu"),"up")); sc.ev(sc.w("hiểu"),"swish",0.4)
SCENES.sort(key=lambda s:s.f0)
for a,b in zip(SCENES,SCENES[1:]): assert a.f1==b.f0,(a.name,b.name,a.f1,b.f0)
assert SCENES[0].f0==0
