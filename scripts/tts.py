"""TTS client: uses the persistent daemon (run/tts.sock), starting it on demand; falls back to in-process.
Usage: tts.py <jobdir>. Env TEMPO (1.32), WHISPER (small|base|tiny|none; default none = syllable-weighted timing)."""
import os, sys, json, socket, subprocess, time, fcntl
B=os.path.dirname(os.path.abspath(__file__)); WD=os.environ.get("WORK_DIR",os.path.join(B,"work")); SOCK=f"{WD}/run/tts.sock"; job=os.path.abspath(sys.argv[1])
req={"job":job,"tempo":float(os.environ.get("TEMPO","1.32")),"whisper":os.environ.get("WHISPER","none")}
def ask(r,timeout=900):
    s=socket.socket(socket.AF_UNIX); s.settimeout(timeout); s.connect(SOCK); s.sendall((json.dumps(r)+"\n").encode())
    f=s.makefile(); return f.readline().strip()
def alive():
    try: return ask({"ping":1},5)=="pong"
    except Exception: return False
if not alive() and not os.environ.get("NO_DAEMON"):
    os.makedirs(f"{B}/run",exist_ok=True)
    with open(f"{WD}/run/tts.start.lock","w") as L:
        fcntl.flock(L,fcntl.LOCK_EX)
        if not alive():
            subprocess.Popen([sys.executable,f"{B}/tts_server.py"],stdout=open(f"{WD}/run/tts_server.log","a"),stderr=subprocess.STDOUT,start_new_session=True)
            for _ in range(180):
                time.sleep(0.5)
                if alive(): break
msg=None
if alive():
    try: msg=ask(req)
    except Exception as e: msg="ERROR "+repr(e)
if not msg or msg.startswith("ERROR"):
    if msg: print("daemon failed, in-process fallback:",msg[:300],file=sys.stderr)
    sys.path.insert(0,B); import tts_core; msg=tts_core.run(job,req["tempo"],req["whisper"])
print(msg)
