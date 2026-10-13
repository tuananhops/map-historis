# Hinton Media v3 motion-graphics engine: per-frame compositing with numpy/OpenCV, cached sprite layers.
import os, json, math, functools
import numpy as np, cv2
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance, ImageOps
cv2.setNumThreads(1)
TK=os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
ROOT=os.environ.get("HINTON_PROJECT",os.getcwd()); os.chdir(ROOT)
W,H,FPS=1080,1920,30
SW,SH=1296,2304          # background source size (1.2x) for subpixel drift
FD=os.path.join(TK,"assets","fonts")+"/"
OR=(236,160,53); DOR=(190,112,14); DK=(26,26,28); MG=(96,94,90); RD=(214,64,44); WH=(255,255,255)
CARD=(252,250,246); YEL=(255,206,84); SEA=(214,228,236)
@functools.lru_cache(None)
def fnt(s,w="Bold"): return ImageFont.truetype(FD+f"BeVietnamPro-{w}.ttf",s)
# ---------- easing ----------
def cl(x): return 0.0 if x<0 else 1.0 if x>1 else x
def e_back(x,s=1.70158): x=cl(x)-1; return 1+(s+1)*x**3+s*x**2
def e_out(x): x=cl(x); return 1-(1-x)**3
def e_io(x): x=cl(x); return 4*x**3 if x<.5 else 1-(-2*x+2)**3/2
def e_sine(x): x=cl(x); return 0.5-0.5*math.cos(math.pi*x)
def lerp(a,b,u): return a+(b-a)*u
def vn(v,dec=0):
    s=f"{v:,.{dec}f}"; return s.replace(",","X").replace(".",",").replace("X",".")
# ---------- sprites (premultiplied float32 RGBA) ----------
class Spr:
    def __init__(s,rgba,base=None,cw=None):
        a=np.asarray(rgba).astype(np.float32)*(1/255.0); a[...,:3]*=a[...,3:4]
        s.a=a; s.h,s.w=a.shape[:2]; s.base=base if base is not None else s.h/2; s.cw=cw or s.w
def pil2spr(im,**k): return Spr(np.asarray(im.convert("RGBA")),**k)
def blit(fr,sp,cx,cy,sc=1.0,rot=0.0,al=1.0):
    if sc<0.02 or al<0.004: return
    M=cv2.getRotationMatrix2D((sp.w/2,sp.h/2),rot,sc); M[0,2]+=cx-sp.w/2; M[1,2]+=cy-sp.h/2
    P=np.array([[0,0,1],[sp.w,0,1],[0,sp.h,1],[sp.w,sp.h,1]],np.float64)@M.T
    x0=max(0,int(math.floor(P[:,0].min()))-1); x1=min(W,int(math.ceil(P[:,0].max()))+1)
    y0=max(0,int(math.floor(P[:,1].min()))-1); y1=min(H,int(math.ceil(P[:,1].max()))+1)
    if x1<=x0 or y1<=y0: return
    M[0,2]-=x0; M[1,2]-=y0
    o=cv2.warpAffine(sp.a,M,(x1-x0,y1-y0),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_CONSTANT,borderValue=(0,0,0,0))
    if al<1: o*=al
    r=fr[y0:y1,x0:x1]; r*=(1-o[...,3:4]); r+=o[...,:3]
def tsp(text,size,color,w="Bold",shadow=0,stroke=0,stroke_fill=None):
    """text sprite; baseline at sp.base; cw = ink width"""
    f=fnt(size,w); asc,desc=f.getmetrics(); d=ImageDraw.Draw(Image.new("L",(1,1)))
    b=d.textbbox((0,0),text,font=f,anchor="ls",stroke_width=stroke); pad=8+shadow*3
    im=Image.new("RGBA",(b[2]-b[0]+2*pad,asc+desc+2*pad),(0,0,0,0))
    org=(pad-b[0],pad+asc)
    if shadow:
        sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((org[0],org[1]+3),text,font=f,fill=(0,0,0,170),anchor="ls",stroke_width=stroke+2,stroke_fill=(0,0,0,170))
        im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(shadow)))
    ImageDraw.Draw(im).text(org,text,font=f,fill=color,anchor="ls",stroke_width=stroke,stroke_fill=stroke_fill)
    return pil2spr(im,base=pad+asc,cw=b[2]-b[0])
def pill_spr(text,size=36,fill=OR,fg=DK,outline=None):
    f=fnt(size); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=d.textlength(text,font=f); pad=30
    w=int(tw+64); h=size+30; im=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([pad+3,pad+9,pad+w+3,pad+h+9],h//2,fill=(0,0,0,90)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(10)))
    dd=ImageDraw.Draw(im); dd.rounded_rectangle([pad,pad,pad+w,pad+h],h//2,fill=fill,outline=outline,width=3 if outline else 0)
    dd.text((pad+w/2,pad+h/2),text,font=f,fill=fg,anchor="mm"); return pil2spr(im)
def card_spr(w,h,fill=CARD,alpha=250,r=34,accent=True,outline=None,ow=4):
    pad=44; im=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([pad+5,pad+15,pad+w+5,pad+h+15],r,fill=(0,0,0,102))
    im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(15)))
    d=ImageDraw.Draw(im); d.rounded_rectangle([pad,pad,pad+w,pad+h],r,fill=fill+(alpha,),outline=outline,width=ow if outline else 0)
    if accent: d.rectangle([pad+w//2-50,pad,pad+w//2+50,pad+8],fill=OR)
    return pil2spr(im)
def box_spr(w,h,color=OR,width=6,r=18):
    im=Image.new("RGBA",(w+20,h+20),(0,0,0,0)); ImageDraw.Draw(im).rounded_rectangle([10,10,10+w,10+h],r,outline=color,width=width); return pil2spr(im)
def cut_spr(name,maxw,maxh):
    im=Image.open(f"assets/cut/{name}.png").convert("RGBA"); r_=min(maxw/im.width,maxh/im.height); im=im.resize((max(1,int(im.width*r_)),max(1,int(im.height*r_))),Image.LANCZOS)
    pad=70; c=Image.new("RGBA",(im.width+2*pad,im.height+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",c.size,(0,0,0,0)); sh.paste((0,0,0,102),(pad+12,pad+20),im.getchannel("A"))
    c.alpha_composite(sh.filter(ImageFilter.GaussianBlur(15))); c.alpha_composite(im,(pad,pad)); return pil2spr(c)
@functools.lru_cache(None)
def glow_spr(d=520,color=OR,a=170):
    yy,xx=np.mgrid[0:d,0:d]; r=np.sqrt((xx-d/2)**2+(yy-d/2)**2)/(d/2); al=(np.clip(1-r,0,1)**1.8*a).astype(np.uint8)
    im=np.zeros((d,d,4),np.uint8); im[...,0],im[...,1],im[...,2]=color; im[...,3]=al; return Spr(im)
# ---------- backgrounds ----------
def cover(im,w,h,fx=.5,fy=.5):
    r=max(w/im.width,h/im.height); im=im.resize((int(im.width*r+.999),int(im.height*r+.999)),Image.LANCZOS)
    x=int((im.width-w)*fx); y=int((im.height-h)*fy); return im.crop((x,y,x+w,y+h))
@functools.lru_cache(None)
def vignette(strength=0.16):
    yy,xx=np.mgrid[0:SH,0:SW]; r=np.sqrt(((xx-SW/2)/(SW/2))**2*0.8+((yy-SH*0.45)/(SH/2))**2*0.9)
    return (1-strength*np.clip(r-0.35,0,1.2)**1.6)[...,None].astype(np.float32)
def finish_bg(a,vig=0.16): return np.clip(a.astype(np.float32)*vignette(vig),0,255).astype(np.uint8)
def photo_bg(key,fx=.5,fy=.5,bright=1.0,grad=None,blur=0,vig=0.14):
    im=cover(Image.open(f"assets/{key}.jpg").convert("RGB"),SW,SH,fx,fy)
    if blur: im=im.filter(ImageFilter.GaussianBlur(blur))
    if bright!=1: im=ImageEnhance.Brightness(im).enhance(bright)
    a=np.asarray(im).astype(np.float32)
    if grad:   # dark gradient only where headline sits (y in frame px, scaled to source)
        y0,y1,a0,a1=grad; ys=np.arange(SH)/SH*H; al=np.clip((ys-y0)/(y1-y0),0,1); al=(a0+(a1-a0)*al)/255; al[ys>y1]=a1/255
        a*=(1-al)[:,None,None]
    return finish_bg(a,vig)
@functools.lru_cache(None)
def paper_bg(tone="beige",seed=1):
    base={"beige":(243,236,223),"grey":(235,235,237),"warm":(246,240,230)}[tone]
    rng=np.random.default_rng(seed); n=np.zeros((SH,SW),np.float32)
    for sc,amp in [(3,2.0),(12,3.0),(48,3.5),(220,4.5)]:
        sm=rng.normal(0,1,(SH//sc+2,SW//sc+2)).astype(np.float32); n+=cv2.resize(sm,(SW,SH),interpolation=cv2.INTER_CUBIC)*amp
    n+=rng.normal(0,1.6,(SH,SW)).astype(np.float32)
    fib=np.zeros((SH,SW),np.float32)
    for _ in range(900):
        x,y=rng.integers(0,SW),rng.integers(0,SH); ang=rng.uniform(0,np.pi); L=rng.integers(8,40)
        cv2.line(fib,(int(x),int(y)),(int(x+L*np.cos(ang)),int(y+L*np.sin(ang))),float(rng.choice([-5,5])),1,cv2.LINE_AA)
    n+=cv2.GaussianBlur(fib,(0,0),0.7)
    a=np.stack([base[0]+n,base[1]+n,base[2]+n*1.05],-1)
    return finish_bg(a,0.20)
class DriftBg:
    """continuous ease-in-out zoom + pan, subpixel via warpAffine (no zoompan jitter)"""
    def __init__(s,src,zin=True,pan=(1,0.4),z=(1.05,1.13),amp=26):
        s.src,s.zin,s.pan,s.z,s.amp=src,zin,pan,z,amp
    def __call__(s,u,t):
        e=e_sine(u); z=lerp(*s.z,e) if s.zin else lerp(s.z[1],s.z[0],e)
        px=s.amp*s.pan[0]*(2*e-1); py=s.amp*s.pan[1]*(2*e-1); k=z*W/SW
        M=np.float32([[k,0,W/2+px-k*SW/2],[0,k,H/2+py-k*SH/2]])
        return cv2.warpAffine(s.src,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT),(px,py)
# ---------- layers ----------
def appear(kind,u):
    f=u*FPS
    if kind=="pop":  return e_back(f/9),0,0,cl(f/3),0
    if kind=="popr": return e_back(f/10),0,0,cl(f/3),-10*(1-e_out(f/10))
    if kind=="drop": x=e_back(f/13); return 1,0,-340*(1-x),cl(f/4),9*(1-e_out(f/13))
    if kind=="up":   return 1,0,240*(1-e_back(f/11)),cl(f/4),0
    if kind=="right":return 1,760*(1-e_back(f/11)),0,cl(f/3),0
    if kind=="left": return 1,-760*(1-e_back(f/11)),0,cl(f/3),0
    if kind=="snap": return 1.5-0.5*e_out(f/4),0,0,cl(f/2),0
    if kind=="fade": return 1,0,0,e_out(f/8),0
    if kind=="static": return 1,0,0,1,0
    if kind=="bounce":   # Quy tắc chữ 9.5: 80->105->100% in 0.3 s
        x=u/0.3
        sc=0.8+0.25*e_out(x/0.6) if x<0.6 else 1.05-0.05*e_sine((x-0.6)/0.4)
        return sc,0,0,cl(u/0.05),0
    if kind=="slide":    # list items: slide in from the left
        return 1,-140*(1-e_out(f/8)),0,cl(f/4),0
    raise ValueError(kind)
def moff(m,t,cam):
    if not m: return 0.0,0.0
    par,amp,per,ph=(list(m)+[0,0,3.2,0])[:4] if len(m)<4 else m
    return par*cam[0]+amp*0.55*math.sin(2*math.pi*t/per+ph+1.3), par*cam[1]+amp*math.sin(2*math.pi*t/per+ph)
class Item:
    def __init__(s,sp,x,y,at=0.0,kind="pop",mot=None,rot=0.0,pulse=0.0,posfn=None):
        s.sp,s.x,s.y,s.at,s.kind,s.mot,s.rot,s.pulse,s.posfn=sp,x,y,at,kind,mot,rot,pulse,posfn
    def draw(s,fr,t,cam):
        if t<s.at: return
        sc,dx,dy,al,r=appear(s.kind,t-s.at); ox,oy=moff(s.mot,t,cam)
        if s.pulse and t-s.at>0.4: sc*=1+s.pulse*math.sin(2*math.pi*(t-s.at-0.4)/0.9)**2
        x,y=(s.posfn(t) if s.posfn else (s.x,s.y))
        blit(fr,s.sp,x+dx+ox,y+dy+oy,sc,s.rot+r,al)
def at_base(sp,cx,base_y): return cx, base_y-sp.base+sp.h/2
class Counter:
    def __init__(s,cx,base_y,at,dur,v0,v1,dec,size,color,prefix="",suffix="",w="Bold",kind="pop",mot=None,shadow=0):
        s.__dict__.update(locals()); del s.__dict__["s"]
        s.cache={}; f=fnt(size,w); asc,desc=f.getmetrics(); d=ImageDraw.Draw(Image.new("L",(1,1)))
        strs=[s.fmt(v0),s.fmt(v1),s.fmt(max(abs(v0),abs(v1))*0.888)]
        s.tw=int(max(d.textlength(x,font=f) for x in strs))+20; s.asc,s.desc=asc,desc; s.pad=8+shadow*3
        s.cw=d.textlength(s.fmt(v1),font=f)
    def fmt(s,v): return f"{s.prefix}{vn(v,s.dec)}{s.suffix}"
    def spr(s,txt):
        if txt not in s.cache:
            f=fnt(s.size,s.w); im=Image.new("RGBA",(s.tw+2*s.pad,s.asc+s.desc+2*s.pad),(0,0,0,0)); org=(s.pad+s.tw/2,s.pad+s.asc)
            if s.shadow:
                sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).text((org[0],org[1]+3),txt,font=f,fill=(0,0,0,170),anchor="ms"); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(s.shadow)))
            ImageDraw.Draw(im).text(org,txt,font=f,fill=s.color,anchor="ms"); s.cache[txt]=pil2spr(im,base=s.pad+s.asc)
        return s.cache[txt]
    def value(s,t):
        u=(t-s.at)/s.dur
        if u>=1: return s.v1
        v=s.v0+(s.v1-s.v0)*e_out(u); q=getattr(s,"q",None)
        return round(v/q)*q if q else v
    def draw(s,fr,t,cam):
        if t<s.at: return
        sp=s.spr(s.fmt(s.value(t))); sc,dx,dy,al,r=appear(s.kind,t-s.at); ox,oy=moff(s.mot,t,cam)
        x,y=at_base(sp,s.cx,s.base_y); blit(fr,sp,x+dx+ox,y+dy+oy,sc,r,al)
class Highlight:
    """marker sweep left->right, multiply blend"""
    def __init__(s,rect,at,dur=0.35,color=YEL,strength=0.9,mot=None):
        s.rect,s.at,s.dur,s.mot=rect,at,dur,mot; c=np.float32(color)/255; s.m=1-strength*(1-c)
    def draw(s,fr,t,cam):
        if t<s.at: return
        p=e_out((t-s.at)/s.dur); x0,y0,x1,y1=s.rect; ox,oy=moff(s.mot,t,cam)
        xa=int(round(x0+ox)); xb=int(round(x0+ox+(x1-x0)*p)); ya=int(round(y0+oy)); yb=int(round(y1+oy))
        xa,xb,ya,yb=max(0,xa),min(W,xb),max(0,ya),min(H,yb)
        if xb>xa and yb>ya: fr[ya:yb,xa:xb]*=s.m
class Strike:
    def __init__(s,x0,x1,y,at,dur=0.25,color=RD,width=12,mot=None): s.__dict__.update(locals()); del s.__dict__["s"]
    def draw(s,fr,t,cam):
        if t<s.at: return
        p=e_out((t-s.at)/s.dur); ox,oy=moff(s.mot,t,cam)
        xa=int(s.x0+ox); xb=int(s.x0+ox+(s.x1-s.x0)*p); ya=int(s.y+oy-s.width/2)
        fr[ya:ya+s.width,max(0,xa):min(W,xb)]=np.float32(s.color)/255
def mask_blend(fr,color,alpha,drawfn):
    m=np.zeros((H,W),np.uint8); drawfn(m); x,y,w,h=cv2.boundingRect(m)
    if w==0: return
    a=m[y:y+h,x:x+w,None].astype(np.float32)*(alpha/65025.0); r=fr[y:y+h,x:x+w]; r*=1-a; r+=a*(np.float32(color)/255)
class Fn:
    def __init__(s,fn): s.fn=fn
    def draw(s,fr,t,cam): s.fn(fr,t,cam)
# ---------- scene ----------
class Scene:
    def __init__(s,name,f0,f1,bg,brand=True,credit=None):
        s.name,s.f0,f1_=name,f0,f1; s.f1=f1; s.bg=bg; s.layers=[]; s.punch=[]; s.zblur=False; s.events=[]; s.t0g=f0/FPS
        s.brand=brand; s.credit=credit; s.T=(f1-f0)/FPS; s.post=[]; s.kind='other'
    def add(s,L,sfx=None,at=None,g=1.0):
        s.layers.append(L)
        if sfx: s.ev(at if at is not None else getattr(L,"at",0),sfx,g)
        return L
    def ev(s,t,kind,g=1.0): s.events.append((round(s.t0g+t,4),kind,g))
    def hit(s,t,boom=True): s.punch.append(t); s.ev(t,"boom" if boom else "pop",0.8)
    def render(s,f):
        t=(f-s.f0)/FPS; u=(f-s.f0)/max(1,s.f1-s.f0-1)
        img,cam=s.bg(u,t); fr=img.astype(np.float32)*(1/255.0)
        for L in s.layers: L.draw(fr,t,cam)
        for p in s.post: fr=p(fr,t)
        if s.brand: blit(fr,BRAND,W/2,199)
        if s.credit: blit(fr,s.credit,W/2,244,al=0.75)
        z=1.0
        for pt in s.punch:
            d=(t-pt)*FPS
            if 0<=d<6: z=max(z,1+0.13*e_out(d/6))
            elif 6<=d<34: z=max(z,1+0.13*(1-e_io((d-6)/28)))
        if z>1.0005:
            M=np.float32([[z,0,(1-z)*540],[0,z,(1-z)*800]]); fr=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
        if s.zblur and t*FPS<8:
            k=(1-t*FPS/8)**1.5; acc=fr.copy(); n=7
            for i in range(1,n+1):
                z=1+0.11*k*i/n; M=np.float32([[z,0,(1-z)*540],[0,z,(1-z)*800]]); acc+=cv2.warpAffine(fr,M,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REFLECT)
            fr=acc/(n+1)
        return (fr*255+0.5).clip(0,255).astype(np.uint8)
def _brand():
    f=fnt(26); d=ImageDraw.Draw(Image.new("L",(1,1))); tw=d.textlength("HINTON MEDIA",font=f); w=int(tw+72); im=Image.new("RGBA",(w,42),(0,0,0,0))
    dd=ImageDraw.Draw(im); dd.rounded_rectangle([0,0,w-1,41],21,fill=(20,20,22,175)); dd.rectangle([16,19,38,23],fill=OR); dd.text((w/2+10,21),"HINTON MEDIA",font=f,fill=OR,anchor="mm")
    return pil2spr(im)
BRAND=_brand()
