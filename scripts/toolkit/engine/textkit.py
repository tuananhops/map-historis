# Hinton Media text kit — implements "Quy tắc chữ" (nqs_kinhte/style_guide.md §9) as reusable presets.
#   roles/hierarchy, VN number format, safe-zone clamp, bounce entry, keyword stacks, numbered lists,
#   question card, source credit, plus a TEXTLOG used by the QA checker.
from mlayers import *
SAFE=(80,200,920,1400)                      # x0,y0,x1,y1 for graphic text (TikTok UI-safe)
# role -> (size, weight, ALL CAPS?)
ROLE={"hero":(170,"ExtraBold",True),"key":(104,"ExtraBold",True),"title":(80,"Bold",True),"label":(56,"Bold",True),
      "map":(34,"Bold",True),"cap":(34,"Bold",True),"item":(50,"SemiBold",False),"axis":(28,"SemiBold",False),"src":(22,"SemiBold",True)}
GREY=(200,206,210); SRC_W=(255,255,255,178); SRC_D=(60,60,64,178)
TEXTLOG=[]                                   # (scene, text, role, (x0,y0,x1,y1), at)
CUR=[None]
def vnum(v,dec=0): return vn(v,dec)          # 7.000 ; 43,1
def caps(t):
    out=t.upper()
    return out.replace("KG","KG")
GLOW_OR=(255,153,0); GLOW_RD=(255,51,51); EXT_DARK=(51,51,51); EXT_BROWN=(62,38,22)
def fx_layers(im,org,text,f,color,fx,anchor="ls"):
    """effects_study B: 'glow' = dark shadow + outer glow (#FF9900 ~15px, red #FF3333 ~20px for negatives);
       'extrude' = 10-step 3D extrusion (+1,+1) in dark grey/brown, no blur; else 40% drop shadow."""
    if fx=="glow" or fx=="glow_red":
        gc=GLOW_RD if (fx=="glow_red" or color==RD) else GLOW_OR; r=20 if gc==GLOW_RD else 15
        sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((org[0],org[1]+6),text,font=f,fill=(0,0,0,150),anchor=anchor)
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(12)))
        m=Image.new("L",im.size,0); ImageDraw.Draw(m).text(org,text,font=f,fill=255,anchor=anchor)
        g=m.filter(ImageFilter.GaussianBlur(r)); g=g.point(lambda v:min(150,int(v*1.25)))
        gl=Image.new("RGBA",im.size,gc+(0,)); gl.putalpha(g); im.alpha_composite(gl)
        color=tuple(int(c+(255-c)*0.22) for c in color[:3])+tuple(color[3:])   # brighter core so the glyph stays crisp
    elif fx in("extrude","extrude_brown"):
        dc=EXT_BROWN if fx=="extrude_brown" else EXT_DARK; d=ImageDraw.Draw(im)
        for i in range(10,0,-1): d.text((org[0]+i,org[1]+i),text,font=f,fill=dc+(255,),anchor=anchor)
    ImageDraw.Draw(im).text(org,text,font=f,fill=color,anchor=anchor)
@functools.lru_cache(None)
def txt(text,role="key",color=WH,shadow=True,size=None,weight=None,fx=None):
    """text sprite in a hierarchy role. shadow = 40% black, 5px down, blur 10 (map/photo legibility).
    fx: None | 'glow' (orange, or red if color==RD) | 'glow_red' | 'extrude' | 'extrude_brown'"""
    sz,wt,up=ROLE[role]; sz=size or sz; wt=weight or ("Black" if fx and fx.startswith("glow") and sz>=90 else wt)
    if up: text=caps(text)
    f=fnt(sz,wt); asc,desc=f.getmetrics(); d=ImageDraw.Draw(Image.new("L",(1,1)))
    b=d.textbbox((0,0),text,font=f,anchor="ls"); pad=26 if not fx else 70
    im=Image.new("RGBA",(b[2]-b[0]+2*pad,asc+desc+2*pad),(0,0,0,0)); org=(pad-b[0],pad+asc)
    if fx: fx_layers(im,org,text,f,color,fx)
    else:
        if shadow:
            sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((org[0],org[1]+5),text,font=f,fill=(0,0,0,102),anchor="ls")
            im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(5)))   # blur radius ~ 10px kernel
        ImageDraw.Draw(im).text(org,text,font=f,fill=color,anchor="ls")
    sp=pil2spr(im,base=pad+asc,cw=b[2]-b[0]); sp.ink=(b[0]+org[0],b[1]+org[1],b[2]+org[0],b[3]+org[1]); sp.text=text; sp.size=sz
    return sp
def ink_box(sp,cx,cy):
    x0,y0,x1,y1=sp.ink; return (cx-sp.w/2+x0,cy-sp.h/2+y0,cx-sp.w/2+x1,cy-sp.h/2+y1)
def clamp_xy(sp,cx,cy,safe=SAFE):
    """move a sprite centre so its ink box sits inside the safe zone"""
    x0,y0,x1,y1=ink_box(sp,cx,cy); sx0,sy0,sx1,sy1=safe
    if x1-x0>sx1-sx0: cx+=(sx0+sx1)/2-(x0+x1)/2
    elif x0<sx0: cx+=sx0-x0
    elif x1>sx1: cx-=x1-sx1
    if y0<sy0: cy+=sy0-y0
    elif y1>sy1: cy-=y1-sy1
    return cx,cy
def log(sc,text,role,box,at): TEXTLOG.append((sc.name,text,role,tuple(round(v) for v in box),round(at,2)))
def K(sc,text,role,color,x,y,at,align="c",kind="bounce",shadow=True,mot=None,sfx="pop",clamp=True,**kw):
    """place one keyword. (x,y)= centre of ink (align c) or left/right edge of ink (align l/r). Bounce in on the spoken word."""
    sp=txt(text,role,color,shadow,**kw)
    if clamp:                                  # auto-fit: shrink until the line fits the safe width
        sz=kw.pop("size",None) or ROLE[role][0]
        while sp.ink[2]-sp.ink[0]>SAFE[2]-SAFE[0] and sz>30: sz-=2; sp=txt(text,role,color,shadow,size=sz,**kw)
    iw=sp.ink[2]-sp.ink[0]; ih=sp.ink[3]-sp.ink[1]
    icx=x if align=="c" else x+iw/2 if align=="l" else x-iw/2
    cx=icx-((sp.ink[0]+sp.ink[2])/2-sp.w/2); cy=y-((sp.ink[1]+sp.ink[3])/2-sp.h/2)
    if clamp: cx,cy=clamp_xy(sp,cx,cy)
    sc.add(Item(sp,cx,cy,at,kind,mot))
    if sfx: sc.ev(at,sfx,0.5)
    box=ink_box(sp,cx,cy); log(sc,sp.text,role,box,at); return box
class FxCounter(Counter):
    """rolling number with glow/extrude (effects_study B)"""
    def spr(s,txt_):
        if txt_ not in s.cache:
            f=fnt(s.size,s.w); im=Image.new("RGBA",(s.tw+2*s.pad,s.asc+s.desc+2*s.pad),(0,0,0,0)); org=(s.pad+s.tw/2,s.pad+s.asc)
            fx_layers(im,org,txt_,f,s.color,s.fx,anchor="ms"); s.cache[txt_]=pil2spr(im,base=s.pad+s.asc)
        return s.cache[txt_]
def KC(sc,role,color,x,y,at,v1,dec=0,pre="",suf="",dur=0.7,q=None,v0=0,shadow=True,mot=None,size=None,fx=None):
    """rolling number in a role; intermediate values quantised to q (default: 1 unit of the last shown decimal)"""
    sz,wt,_=ROLE[role]; sz=size or sz; suf=caps(suf); pre=caps(pre)
    if fx: wt="Black" if fx.startswith("glow") and sz>=90 else wt
    c=(FxCounter if fx else Counter)(x,0,at,dur,v0,v1,dec,sz,color,pre,suf,wt,"bounce",mot,5 if shadow else 0)
    if fx: c.fx=fx; c.pad=70
    c.q=q if q is not None else (10**-dec if dec else max(1,10**(len(str(int(abs(v1))))-2)))
    f=fnt(sz,wt); asc=f.getmetrics()[0]; capH=sz*0.72
    c.base_y=y+capH/2; c.cx=x
    tw=c.cw; box=(x-tw/2,y-capH/2,x+tw/2,y+capH/2)
    dx=0
    if box[0]<SAFE[0]: dx=SAFE[0]-box[0]
    if box[2]>SAFE[2]: dx=SAFE[2]-box[2]
    c.cx+=dx; box=(box[0]+dx,box[1],box[2]+dx,box[3])
    sc.add(c); sc.ev(at,"pop",0.5); [sc.ev(at+k*0.07,"tick",0.4) for k in range(int(dur/0.07))]
    log(sc,c.fmt(v1),role,box,at); return box
def stack(sc,x,y,rows,align="c",gap=None):
    """vertical keyword block. rows: (text|dict(ctr=...), role, color, at). y = top of block. hierarchy-aware spacing."""
    boxes=[]; cy=y
    for r in rows:
        if r is None: cy+=24; continue
        text,role,color,at=r[:4]; sz=ROLE[role][0]; h=sz*0.74
        cy+=h/2
        if isinstance(text,dict): b=KC(sc,role,color,x,cy,at,**text)
        else: b=K(sc,text,role,color,x,cy,at,align)
        boxes.append(b); cy+=h/2+(gap if gap is not None else max(18,sz*0.30))
    return boxes
def src(sc,text,x,y,at,dark=True,align="c"):
    """source credit: 22 px caps, white 70% (dark text on paper), directly under the data point"""
    col=SRC_W if dark else SRC_D
    return K(sc,text,"src",col,x,y,at,align,kind="fade",shadow=dark,sfx=None)
def listing(sc,title,items,x0,y0,t_title,dark=True,title_col=None,step=118,isize=54):
    """bold caps title + orange numerals + sentence-case items sliding in from the left on the spoken word"""
    base=WH if dark else DK
    K(sc,title,"title",title_col or base,x0,y0,t_title,align="l")
    y=y0+ROLE["title"][0]*0.5+70
    for i,(t,at) in enumerate(items):
        y+=step if i else 40
        n=txt(str(i+1),"key",OR,dark,size=84)
        nx=x0+(n.ink[2]-n.ink[0])/2; ncx=nx-((n.ink[0]+n.ink[2])/2-n.w/2); ncy=y-((n.ink[1]+n.ink[3])/2-n.h/2)
        sc.add(Item(n,ncx,ncy,at,"bounce")); log(sc,str(i+1),"key",ink_box(n,ncx,ncy),at)
        sp=txt(t,"item",base,dark,size=isize,weight="Bold")
        ix=x0+80; cx=ix+sp.w/2-sp.ink[0]; cy=y-((sp.ink[1]+sp.ink[3])/2-sp.h/2)+4
        cx,cy=clamp_xy(sp,cx,cy); sc.add(Item(sp,cx,cy,at,"slide")); sc.ev(at,"swish",0.5); log(sc,sp.text,"item",ink_box(sp,cx,cy),at)
    return y
def qcard(sc,lines,cy=760,size=84,dark=True,alt=(WH,OR),scrim=True):
    """central question card: centred caps 70-90 px, lines alternate white/orange, phrase-by-phrase bounce"""
    for t,_ in lines:                         # auto-shrink so every line fits the safe width (min 70 px)
        while size>70 and (lambda sp:sp.ink[2]-sp.ink[0])(txt(t,"title",WH,True,size=size))>SAFE[2]-SAFE[0]: size-=2
    n=len(lines); lh=size*1.18; y=cy-lh*(n-1)/2
    if scrim: sc.add(Item(glow_spr(1300,(0,0,0),120),540,cy,0.0,"fade"))
    out=[]
    for i,(t,at) in enumerate(lines):
        col=alt[i%2] if dark else (DK,OR)[i%2]
        out.append(K(sc,t,"title",col,540,y+i*lh,at,size=size)); 
    return out
# -------- subtitle-free guard: scenes flagged sub=True must not get graphic text (checked in QA)
