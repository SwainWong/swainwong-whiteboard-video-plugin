"""Check declared attention measurements and independent semantic review records."""
import math
import hashlib
import json
from pathlib import Path
CATALOG = json.loads((Path(__file__).resolve().parents[1]/"docs/layout-catalog.json").read_text())
LAYOUTS = {row["id"]:row for row in CATALOG["layouts"]}


def union_area(rects):
    xs=sorted({r[0] for r in rects}|{r[0]+r[2] for r in rects})
    area=0
    for left,right in zip(xs,xs[1:]):
        intervals=sorted((y,y+h) for x,y,w,h in rects if x<right and x+w>left)
        total=0; end=-float('inf')
        for a,b in intervals:
            total+=max(0,b-max(a,end));end=max(end,b)
        area+=(right-left)*total
    return area


def validate(data, target_ids, element_ids, mode, artifact, narration_sha256=None):
    errors=[]
    def check(ok,msg):
        if not ok:errors.append('A01: '+msg)
        return ok
    def num(x):return isinstance(x,(int,float)) and not isinstance(x,bool) and math.isfinite(x)
    def rect(r):return isinstance(r,list) and len(r)==4 and all(num(x) for x in r) and r[2]>0 and r[3]>0
    if not isinstance(data,dict):return ['A01: attention plan required']
    paint=data.get('paint')
    if check(isinstance(paint,list),'paint inventory required, empty only if no painting'):
        for row in paint:
            if not isinstance(row,dict):check(False,'paint row must be object');continue
            check(row.get('element_id') in element_ids,'unknown paint element')
            passes=row.get('passes')
            check(isinstance(passes,int) and not isinstance(passes,bool) and 1<=passes<=3,'painting requires 1–3 visible passes per object')
            a,b=row.get('start'),row.get('end')
            check(num(a) and num(b) and 0<=a<b and b-a<=1.5,'paint elapsed time must be <=1.5s including travel')
    shots=data.get('shots'); seen=set()
    if check(isinstance(shots,list) and bool(shots),'departure/hold shot measurements required'):
        for s in shots:
            if not isinstance(s,dict):check(False,'shot must be object');continue
            sid=s.get('id');check(isinstance(sid,str) and sid and sid not in seen,'unique shot IDs required')
            if isinstance(sid,str):seen.add(sid)
            safe=s.get('safe_rect'); viewport=s.get('viewport')
            if not check(rect(safe) and isinstance(viewport,list) and len(viewport)==2 and all(num(v) and v>0 for v in viewport),'valid viewport and safe_rect required'):continue
            x,y,w,h=safe;vw,vh=viewport
            check(x>=vw*.05 and y>=vh*.05 and x+w<=vw*.95 and y+h<=vh*.95,'reserve at least 5% padding on every side plus UI exclusions')
            boxes=s.get('subjects');rects=[];focals=[]
            if not check(isinstance(boxes,list) and bool(boxes),'tight semantic subject footprints required'):continue
            layout=LAYOUTS.get(s.get('layout_id'))
            check(layout is not None,'known layout_id required')
            check(4<=len(boxes)<=7 or isinstance(s.get('count_exception'),str) and bool(s['count_exception'].strip()),'prefer 4–7 illustration groups; other counts require a semantic reason')
            check(layout is None or layout['count']==len(boxes) or bool(s.get('adaptation_reason')),'layout count mismatch requires adaptation_reason')
            groups=[b.get('group_id') for b in boxes if isinstance(b,dict)]
            check(len(groups)==len(boxes) and all(isinstance(g,str) and g for g in groups) and len(set(g for g in groups if isinstance(g,str)))==len(groups),'unique semantic group IDs required')
            check(sum(b.get('entry') in ('fly','fade') for b in boxes if isinstance(b,dict))<=len(boxes)//3,'direct entries exceed one third of illustration groups')
            for box in boxes:
                if not isinstance(box,dict):check(False,'subject must be object');continue
                check(box.get('entry') in ('pen','fly','fade'),'entry must be pen/fly/fade')
                r=box.get('rect')
                if not check(rect(r),'invalid subject footprint'):continue
                check(box.get('element_id') in element_ids,'unknown subject element')
                xx,yy,ww,hh=r
                check(ww*hh/(w*h)<=.35,'one illustration group exceeds 35% of safe area')
                check(x<=xx and y<=yy and xx+ww<=x+w and yy+hh<=y+h,'subject clipped by safe area')
                rects.append([max(x,xx),max(y,yy),max(0,min(x+w,xx+ww)-max(x,xx)),max(0,min(y+h,yy+hh)-max(y,yy))])
                if box.get('focal') is True:focals.append(r)
            check(union_area(rects)/(w*h)>=.60,'semantic footprint union must occupy >=60% of safe area; aim for 60–85%')
            check(bool(focals) and all(min(r[2],r[3])>=min(w,h)*.15 for r in focals),'focal subject short side must be >=15% of safe-area short side')
            artifact(s.get('frame'),'attention measured frame')
    associations=data.get('associations');covered=set()
    if check(isinstance(associations,list),'semantic associations required'):
        for row in associations:
            if not isinstance(row,dict):check(False,'association must be object');continue
            tid=row.get('target_id')
            check(isinstance(tid,str) and tid in target_ids and tid not in covered,'unique known semantic target required')
            if isinstance(tid,str):covered.add(tid)
            check(all(isinstance(row.get(k),str) and row[k].strip() for k in ('literal_meaning','depiction','why_direct','likely_confusion')),'association must explain literal meaning, depiction and confusion')
            choices=row.get('alternatives');check(isinstance(choices,list) and len(choices)>=2 and all(isinstance(v,str) and v.strip() for v in choices),'compare at least two concrete visual alternatives')
            if mode=='delivery':
                review=row.get('review',{})
                if not isinstance(review,dict):check(False,'independent review required');continue
                author=review.get('author_agent');reviewer=review.get('reviewer_agent')
                check(isinstance(author,str) and bool(author) and isinstance(reviewer,str) and bool(reviewer) and author!=reviewer,'reviewer must differ from author')
                check(review.get('blind_first') is True and isinstance(review.get('blind_guess'),str) and bool(review['blind_guess'].strip()),'saved blind recognition required')
                expected=hashlib.sha256(json.dumps(data.get('shots'),sort_keys=True,ensure_ascii=False).encode()).hexdigest()
                check(review.get('frames_sha256')==expected and review.get('narration_sha256')==narration_sha256,'independent review must bind current frames and narration')
                craft=review.get('craft_scores',[])
                check(isinstance(craft,list) and len(craft)==3 and all(num(v) and 4<=v<=5 for v in craft) and isinstance(review.get('craft_evidence'),str) and bool(review['craft_evidence'].strip()),'structure, depth and detail scores/evidence required')
                scores=review.get('scores',[])
                check(isinstance(scores,list) and len(scores)==4 and all(num(v) and 4<=v<=5 for v in scores) and sum(scores)>=17,'each semantic score >=4/5 and total >=17/20 required')
                check(review.get('status')=='PASS' and review.get('small_preview_readable') is True,'semantic and 320px readability review must pass')
                artifact(review.get('evidence'),'independent semantic review transcript')
    check(covered==set(target_ids),'every narration target needs an association')
    return errors
