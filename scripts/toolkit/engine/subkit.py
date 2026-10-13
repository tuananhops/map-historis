# Subtitle phrase-breaker (Quy tắc chữ §9.6): Vietnamese phrase heuristics, max ~30 chars/line, 1-2 lines,
# no one-word orphan lines, never split number+unit or common compounds; ASS writer with orange bar, no box.
import re
MAXC=30; MAXL=2
CONJ={"nhưng","và","mà","rồi","hay","hoặc","vì","nên","khi","để","thì","là","còn","nếu","chỉ","giờ","kể"}
PREP={"của","cho","với","trong","trên","ở","từ","đến","so","sau","về","ra","vào","tới","lên","xuống","bằng"}
BIND_NEXT={"các","những","một","mỗi","hơn","rất","đã","đang","sẽ","không","chưa","được","bị","thứ","nước","năm","tháng","người","cây","hạt","giá","số","tiền","khoảng","gần","lớn","cà","Việt","Tây","Nhật","Hinton","Bộ","Nông","Brazil,"}
COMP={("cà","phê"),("Việt","Nam"),("Tây","Nguyên"),("Tây","Ban"),("Ban","Nha"),("Nhật","Bản"),("thế","giới"),("năm","ngoái"),("nông","dân"),("Bộ","Nông"),
      ("Nông","nghiệp"),("nghiệp","Mỹ"),("đô","la"),("sản","lượng"),("giá","trị"),("đóng","gói"),("hòa","tan"),("rang","xay"),("thương","hiệu"),("kinh","tế"),
      ("mỗi","ngày"),("hạt","thô"),("châu","Âu"),("thu","về"),("ít","hơn"),("nhiều","hơn"),("mở","rộng"),("đất","đỏ"),("vụ","mùa"),("lịch","sử"),("Hinton","Media"),
      ("khối","lượng"),("xuất","khẩu"),("bình","quân"),("kéo","dài"),("khắp","nơi"),("thú","vị"),("đầu","tiên"),("quay","lại"),("chủ","yếu"),("được","mùa"),("trồng","được"),("đi","xuống")}
UNIT={"triệu","tỷ","nghìn","tấn","đồng","đô","bao","ký","%","năm"}
def isnum(w): return bool(re.match(r"^[\d.,%]+$",w.strip(",.?!:")))
def bad_split(a,b):
    """cost of breaking between word a | b"""
    ca,cb=a.strip(",.?!:;"),b.strip(",.?!:;")
    c=0.0
    if a[-1] in ",.?!:;": return -6.0
    if (ca,cb) in COMP or (ca.lower(),cb.lower()) in COMP: c+=12
    if isnum(ca) and cb.lower() in UNIT|{"triệu","tỷ"}: c+=14
    if ca.lower() in UNIT and isnum(cb): c+=3
    if ca in BIND_NEXT or ca.lower() in BIND_NEXT: c+=5
    if ca.lower() in PREP: c+=6          # a preposition belongs with the noun phrase after it
    if cb.lower() in CONJ: c-=3
    if cb.lower() in PREP: c-=1.5
    return c
def lines_for(ws,with_cost=False):
    """best 1-2 line layout for a cue (list of display words); returns list[str] or None if impossible"""
    s=" ".join(ws)
    if len(s)<=MAXC: return ([s],0.0) if with_cost else [s]
    best=None
    for k in range(2,len(ws)-1):          # each line >= 2 words (no orphans)
        a=" ".join(ws[:k]); b=" ".join(ws[k:])
        if len(a)>MAXC+3 or len(b)>MAXC+3: continue
        cost=bad_split(ws[k-1],ws[k])+abs(len(a)-len(b))*0.08+sum(2 for w in ws[:k-1]+ws[k:-1] if w[-1] in ",.")+max(0,len(a)-MAXC)*2+max(0,len(b)-MAXC)*2
        if best is None or cost<best[0]: best=(cost,[a,b])
    if with_cost: return (best[1],best[0]) if best else (None,99)
    return best[1] if best else None
def make_cues(words,t_end,gap_break=0.45):
    """words: list of dict(d=display text, t0, t1) for ONE subtitled scene.
    Dynamic programming over cue cut points: each cue = 1-2 lines (best phrase break), cuts preferred at
    punctuation/pauses, never inside compounds/number+unit, cues >= 2 words, not too short on screen."""
    n=len(words); ds=[w["d"] for w in words]; INF=1e9
    best=[INF]*(n+1); prev=[0]*(n+1); best[0]=0.0
    for i in range(1,n+1):
        for j in range(max(0,i-14),i):
            if i-j<2 and not (i==n and j==0): continue
            L,c=lines_for(ds[j:i],True)
            if L is None: continue
            dur=words[i-1]["t1"]-words[j]["t0"]
            cost=best[j]+c+3.0+max(0,1.3-dur)*12+(4 if i-j<3 else 0)
            if i<n:
                cut=bad_split(ds[i-1],ds[i]); cut=cut*1.6 if cut>0 else cut*0.7
                if words[i]["t0"]-words[i-1]["t1"]>gap_break: cut-=5
                if ds[i-1][-1] not in ".?!,:;" and words[i]["t0"]-words[i-1]["t1"]<=gap_break: cut+=3
                cost+=cut
            if cost<best[i]: best[i]=cost; prev[i]=j
    cuts=[]; i=n
    while i>0: cuts.append((prev[i],i)); i=prev[i]
    cuts.reverse(); cues=[]
    for j,i in cuts: cues.append(dict(t0=words[j]["t0"],t1=words[i-1]["t1"],lines=lines_for(ds[j:i])))
    for i,cu in enumerate(cues):
        nxt=cues[i+1]["t0"] if i+1<len(cues) else t_end
        cu["t1"]=nxt if nxt-cu["t1"]<0.7 else cu["t1"]+0.35   # hard cut: hold until next phrase (or scene cut)
        cu["t1"]=min(cu["t1"],t_end)
    return cues
def ts(t): return f"{int(t//3600)}:{int(t%3600//60):02d}:{t%60:05.2f}"
def write_ass(cues,path,size=45,lh=1.3,bottom=1500,x_bar=80,bar_w=10,gap=20):
    L=size*lh; xt=x_bar+bar_w+gap
    ass=["[Script Info]","ScriptType: v4.00+","PlayResX: 1080","PlayResY: 1920","WrapStyle: 2","ScaledBorderAndShadow: yes","",
    "[V4+ Styles]","Format: Name, Fontname, Fontsize, PrimaryColour, SecondaryColour, OutlineColour, BackColour, Bold, Italic, Underline, StrikeOut, ScaleX, ScaleY, Spacing, Angle, BorderStyle, Outline, Shadow, Alignment, MarginL, MarginR, MarginV, Encoding",
    f"Style: Sub,Be Vietnam Pro,{size},&H00FFFFFF,&H000000FF,&H00000000,&H99000000,-1,0,0,0,100,100,0,0,1,0,3,1,0,0,0,1",
    "Style: Bar,Be Vietnam Pro,20,&H0035A0EC,&H0035A0EC,&H00000000,&H00000000,0,0,0,0,100,100,0,0,1,0,0,7,0,0,0,1","",
    "[Events]","Format: Layer, Start, End, Style, Name, MarginL, MarginR, MarginV, Effect, Text"]
    for c in cues:
        n=len(c["lines"]); top=bottom-n*L
        ass.append(f"Dialogue: 1,{ts(c['t0'])},{ts(c['t1'])},Bar,,0,0,0,,{{\\an7\\pos({x_bar},{top+size*0.28:.0f})\\p1}}m 0 0 l {bar_w} 0 l {bar_w} {n*L-size*0.3:.0f} l 0 {n*L-size*0.3:.0f}{{\\p0}}")
        for i,l in enumerate(c["lines"]):
            yb=bottom-(n-1-i)*L
            ass.append(f"Dialogue: 2,{ts(c['t0'])},{ts(c['t1'])},Sub,,0,0,0,,{{\\an1\\pos({xt},{yb:.0f})\\blur0.6}}{l}")
    open(path,"w").write("\n".join(ass)+"\n")
