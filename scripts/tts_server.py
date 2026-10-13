"""Persistent TTS daemon: keeps MMS + whisper loaded. Unix socket run/tts.sock; request = JSON line {job,tempo,whisper}; reply = one line."""
import os, sys, json, socketserver, threading, traceback, torch
sys.path.insert(0,os.path.dirname(os.path.abspath(__file__))); import tts_core
torch.set_num_threads(int(os.environ.get("TTHREADS","3")))
SOCK=os.path.join(os.environ.get("WORK_DIR",os.path.join(os.path.dirname(os.path.abspath(__file__)),"work")),"run","tts.sock"); os.makedirs(os.path.dirname(SOCK),exist_ok=True)
tts_core.load(os.environ.get("WHISPER","none")); SEM=threading.Semaphore(2)
class H(socketserver.StreamRequestHandler):
    def handle(self):
        r=json.loads(self.rfile.readline())
        if r.get("ping"): self.wfile.write(b"pong\n"); return
        with SEM:
            try: msg=tts_core.run(r["job"],float(r.get("tempo",1.32)),r.get("whisper","small"))
            except Exception: msg="ERROR "+traceback.format_exc().replace("\n"," | ")
        self.wfile.write((msg+"\n").encode())
class S(socketserver.ThreadingMixIn,socketserver.UnixStreamServer): daemon_threads=True
if os.path.exists(SOCK): os.unlink(SOCK)
tmp=SOCK+".tmp"; 
if os.path.exists(tmp): os.unlink(tmp)
srv=S(tmp,H); os.rename(tmp,SOCK); print("tts daemon ready",flush=True); srv.serve_forever()
