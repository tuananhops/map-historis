# Generic scene builder: copied into each job dir as scenes.py; builds every scene from topic.json with histkit templates.
import json
from histkit import *
import histkit
from sat import region
T=json.load(open("topic.json"))
histkit.EXCL=set(T.get("exclude_countries",[]))
for k,v in T.get("sat_regions",{}).items(): region(k,v)
CAPC=mk_credit(T.get("map_credit","Ảnh vệ tinh: NASA Blue Marble · Sentinel-2 cloudless © EOX (CC BY 4.0) · ranh giới minh hoạ"))
COL={"red":RD,"gold":GOLD,"orange":OR,"white":WH,"blue":(110,190,255),"green":(80,220,120)}
def col(c): return COL.get(c,c) if isinstance(c,str) else tuple(c)
def polys(spec):
    out=[]
    for p in spec: out.append(p if isinstance(p,str) else [tuple(x) for x in p])
    return out
def at_of(sc,v,default=0.0):
    if v is None: return default
    if isinstance(v,(int,float)): return float(v)
    try: return sc.w(v)
    except KeyError: return default
for S in T["scenes"]:
    n=S["name"]; ty=S["type"]; d=dur_of(n)
    if ty=="intro":
        sc=earth_intro(n,tuple(S["to"]),S.get("R",5200),tuple(S.get("start",[30,30])),S.get("zoom_at",0.5)); sc.credit=CAPC
        title(sc,S.get("title","Bạn có biết?"),col(S.get("title_color","orange")),330,0.05,104); sc.hit(0.1)
    elif ty=="map":
        keys=[(f*d,lo,la,k) for f,lo,la,k in S["cam"]]
        sc,bg=satscene(n,keys,tuple(S.get("layers",[])),S.get("sy",900),S.get("drift",0.04),CAPC)
        st=[(polys(x["polys"]),at_of(sc,x.get("at"),0.2),x.get("dur",1.0)) for x in S.get("territories",[])]
        if st: sc.add(EmpireFX(bg,st,alpha=S.get("territory_alpha",0.48)))
        g=S.get("glow")
        if g: sc.add(DaiVietFX(bg,at_of(sc,g.get("at"),0.3),0.6,g.get("alpha",0.7)))
        if S.get("hs_ts"): hsts(sc,bg,0.2,22)
        for a in S.get("armies",[]):
            at=at_of(sc,a.get("at"),0.2); sc.add(ArmyDots(bg,tuple(a["from"]),tuple(a["to"]),at,a.get("dur",1.2),a.get("n",36),col(a.get("color","red")),a.get("bend",0.15),a.get("spread",34),7,a.get("seed",1)))
            sc.ev(at,a.get("sfx","horse"),0.8)
        for p in S.get("pins",[]):
            at=at_of(sc,p.get("at"),0.3); sc.add(GlowPin(bg,*p["ll"],at,col(p.get("color","orange")),12)); sc.ev(at,"pop",0.6)
            if p.get("label"): pin_label(sc,bg,p["label"],tuple(p["ll"]),at+0.1,p.get("dx",0),p.get("dy",-58))
        for s_ in S.get("ships",[]):
            def fl(fr,t,cam,bg=bg,s_=s_,d=d):
                for i in range(s_.get("n",10)):
                    u=e_io(t/d); a,b=s_["from"],s_["to"]; lo=lerp(a[0]+0.04*(i%4),b[0]+0.01*(i%4),u); la=lerp(a[1]-0.05*(i//4),b[1]-0.01*(i//4),u)
                    P=P1(bg,lo,la); blit(fr,ship_spr(col(s_.get("color","red")) if s_.get("color")!="red" else RD2,s_.get("size",64)),P[0],P[1],1.0,s_.get("rot",155))
            sc.add(Fn(fl))
        if S.get("hud"): h=S["hud"]; hud(sc,[(h["year"],h.get("caption",""),0.0)],col=col(h.get("color","red")))
        elif S.get("title"): title(sc,S["title"],col(S.get("title_color","orange")),330,0.1)
        if S.get("counter"):
            c=S["counter"]; at=at_of(sc,c.get("at"),0.6); scrim(sc,200,700,0.5)
            KC(sc,"hero",col(c.get("color","white")),540,520,at,c["value"],dur=0.7,fx="glow"); K(sc,c.get("label",""),"label",OR,540,640,at+0.3); sc.hit(at+0.05)
        for x in S.get("xstamps",[]):
            at=at_of(sc,x.get("at"),d*0.7); P=P1(bg.at(min(d,at+0.3)),*x["ll"]); xstamp(sc,P[0],P[1],at); sc.ev(at,"clash",0.7)
        for e in S.get("sfx",[]): sc.ev(at_of(sc,e.get("at"),0),e["kind"],e.get("gain",0.8))
    elif ty=="image":
        kb=S.get("kb",{}); sc=new(n,KB(S["file"],tuple(kb.get("z",[1.0,1.25])),tuple(kb.get("fx",[0.5,0.5])),tuple(kb.get("fy",[0.5,0.42])),d),"photo",credit=mk_credit(S.get("credit","")))
        sc.ev(0,"whoosh",0.9)
        for e in S.get("sfx",[]): sc.ev(at_of(sc,e.get("at"),0),e["kind"],e.get("gain",0.8))
        if S.get("title"): title(sc,S["title"],col(S.get("title_color","orange")),330,0.15)
    elif ty=="photo":
        if S.get("bg","paper")=="paper": sc,_=T_paper(n,"warm"); fx="extrude_brown"
        else: sc=new(n,KB(S["file"],(1.1,1.25),(0.5,0.5),(0.4,0.35),d,blur=18,dark=0.55),"photo"); fx="glow"
        sc.credit=mk_credit(S.get("credit","")); sc.ev(0,"whoosh",0.8)
        if S.get("title"): title(sc,S["title"],col(S.get("title_color","orange")),330,0.0,104,fx); sc.hit(0.05)
        sc.add(Item(polaroid(S["file"],S.get("width",640),S.get("rot",-3),tuple(S["crop"]) if S.get("crop") else None),540,S.get("y",860),0.25,"drop",(0,6,3.2,0))); sc.ev(0.25,"boom",0.8)
        if S.get("caption"): K(sc,S["caption"],"cap",DK if S.get("bg","paper")=="paper" else WH,540,1330,at_of(sc,S.get("caption_at"),0.8),shadow=False)
    elif ty=="outro":
        earth_outro(n,tuple(S.get("from",[106,21])),S.get("title1","Lịch sử thế giới"),S.get("title2","qua bản đồ"),T.get("brand","HINTON MEDIA")).credit=CAPC
    else: raise ValueError(ty)
add_captions(1250)
USED=finish()
