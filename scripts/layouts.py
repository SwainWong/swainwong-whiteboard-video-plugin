#!/usr/bin/env python3
"""List or resolve reusable layout envelopes into a project's safe-area pixels."""
import argparse
import json
from pathlib import Path

CATALOG=Path(__file__).resolve().parents[1]/'docs/layout-catalog.json'

def resolve(layout, x, y, width, height):
    if width<=0 or height<=0:raise ValueError('positive safe-area dimensions required')
    return {**layout,'slots':[{'id':s['id'],'rect':[x+s['rect'][0]*width,y+s['rect'][1]*height,s['rect'][2]*width,s['rect'][3]*height]} for s in layout['slots']]}

if __name__=='__main__':
    p=argparse.ArgumentParser(description=__doc__);p.add_argument('--id');p.add_argument('--count',type=int,choices=[4,5,6,7]);p.add_argument('--safe',type=float,nargs=4,metavar=('X','Y','W','H'));a=p.parse_args()
    rows=json.loads(CATALOG.read_text())['layouts']
    if a.count:rows=[r for r in rows if r['count']==a.count]
    if a.id:
        rows=[r for r in rows if r['id']==a.id]
        if not rows:p.error('unknown layout id or count mismatch')
    if a.safe:
        try:rows=[resolve(r,*a.safe) for r in rows]
        except ValueError as e:p.error(str(e))
    print(json.dumps(rows,ensure_ascii=False,indent=2))
