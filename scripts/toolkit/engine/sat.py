from maps import *
SAT="assets/sat/"
def _rgb(p): return cv2.cvtColor(cv2.imread(p),cv2.COLOR_BGR2RGB)
def _grade(t,gain=1.12,sat=1.1,gamma=0.92):
    im=t.img.astype(np.float32)/255; im=im**gamma*gain; g=im.mean(2,keepdims=True); im=g+(im-g)*sat
    t.img=np.clip(im*255,0,255).astype(np.uint8); return t
_T={}
def _tex(k):
    """lazy textures: 'BM' world, 'BMV' Vietnam crop, 'BME' Europe crop, else assets/sat/eox_<k>.jpg (None if missing)"""
    if k in _T: return _T[k]
    if k=="BM": t=_grade(EquiTex(_rgb(SAT+"bm_5400.jpg"),-180,180,-90,90))
    elif k=="BMV": t=_grade(EquiTex(_rgb(SAT+"bm_vn.png"),95,125,0,25,feather=0.04))
    elif k=="BME": t=_grade(EquiTex(_rgb(SAT+"bm_eu.png"),0,20,45,60,feather=0.04))
    else:
        f=0.05 if k.endswith("8") else 0.08
        t=MercTex(SAT+f"eox_{k}.jpg",f) if os.path.exists(SAT+f"eox_{k}.jpg") else None
    _T[k]=t; return t
def E(k,f=0.08): return _tex(k)
# region -> [(texture key, (R_start, R_full) in px-per-radian*D2R)] ; add your own with region()
REG={"vn":[("BMV",(8,30)),("vn8",(70,200)),("dl11",(380,1300)),("dl14",(2600,9000))],
     "hcm":[("BMV",(8,30)),("vn8",(70,200)),("hcm11",(380,1300)),("cl14",(2600,9000))],
     "hh":[("BME",(8,30)),("hh8",(70,200)),("hh11",(380,1300)),("hh14",(2600,9000))],
     "globe":[("BMV",(8,30))]}
def region(name,keys): REG[name]=[(k,r) for k,r in zip(keys,[(8,30),(70,200),(380,1300),(2600,9000)])]
def sat_levels(R,region="vn"):
    s=R*D2R
    return [(_tex("BM"),1.0)]+[(_tex(k),smooth(a,b,s)) for k,(a,b) in REG[region] if _tex(k) is not None]
BM=None
class SatCam:
    """path(t)->(lon,lat,R,rot,tilt[,cy]); renders ortho globe on canvas then perspective tilt"""
    def __init__(s,path,region="vn",cx=540,cy=820,dim=1.0): s.path,s.region,s.cx,s.cy,s.cy0,s.dim=path,region,cx,cy,cy,dim
    def H(s,tilt):
        k=1+0.65*tilt; up=1+0.45*tilt
        src=np.float32([[s.CW/2-540*k,s.CY-s.cy*up],[s.CW/2+540*k,s.CY-s.cy*up],[s.CW/2+540,s.CY+(H-s.cy)],[s.CW/2-540,s.CY+(H-s.cy)]])
        dst=np.float32([[0,0],[W,0],[W,H],[0,H]]); return cv2.getPerspectiveTransform(src,dst)
    def __call__(s,u,t):
        v=s.path(t); lon,lat,R,rot,tilt=v[:5]; s.cy=v[5] if len(v)>5 else s.cy0; s.state=(lon,lat,R,rot,tilt)
        if tilt>0.002:
            k=1+0.65*tilt; s.CW=int(1080*k)+8; s.CY=int(s.cy*(1+0.45*tilt))+4; CH=s.CY+(H-s.cy)+4
            cx,cy=s.CW/2,s.CY
        else: s.CW,CH=W,H; s.CY=s.cy; cx,cy=s.cx,s.cy
        space=starfield(s.CW,CH)
        img=render_globe(s.CW,CH,cx,cy,R,lon,lat,rot,sat_levels(R,s.region),space)
        if R<4000: atmosphere(img,cx,cy,R,1.0 if R<1500 else max(0,(4000-R)/2500))
        s.gcx,s.gcy=cx,cy
        if tilt>0.002:
            s.Hm=s.H(tilt); img=cv2.warpPerspective(img,s.Hm,(W,H),flags=cv2.INTER_LINEAR,borderMode=cv2.BORDER_REPLICATE)
            ys=np.linspace(0,1,H,dtype=np.float32)[:,None,None]; haze=np.clip(1-ys/0.42,0,1)**2*0.55*tilt
            img=img*(1-haze)+haze*np.float32((0.72,0.82,0.92))
        else: s.Hm=None
        d=s.dim(t) if callable(s.dim) else s.dim
        if d!=1.0: img=img*d
        return (np.clip(img,0,1)*255).astype(np.uint8),(0.0,0.0)
    def proj(s,lon,lat):
        lo,la,R,rot,tilt=s.state
        P,vis=ortho_fwd(np.atleast_1d(lon),np.atleast_1d(lat),s.gcx,s.gcy,R,lo,la,rot); s.vis=vis
        if s.Hm is not None: P=cv2.perspectiveTransform(P.reshape(-1,1,2).astype(np.float64),s.Hm.astype(np.float64)).reshape(-1,2)
        return P
