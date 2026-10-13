# procedural illustration cut-outs (all drawn here; no third-party imagery)
from maps import *
CJK="/usr/share/fonts/opentype/noto/NotoSansCJK-Bold.ttc"
TIN=FD
def F(s,w="Bold"): return fnt(s,w)
def cjk(s): return ImageFont.truetype(CJK,s,index=0)
def save(im,name,scale=0.5):
    if scale!=1: im=im.resize((int(im.width*scale),int(im.height*scale)),Image.LANCZOS)
    im.save(f"assets/cut/{name}.png"); return im
def baby():
    S=800; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([60,60,740,740],fill=(255,255,255,255),outline=OR,width=22)
    d.rounded_rectangle([210,400,590,700],170,fill=(150,196,232))          # swaddle
    d.polygon([(220,470),(400,560),(580,470),(560,520),(400,610),(240,520)],fill=(124,172,214))
    d.ellipse([255,170,545,450],fill=(246,206,168))                         # head
    d.pieslice([255,160,545,330],180,360,fill=(120,84,60))                 # hair
    d.ellipse([235,290,275,350],fill=(240,190,150)); d.ellipse([525,290,565,350],fill=(240,190,150))
    for x in (350,450): d.ellipse([x-16,315,x+16,347],fill=(40,34,30))
    d.arc([360,350,440,405],20,160,fill=(170,80,60),width=9)
    d.ellipse([300,350,335,375],fill=(244,170,150)); d.ellipse([465,350,500,375],fill=(244,170,150))
    return save(im,"baby")
def coin(sym="¥",name="coin"):
    S=600; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([20,40,580,600],fill=(150,98,10)); d.ellipse([20,20,580,580],fill=(236,170,48))
    d.ellipse([60,60,540,540],fill=(250,196,74)); d.ellipse([80,80,520,520],outline=(214,146,30),width=10)
    d.text((300,305),sym,font=F(300),fill=(196,124,16),anchor="mm"); d.text((296,298),sym,font=F(300),fill=(255,232,170),anchor="mm")
    return save(im,name)
def yen_note():
    Wn,Hn=1500,760; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([0,0,Wn-1,Hn-1],26,fill=(226,214,186))
    a=np.asarray(im).copy(); yy,xx=np.mgrid[0:Hn,0:Wn]
    g=(np.sin(xx/14+np.sin(yy/40)*3)*0.5+0.5)*(np.sin(yy/11+np.cos(xx/60)*2)*0.5+0.5)
    for c,v in enumerate((150,120,90)): a[...,c]=np.where(a[...,3]>0,(a[...,c]*(1-0.18*g)+v*0.18*g),a[...,c]).astype(np.uint8)
    im=Image.fromarray(a); d=ImageDraw.Draw(im)
    d.rounded_rectangle([30,30,Wn-31,Hn-31],18,outline=(122,92,58),width=8); d.rounded_rectangle([52,52,Wn-53,Hn-53],12,outline=(150,118,80),width=3)
    d.ellipse([980,150,1380,550],fill=(238,230,210),outline=(150,118,80),width=6)      # watermark window
    d.ellipse([1060,230,1300,470],outline=(200,186,160),width=4)
    d.text((120,120),"10000",font=F(130),fill=(98,70,44)); d.text((120,560),"¥10.000",font=F(70),fill=(98,70,44))
    d.text((740,640),"壱万円",font=cjk(84),fill=(98,70,44),anchor="ms"); d.text((700,170),"日本",font=cjk(70),fill=(122,92,58))
    d.ellipse([560,330,700,470],fill=(196,64,44)); d.text((630,402),"券",font=cjk(70),fill=(240,220,200),anchor="mm")
    d.text((1180,610),"MINH HỌA",font=F(30),fill=(150,118,80),anchor="mm")
    return save(im,"yen_note",0.5)
def notepad():
    Wn,Hn=900,1100; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([20,80,Wn-20,Hn-20],fill=(255,240,160)); d.rectangle([20,80,Wn-20,170],fill=(214,72,52))
    for y in range(240,Hn-40,56): d.line([(40,y),(Wn-40,y)],fill=(150,186,214),width=3)
    d.line([(130,170),(130,Hn-20)],fill=(226,120,120),width=4)
    for x in range(80,Wn-40,70): d.ellipse([x-16,48,x+16,112],outline=(90,90,96),width=9)
    return save(im,"notepad")
def bond(rate,name,col,tag):
    Wn,Hn=1400,860; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rectangle([0,0,Wn-1,Hn-1],fill=(250,246,234))
    d.rectangle([24,24,Wn-25,Hn-25],outline=col,width=10); d.rectangle([48,48,Wn-49,Hn-49],outline=col,width=3)
    for k in range(0,Wn-120,26): d.arc([60+k,60,100+k,100],0,180,fill=col,width=3); d.arc([60+k,Hn-100,100+k,Hn-60],180,360,fill=col,width=3)
    d.text((Wn*0.38,170),"TRÁI PHIẾU CHÍNH PHỦ NHẬT",font=F(56),fill=(60,52,44),anchor="mm")
    d.text((Wn*0.38,240),"JAPANESE GOVERNMENT BOND · 10 NĂM",font=F(32,"SemiBold"),fill=(120,110,96),anchor="mm")
    d.text((Wn*0.38,450),rate,font=F(220),fill=col,anchor="mm"); d.text((Wn*0.38,600),"LÃI SUẤT / NĂM",font=F(44),fill=(90,80,70),anchor="mm")
    d.text((Wn*0.38,700),tag,font=F(36,"SemiBold"),fill=(120,110,96),anchor="mm")
    x0=Wn-330
    for y in range(80,Hn-80,6):
        if (y//12)%2==0: d.line([(x0,y),(x0,y+6)],fill=(150,140,120),width=3)
    for k in range(4):
        y=110+k*165; d.rounded_rectangle([x0+30,y,Wn-80,y+140],10,outline=col,width=4); d.text(((x0+30+Wn-80)/2,y+70),"COUPON",font=F(30),fill=col,anchor="mm")
    return save(im,name,0.5)
def invoice(name,title,amount,seed=1,stamp=True):
    rng=np.random.default_rng(seed); Wn,Hn=760,1000; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    pts=[(0,0),(Wn,0),(Wn,Hn-40)]+[(Wn-i*40-(20 if True else 0),Hn-(0 if i%2==0 else 40)) for i in range(0,Wn//40+1)]
    pts=[(0,0),(Wn,0),(Wn,Hn-40)]; x=Wn
    while x>0: pts+= [(x-20,Hn),(max(0,x-40),Hn-40)]; x-=40
    d.polygon(pts,fill=(255,255,252))
    d.text((Wn/2,90),title,font=F(52),fill=DK,anchor="mm"); d.line([(60,150),(Wn-60,150)],fill=(60,60,60),width=4)
    for k in range(6):
        y=210+k*70; w_=rng.integers(220,420); d.rectangle([60,y,60+w_,y+18],fill=(200,200,204)); d.rectangle([Wn-200,y,Wn-60,y+18],fill=(214,214,218))
    d.line([(60,650),(Wn-60,650)],fill=(60,60,60),width=3)
    d.text((60,720),"TỔNG",font=F(44),fill=DK,anchor="lm"); d.text((Wn-60,720),amount,font=F(56),fill=RD,anchor="rm")
    if stamp:
        st=Image.new("RGBA",(420,170),(0,0,0,0)); sd=ImageDraw.Draw(st); sd.rounded_rectangle([6,6,414,164],18,outline=(214,64,44,230),width=10)
        sd.text((210,88),"PHẢI TRẢ",font=F(70),fill=(214,64,44,230),anchor="mm"); st=st.rotate(-14,expand=True,resample=Image.BICUBIC); im.alpha_composite(st,(Wn-st.width-30,760))
    return save(im,name)
def coin_stack(n,name,col=(236,170,48)):
    Wn=360; ch=34; Hn=n*ch+160; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    dark=tuple(int(c*0.62) for c in col); light=tuple(min(255,int(c*1.12)) for c in col)
    for k in range(n):
        y=Hn-80-k*ch; d.ellipse([10,y-10,Wn-10,y+70],fill=dark); d.rectangle([10,y-40+10,Wn-10,y+30],fill=dark)
        d.arc([10,y-10,Wn-10,y+70],0,180,fill=tuple(int(c*0.42) for c in col),width=4)
        d.ellipse([10,y-50,Wn-10,y+30],fill=col); d.ellipse([40,y-38,Wn-40,y+18],outline=light,width=5)
        for x in range(30,Wn-20,28): d.line([(x,y-6),(x,y+26)],fill=tuple(int(c*0.5) for c in col),width=2)
    return save(im,name,1.0)
def arrow(name,col=RD,up=True,label=None):
    Wn,Hn=420,640; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    P=[(210,10),(410,250),(290,250),(290,630),(130,630),(130,250),(10,250)]
    if not up: P=[(x,Hn-y) for x,y in P]
    d.polygon(P,fill=col)
    if label: d.text((210,430 if up else 210),label,font=F(110),fill=WH,anchor="mm")
    return save(im,name)
def person(name,col):
    S=300; im=Image.new("RGBA",(S,S*2),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([90,20,210,140],fill=col); d.rounded_rectangle([50,160,250,420],90,fill=col); d.rectangle([90,380,140,590],fill=col); d.rectangle([160,380,210,590],fill=col)
    return save(im,name,0.5)
def bank():
    Wn,Hn=900,760; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im); c=(64,70,80); l=(246,244,238)
    d.polygon([(450,20),(870,230),(30,230)],fill=c); d.polygon([(450,70),(780,215),(120,215)],fill=l); d.text((450,165),"¥",font=F(110),fill=c,anchor="mm")
    d.rectangle([60,240,840,290],fill=c)
    for k in range(6): x=110+k*136; d.rectangle([x,310,x+70,640],fill=l,outline=c,width=8)
    d.rectangle([40,650,860,700],fill=c); d.rectangle([10,710,890,750],fill=c)
    return save(im,"bank")
def japan_sil(name="japan_sil",col=(46,46,52),outline=OR):
    rs=[r for r in COUNTRIES["Japan"] if len(r)>8]
    lon,lat=merc_inv(np.vstack(rs)); 
    allp=np.vstack(rs); mn=allp.min(0); mx=allp.max(0); S=1400/(mx-mn).max()
    Wn,Hn=int((mx-mn)[0]*S)+80,int((mx-mn)[1]*S)+80; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    for r in rs:
        P=[(float((p[0]-mn[0])*S+40),float((mx[1]-p[1])*S+40)) for p in r]; d.polygon(P,fill=col,outline=outline,width=6 if outline else 0)
    return save(im,name,0.5)
def build_all():
    baby(); coin(); coin("$","coin_usd"); yen_note(); notepad(); bank(); japan_sil(); japan_sil("japan_or",OR,None)
    bond("0,1%","bond_old",(96,128,110),"phát hành giai đoạn 2016–2021"); bond("~3%","bond_new",RD,"lợi suất 10 năm hiện nay ≈ 3%")
    for i in range(6): invoice(f"inv{i}","HÓA ĐƠN TIỀN LÃI",["13 nghìn tỷ ¥","+24%","¥¥¥","13 nghìn tỷ ¥","¥¥¥","+1%"][i],i,stamp=i%2==0)
    coin_stack(6,"stack6"); coin_stack(10,"stack10"); coin_stack(14,"stack14"); coin_stack(4,"stack4",(170,176,186)); coin_stack(9,"stack9g",(170,176,186))
    arrow("arr_up",RD,True,"%"); arrow("arr_dn",(90,110,130),False); arrow("arr_up_or",OR,True)
    person("pers_g",(160,166,176)); person("pers_o",OR); person("pers_d",(60,64,72))
if __name__=="__main__" and len(__import__("sys").argv)==1: build_all(); print(sorted(os.listdir("assets/cut")))
# ---------------- coffee set (video03) ----------------
def _bean(d,cx,cy,rx,ry,ang,col=(92,52,30),crease=(40,22,12)):
    b=Image.new("RGBA",(int(rx*2.6),int(rx*2.6)),(0,0,0,0)); bd=ImageDraw.Draw(b); c=b.width/2
    bd.ellipse([c-rx,c-ry,c+rx,c+ry],fill=col); bd.ellipse([c-rx*0.8,c-ry*0.85,c+rx*0.3,c-ry*0.1],fill=tuple(min(255,int(v*1.35)) for v in col))
    bd.arc([c-rx*0.25,c-ry*0.95,c+rx*0.25,c+ry*0.95],100,260,fill=crease,width=max(3,int(rx*0.12)))
    return b.rotate(ang,expand=False,resample=Image.BICUBIC)
def beans(name="beans",n=70,green=False,seed=3):
    rng=np.random.default_rng(seed); S=900; im=Image.new("RGBA",(S,int(S*0.62)),(0,0,0,0))
    col=(150,160,96) if green else (92,52,30); cr=(96,104,60) if green else (40,22,12)
    for k in range(n):
        u=rng.random(); x=S/2+(rng.random()-0.5)*S*0.85*(1-0.5*u); y=im.height*0.92-u*im.height*0.75*(1-abs(x-S/2)/(S*0.5))
        rx=rng.uniform(38,50); b=_bean(None,0,0,rx,rx*0.72,rng.uniform(0,360),tuple(int(v*rng.uniform(0.85,1.1)) for v in col),cr)
        im.alpha_composite(b,(int(x-b.width/2),int(y-b.height/2)))
    return save(im,name,0.6)
def sack(name="sack",label="60 KG",col=(196,160,104),green=True):
    Wn,Hn=760,900; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.polygon([(120,170),(640,170),(700,820),(380,880),(60,820)],fill=col)
    a=np.asarray(im).copy(); yy,xx=np.mgrid[0:Hn,0:Wn]; g=((xx//6+yy//6)%2)*10
    for c in range(3): a[...,c]=np.where(a[...,3]>0,np.clip(a[...,c].astype(int)-g,0,255),a[...,c])
    im=Image.fromarray(a); d=ImageDraw.Draw(im)
    d.ellipse([110,90,650,250],fill=tuple(int(v*0.8) for v in col)); d.ellipse([150,110,610,230],fill=(70,40,22))
    for k in range(26):
        x=170+(k*37)%430; y=130+(k*23)%80; d.ellipse([x,y,x+40,y+28],fill=(150,160,96) if green else (92,52,30))
    d.rectangle([180,460,580,620],outline=(120,70,40),width=8); d.text((380,540),label,font=F(84),fill=(120,70,40),anchor="mm")
    d.text((380,700),"VIỆT NAM",font=F(52),fill=(120,70,40),anchor="mm")
    return save(im,name,0.6)
def pouch(name="pouch",brand="RANG XAY",col=(36,30,28),band=OR):
    Wn,Hn=620,900; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.rounded_rectangle([40,60,580,880],40,fill=col); d.rectangle([40,60,580,140],fill=tuple(min(255,v+30) for v in col))
    for x in range(60,580,14): d.line([(x,70),(x,130)],fill=tuple(min(255,v+50) for v in col),width=3)
    d.rectangle([40,380,580,560],fill=band); d.text((310,470),brand,font=F(70),fill=DK,anchor="mm")
    d.ellipse([235,600,385,750],outline=band,width=8); im.alpha_composite(_bean(None,0,0,48,34,30,(160,100,60),(80,40,20)),(250,615))
    d.text((310,250),"CÀ PHÊ",font=F(84),fill=WH,anchor="mm")
    return save(im,name,0.6)
def tag(name="tag",col=(255,255,252)):
    Wn,Hn=900,330; im=Image.new("RGBA",(Wn,Hn),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.polygon([(0,165),(120,0),(Wn,0),(Wn,Hn),(120,Hn)],fill=col); d.ellipse([70,140,120,190],fill=(0,0,0,0))
    a=np.asarray(im).copy(); a[140:191,70:121][((np.mgrid[140:191,70:121][0]-165)**2+(np.mgrid[140:191,70:121][1]-95)**2)<25**2]=0; im=Image.fromarray(a)
    ImageDraw.Draw(im).ellipse([70,140,120,190],outline=(150,150,150),width=4)
    return save(im,name,1.0)
def cup(name="cup"):
    S=700; im=Image.new("RGBA",(S,S),(0,0,0,0)); d=ImageDraw.Draw(im)
    d.ellipse([60,560,640,660],fill=(230,226,220)); d.polygon([(150,250),(550,250),(500,600),(200,600)],fill=(250,248,244))
    d.ellipse([150,215,550,290],fill=(250,248,244)); d.ellipse([170,228,530,280],fill=(70,40,22)); d.arc([500,300,640,470],-90,90,fill=(250,248,244),width=30)
    for k,x in enumerate((280,350,420)): d.arc([x-30,60,x+30,200],90+40*k,270+40*k,fill=(200,200,200,160),width=10)
    return save(im,name,0.6)
def build_coffee():
    os.makedirs("assets/cut",exist_ok=True)
    beans("beans"); beans("beans_g",green=True,seed=5); sack("sack"); pouch("pouch"); tag("tag"); cup("cup")
    arrow("arr_dn",RD,False); arrow("arr_up_or",OR,True); arrow("arr_dn_g",(90,110,130),False)
    coin_stack(10,"stack10"); coin_stack(4,"stack4",(170,176,186))
if __name__=="__main__" and len(__import__("sys").argv)>1: build_coffee(); print(sorted(os.listdir("assets/cut")))
