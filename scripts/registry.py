"""Topic registry (no repeats). Path: $REGISTRY or $WORK_DIR/topics_done.json.
Atomic registry ops (flock on topics_done.json.lock, write via tmp+rename).
  registry.py reserve "<title>"        -> prints number (adds to in_progress, nums, bumps next_num)
  registry.py done "<title>" [link]    -> moves to done (+uploaded link)
  registry.py fail "<title>"           -> removes from in_progress"""
import json, sys, os, fcntl
B=os.path.dirname(os.path.abspath(__file__)); WD=os.environ.get("WORK_DIR",os.path.join(B,"work")); R=os.environ.get("REGISTRY",f"{WD}/topics_done.json")
os.makedirs(os.path.dirname(os.path.abspath(R)),exist_ok=True)
if len(sys.argv)<3: print(__doc__); sys.exit(0)
if not os.path.exists(R): json.dump({"next_num":1,"done":[],"in_progress":[],"nums":{},"uploaded":{}},open(R,"w"))
with open(R+".lock","a") as L:
    fcntl.flock(L,fcntl.LOCK_EX); d=json.load(open(R)); op,t=sys.argv[1],sys.argv[2]
    if op=="reserve":
        if t in d.get("nums",{}):
            if t not in d["in_progress"]: d["in_progress"].append(t)
            json.dump(d,open(R+".tmp","w"),ensure_ascii=False,indent=1); os.replace(R+".tmp",R)
            print(d["nums"][t]); sys.exit()
        n=d["next_num"]; d["next_num"]=n+1; d.setdefault("nums",{})[t]=n
        if t not in d["in_progress"]: d["in_progress"].append(t)
        print(n)
    elif op=="done":
        if t in d["in_progress"]: d["in_progress"].remove(t)
        if t not in d["done"]: d["done"].append(t)
        if len(sys.argv)>3: d.setdefault("uploaded",{})[t]=sys.argv[3]
    elif op=="fail":
        if t in d["in_progress"]: d["in_progress"].remove(t)
    json.dump(d,open(R+".tmp","w"),ensure_ascii=False,indent=1); os.replace(R+".tmp",R)
