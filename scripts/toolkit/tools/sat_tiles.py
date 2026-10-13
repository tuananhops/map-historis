"""Tải mosaic vệ tinh Sentinel-2 cloudless (EOX, CC BY 4.0 — ghi credit) cho cảnh satellite fly-in.
  python3 tools/sat_tiles.py <project>/assets/sat <key> <zoom> <lon0> <lon1> <lat0> <lat1>
  vd: python3 tools/sat_tiles.py proj/assets/sat dl14 14 107.93 108.17 12.6 12.78   → eox_dl14.jpg (+ .txt)
Gợi ý 3 tầng: z8 (vùng ~15°), z11 (~1°), z14 (~0.2°); engine/sat.py: REG/E(k) đọc eox_<key>.jpg."""
import math, os, sys, concurrent.futures, urllib.request
from PIL import Image
def tx(lon,z): return (lon+180)/360*2**z
def ty(lat,z): r=math.radians(lat); return (1-math.log(math.tan(r)+1/math.cos(r))/math.pi)/2*2**z
def mosaic(d,z,lon0,lon1,lat0,lat1,out):
    x0,x1=int(tx(lon0,z)),int(tx(lon1,z)); y0,y1=int(ty(lat1,z)),int(ty(lat0,z))
    cache=os.path.join(d,f"t{z}"); os.makedirs(cache,exist_ok=True)
    jobs=[(x,y) for x in range(x0,x1+1) for y in range(y0,y1+1)]
    def get(xy):
        x,y=xy; p=f"{cache}/{y}_{x}.jpg"
        if not os.path.exists(p):
            req=urllib.request.Request(f"https://tiles.maps.eox.at/wmts/1.0.0/s2cloudless_3857/default/g/{z}/{y}/{x}.jpg",headers={"User-Agent":"HintonMedia-research/1.0"})
            open(p,"wb").write(urllib.request.urlopen(req,timeout=60).read())
        return p
    with concurrent.futures.ThreadPoolExecutor(8) as ex: list(ex.map(get,jobs))
    im=Image.new("RGB",((x1-x0+1)*256,(y1-y0+1)*256))
    for x,y in jobs: im.paste(Image.open(f"{cache}/{y}_{x}.jpg"),((x-x0)*256,(y-y0)*256))
    im.save(out,quality=93); open(out+".txt","w").write(f"{z} {x0} {y0}\n"); print(out,im.size,len(jobs),"tiles")
if __name__=="__main__":
    d,k=sys.argv[1],sys.argv[2]; z=int(sys.argv[3]); a,b,c,e=map(float,sys.argv[4:8]); os.makedirs(d,exist_ok=True)
    mosaic(d,z,a,b,c,e,os.path.join(d,f"eox_{k}.jpg"))
