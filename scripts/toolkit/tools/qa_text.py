# automated text-rule QA (style_guide §9): safe zone, subtitle/graphic exclusivity, VN number format, caps, sizes
import sys, re, json, os; sys.path.insert(0,os.path.join(os.path.dirname(os.path.abspath(__file__)),"..","engine")); sys.path.insert(0,os.getcwd())
import scenes as S
from textkit import TEXTLOG, SAFE, ROLE
FPS=30; bad=[]
sub={s.name for s in S.SCENES if s.sub}; dur={s.name:(s.f1-s.f0)/FPS for s in S.SCENES}
for scn,text,role,(x0,y0,x1,y1),at in TEXTLOG:
    if scn in sub: bad.append(("TEXT IN SUBTITLE SCENE",scn,text))
    if scn!="end" and (x0<SAFE[0]-2 or x1>SAFE[2]+2 or y0<SAFE[1]-2 or y1>SAFE[3]+2): bad.append(("OUTSIDE SAFE ZONE",scn,text,(x0,y0,x1,y1)))
    if re.search(r"\d,\d{3}\b",text) or re.search(r"\d\.\d{1,2}(?!\d)",text): bad.append(("NON-VN NUMBER",scn,text))
    if role in ("hero","key","title","label","cap","src","map") and not text.startswith("[") and text!=text.upper(): bad.append(("NOT CAPS",scn,text))
    if at>dur[scn]: bad.append(("APPEARS AFTER CUT",scn,text,at))
try:   # glyph coverage: Be Vietnam Pro has no arrows (→ renders blank)
    from fontTools.ttLib import TTFont; from engine import FD
    CM=TTFont(FD+"BeVietnamPro-Bold.ttf").getBestCmap()
    for scn,text,role,box,at in TEXTLOG:
        miss=[ch for ch in text if not ch.isspace() and ord(ch) not in CM]
        if miss: bad.append(("MISSING GLYPH",scn,text,"".join(miss)))
except ImportError: pass
cues=json.load(open("assets/cues.json")); tl=json.load(open("assets/timeline.json"))
for c in cues:
    sc=[n for a,b,n,s in tl if a/FPS<=c["t0"]<b/FPS][0]
    if sc not in sub: bad.append(("SUBTITLE IN GRAPHIC SCENE",sc,c["lines"]))
    for a,b,n,s in tl:
        if a/FPS<c["t1"]-0.01 and b/FPS>c["t0"] and n!=sc: bad.append(("SUBTITLE CROSSES CUT",sc,n,c["lines"]))
    for l in c["lines"]:
        if len(l.split())<2: bad.append(("ORPHAN LINE",l))
        if len(l)>33: bad.append(("LINE TOO LONG",l,len(l)))
    if len(c["lines"])>2: bad.append(("3+ LINES",c["lines"]))
tot=tl[-1][1]/FPS; subs=sum((b-a)/FPS for a,b,n,s in tl if s); maps=sum((b-a)/FPS for a,b,n,s in tl if [x for x in S.SCENES if x.name==n][0].kind=="map")
print(f"text items {len(TEXTLOG)}; subtitle scenes {subs:.1f}s = {subs/tot*100:.1f}%; keyword-graphic scenes {tot-subs:.1f}s = {(tot-subs)/tot*100:.1f}%; map scenes {maps:.1f}s = {maps/tot*100:.1f}%")
for b in bad: print("FAIL",b)
print("ALL TEXT RULES PASS" if not bad else f"{len(bad)} problems")
