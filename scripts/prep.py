"""topic.json -> script.txt + spec.json in the job dir"""
import json, sys, os
os.chdir(sys.argv[1]); T=json.load(open("topic.json"))
txt=" ".join(s["text"].strip() for s in T["scenes"]); open("script.txt","w").write(txt+"\n")
spec={"title":T["title"],"script":"script.txt","tail":T.get("tail",1.4),"music":T.get("music","epic"),"reuse_tts":True,
      "scenes":[{"name":s["name"],"start":s.get("start") or " ".join(s["text"].split()[:2]),"sub":False} for s in T["scenes"]]}
json.dump(spec,open("spec.json","w"),ensure_ascii=False,indent=1)
if T.get("spell"): json.dump(T["spell"],open("spell.json","w"),ensure_ascii=False)
print(len(txt.split()),"words,",len(T["scenes"]),"scenes")
