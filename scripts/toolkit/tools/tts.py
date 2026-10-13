"""edge-tts + word timings.  python3 tools/tts.py [voice] [rate]   (chạy trong thư mục project; đọc script_tts.txt)"""
import asyncio, edge_tts, json, sys, os
voice=sys.argv[1] if len(sys.argv)>1 else 'vi-VN-HoaiMyNeural'; rate=sys.argv[2] if len(sys.argv)>2 else '+15%'
text=open('script_tts.txt').read().strip(); os.makedirs('assets',exist_ok=True)
async def main():
    c=edge_tts.Communicate(text,voice=voice,rate=rate,boundary='WordBoundary')
    words=[]; f=open('assets/vo_raw.mp3','wb')
    async for ev in c.stream():
        if ev['type']=='WordBoundary': words.append({'t0':ev['offset']/1e7,'t1':(ev['offset']+ev['duration'])/1e7,'w':ev['text']})
        elif ev['type']=='audio': f.write(ev['data'])
    f.close(); json.dump(words,open('assets/words.json','w'),ensure_ascii=False,indent=0)
    print(len(words),'words; last end',words[-1]['t1'])
asyncio.run(main())
