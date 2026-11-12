import copy
import hashlib
import importlib.util
import json
from pathlib import Path
import tempfile
import unittest

spec=importlib.util.spec_from_file_location('production',Path(__file__).resolve().parents[1]/'scripts/check_production.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)


def identity(base,name):
    return {'path':name,'sha256':m.sha(base/name)}


def fixture(base):
    # Synthetic bytes only test identities/configuration, not playable audio or artistic quality.
    (base/'voice.wav').write_bytes(b'synthetic audio identity fixture')
    (base/'paths.json').write_text(json.dumps({'scene':{'effectId':'D01','durationFrames':90,'pen':{'layers':[{'id':'ink'}],'strokes':[{'id':'s1','layer':'ink','d':'M0 0L10 10','width':5,'color':'#151515','start':20,'end':23}]}}}))
    sentences=[{'id':f'h{i}','phase':'hook','text':f'Hook sentence {i}.','start':i-1,'end':i} for i in range(1,4)]
    sentences += [{'id':'brand','phase':'brand','text':'SwainTalk. Follow the tech. Follow the money.','start':3,'end':6},
                  {'id':'b1','phase':'body','text':'A person receives a message.','start':6,'end':8},
                  {'id':'b2','phase':'body','text':'The message opens a door.','start':8,'end':10}]
    for s in sentences:
        if s['phase']!='brand': s['targets']=[{'id':'t-'+s['id'],'mention':s['text'],'depiction':'person and message','entity_type':'object'}]
    (base/'narration.json').write_text(json.dumps({'audio':identity(base,'voice.wav'),'sentences':sentences}))
    brand={'start':3,'end':6,'first_identity_at':3,'phrases':[{'text':text,'start':3+i,'end':4+i,'visible_start':3+i,'visible_end':6} for i,text in enumerate(m.BRAND_PHRASES)]}
    events=[{'id':'v-'+s['id'],'sentence_id':s['id'],'subject':'person and message','meaning':s['text'],'kind':'draw_paths','start':s['start'],'end':s['end']-.2,'readable_until':s['end'],'asset':identity(base,'paths.json')} for s in sentences if s['phase']!='brand']
    data={'schema':'whiteboard.production.v2','duration':10,'narration':identity(base,'narration.json'),'brand':brand,'visual_events':events}
    data['canvas']={'world_id':'paper','persistent':True,'layout':'semantic_freeform','elements':[{'id':'el-'+e['id'],'event_id':e['id'],'target_ids':['t-'+e['sentence_id']],'role':'drawing','world_id':'paper','bounds':[i*100, (i%2)*120,80,80],'reveal':{'method':'pen_path','program':identity(base,'paths.json'),'layer_id':'ink','offset':e['start'],'fps':30}} for i,e in enumerate(events)],'overlaps':[], 'camera':{'world_id':'paper','interpolation':'continuous','route_basis':'Follow related subjects','keyframes':[{'t':0,'x':0,'y':0,'scale':1},{'t':10,'x':100,'y':200,'scale':1}]}}
    (base/'production.json').write_text(json.dumps(data))
    return data


class Production(unittest.TestCase):
    def test_valid_plan_and_hook_footage(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base)
            self.assertEqual(m.validate(x,base),[])
            x['visual_events'][0]['kind']='footage'
            x['canvas']['elements'][0]['role']='footage'
            x['canvas']['elements'][0]['reveal']={'method':'hook_footage'}
            self.assertEqual(m.validate(x,base),[])

    def test_missing_sentence_hold_text_and_paragraph_event_fail(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);original=fixture(base)
            for change in ['missing','hold','text','camera','paragraph']:
                x=copy.deepcopy(original)
                if change=='missing': x['visual_events'].pop()
                elif change=='paragraph': x['visual_events'][-1]['sentence_id']='b1'
                else:x['visual_events'][-1]['kind']=change
                with self.subTest(change=change): self.assertTrue(any('b2' in e for e in m.validate(x,base)))

    def test_logo_before_hook_end_and_wrong_brand_speech_fail(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);x['brand']['first_identity_at']=0
            self.assertTrue(any('H02' in e for e in m.validate(x,base)))
            x=fixture(base);n=json.loads((base/'narration.json').read_text());n['sentences'][3]['text']='Today we discuss the theft.'
            (base/'narration.json').write_text(json.dumps(n));x['narration']=identity(base,'narration.json')
            self.assertTrue(any('B02' in e for e in m.validate(x,base)))

    def test_hook_sentence_count_and_phase_order(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);n=json.loads((base/'narration.json').read_text());n['sentences'][0]['phase']='body'
            (base/'narration.json').write_text(json.dumps(n));x['narration']=identity(base,'narration.json')
            errors=m.validate(x,base)
            self.assertTrue(any('3–5' in e for e in errors));self.assertTrue(any('order must' in e for e in errors))

    def test_brand_leaves_early_and_visual_outside_sentence(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);x['brand']['phrases'][0]['visible_end']=3.5
            self.assertTrue(any('readable throughout' in e for e in m.validate(x,base)))
            x=fixture(base);x['visual_events'][-1]['start']=7
            self.assertTrue(any('within its spoken sentence' in e for e in m.validate(x,base)))

    def test_audio_change_and_bitmap_drawing_rejected(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);(base/'voice.wav').write_bytes(b'changed voice')
            self.assertTrue(any('stale hash' in e for e in m.validate(x,base)))
            x=fixture(base);(base/'image.png').write_bytes(b'bitmap');x['visual_events'][-1]['asset']=identity(base,'image.png')
            self.assertTrue(any('not bitmap' in e for e in m.validate(x,base)))

    def test_delivery_requires_real_review_records_and_current_identity(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base)
            self.assertTrue(m.validate(x,base,'delivery'))
            (base/'candidate.mp4').write_bytes(b'synthetic candidate');(base/'film.html').write_text('synthetic timeline')
            x['candidate']=identity(base,'candidate.mp4');x['timeline']=identity(base,'film.html')
            review={'candidate_sha256':x['candidate']['sha256'],'timeline_sha256':x['timeline']['sha256'],
                    'narration_sha256':x['narration']['sha256'],'normal_speed_viewing':True,'actual_audio_listening':True,
                    'hook_no_brand':'PASS','brand_av_sync':'PASS','sentences':[{'id':e['sentence_id'],'status':'PASS','evidence':'synthetic test record only'} for e in x['visual_events']]}
            for key,field in [('visual_events_sha256','visual_events'),('brand_sha256','brand'),('canvas_sha256','canvas')]:
                review[key]=hashlib.sha256(json.dumps(x[field],sort_keys=True,ensure_ascii=False).encode()).hexdigest()
            review['canvas_checks']={rule:{'status':'PASS','evidence':'synthetic test only'} for rule in ('pen_contact','no_automatic_reveal','literal_semantics','freeform_layout','canvas_continuity')}
            (base/'review.json').write_text(json.dumps(review));x['review']=identity(base,'review.json')
            self.assertEqual(m.validate(x,base,'delivery'),[])
            old_x=copy.deepcopy(x)
            x['canvas']['camera']['route_basis']='changed route'
            self.assertTrue(any('stale canvas' in e for e in m.validate(x,base,'delivery')))
            x=old_x
            checks=review.pop('canvas_checks')
            (base/'review.json').write_text(json.dumps(review));x['review']=identity(base,'review.json')
            self.assertTrue(any('actual pen_contact evidence' in e for e in m.validate(x,base,'delivery')))
            review['canvas_checks']=checks
            review['sentences'].append(dict(review['sentences'][0],status='REVISE'))
            (base/'review.json').write_text(json.dumps(review));x['review']=identity(base,'review.json')
            self.assertTrue(any('unique review' in e for e in m.validate(x,base,'delivery')))
            review['sentences'].pop()
            (base/'review.json').write_text(json.dumps(review));x['review']=identity(base,'review.json')
            x['visual_events'][0]['meaning']='changed semantic plan'
            self.assertTrue(any('stale visual events' in e for e in m.validate(x,base,'delivery')))
            review['actual_audio_listening']=False
            (base/'review.json').write_text(json.dumps(review));x['review']=identity(base,'review.json')
            self.assertTrue(any('actual viewing and listening' in e for e in m.validate(x,base,'delivery')))

    def test_malformed_inputs_and_path_escape(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d)
            for data in [None,{},[],{'schema':'whiteboard.production.v2','duration':float('nan')}]:
                self.assertTrue(m.validate(data,base))
            x=fixture(base);x['narration']['path']='../outside.json'
            self.assertTrue(any('escapes' in e for e in m.validate(x,base)))

if __name__=='__main__':unittest.main()
