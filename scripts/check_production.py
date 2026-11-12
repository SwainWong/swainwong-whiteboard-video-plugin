#!/usr/bin/env python3
"""Check declared hook, brand timing and sentence coverage; never certify pixels/audio."""
import hashlib
import json
import math
from pathlib import Path
import re
import sys

BODY_KINDS = {'draw_paths', 'outline_trace', 'hand_place'}
HOOK_KINDS = BODY_KINDS | {'footage', 'photo'}
BRAND_PHRASES = ['SwainTalk', 'Follow the tech.', 'Follow the money.']


def sha(path):
    return hashlib.sha256(path.read_bytes()).hexdigest()


def normalized(text):
    return re.sub(r'[^\w]+', ' ', str(text)).strip().casefold()


def validate(data, base, mode='plan'):
    errors = []
    base = Path(base).resolve()

    def require(condition, message):
        if not condition:
            errors.append(message)
        return condition

    def number(value):
        return isinstance(value, (int, float)) and not isinstance(value, bool) and math.isfinite(value)

    def interval(row, label, a='start', b='end'):
        x, y = row.get(a), row.get(b)
        return require(number(x) and number(y) and 0 <= x < y <= duration,
                       f'{label}: invalid {a}/{b}')

    def artifact(value, label):
        if not isinstance(value, dict):
            errors.append(f'{label}: file identity required'); return None
        name = value.get('path')
        if not isinstance(name, str) or not name:
            errors.append(f'{label}: relative path required'); return None
        path = (base / name).resolve()
        if not require(not Path(name).is_absolute() and path.is_relative_to(base), f'{label}: path escapes project'):
            return None
        if not require(path.is_file(), f'{label}: missing file'):
            return None
        if not require(value.get('sha256') == sha(path), f'{label}: stale hash'):
            return None
        return path

    if not isinstance(data, dict):
        return ['production must be an object']
    require(mode in {'plan', 'delivery'}, 'mode must be plan or delivery')
    require(data.get('schema') == 'whiteboard.production.v1', 'production schema required')
    duration = data.get('duration')
    if not require(number(duration) and duration > 0, 'positive duration required'):
        return errors
    narration_path = artifact(data.get('narration'), 'narration')
    if not narration_path:
        return errors
    try:
        narration = json.loads(narration_path.read_text())
    except (OSError, ValueError):
        return errors + ['narration: invalid JSON']
    if not isinstance(narration, dict):
        return errors + ['narration: expected object']
    artifact(narration.get('audio'), 'final narration audio')
    sentences = narration.get('sentences')
    if not require(isinstance(sentences, list) and bool(sentences), 'sentence inventory required'):
        return errors
    ids = {}; previous = 0
    for s in sentences:
        if not isinstance(s, dict):
            errors.append('sentence must be object'); continue
        sid = s.get('id')
        if not require(isinstance(sid, str) and bool(sid) and sid not in ids, 'unique sentence IDs required'):
            continue
        ids[sid] = s
        require(isinstance(s.get('text'), str) and bool(s['text'].strip()), f'{sid}: exact narration required')
        require(s.get('phase') in {'hook', 'brand', 'body'}, f'{sid}: invalid phase')
        if interval(s, sid):
            require(s['start'] >= previous, f'{sid}: sentence order/overlap')
            previous = s['end']
    if errors:
        return errors
    hook = [s for s in sentences if s['phase'] == 'hook']
    brands = [s for s in sentences if s['phase'] == 'brand']
    body = [s for s in sentences if s['phase'] == 'body']
    require(3 <= len(hook) <= 5, 'H01: hook must contain 3–5 complete spoken sentences')
    require(bool(body), 'body sentences required')
    require(len(brands) == 1, 'B01: one spoken intro brand cue required')
    require([s['phase'] for s in sentences] == ['hook']*len(hook)+['brand']*len(brands)+['body']*len(body),
            'H01: order must be hook → spoken brand → body')
    brand = data.get('brand')
    if not isinstance(brand, dict):
        return errors + ['B01: brand timing required']
    if not interval(brand, 'brand') or not hook or len(brands) != 1 or not body:
        return errors
    require(hook[-1]['end'] <= brand['start'] and brand['end'] <= body[0]['start'], 'B01: brand must follow hook and precede body')
    require(brand['start'] <= brands[0]['start'] and brands[0]['end'] <= brand['end'], 'B02: voice must fit brand station')
    require(normalized(brands[0]['text']) == normalized(' '.join(BRAND_PHRASES)), 'B02: voice must say channel name and exact slogan')
    first = brand.get('first_identity_at')
    require(number(first) and brand['start'] <= first <= brands[0]['start'], 'H02: no logo, slogan, watermark or channel identity before brand station')
    phrases = brand.get('phrases')
    if not require(isinstance(phrases, list) and len(phrases) == 3, 'B02: three aligned brand phrases required'):
        return errors
    previous = brands[0]['start']
    for i, (phrase, expected) in enumerate(zip(phrases, BRAND_PHRASES)):
        label = f'B02 phrase {i+1}'
        if not isinstance(phrase, dict):
            errors.append(f'{label}: expected object'); continue
        require(normalized(phrase.get('text')) == normalized(expected), f'{label}: wrong text')
        if interval(phrase, label) and interval(phrase, label, 'visible_start', 'visible_end'):
            a,b = phrase['start'],phrase['end']
            require(previous <= a and b <= brands[0]['end'], f'{label}: outside brand audio/order')
            previous = b
            require(brand['start'] <= phrase['visible_start'] <= a and b <= phrase['visible_end'] <= brand['end'],
                    f'{label}: corresponding logo/slogan must be readable throughout spoken phrase')
            require(number(first) and first <= phrase['visible_start'], f'{label}: identity visibility contradicts first_identity_at')
    events = data.get('visual_events')
    if not require(isinstance(events, list), 'visual_events required'):
        return errors
    covered = set(); event_ids = set()
    for e in events:
        if not isinstance(e, dict):
            errors.append('visual event must be object'); continue
        eid = e.get('id'); sid = e.get('sentence_id'); sentence = ids.get(sid) if isinstance(sid,str) else None
        require(isinstance(eid,str) and bool(eid) and eid not in event_ids, 'V01: unique visual event IDs required')
        if isinstance(eid,str): event_ids.add(eid)
        if not require(sentence is not None and sentence['phase'] != 'brand', f'{eid}: unknown/non-content sentence'):
            continue
        valid = interval(e, str(eid))
        allowed = HOOK_KINDS if sentence['phase']=='hook' else BODY_KINDS
        valid = require(e.get('kind') in allowed, f'{sid}: static hold, text, camera motion or unrelated decoration cannot count as coverage') and valid
        valid = require(all(isinstance(e.get(k),str) and bool(e[k].strip()) for k in ['subject','meaning']), f'{sid}: subject and spoken meaning required') and valid
        if valid:
            valid = require(sentence['start'] <= e['start'] < e['end'] <= sentence['end'], f'{sid}: visual action must occur within its spoken sentence') and valid
            valid = require(number(e.get('readable_until')) and e['end'] <= e['readable_until'] <= duration and e['readable_until'] >= sentence['end'], f'{sid}: retain completed image through sentence end') and valid
        asset = artifact(e.get('asset'), f'{sid} asset')
        if asset and e.get('kind') in {'draw_paths','outline_trace'}:
            valid = require(asset.suffix.lower() in {'.svg','.json'}, f'{sid}: drawing requires editable path asset, not bitmap') and valid
        if valid and asset:
            covered.add(sid)
    required = {s['id'] for s in sentences if s['phase'] != 'brand'}
    for sid in sorted(required-covered): errors.append(f'V01: sentence {sid} has no qualifying visual event')
    if mode == 'delivery':
        candidate = artifact(data.get('candidate'), 'candidate video')
        timeline = artifact(data.get('timeline'), 'editable timeline')
        review_path = artifact(data.get('review'), 'review')
        if review_path:
            try:
                review = json.loads(review_path.read_text())
                require(isinstance(review,dict), 'review must be object')
                if isinstance(review,dict):
                    for key, expected in [('candidate_sha256',sha(candidate) if candidate else None),
                                          ('timeline_sha256',sha(timeline) if timeline else None),
                                          ('narration_sha256',sha(narration_path))]:
                        require(expected is not None and review.get(key)==expected, f'review: stale {key}')
                    require(review.get('visual_events_sha256') == hashlib.sha256(json.dumps(events,sort_keys=True,ensure_ascii=False).encode()).hexdigest(), 'review: stale visual events')
                    require(review.get('brand_sha256') == hashlib.sha256(json.dumps(brand,sort_keys=True,ensure_ascii=False).encode()).hexdigest(), 'review: stale brand timing')
                    require(review.get('normal_speed_viewing') is True and review.get('actual_audio_listening') is True, 'delivery: actual viewing and listening records required')
                    require(review.get('hook_no_brand') == 'PASS' and review.get('brand_av_sync') == 'PASS', 'delivery: hook/brand review must pass')
                    rows = review.get('sentences',[])
                    require(isinstance(rows,list), 'delivery: review sentences must be array')
                    rows = rows if isinstance(rows,list) else []
                    row_ids = [r.get('id') for r in rows if isinstance(r,dict) and isinstance(r.get('id'),str)]
                    require(len(row_ids)==len(rows) and len(set(row_ids))==len(row_ids), 'delivery: unique review sentence IDs required')
                    passed = {r.get('id') for r in rows if isinstance(r,dict) and isinstance(r.get('id'),str) and r.get('status')=='PASS' and isinstance(r.get('evidence'),str) and r['evidence'].strip()}
                    require(required <= passed, 'delivery: per-sentence semantic/visual review evidence missing')
            except (OSError, ValueError, TypeError): errors.append('review: invalid JSON')
    return errors


def main():
    import argparse
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('manifest',type=Path)
    parser.add_argument('--mode',choices=['plan','delivery'],default='plan')
    args=parser.parse_args()
    try:
        errors=validate(json.loads(args.manifest.read_text()),args.manifest.parent,args.mode)
    except (OSError,ValueError,TypeError,KeyError) as e: errors=[str(e)]
    print(json.dumps({'status':'FAIL' if errors else 'PASS','mode':args.mode,
                      'scope':'declared timing, coverage, file identities and review records only; not independent audiovisual verification',
                      'errors':errors},ensure_ascii=False,indent=2))
    return bool(errors)

if __name__=='__main__': sys.exit(main())
