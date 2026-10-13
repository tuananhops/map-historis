from sat import *
from gfx import TIN, CJK
ORf=np.float32(OR)/255; RDf=np.float32(RD)/255; WHf=np.float32((1,1,1))
class VecBg:
    def __init__(s,path,dark=1.0,grat=True): s.path,s.dark,s.grat=path,dark,grat
    def __call__(s,u,t):
        v=s.path(t); lon,lat,k,rot=v[:4]; s.cam=Cam(lon,lat,k,rot,sy=v[4] if len(v)>4 else 820); fr,s.rs=draw_vecmap(W,H,s.cam,s.dark,s.grat)
        return (np.clip(fr,0,1)*255).astype(np.uint8),(0.0,0.0)
    def at(s,t):
        v=s.path(t); s.cam=Cam(v[0],v[1],v[2],v[3],sy=v[4] if len(v)>4 else 820); return s
    def proj(s,lon,lat):
        if not hasattr(s,"cam"): s.at(0)
        return s.cam.proj(np.atleast_1d(lon),np.atleast_1d(lat))
def P1(bg,lon,lat): return bg.proj(lon,lat)[0]
class CountryFX:
    def __init__(s,bg,names,stroke=None,fill=None,alpha=0.92,color=OR,pulse=0.0,glow=0.6,nstroke=3,width=4):
        s.__dict__.update(locals()); del s.__dict__["s"]; s.col=np.float32(color)/255
    def draw(s,fr,t,cam):
        cm=s.bg.cam; rs=[x for x in s.bg.rs if x[0] in s.names]
        if not rs: return
        if s.fill and t>=s.fill[0]:
            a=e_out((t-s.fill[0])/(s.fill[1]-s.fill[0]))*s.alpha
            if s.pulse and t>s.fill[1]: a*=1-s.pulse*(0.5+0.5*math.sin(2*math.pi*(t-s.fill[1])/1.1+math.pi/2))
            m=poly_mask(W,H,cm,rs,True)
            if s.glow: glow_mask(fr,m,s.col,s.glow*a/s.alpha*(0.7+0.3*math.sin(t*5)),12)
            blend_mask(fr,m,s.col,a)
        if s.stroke and t>=s.stroke[0]:
            p=e_io((t-s.stroke[0])/(s.stroke[1]-s.stroke[0])); big=sorted(rs,key=lambda x:-len(x[1]))
            m=np.zeros((H,W),np.uint8)
            for i,(_,r) in enumerate(big):
                if i>=s.nstroke and p<1: continue
                P=cm.mp(partial(r,p) if i<s.nstroke else r)
                cv2.polylines(m,[np.round(P*16).astype(np.int32)],p>=1,255,s.width,cv2.LINE_AA,4)
            glow_mask(fr,m,s.col,0.9,8); blend_mask(fr,m,np.minimum(s.col*1.15,1),1.0)
class GlowPin:
    def __init__(s,bg,lon,lat,at,color=OR,size=14,label=None,rings=True):
        s.__dict__.update(locals()); del s.__dict__["s"]; s.col=np.float32(color)/255
    def pos(s): return P1(s.bg,s.lon,s.lat)
    def draw(s,fr,t,cam):
        if t<s.at: return
        x,y=s.pos(); u=t-s.at; sc_=e_back(u*FPS/9)
        blit(fr,glow_spr(int(s.size*9),s.color,200),x,y,sc_*(1+0.12*math.sin(u*6)))
        if s.rings:
            m=np.zeros((H,W),np.uint8)
            for ph0 in (0,0.5):
                ph=((u/1.3)+ph0)%1.0; r=s.size*(1.2+3.2*ph); al=int(255*(1-ph)**1.5)
                cv2.circle(m,(int(x*16),int(y*16)),int(r*16),al,3,cv2.LINE_AA,4)
            blend_mask(fr,m,s.col,1.0)
        m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(x*16),int(y*16)),int(s.size*sc_*16),255,-1,cv2.LINE_AA,4); blend_mask(fr,m,WHf,1)
        m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(x*16),int(y*16)),int(s.size*sc_*0.55*16),255,-1,cv2.LINE_AA,4); blend_mask(fr,m,s.col,1)
class PCounter(Counter):
    def __init__(s,posfn,*a,**k): super().__init__(0,0,*a,**k); s.posfn=posfn
    def draw(s,fr,t,cam):
        s.cx,s.base_y=s.posfn(t); super().draw(fr,t,cam)
def card2(w,h,dark=True,accent=OR):
    pad=40; im=Image.new("RGBA",(w+2*pad,h+2*pad),(0,0,0,0))
    sh=Image.new("RGBA",im.size,(0,0,0,0)); ImageDraw.Draw(sh).rounded_rectangle([pad+4,pad+12,pad+w+4,pad+h+12],18,fill=(0,0,0,140)); im.alpha_composite(sh.filter(ImageFilter.GaussianBlur(14)))
    d=ImageDraw.Draw(im); d.rounded_rectangle([pad,pad,pad+w,pad+h],18,fill=(16,28,38,236) if dark else (252,250,246,250),outline=(80,130,140) if dark else None,width=2)
    if accent: d.rectangle([pad,pad+16,pad+8,pad+h-16],fill=accent)
    return pil2spr(im)
class Leader:
    """anchor dot + elbow leader line drawn on; end point follows map"""
    def __init__(s,bg,lon,lat,at,dx,dy,color=WH,dur=0.35):
        s.__dict__.update(locals()); del s.__dict__["s"]; s.col=np.float32(color)/255
    def end(s,t): a=P1(s.bg,s.lon,s.lat); return a+np.array([s.dx,s.dy])
    def draw(s,fr,t,cam):
        if t<s.at: return
        a=P1(s.bg,s.lon,s.lat); p=e_out((t-s.at)/s.dur)
        e=s.endfn(t) if getattr(s,"endfn",None) else a+np.array([s.dx,s.dy])
        P=np.array([a,np.array([a[0]+(e[0]-a[0])*0.35,e[1]]),e]); Q=partial(P,p)
        m=np.zeros((H,W),np.uint8); cv2.polylines(m,[np.round(Q*16).astype(np.int32)],False,255,3,cv2.LINE_AA,4)
        cv2.circle(m,(int(a[0]*16),int(a[1]*16)),9*16,255,-1,cv2.LINE_AA,4); blend_mask(fr,m,s.col,0.95)
        m=np.zeros((H,W),np.uint8); cv2.circle(m,(int(a[0]*16),int(a[1]*16)),int((14+6*math.sin(t*6))*16),255,2,cv2.LINE_AA,4); blend_mask(fr,m,ORf,0.9)
def callout(sc,bg,lon,lat,at,dx,dy,rows,w=330,dark=True,anchor_side=None,lcolor=WH):
    """rows: list of dict(t=text|ctr=(v0,v1,dec,pre,suf,dur), s=size, c=color, at=)"""
    L=Leader(bg,lon,lat,at,dx,dy,lcolor); sc.add(L); sc.ev(at,"swish",0.4)
    hh=sum(r["s"]*1.25 for r in rows)+34; side=anchor_side or (1 if dx>=0 else -1)
    def cc(t):
        e=L.end(t); x=min(max(e[0]+side*(w/2),w/2+60),920-w/2+20); y=min(max(e[1],210+hh/2),1390-hh/2); return x,y
    L.endfn=lambda t:(lambda c:np.array([c[0]-side*w/2,c[1]]))(cc(t))
    ca=at+0.3; sp=card2(w,int(hh),dark)
    sc.add(Item(sp,0,0,ca,"pop",posfn=lambda t:cc(t))); sc.ev(ca,"pop",0.6)
    y=-hh/2+17
    for r in rows:
        y+=r["s"]*1.0; ra=max(ca+0.05,r.get("at",ca+0.08)); yy=y
        if "ctr" in r:
            v0,v1,dec,pre,suf,dur=r["ctr"]
            sc.add(PCounter(lambda t,yy=yy:(cc(t)[0]+8,cc(t)[1]+yy),ra,dur,v0,v1,dec,r["s"],r["c"],pre,suf,kind="pop"))
            [sc.ev(ra+k*0.07,"tick",0.45) for k in range(int(dur/0.07))]
        else:
            spr=tsp(r["t"],r["s"],r["c"],r.get("w","Bold"))
            sc.add(Item(spr,0,0,ra,"pop",posfn=lambda t,yy=yy,spr=spr:(cc(t)[0]+8,cc(t)[1]+yy-spr.base+spr.h/2)))
        y+=r["s"]*0.25
    return L
class Route:
    def __init__(s,bg,a,b,at,dur=1.0,bend=0.25,color=OR,width=6,dash=False,flow=True):
        s.__dict__.update(locals()); del s.__dict__["s"]; s.col=np.float32(color)/255
    def path(s):
        A=P1(s.bg,*s.a) if s.bg is not None else np.array(s.a,float); B=P1(s.bg,*s.b) if s.bg is not None else np.array(s.b,float); d=B-A; n=np.array([d[1],-d[0]]); C=(A+B)/2+n*s.bend
        u=np.linspace(0,1,80)[:,None]; return (1-u)**2*A+2*(1-u)*u*C+u**2*B
    def draw(s,fr,t,cam):
        if t<s.at: return
        p=e_io((t-s.at)/s.dur); P=s.path(); Q=partial(P,max(p,0.01))
        m=np.zeros((H,W),np.uint8); cv2.polylines(m,[np.round(Q*16).astype(np.int32)],False,255,s.width,cv2.LINE_AA,4)
        glow_mask(fr,m,s.col,1.2,10); blend_mask(fr,m,np.minimum(s.col*1.1,1),1)
        h=Q[-1]; tg=Q[-1]-Q[-3] if len(Q)>2 else P[1]-P[0]; tg=tg/max(np.linalg.norm(tg),1e-6); nn=np.array([-tg[1],tg[0]])
        tri=np.array([h+tg*26,h-tg*10+nn*18,h-tg*10-nn*18]); m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.round(tri*16).astype(np.int32)],255,cv2.LINE_AA,4); blend_mask(fr,m,s.col,1)
        if p<1: blit(fr,glow_spr(120,s.color,230),h[0],h[1])
        elif s.flow:
            for k in range(3):
                q=((t-s.at-s.dur)*0.6+k/3)%1; X=partial(P,q)[-1]; blit(fr,glow_spr(70,(255,240,200),220),X[0],X[1])
class LineChart:
    def __init__(s,sc,rect,xs,ys,xlim,ylim,t0,t1,color=OR,dark=True,yfmt=lambda v:vn(v,0)+"%",xticks=None,yticks=None,head_fmt=None,size=30,head_size=44,glow=True,width=8):
        s.__dict__.update(locals()); del s.__dict__["s"]; s.col=np.float32(color)/255
        x0,y0,x1,y1=rect; s.P=np.array([[s.X(x),s.Y(y)] for x,y in zip(xs,ys)])
        im=Image.new("RGBA",(W,H),(0,0,0,0)); d=ImageDraw.Draw(im); fg=(220,232,236,200) if dark else (90,88,84,230); gl=(255,255,255,40) if dark else (0,0,0,40)
        for v in (yticks or []): yy=s.Y(v); d.line([(x0,yy),(x1,yy)],fill=gl,width=2); d.text((x0-14,yy),yfmt(v),font=fnt(size-4,"SemiBold"),fill=fg,anchor="rm")
        d.line([(x0,y1),(x1,y1)],fill=fg,width=3)
        for v,lab in (xticks or []): d.text((s.X(v),y1+20),lab,font=fnt(size-2,"SemiBold"),fill=fg,anchor="mt")
        s.axes=pil2spr(im); s.cache={}
        sc.add(Item(s.axes,W/2,H/2,t0-0.25,"fade")); sc.add(Fn(s.draw))
        for k in range(int((t1-t0)/0.12)): sc.ev(t0+k*0.12,"tick",0.35)
    def X(s,v): x0,y0,x1,y1=s.rect; return x0+(v-s.xlim[0])/(s.xlim[1]-s.xlim[0])*(x1-x0)
    def Y(s,v): x0,y0,x1,y1=s.rect; return y1-(v-s.ylim[0])/(s.ylim[1]-s.ylim[0])*(y1-y0)
    def head(s,t):
        p=e_io((t-s.t0)/(s.t1-s.t0)); X=s.P[0,0]+(s.P[-1,0]-s.P[0,0])*p; k=int(np.searchsorted(s.P[:,0],X)); k=max(1,min(k,len(s.P)-1))
        f=(X-s.P[k-1,0])/max(s.P[k,0]-s.P[k-1,0],1e-6); Yp=s.P[k-1,1]+(s.P[k,1]-s.P[k-1,1])*f; val=s.ys[k-1]+(s.ys[k]-s.ys[k-1])*f
        return p,k,np.array([X,Yp]),val
    def draw(s,fr,t,cam):
        if t<s.t0: return
        p,k,hp,val=s.head(t); pts=np.vstack([s.P[:k],hp])
        m=np.zeros((H,W),np.uint8); cv2.polylines(m,[np.round(pts*16).astype(np.int32)],False,255,s.width,cv2.LINE_AA,4)
        if s.glow: glow_mask(fr,m,s.col,0.9,10)
        blend_mask(fr,m,s.col,1)
        blit(fr,glow_spr(150,s.color,220),hp[0],hp[1],1+0.15*math.sin(t*12))
        mm=np.zeros((H,W),np.uint8); cv2.circle(mm,(int(hp[0]*16),int(hp[1]*16)),14*16,255,-1,cv2.LINE_AA,4); blend_mask(fr,mm,WHf,1)
        if s.head_fmt:
            txt=s.head_fmt(val)
            if txt not in s.cache: s.cache[txt]=tsp(txt,s.head_size,WH if s.dark else DK,shadow=3 if s.dark else 0)
            sp=s.cache[txt]; x,y=at_base(sp,hp[0],hp[1]-30); blit(fr,sp,min(x,W-sp.w/2-20),y)
class DocCard:
    """styled document excerpt; highlights = list of (phrase, at, dur)"""
    def __init__(s,sc,header,sub,body,hls,at,y=700,w=900,size=34,src_line="",kind="right",z=(1.0,1.07),rot=(-1.5,0.5),font="Tinos",logo="IMF"):
        s.__dict__.update(locals()); del s.__dict__["s"]
        S=2; pad=60*S; fb=ImageFont.truetype(TIN+"Tinos-Regular.ttf",size*S); fh=ImageFont.truetype(TIN+"Tinos-Bold.ttf",int(size*1.05*S)); fs=fnt(int(19*S),"SemiBold")
        d0=ImageDraw.Draw(Image.new("L",(1,1))); words=body.split(); lines=[]; cur=[]
        for wd in words:
            if d0.textlength(" ".join(cur+[wd]),font=fb)>w*S-2*pad and cur: lines.append(cur); cur=[wd]
            else: cur.append(wd)
        lines.append(cur); lh=int(size*1.55*S); top=pad+int(150*S)
        hgt=top+lh*len(lines)+int(110*S); im=Image.new("RGBA",(w*S,hgt),(255,255,253,255)); d=ImageDraw.Draw(im)
        if logo=="IMF":
            d.rectangle([pad,pad,pad+int(70*S),pad+int(70*S)],fill=(0,74,128)); d.text((pad+int(35*S),pad+int(36*S)),"IMF",font=fnt(int(24*S)),fill=WH,anchor="mm")
        else:
            lt,lc=logo; d.rectangle([pad,pad,pad+int(70*S),pad+int(70*S)],fill=lc); d.text((pad+int(35*S),pad+int(36*S)),lt,font=fnt(int(18*S)),fill=WH,anchor="mm")
        d.text((pad+int(90*S),pad+int(18*S)),header,font=ImageFont.truetype(TIN+"Tinos-Bold.ttf",int(24*S)),fill=(30,30,34))
        d.text((pad+int(90*S),pad+int(52*S)),sub,font=ImageFont.truetype(TIN+"Tinos-Italic.ttf",int(21*S)),fill=(90,90,96))
        d.line([(pad,pad+int(100*S)),(w*S-pad,pad+int(100*S))],fill=(30,30,34),width=2*S)
        s.boxes=[]; y_=top
        for ln in lines:
            x_=pad
            for wd in ln:
                ww=d.textlength(wd,font=fb); s.boxes.append((wd,x_,y_,x_+ww)); d.text((x_,y_),wd,font=fb,fill=(28,28,30)); x_+=ww+d.textlength(" ",font=fb)
            y_+=lh
        d.text((pad,hgt-int(60*S)),src_line,font=fs,fill=(120,120,126))
        s.lh=lh; s.S=S; s.base=np.asarray(im.resize((w,hgt//S),Image.LANCZOS)).astype(np.float32)/255; s.h=hgt//S
        s.hl_rects=[]
        bw=[b[0] for b in s.boxes]
        for ph,a,du in hls:
            pw=ph.split(); idx=None
            for i in range(len(bw)-len(pw)+1):
                if [x.strip(",.()") for x in bw[i:i+len(pw)]]==[x.strip(",.()") for x in pw]: idx=i; break
            assert idx is not None,ph
            segs={}
            for wd,x0,y0,x1 in s.boxes[idx:idx+len(pw)]: segs.setdefault(y0,[x0,x1]); segs[y0][1]=x1
            s.hl_rects.append(([(x0/S-4,y0/S+size*0.05,x1/S+4,y0/S+size*1.22) for y0,(x0,x1) in sorted(segs.items())],a,du))
        sc.add(s); sc.ev(at,"whoosh",0.7)
        for _,a,_ in hls: sc.ev(a,"swish",0.4)
        s.T=sc.T
    def draw(s,fr,t,cam):
        if t<s.at: return
        img=s.base.copy(); m=1-0.62*(1-np.float32(YEL)/255)
        for rects,a,du in s.hl_rects:
            if t<a: continue
            tot=sum(r[2]-r[0] for r in rects); done=e_out((t-a)/du)*tot
            for x0,y0,x1,y1 in rects:
                L=min(x1-x0,max(0,done)); done-=x1-x0
                if L>0: img[int(y0):int(y1),int(x0):int(x0+L),:3]*=m
        u=t-s.at; sc_,dx,dy,al,r=appear(s.kind,u); z=lerp(s.z[0],s.z[1],e_sine(u/max(s.T-s.at,1)))
        rot=lerp(s.rot[0],s.rot[1],e_sine(u/max(s.T-s.at,1)))
        sp=s._spr(img); blit(fr,sp,W/2+dx,s.y+dy,sc_*z,rot+r,al)
    def _spr(s,img):
        sp=Spr.__new__(Spr); a=img.copy(); a[...,:3]*=a[...,3:4]
        # baked soft shadow
        pad=40; out=np.zeros((a.shape[0]+2*pad,a.shape[1]+2*pad,4),np.float32)
        out[pad+14:pad+14+a.shape[0],pad+6:pad+6+a.shape[1],3]=0.35; out[...,3]=cv2.GaussianBlur(out[...,3],(0,0),14)
        al=a[...,3:4]; reg=out[pad:pad+a.shape[0],pad:pad+a.shape[1]]; reg[...,:3]=reg[...,:3]*(1-al)+a[...,:3]; reg[...,3:4]=reg[...,3:4]*(1-al)+al
        sp.a=out; sp.h,sp.w=out.shape[:2]; sp.base=sp.h/2; sp.cw=sp.w; return sp
def edge_blur(strength=1.0,center=(540,760)):
    yy,xx=np.mgrid[0:H,0:W]; r=np.sqrt(((xx-center[0])/W*1.1)**2+((yy-center[1])/H*0.9)**2)
    m=np.clip((r-0.28)/0.35,0,1)[...,None].astype(np.float32)*strength; vig=(1-0.35*np.clip(r-0.25,0,1)**1.3)[...,None].astype(np.float32)
    def post(fr,t):
        sm=cv2.resize(fr,(W//4,H//4),interpolation=cv2.INTER_AREA); sm=cv2.GaussianBlur(sm,(0,0),3.5); b=cv2.resize(sm,(W,H),interpolation=cv2.INTER_LINEAR)
        return (fr*(1-m)+b*m)*vig
    return post
class BottomGlobe:
    def __init__(s,tex,cy=2050,R=900,lon0=100,speed=6,lat0=18,at=0.0,rise=0.8,cx=540,atm=1.0):
        s.__dict__.update(locals()); del s.__dict__["s"]
    def draw(s,fr,t,cam):
        if t<s.at: return
        u=e_out((t-s.at)/s.rise) if s.rise else 1; cy=s.cy+(1-u)*600
        g=render_globe(W,H,s.cx,cy,s.R,s.lon0+s.speed*t,s.lat0,0,[(s.tex,1)],fr,limb=0.45)
        atmosphere(g,s.cx,cy,s.R,s.atm); fr[...]=g
class Bar3D:
    """vertical prism bar rising from a screen point"""
    def __init__(s,posfn,at,h,dur=0.8,w=56,color=OR):
        s.__dict__.update(locals()); del s.__dict__["s"]
    def cur(s,t): return s.h*e_out((t-s.at)/s.dur)
    def draw(s,fr,t,cam):
        if t<s.at: return
        x,y=s.posfn(t); hh=s.cur(t); w=s.w; dz=w*0.35; c=np.float32(s.color)/255
        if hh<1: return
        front=np.array([[x-w/2,y],[x+w/2,y],[x+w/2,y-hh],[x-w/2,y-hh]]); side=np.array([[x+w/2,y],[x+w/2+dz,y-dz*0.6],[x+w/2+dz,y-hh-dz*0.6],[x+w/2,y-hh]])
        top=np.array([[x-w/2,y-hh],[x+w/2,y-hh],[x+w/2+dz,y-hh-dz*0.6],[x-w/2+dz,y-hh-dz*0.6]])
        for P,k in ((side,0.62),(front,1.0),(top,1.25)):
            m=np.zeros((H,W),np.uint8); cv2.fillPoly(m,[np.round(P*16).astype(np.int32)],255,cv2.LINE_AA,4); blend_mask(fr,m,np.minimum(c*k,1),1)

class TItem(Item):
    """Item with exit: until=time, exit in ('fade','left','right','up','shrink')"""
    def __init__(s,*a,until=1e9,exit="fade",**k): super().__init__(*a,**k); s.until=until; s.exit=exit
    def draw(s,fr,t,cam):
        if t<s.at: return
        if t<s.until: return super().draw(fr,t,cam)
        u=e_io((t-s.until)/0.35)
        if u>=1: return
        sc,dx,dy,al,r=appear(s.kind,t-s.at); ox,oy=moff(s.mot,t,cam); x,y=(s.posfn(t) if s.posfn else (s.x,s.y))
        if s.exit=="fade": al*=1-u
        elif s.exit=="left": dx-=1300*u
        elif s.exit=="right": dx+=1300*u
        elif s.exit=="up": dy-=1500*u
        elif s.exit=="shrink": sc*=1-u; al*=1-u
        blit(fr,s.sp,x+dx+ox,y+dy+oy,sc,s.rot+r,al)
def text_spr(t,size,color=WH,w="Bold",stroke=4,sf=(10,20,28)): return tsp(t,size,color,w,stroke=stroke,stroke_fill=sf)
