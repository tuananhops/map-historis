# Map toolkit (video02/03): orthographic satellite globe w/ multi-level texture crossfade, perspective tilt,
# dark-teal vector mercator maps (per-frame vector fill), vector-styled globe.
from engine import *
D2R=math.pi/180
# ---------------- textures ----------------
class EquiTex:
    """equirectangular texture covering lon0..lon1, lat1..lat0 (top..bottom)"""
    def __init__(s,img,lon0,lon1,lat0,lat1,feather=0.0):
        s.img=img; s.h,s.w=img.shape[:2]; s.lon0,s.lon1,s.lat0,s.lat1=lon0,lon1,lat0,lat1; s.kx=s.w/(lon1-lon0); s.ky=s.h/(lat1-lat0)
        s.feather=feather
        s.res=s.kx    # px per degree
    def coords(s,lon,lat):
        return ((lon-s.lon0)*s.kx).astype(np.float32),((s.lat1-lat)*s.ky).astype(np.float32)
class MercTex:
    def __init__(s,path,feather=0.06):
        im=cv2.cvtColor(cv2.imread(path),cv2.COLOR_BGR2RGB); s.img=im; s.h,s.w=im.shape[:2]
        z,x0,y0=map(int,open(path+".txt").read().split()); s.z,s.x0,s.y0=z,x0,y0; s.n=2**z*256
        s.feather=feather; s.res=s.n/360.0
        s.lon0=x0*256/s.n*360-180; s.lon1=(x0*256+s.w)/s.n*360-180
    def coords(s,lon,lat):
        x=((lon+180)/360*s.n-s.x0*256).astype(np.float32)
        r=lat*D2R; y=((1-np.log(np.tan(r)+1/np.cos(r))/math.pi)/2*s.n-s.y0*256).astype(np.float32); return x,y
def feather_mask(w,h,f):
    fx=np.clip(np.minimum(np.arange(w),w-1-np.arange(w))/(f*w),0,1); fy=np.clip(np.minimum(np.arange(h),h-1-np.arange(h))/(f*h),0,1)
    return (np.outer(fy,fx)**1.0).astype(np.float32)
def smooth(a,b,x): return e_sine((x-a)/(b-a))
# ---------------- orthographic globe ----------------
def ortho_inv(Wc,Hc,cx,cy,R,lon0,lat0,rot=0.0,box=None):
    """returns lon,lat arrays (float32) and inside-mask for canvas region; box=(x0,y0,x1,y1) restricts compute"""
    x0,y0,x1,y1=box or (0,0,Wc,Hc)
    xs=np.arange(x0,x1,dtype=np.float32)+0.5-cx; ys=np.arange(y0,y1,dtype=np.float32)+0.5-cy
    X,Y=np.meshgrid(xs/R,ys/R)
    if rot:
        c,s_=math.cos(rot*D2R),math.sin(rot*D2R); X,Y=X*c-Y*s_,X*s_+Y*c
    V=-Y; rho2=X*X+V*V; inside=rho2<1.0; Z=np.sqrt(np.clip(1-rho2,0,1))
    cl0,sl0=math.cos(lat0*D2R),math.sin(lat0*D2R)
    lat=np.arcsin(np.clip(V*cl0+Z*sl0,-1,1))/D2R
    lon=lon0+np.arctan2(X,Z*cl0-V*sl0)/D2R
    lon=(lon+180)%360-180
    return lon,lat,inside,Z
def ortho_fwd(lon,lat,cx,cy,R,lon0,lat0,rot=0.0):
    lon=np.asarray(lon,np.float64)*D2R; lat=np.asarray(lat,np.float64)*D2R; l0,p0=lon0*D2R,lat0*D2R
    x=np.cos(lat)*np.sin(lon-l0); y=np.cos(p0)*np.sin(lat)-np.sin(p0)*np.cos(lat)*np.cos(lon-l0)
    vis=np.sin(p0)*np.sin(lat)+np.cos(p0)*np.cos(lat)*np.cos(lon-l0)>0
    X,Y=x*R,-y*R
    if rot:
        c,s_=math.cos(-rot*D2R),math.sin(-rot*D2R); X,Y=X*c-Y*s_,X*s_+Y*c
    return np.stack([X+cx,Y+cy],-1),vis
def render_globe(Wc,Hc,cx,cy,R,lon0,lat0,rot,levels,space,limb=0.35):
    """levels: list of (tex, alpha_scalar) base first. space: background image (Hc,Wc,3) float32 0..1"""
    out=space.copy()
    bx0=max(0,int(cx-R)-1); by0=max(0,int(cy-R)-1); bx1=min(Wc,int(cx+R)+2); by1=min(Hc,int(cy+R)+2)
    if bx1<=bx0 or by1<=by0: return out
    lon,lat,inside,Z=ortho_inv(Wc,Hc,cx,cy,R,lon0,lat0,rot,(bx0,by0,bx1,by1))
    acc=None
    for tex,al in levels:
        if al<=0.001: continue
        mx,my=tex.coords(lon,lat)
        if isinstance(tex,EquiTex) and tex.lon1-tex.lon0>=359: mode=cv2.BORDER_WRAP
        else: mode=cv2.BORDER_CONSTANT
        col=cv2.remap(tex.img,mx,my,cv2.INTER_LINEAR,borderMode=mode).astype(np.float32)*(1/255)
        if acc is None: acc=col; continue
        if tex.feather:
            fx=np.clip(np.minimum(mx,tex.w-1-mx)/(tex.feather*tex.w),0,1); fy=np.clip(np.minimum(my,tex.h-1-my)/(tex.feather*tex.h),0,1); a=fx*fy*al
        else: a=np.full(lon.shape,al,np.float32)
        a=a[...,None]; acc=acc*(1-a)+col*a
    if limb: acc*=(1-limb+limb*Z**0.45)[...,None]
    # anti-aliased disk edge
    xs=np.arange(bx0,bx1,dtype=np.float32)+0.5-cx; ys=np.arange(by0,by1,dtype=np.float32)+0.5-cy
    d=np.sqrt(xs[None,:]**2+ys[:,None]**2); a=np.clip(R-d+0.5,0,1)[...,None]
    reg=out[by0:by1,bx0:bx1]; out[by0:by1,bx0:bx1]=reg*(1-a)+acc*a
    return out
@functools.lru_cache(maxsize=3)   # tilt changes canvas size every frame → bounded (was an OOM leak)
def starfield(Wc,Hc,seed=3):
    rng=np.random.default_rng(seed); im=np.zeros((Hc,Wc,3),np.float32)
    yy,xx=np.mgrid[0:Hc,0:Wc]; g=0.035+0.03*np.exp(-(((xx-Wc*0.5)/Wc)**2+((yy-Hc*0.45)/Hc)**2)*3)
    im[...]=np.stack([g*0.55,g*0.7,g*1.25],-1)
    n=int(Wc*Hc/900); xs=rng.integers(0,Wc,n); ys=rng.integers(0,Hc,n); b=rng.random(n)**3
    for x,y,v in zip(xs,ys,b): im[y,x]+=0.25+0.75*v
    im=cv2.GaussianBlur(im,(0,0),0.6)*1.4
    return np.clip(im,0,1)
def atmosphere(fr,cx,cy,R,strength=1.0,color=(0.45,0.7,1.0)):
    Hc,Wc=fr.shape[:2]; pad=int(R*0.18)+6
    x0,y0,x1,y1=max(0,int(cx-R-pad)),max(0,int(cy-R-pad)),min(Wc,int(cx+R+pad)),min(Hc,int(cy+R+pad))
    if x1<=x0 or y1<=y0: return
    xs=np.arange(x0,x1,dtype=np.float32)+0.5-cx; ys=np.arange(y0,y1,dtype=np.float32)+0.5-cy
    d=np.sqrt(xs[None,:]**2+ys[:,None]**2)/R
    outer=np.where(d>=1,np.exp(-(d-1)/0.045),0)*0.9; inner=np.where(d<1,np.exp(-(1-d)/0.035),0)*0.6
    a=((outer+inner)*strength).astype(np.float32)[...,None]
    fr[y0:y1,x0:x1]+=a*np.float32(color)
# ---------------- vector data ----------------
GEO=json.load(open("assets/countries50.geojson"))
def _rings(g):
    if g["type"]=="Polygon": return [g["coordinates"][0]]
    if g["type"]=="MultiPolygon": return [p[0] for p in g["coordinates"]]
    return []
def merc(lon,lat):
    lat=np.clip(np.asarray(lat,np.float64),-85,85); return np.stack([np.asarray(lon,np.float64)*D2R,np.log(np.tan(math.pi/4+lat*D2R/2))],-1)
COUNTRIES={}
for ft in GEO["features"]:
    nm=ft["properties"]["NAME"]; rs=[]
    for rg in _rings(ft["geometry"]):
        a=np.array(rg,np.float64)
        if len(a)<4: continue
        rs.append(merc(a[:,0],a[:,1]))
    COUNTRIES.setdefault(nm,[]).extend(rs)
ALLR=[(nm,r,r[:,0].min(),r[:,0].max(),r[:,1].min(),r[:,1].max()) for nm,rs in COUNTRIES.items() for r in rs]
HS=[(111.6,16.5),(112.3,16.8),(112.0,16.2),(111.2,15.9),(112.7,16.1)]
TS=[(114.3,11.2),(113.6,10.6),(112.6,9.6),(115.0,9.9),(114.6,8.7),(113.0,8.5),(114.9,10.8)]
# palette (dark teal / navy)
OCEAN_T=np.float32((14,36,52))/255; OCEAN_B=np.float32((8,22,34))/255
LAND=np.float32((30,78,88))/255; COAST=np.float32((84,150,156))/255; BORDER=np.float32((52,112,120))/255
@functools.lru_cache(maxsize=3)
def ocean_img(Wc,Hc):
    ys=np.linspace(0,1,Hc,dtype=np.float32)[:,None,None]; xs=np.linspace(-1,1,Wc,dtype=np.float32)[None,:,None]
    g=OCEAN_T*(1-ys)+OCEAN_B*ys; g=g*(1-0.25*xs**2)
    rng=np.random.default_rng(5); n=cv2.resize(rng.normal(0,1,(Hc//6+1,Wc//6+1)).astype(np.float32),(Wc,Hc))[...,None]*0.006
    return np.broadcast_to(g+n,(Hc,Wc,3)).astype(np.float32).copy()
class Cam:
    """mercator camera: lon,lat centre; k = px per degree lon; rot deg; screen centre (sx,sy)"""
    def __init__(s,lon,lat,k,rot=0.0,sx=540,sy=820):
        s.c=merc(lon,lat); s.S=k/D2R; s.rot=rot; s.sx,s.sy=sx,sy
        r=rot*D2R; s.Rm=np.array([[math.cos(r),-math.sin(r)],[math.sin(r),math.cos(r)]])
    def mp(s,M):   # mercator -> screen
        d=(np.atleast_2d(M)-s.c)*np.array([1,-1])*s.S; return d@s.Rm.T+np.array([s.sx,s.sy])
    def proj(s,lon,lat=None):
        if lat is None: lon,lat=np.atleast_2d(lon)[:,0],np.atleast_2d(lon)[:,1]
        return s.mp(merc(lon,lat))
    def view(s,Wc,Hc):  # mercator bbox of view (generous)
        R=math.hypot(Wc,Hc)/2/s.S*1.05; cx,cy=s.c+np.array([(Wc/2-s.sx),-(Hc/2-s.sy)])/s.S
        return cx-R,cx+R,cy-R,cy+R
def rings_in_view(cam,Wc,Hc,names=None):
    x0,x1,y0,y1=cam.view(Wc,Hc); out=[]
    for nm,r,a,b,c,d in ALLR:
        if names is not None and nm not in names: continue
        for off in (0.0,2*math.pi,-2*math.pi):
            if b+off<x0 or a+off>x1 or d<y0 or c>y1: continue
            out.append((nm,r if off==0 else r+np.array([off,0])))
    return out
def poly_mask(Wc,Hc,cam,rings,fill=True,width=2):
    m=np.zeros((Hc,Wc),np.uint8)
    pts=[np.round(cam.mp(r)*16).astype(np.int32) for _,r in rings]
    pts=[p for p in pts if len(p)>2]
    if not pts: return m
    if fill: cv2.fillPoly(m,pts,255,cv2.LINE_AA,4)
    else: cv2.polylines(m,pts,True,255,width,cv2.LINE_AA,4)
    return m
def blend_mask(fr,m,color,alpha=1.0):
    if alpha<=0: return
    x,y,w,h=cv2.boundingRect(m)
    if w==0: return
    a=m[y:y+h,x:x+w,None].astype(np.float32)*(alpha/255.0); r=fr[y:y+h,x:x+w]; r*=1-a; r+=a*np.float32(color)
def glow_mask(fr,m,color,alpha=0.8,sigma=14):
    if alpha<=0: return
    sm=cv2.resize(m,(m.shape[1]//4,m.shape[0]//4),interpolation=cv2.INTER_AREA).astype(np.float32)/255
    sm=cv2.GaussianBlur(sm,(0,0),sigma/4); g=cv2.resize(sm,(m.shape[1],m.shape[0]),interpolation=cv2.INTER_LINEAR)
    fr+=(g*alpha)[...,None]*np.float32(color)
def draw_vecmap(Wc,Hc,cam,dark=1.0,grat=True,land=LAND):
    fr=ocean_img(Wc,Hc).copy()
    if grat:
        m=np.zeros((Hc,Wc),np.uint8)
        x0,x1,y0,y1=cam.view(Wc,Hc); step=10 if cam.S*D2R<60 else 5 if cam.S*D2R<200 else 1
        lo0=math.floor(x0/D2R/step)*step; lo1=math.ceil(x1/D2R/step)*step
        for lon in np.arange(lo0,lo1+step,step):
            P=cam.proj(np.full(40,lon),np.linspace(-80,80,40)); cv2.polylines(m,[np.round(P*16).astype(np.int32)],False,255,1,cv2.LINE_AA,4)
        for lat in np.arange(-80,81,step):
            P=cam.proj(np.linspace(lo0,lo1,60),np.full(60,lat)); cv2.polylines(m,[np.round(P*16).astype(np.int32)],False,255,1,cv2.LINE_AA,4)
        blend_mask(fr,m,(0.35,0.6,0.7),0.10)
    rs=rings_in_view(cam,Wc,Hc)
    lm=poly_mask(Wc,Hc,cam,rs,True)
    # soft land shadow for depth
    sh=cv2.GaussianBlur(cv2.resize(lm,(Wc//4,Hc//4)),(0,0),3); sh=cv2.resize(sh,(Wc,Hc)); sh=np.roll(sh,(6,4),(0,1))
    fr*=1-(sh.astype(np.float32)/255*0.45)[...,None]
    blend_mask(fr,lm,land,1.0)
    bm=poly_mask(Wc,Hc,cam,rs,False,1); blend_mask(fr,bm,COAST,0.75)
    if dark!=1.0: fr*=dark
    return fr,rs
def hs_ts(fr,cam,t,at=0.0,labels=True,scale=1.0):
    """draw Vietnamese Hoàng Sa / Trường Sa dots (+labels handled by caller layers)"""
    if t<at: return
    P=cam.proj(np.array(HS+TS)); rad=max(3,int(3+cam.S*D2R/90))
    m=np.zeros(fr.shape[:2],np.uint8)
    for q in P: cv2.circle(m,(int(q[0]*16),int(q[1]*16)),rad*16,255,-1,cv2.LINE_AA,4)
    blend_mask(fr,m,LAND*1.6,cl((t-at)*4))
    m2=np.zeros(fr.shape[:2],np.uint8)
    for q in P: cv2.circle(m2,(int(q[0]*16),int(q[1]*16)),rad*16,255,1,cv2.LINE_AA,4)
    blend_mask(fr,m2,COAST*1.4,cl((t-at)*4))
def partial(P,p):
    if p>=1: return P
    seg=np.sqrt(((P[1:]-P[:-1])**2).sum(1)); cum=np.concatenate([[0],np.cumsum(seg)]); L=cum[-1]*p
    k=np.searchsorted(cum,L); k=max(1,min(k,len(P)-1)); f=(L-cum[k-1])/max(seg[k-1],1e-9)
    return np.vstack([P[:k],P[k-1]+(P[k]-P[k-1])*f])
def biggest(name,n=1): return sorted(COUNTRIES[name],key=len,reverse=True)[:n]
def centroid(name):
    r=biggest(name)[0]; return r.mean(0)
def merc_inv(M): return M[...,0]/D2R, (2*np.arctan(np.exp(M[...,1]))-math.pi/2)/D2R
# ---------------- vector-styled globe texture ----------------
def vec_equi(hl=("Japan",),Wt=4096,Ht=2048,hlcol=OR):
    p=f"assets/vec_equi_{'_'.join(hl)}.png"
    if os.path.exists(p): return EquiTex(cv2.cvtColor(cv2.imread(p),cv2.COLOR_BGR2RGB),-180,180,-90,90)
    ys=np.linspace(0,1,Ht,dtype=np.float32)[:,None,None]
    img=np.broadcast_to(np.float32((16,42,60))/255*(1-0.3*np.abs(ys-0.5)*2),(Ht,Wt,3)).copy()
    def tp(r): a=np.array(r,np.float64); return np.round(np.stack([(a[:,0]+180)/360*Wt,(90-a[:,1])/180*Ht],-1)*16).astype(np.int32)
    lm=np.zeros((Ht,Wt),np.uint8); hm=np.zeros((Ht,Wt),np.uint8); bm=np.zeros((Ht,Wt),np.uint8)
    for ft in GEO["features"]:
        nm=ft["properties"]["NAME"]
        for rg in _rings(ft["geometry"]):
            q=tp(rg); cv2.fillPoly(hm if nm in hl else lm,[q],255,cv2.LINE_AA,4); cv2.polylines(bm,[q],True,255,1,cv2.LINE_AA,4)
    for lon in range(-180,181,15): cv2.line(img,(int((lon+180)/360*Wt),0),(int((lon+180)/360*Wt),Ht),(0.09,0.2,0.27),1,cv2.LINE_AA)
    for lat in range(-75,76,15): y=int((90-lat)/180*Ht); cv2.line(img,(0,y),(Wt,y),(0.09,0.2,0.27),1,cv2.LINE_AA)
    blend_mask(img,lm,LAND*1.15,1); blend_mask(img,hm,np.float32(hlcol)/255,1); blend_mask(img,bm,COAST,0.8)
    vm=np.zeros((Ht,Wt),np.uint8)     # Hoàng Sa & Trường Sa drawn in Vietnam's colour
    for lo,la in HS+TS: cv2.circle(vm,(int((lo+180)/360*Wt*16),int((90-la)/180*Ht*16)),int(4*16),255,-1,cv2.LINE_AA,4)
    blend_mask(img,vm,np.float32(hlcol)/255 if "Vietnam" in hl else LAND*1.3,1)
    out=(np.clip(img,0,1)*255).astype(np.uint8); cv2.imwrite(p,cv2.cvtColor(out,cv2.COLOR_RGB2BGR))
    return EquiTex(out,-180,180,-90,90)
