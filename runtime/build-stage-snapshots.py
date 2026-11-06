"""Extract actual completed frames, retaining their entire rendered content and provenance."""
from pathlib import Path
import json,subprocess,hashlib
p=Path(__file__).resolve().parent
rows=json.loads((p/'composition-map.json').read_text())
selected=[r for r in rows if r['id']!='D10']
output=p/'public/assets/completed-stages';output.mkdir(parents=True,exist_ok=True)
stages=[]
for i,r in enumerate(selected):
 src=p/'out'/f"{r['composition']}.mp4"
 info=json.loads(subprocess.check_output(['ffprobe','-v','error','-select_streams','v:0','-show_entries','stream=nb_frames','-of','json',str(src)]))
 frame=int(info['streams'][0]['nb_frames'])-1
 dst=output/f"{r['id']}.png"
 subprocess.run(['ffmpeg','-y','-v','error','-i',str(src),'-vf',f'select=eq(n\\,{frame})','-frames:v','1',str(dst)],check=True)
 stages.append({'id':r['id'],'src':str(dst.relative_to(p/'public')),'provenance':{'sourceComposition':r['composition'],'sourceVideoSHA256':hashlib.sha256(src.read_bytes()).hexdigest(),'frame':frame,'snapshotSHA256':hashlib.sha256(dst.read_bytes()).hexdigest()}})
(p/'src/stage-snapshots.json').write_text(json.dumps(stages,ensure_ascii=False,indent=2))
print(f'Extracted {len(stages)} actual completed frames; no crop or invented content')
