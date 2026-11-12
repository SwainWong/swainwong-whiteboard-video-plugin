"""Declared element, entity and world-camera checks; not pixel/semantic recognition."""
import json
import math
import re


def validate_canvas(data, sentences, artifact):
    errors = []
    def require(ok, message):
        if not ok: errors.append(message)
        return ok
    def number(x): return isinstance(x, (int, float)) and not isinstance(x, bool) and math.isfinite(x)
    def text(x): return isinstance(x, str) and bool(x.strip())
    canvas = data.get('canvas')
    if not isinstance(canvas, dict): return ['C01: persistent canvas inventory required']
    require(canvas.get('layout') == 'semantic_freeform' and canvas.get('persistent') is True,
            'C01: use persistent semantic_freeform canvas, not fixed slots or page resets')
    world = canvas.get('world_id')
    require(text(world), 'C01: shared world_id required')
    events = {e['id']:e for e in data.get('visual_events', []) if isinstance(e,dict) and text(e.get('id'))}
    targets = {}
    for s in sentences:
        if s['phase'] == 'brand': continue
        rows = s.get('targets')
        if not require(isinstance(rows,list) and bool(rows), f"S01 {s['id']}: literal visual targets required"): continue
        for target in rows:
            if not isinstance(target,dict): errors.append('S01: target must be object'); continue
            tid = target.get('id')
            if not require(text(tid) and tid not in targets,'S01: unique target IDs required'): continue
            targets[tid] = (target,s)
            require(text(target.get('mention')) and target['mention'] in s['text'],f'S01 {tid}: mention must quote actual sentence')
            require(text(target.get('depiction')), f'S01 {tid}: direct depiction required')
            kind = target.get('entity_type')
            require(kind in ('named_person','organization','product','role','object','action','data'),f'S01 {tid}: invalid entity type')
            if kind in ('named_person','organization','product'):
                require(text(target.get('identity')) and text(target.get('recognition_cues')),f'S02 {tid}: exact identity and recognition cues required')
                artifact(target.get('reference'), f'S02 {tid} identity reference')
                require(text(target.get('source')),f'S02 {tid}: reference source required')
            if kind == 'role':
                require(target.get('illustrative') is True,f'S02 {tid}: anonymous role must be labeled illustrative')
    elements = canvas.get('elements')
    if not require(isinstance(elements,list) and bool(elements),'R01: inventory every board element, including text and color'): return errors
    ids = {}; covered = set(); event_elements = set(); program_layers = {}; bound_layers = set()
    for el in elements:
        if not isinstance(el,dict): errors.append('R01: element must be object'); continue
        eid=el.get('id'); event=events.get(el.get('event_id')) if isinstance(el.get('event_id'),str) else None
        if not require(text(eid) and eid not in ids,'R01: unique element IDs required'): continue
        ids[eid]=el
        require(el.get('world_id')==world, f'C01 {eid}: all board elements share one world')
        bounds=el.get('bounds')
        require(isinstance(bounds,list) and len(bounds)==4 and all(number(n) for n in bounds) and bounds[2]>0 and bounds[3]>0,f'C02 {eid}: finite [x,y,width,height] bounds required')
        if not require(event is not None,f'R01 {eid}: element must belong to a visual event'): continue
        event_elements.add(event['id'])
        tids=el.get('target_ids')
        if require(isinstance(tids,list) and bool(tids) and all(isinstance(t,str) and t in targets for t in tids), f'S01 {eid}: known semantic targets required'):
            for tid in tids:
                target,s=targets[tid]
                require(event['start']<=s['end'],f'S01 {tid}: depiction appears after its sentence')
                if event['start']<=s['end']: covered.add(tid)
        role=el.get('role')
        require(role in ('drawing','text','image','footage'),f'R01 {eid}: invalid element role')
        reveal=el.get('reveal')
        if not isinstance(reveal,dict): errors.append(f'R01 {eid}: pen-driven reveal required'); continue
        method=reveal.get('method')
        if role == 'footage':
            require(event.get('kind')=='footage' and method=='hook_footage',f'R01 {eid}: footage only in topic hook')
            continue
        expected='pen_mask' if role=='image' else 'pen_path'
        require(method==expected,f'R01 {eid}: no fade, automatic fill, preset text or placement; expected {expected}')
        program=artifact(reveal.get('program'),f'R02 {eid} pen program')
        if not program: continue
        try:
            payload=json.loads(program.read_text()); scene=payload.get('scene',payload); pen=scene.get('pen',{})
            require(scene.get('effectId')=='D01' and not any(scene.get(k) for k in ('draw','objects','foreground','title')),f'R02 {eid}: strict pen program required, legacy fill/title forbidden')
            layers=pen.get('layers',[]); strokes=pen.get('strokes',[])
            if not isinstance(layers,list) or not isinstance(strokes,list): raise ValueError('invalid layers/strokes')
            layer_id=reveal.get('layer_id')
            require(isinstance(layer_id,str) and bool(layer_id),f'R02 {eid}: layer ID required')
            layer=next((l for l in layers if isinstance(l,dict) and l.get('id')==layer_id),None)
            if not require(layer is not None,f'R02 {eid}: missing pen layer'): continue
            require(bool(layer.get('image')) == (role=='image'),f'R02 {eid}: image mask / ink layer mismatch')
            offset=reveal.get('offset'); fps=reveal.get('fps')
            if not require(number(offset) and fps==30,f'R02 {eid}: global offset and runtime fps=30 required'): continue
            key=(str(program),offset)
            layer_names=[l.get('id') for l in layers if isinstance(l,dict)]
            require(len(layer_names)==len(layers) and all(isinstance(n,str) and n for n in layer_names) and len(set(n for n in layer_names if isinstance(n,str)))==len(layer_names),f'R02 {eid}: unique program layers required')
            program_layers[key]={n for n in layer_names if isinstance(n,str)}
            binding=(key,str(layer_id))
            require(binding not in bound_layers,f'R02 {eid}: same layer cannot masquerade as multiple objects')
            bound_layers.add(binding)
            selected=[s for s in strokes if isinstance(s,dict) and s.get('layer')==layer_id]
            require(bool(selected),f'R02 {eid}: layer has no strokes')
            for stroke in selected:
                a,b=stroke.get('start'),stroke.get('end')
                require(number(a) and number(b) and event['start']<=offset+a/fps<offset+b/fps<=event['end'],f'R02 {eid}: ink/paint strokes must complete inside sentence event')
                require(text(stroke.get('d')) and len(re.findall('[mM]',stroke['d']))==1 and number(stroke.get('width')) and stroke['width']>0,f'R02 {eid}: real continuous brush path/width required')
        except (OSError,ValueError,TypeError,AttributeError,KeyError): errors.append(f'R02 {eid}: invalid pen program')
    for key,names in program_layers.items():
        require(all((key,name) in bound_layers for name in names),'R01: pen program contains uninventoried layers')
    for tid in sorted(targets.keys()-covered): errors.append(f'S01 {tid}: spoken target has no direct depicted element')
    for eid in sorted(events.keys()-event_elements): errors.append(f'R01 {eid}: visual event has no inventoried board element')
    # Explicit, reasoned overlaps permit arrows/contact/compositing, not accidental layout collisions.
    allowed=set()
    overlaps=canvas.get('overlaps',[])
    if not isinstance(overlaps,list): errors.append('C02: overlaps must be list'); overlaps=[]
    for pair in overlaps:
        if not isinstance(pair,dict): errors.append('C02: invalid overlap'); continue
        names=pair.get('elements')
        if require(isinstance(names,list) and len(names)==2 and all(isinstance(n,str) and n in ids for n in names) and names[0]!=names[1] and text(pair.get('reason')),'C02: intentional overlap needs two known IDs and reason'):
            allowed.add(frozenset(names))
    valid=[el for el in ids.values() if isinstance(el.get('bounds'),list) and len(el['bounds'])==4 and all(number(n) for n in el['bounds']) and el['bounds'][2]>0 and el['bounds'][3]>0]
    for i,a in enumerate(valid):
        x,y,w,h=a['bounds']
        for b in valid[i+1:]:
            xx,yy,ww,hh=b['bounds']
            if min(x+w,xx+ww)>max(x,xx) and min(y+h,yy+hh)>max(y,yy):
                require(frozenset((a['id'],b['id'])) in allowed,f"C02: unaccounted overlap {a['id']} / {b['id']}")
    camera=canvas.get('camera')
    if not isinstance(camera,dict): return errors+['C03: one continuous world camera required']
    require(camera.get('world_id')==world and camera.get('interpolation')=='continuous' and camera.get('route_basis'), 'C03: continuous camera and semantic route basis required')
    keys=camera.get('keyframes')
    if not require(isinstance(keys,list) and len(keys)>=2,'C03: camera keyframes required'): return errors
    previous=-1
    for key in keys:
        if not isinstance(key,dict): errors.append('C03: keyframe must be object'); continue
        if require(all(number(key.get(k)) for k in ('t','x','y','scale')) and key['scale']>0,'C03: finite camera keyframe required'):
            require(previous<key['t']<=data['duration'],'C03: unique ordered camera times; no cuts/resets')
            previous=key['t']
    require(isinstance(keys[0],dict) and keys[0].get('t')==0 and isinstance(keys[-1],dict) and keys[-1].get('t')==data['duration'],'C03: camera must cover full timeline')
    # Direction is intentionally not counted: narration determines routes, never a random quota.
    return errors
