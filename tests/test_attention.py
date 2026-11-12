import copy
import hashlib
import json
from pathlib import Path
import tempfile
import unittest
from test_production import fixture, m, identity


class Attention(unittest.TestCase):
    def test_union_counts_overlap_once_and_excludes_gaps(self):
        self.assertEqual(m._attention.union_area([[0,0,10,10],[5,0,10,10]]),150)
        self.assertEqual(m._attention.union_area([[0,0,10,10],[90,90,10,10]]),200)

    def test_reject_slow_paint_small_subject_sparse_and_missing(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);original=fixture(base)
            mutations=[lambda x:x.pop('attention'),
                       lambda x:x['attention'].update(paint=[{'element_id':'el-v-h1','passes':4,'start':0,'end':1}]),
                       lambda x:x['attention'].update(paint=[{'element_id':'el-v-h1','passes':3,'start':0,'end':3}]),
                       lambda x:x['attention']['shots'][0]['subjects'][0].update(rect=[5,5,20,20]),
                       lambda x:x['attention']['shots'][0]['subjects'].append({'element_id':'el-v-h2','rect':[5,5,5,5],'focal':True}),
                       lambda x:x['attention']['associations'].pop()]
            for change in mutations:
                x=copy.deepcopy(original);change(x)
                self.assertTrue(m.validate(x,base))

    def test_independent_scores_and_current_binding(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);a=x['attention']
            for row in a['associations']:
                row['review']={'author_agent':'author','reviewer_agent':'reviewer','blind_first':True,'blind_guess':'synthetic guess','scores':[5,4,4,4],'status':'PASS','small_preview_readable':True,'evidence':identity(base,'paths.json'),'narration_sha256':x['narration']['sha256'],'frames_sha256':hashlib.sha256(json.dumps(a['shots'],sort_keys=True,ensure_ascii=False).encode()).hexdigest()}
            ids={r['target_id'] for r in a['associations']};els={e['id'] for e in x['canvas']['elements']}
            def run(a):return m._attention.validate(a,ids,els,'delivery',lambda v,label:base/v['path'],x['narration']['sha256'])
            self.assertEqual(run(a),[])
            for values in [{'reviewer_agent':'author'},{'scores':[4,4,4,4]},{'scores':[5,5,5,3]},{'blind_first':False},{'frames_sha256':'stale'},{'status':'REVISE'}]:
                changed=copy.deepcopy(a);changed['associations'][0]['review'].update(values)
                self.assertTrue(run(changed))
