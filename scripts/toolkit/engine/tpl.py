# tpl — high-level SCENE TEMPLATES (fast production). Each returns (sc, bg). Text is added with K/KC/KX/stack/listing/src.
#   from tpl import *          (in a project's scenes.py, after `new` timeline exists)
from scenekit import *
def dur_of(name): a,b,s=TL[name]; return (b-a)/FPS
# ---------------- satellite / globe (presenter-replacement beats; usually SUB) ----------------
def T_satfly(name,target,region="vn",R1=60000,snap=True,start=(100,5),tilt=0.55):
    """globe → target. snap=True: last part is a snap zoom (EaseInOutExpo + radial blur, whoosh)."""
    d=dur_of(name); ts=max(0.6,d*0.35); tsn=min(0.62,d*0.25)
    holder={}
    def p(t):
        c=e_out((t-0.2)/max(0.5,ts+tsn)); lon=lerp(start[0],target[0],c); lat=lerp(start[1],target[1],c)
        if snap:
            if t<ts: R=log_lerp(340,2400,e_io(t/ts))
            else: R=log_lerp(2400,R1,holder["u"](t)) if "u" in holder else 2400
            R*=1+0.06*cl((t-ts-tsn)/max(0.1,d-ts-tsn))
        else: R=log_lerp(340,R1,e_io(t/max(0.5,d*0.8)))
        return lon,lat,R,-8*e_sine(t/d),tilt*e_io((t-ts)/max(0.3,d-ts))
    bg=SatCam(p,region); sc=new(name,bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.8)
    if snap: holder["u"]=snap_zoom(sc,ts,int(tsn*FPS))
    sat_hsts(sc,bg,0.0,d); return sc,bg
def T_sathold(name,target,region="vn",R=(60000,80000),rot=(20,8),tilt=0.5,dlon=0.06,dlat=-0.03):
    d=dur_of(name)
    def p(t): u=e_sine(t/d); return target[0]+dlon*u,target[1]+dlat*u,log_lerp(R[0],R[1],u),lerp(rot[0],rot[1],u),tilt
    bg=SatCam(p,region); sc=new(name,bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.6); sat_hsts(sc,bg,0,d); return sc,bg
def T_globe(name,a,b,R=470,region="globe"):
    d=dur_of(name)
    def p(t): u=e_io(t/d); return lerp(a[0],b[0],u),lerp(a[1],b[1],u),R*(1+0.04*u),0,0,820
    bg=SatCam(p,region); sc=new(name,bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.8); sat_hsts(sc,bg,0,d); return sc,bg
def T_zoomout(name,frm,region="vn",R0=200000,to=(108,14)):
    d=dur_of(name); tz=min(4.0,d*0.75)
    def p(t):
        if t<tz: u=e_io(t/tz); return lerp(frm[0],to[0],u),lerp(frm[1],to[1],u),log_lerp(R0,470,u),-10*(1-u),0.5*(1-e_out(t/1.4)),820
        return to[0]-4*(t-tz),to[1],470,0,0,820
    bg=SatCam(p,region); sc=new(name,bg,"map",credit=CR_SAT); sc.ev(0,"whoosh",0.9); sat_hsts(sc,bg,0,d); return sc,bg
# ---------------- vector maps ----------------
VN_HS=(112.0,16.4)
def T_map(name,center,k,sy=880,dark=0.9,zoom=0.06,glow=(),fill=(),pins=(),routes=(),hs=None,fly=None,snap_at=None,kind="map"):
    """dark-teal vector map. glow/fill: [(country, at)], pins [(lon,lat,at[,color])], routes [((a),(b),at,bend[,color,width])].
    fly=(center0,k0,t) eases in from a wider view; snap_at=t adds a snap zoom (x2.4) with radial blur at t.
    hs: True/False to force Hoàng Sa/Trường Sa labels (auto when Vietnam is in view)."""
    d=dur_of(name); hold={}
    def p(t):
        c,kk=center,k
        if fly:
            e=e_io(t/fly[2]); c=(lerp(fly[0][0],center[0],e),lerp(fly[0][1],center[1],e)); kk=log_lerp(fly[1],k,e)
        if snap_at is not None and "u" in hold: kk=kk*log_lerp(1,2.4,hold["u"](t))
        return c[0],c[1],kk*(1+zoom*e_sine(t/d)),0,sy
    bg=VecBg(p,dark); sc=new(name,bg,kind,credit=CR_NE); sc.ev(0,"whoosh",0.7)
    if snap_at is not None: hold["u"]=snap_zoom(sc,snap_at,18,0.2,540,sy)
    for c_,at in glow: sc.add(CountryFX(bg,[c_],stroke=(at,at+1.0),fill=(at+0.3,at+0.9),alpha=0.8,pulse=0.12,nstroke=3))
    for c_,at in fill: sc.add(CountryFX(bg,[c_],fill=(at,at+0.4),alpha=0.6,glow=0.3))
    for r in routes:
        a,b_,at,bend=r[:4]; col=r[4] if len(r)>4 else OR; wd=r[5] if len(r)>5 else 5
        sc.add(Route(bg,a,b_,at,0.8,bend,col,wd)); sc.ev(at,"swish",0.4)
    for pn in pins: sc.add(GlowPin(bg,pn[0],pn[1],pn[2],pn[3] if len(pn)>3 else OR,12)); sc.ev(pn[2],"pop",0.6)
    if hs is None:
        bg.at(d/2); P=P1(bg,*VN_HS); hs=(0<P[0]<W and 150<P[1]<1750)
    if hs: hsts(sc,bg,0.1,20,True)
    return sc,bg
def map_bar(sc,bg,lon,lat,at,v,scale,label,name=None,col=OR,w=64,dx_name=0,dy_name=44,lab_fx=None):
    b=Bar3D(lambda t,bg=bg:tuple(P1(bg,lon,lat)),at,v*scale,0.7,w,col); sc.add(b); sc.ev(at,"swish",0.5)
    P=P1(bg.at(1.0),lon,lat); K(sc,label,"label",WH,P[0]+8,P[1]-v*scale-60,at+0.25,fx=lab_fx)
    if name: K(sc,name,"map",WH,P[0]+dx_name,P[1]+dy_name,at+0.1,sfx=None)
# ---------------- flat backgrounds ----------------
def T_paper(name,tone="grey",seed=None,kind="collage"):
    bg=drift(paper_bg(tone,seed or (abs(hash(name))%90+10))); sc=new(name,bg,kind); return sc,bg
def T_dark(name,seed=5,globe=True,kind="kinetic"):
    bg=drift(dark_bg(seed),z=(1.0,1.05)); sc=new(name,bg,kind); sc.ev(0,"whoosh",0.8)
    if globe: sc.add(BottomGlobe(VEQ,2140,900,-35,5,10,0.0,0.6))
    return sc,bg
def T_question(name,lines,cy=760,size=88):
    sc,bg=T_dark(name); sc.zblur=True
    qcard(sc,[(l,sc.w(w)) for l,w in lines],cy=cy,size=size,alt=(WH,OR)); return sc,bg
def T_openq(name,lines,cy=600,size=86,cuts=()):
    sc,bg=T_dark(name,6,False); sc.zblur=True
    qcard(sc,[(l,sc.w(w)) for l,w in lines],cy=cy,size=size)
    for nm,x,y,w_,h_,word in cuts: cutout(sc,nm,x,y,sc.w(word),w_,h_,kind="drop",gsize=380)
    return sc,bg
def T_end(name="end"):
    sc=new(name,drift(dark_bg(7),z=(1.0,1.06)),"end",brand=False); sc.zblur=True; sc.ev(0,"whoosh",0.8)
    sc.add(BottomGlobe(VEQ,2120,900,100,5,14,0.0,0.8))
    sc.add(Item(glow_spr(900,OR,60),540,560,0.0,"pop",(0,10,4,0)))
    sc.add(Strike(450,630,336,0.05,0.3,OR,12))
    sc.add(Item(txt("HINTON","hero",WH,fx="glow",size=160),540,470,sc.w("hinton")-0.1,"bounce")); sc.ev(sc.w("hinton")-0.1,"pop",0.7)
    sc.add(Item(txt("MEDIA","hero",OR,fx="glow",size=160),540,630,sc.w("media")-0.1,"bounce")); sc.ev(sc.w("media")-0.1,"pop",0.7)
    sc.add(Item(pill_spr("+  THEO DÕI",52,OR,DK),540,841,sc.w("để")-0.25,"bounce",pulse=0.045)); sc.ev(sc.w("để")-0.25,"boom",0.6)
    sc.add(Item(tsp("để hiểu kinh tế mỗi ngày",46,(176,176,180),"Bold"),540,975,sc.w("hiểu"),"bounce")); sc.ev(sc.w("hiểu"),"swish",0.4)
    for t_,r_,b_ in [("HINTON","hero",(540-300,470-60,540+300,470+60)),("MEDIA","hero",(540-260,630-60,540+260,630+60)),("+ THEO DÕI","label",(380,800,700,880)),("để hiểu kinh tế mỗi ngày","item",(290,950,790,1000))]: log(sc,t_,r_,b_,0)
    return sc,None
# ---------------- widgets ----------------
def hbar(sc,y,frac,at,col,x0=90,x1=910,h=32,track=(150,150,156)):
    def f(fr,t,cam):
        fr[int(y-h/2):int(y+h/2),x0:x1]=fr[int(y-h/2):int(y+h/2),x0:x1]*0.8+0.2*np.float32(track)/255
        if t<at: return
        p=e_out((t-at)/0.7); fr[int(y-h/2):int(y+h/2),x0:int(x0+(x1-x0)*frac*p)]=np.float32(col)/255
    sc.add(Fn(f)); sc.ev(at,"swish",0.4)
def bar_rows(sc,rows,y0,step=185,dark=False,x0=90,x1=910):
    """rows: (label, value_text, frac, color, at)  — label left, value right, bar below"""
    lc=MG if not dark else GREY
    for i,(lab,val,frac,col,at) in enumerate(rows):
        y=y0+i*step
        K(sc,lab,"cap",lc,x0,y,at,align="l",shadow=dark); K(sc,val,"key",col,x1,y-10,at+0.1,align="r",shadow=dark,size=88)
        hbar(sc,y+80,frac,at+0.1,col,x0,x1)
def tag(sc,x,y,at,head,val,unit,col=DK,strike_at=None,counter=None,chach=True,ctr_from=None,size=None):
    sc.add(Item(cut_spr("tag",600,220),x,y,at-0.1,"right",(0.5,2,3.5,0))); sc.ev(at-0.1,"swish",0.5)
    K(sc,head,"cap",MG,x+20,y-70,at,shadow=False)
    if counter: KC(sc,"key",col,x+20,y+20,at,counter,dur=0.7,q=1000,v0=ctr_from or 0,shadow=False)
    else: K(sc,val,"key",col,x+20,y+20,at,shadow=False,size=size)
    K(sc,unit,"cap",MG,x+20,y+92,at+0.3,shadow=False)
    if chach: chaching(sc,at+0.05)
    if strike_at is not None: sc.add(Strike(x-180,x+220,y+20,strike_at,0.3,RD,14),"swish",strike_at,0.6)
def neon_cut(sc,name,x,y,at,w=380,h=380,glow=True,color=OR):
    cutout(sc,name,x,y,at,w,h,kind="drop",glow=glow); sc.add(NeonOutline(name,x,y,at+0.35,w,h,color,mot=MOT_CUT))
def finish(transitions=True):
    SCENES.sort(key=lambda s:s.f0)
    for a,b in zip(SCENES,SCENES[1:]): assert a.f1==b.f0,(a.name,b.name,a.f1,b.f0)
    assert SCENES[0].f0==0
    used=auto_transitions(SCENES) if transitions else []
    json.dump(used,open("assets/transitions.json","w"))
    return used
