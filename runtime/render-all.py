from pathlib import Path
import subprocess,json,hashlib,sys,os
p=Path(__file__).resolve().parent
rows=json.loads((p/'composition-map.json').read_text());selected=set(sys.argv[1:]);(p/'out').mkdir(exist_ok=True)
validation=[]
for r in sorted(rows,key=lambda r:r['id']=='D10'):
 if selected and r['composition'] not in selected:continue
 if r['id']=='D10':subprocess.run([sys.executable,str(p/'build-stage-snapshots.py')],check=True)
 out=p/'out'/f"{r['composition']}.mp4"
 with (p/'out'/f"{r['composition']}.log").open('w') as log:subprocess.run(['npx','remotion','render','src/index.ts',r['composition'],str(out),'--concurrency=4']+(['--browser-executable='+os.environ['REMOTION_BROWSER_EXECUTABLE']] if os.environ.get('REMOTION_BROWSER_EXECUTABLE') else []),cwd=p,stdout=log,stderr=subprocess.STDOUT,check=True)
 d=subprocess.run(['ffmpeg','-v','error','-i',str(out),'-f','null','-'],capture_output=True)
 validation.append({'composition':r['composition'],'sha256':hashlib.sha256(out.read_bytes()).hexdigest(),'decode_exit':d.returncode})
 print(r['composition'],'rendered',flush=True)
if selected and (p/'out/validation.json').exists():validation=[v for v in json.loads((p/'out/validation.json').read_text())['videos'] if v['composition'] not in selected]+validation
(p/'out/validation.json').write_text(json.dumps({'videos':validation,'normal_speed_visual_acceptance':False,'audio':'silent animation recipes'},indent=2))
