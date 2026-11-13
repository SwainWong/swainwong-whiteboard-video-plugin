import copy
import tempfile
import unittest
from pathlib import Path
from test_production import fixture,m,identity

class LayoutMix(unittest.TestCase):
    def test_twenty_distinct_bounded_nonoverlapping_layouts(self):
        rows=m._attention.CATALOG['layouts']
        self.assertEqual(len(rows),20)
        self.assertEqual(len({r['id'] for r in rows}),20)
        for n in range(4,8):self.assertEqual(sum(r['count']==n for r in rows),5)
        for r in rows:
            self.assertEqual(len(r['slots']),r['count'])
            self.assertEqual(sorted(r['suggested_order']),list(range(1,r['count']+1)))
            boxes=[s['rect'] for s in r['slots']]
            for x,y,w,h in boxes:self.assertTrue(0<=x<x+w<=1 and 0<=y<y+h<=1)
            self.assertAlmostEqual(m._attention.union_area(boxes),sum(b[2]*b[3] for b in boxes),places=6)
        self.assertEqual(len({str([s['rect'] for s in r['slots']]) for r in rows}),20)

    def test_direct_entry_quota_and_registered_assets(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base)
            def direct(i):
                x['visual_events'][i]['kind']='fade'
                x['canvas']['elements'][i]['reveal']={'method':'fade','asset':identity(base,'paths.json'),'exit':'hold'}
                x['attention']['shots'][0]['subjects'][i]['entry']='fade'
            direct(0);self.assertEqual(m.validate(x,base),[])
            direct(1);self.assertTrue(any('one third' in e for e in m.validate(x,base)))

    def test_layout_and_oversized_group_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base)
            x['attention']['shots'][0]['layout_id']='missing'
            self.assertTrue(any('layout_id' in e for e in m.validate(x,base)))
            x=fixture(base);x['attention']['shots'][0]['subjects'][0]['rect']=[5,5,90,90]
            self.assertTrue(any('35%' in e for e in m.validate(x,base)))
