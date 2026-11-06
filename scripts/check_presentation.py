#!/usr/bin/env python3
"""Validate full-film presentation inputs, not rendered pixels or AV acceptance."""
import hashlib
import json
import math
from pathlib import Path
import sys
PROFILE = Path(__file__).resolve().parents[1] / 'docs/presentation-profile.json'

def validate(data, base):
    errors=[]
    def require(ok, msg):
        if not ok: errors.append(msg)
    def number(v): return isinstance(v,(int,float)) and not isinstance(v,bool) and math.isfinite(v)
    defaults=json.loads(PROFILE.read_text())
    require(data.get('schema')==defaults['schema'],'schema must be whiteboard.presentation.v1')
    require(data.get('platform') in defaults['platforms'] or bool(data.get('platform_override')),'explicit supported platform or documented override required')
    require(bool(data.get('selection_basis')),'selection_basis required')
    require(bool(data.get('spoken_language')),'spoken_language required')
    langs=data.get('subtitle_languages')
    require(isinstance(langs,list) and len(langs)<=2 and all(isinstance(x,str) and x for x in langs),'subtitle_languages must be explicit array of 0–2 languages')
    require(bool(data.get('subtitle_authority')) if langs else data.get('subtitle_authority')=='none','one subtitle authority required; none for no subtitles')
    duration=data.get('duration'); require(number(duration) and duration>0,'positive duration required')
    size=data.get('size'); require(isinstance(size,list) and len(size)==2 and all(number(x) and x>0 for x in size),'positive size pair required')
    override=bool(data.get('layout_override')) and bool(data.get('review_evidence'))
    if size and isinstance(size,list) and len(size)==2 and all(number(x) and x>0 for x in size):
        require(abs(size[0]/size[1]-16/9)<0.001 or override,'non-16:9 requires reviewed layout override')
    require(data.get('layout')==defaults or override,'layout must equal reference profile or have reviewed override')
    if override:
        evidence=base/str(data['review_evidence'])
        require(evidence.is_file(),'review_evidence file missing')
    chapters=data.get('chapters',[]); require(isinstance(chapters,list) and bool(chapters),'chapters required')
    previous=0
    if isinstance(chapters,list):
        for c in chapters:
            if not isinstance(c,dict): errors.append('chapter must be object'); continue
            a,b=c.get('start'),c.get('end')
            valid=number(a) and number(b) and a>=0 and b>a
            require(valid,'invalid chapter interval')
            if valid:
                require(abs(a-previous)<0.001,'chapters must cover timeline continuously'); previous=b
            require(bool(c.get('label')) and c.get('label','').strip().lower() not in {'intro','outro','summary','opening','开篇','总结'},'chapter needs a specific argument label')
        if number(duration): require(abs(previous-duration)<0.001,'chapters must end at actual duration')
    name=data.get('logo_path',''); path=base/name
    require(bool(name) and not Path(name).is_absolute() and path.resolve().is_relative_to(base.resolve()),'logo_path must be project-relative')
    require(path.is_file(),'logo asset missing')
    if path.is_file(): require(hashlib.sha256(path.read_bytes()).hexdigest()==defaults['logo']['sha256'] or bool(data.get('logo_override_basis')),'original logo hash mismatch')
    require(bool(data.get('logo_only_reason')),'corner logo-only readability reason required')
    return errors

if __name__=='__main__':
    try:
        path=Path(sys.argv[1]); data=json.loads(path.read_text())
        errors=validate(data,path.parent)
    except (IndexError,ValueError,TypeError,OSError) as e: errors=[str(e)]
    print(json.dumps({'status':'FAIL' if errors else 'PASS','scope':'configuration only; not pixels or audiovisual acceptance','errors':errors},ensure_ascii=False,indent=2))
    sys.exit(bool(errors))
