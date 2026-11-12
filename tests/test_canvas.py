import copy
import json
from pathlib import Path
import tempfile
import unittest
from test_production import m, fixture, identity


class Canvas(unittest.TestCase):
    def check_change(self, change, expected):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); x=fixture(base); change(x,base)
            self.assertTrue(any(expected in e for e in m.validate(x,base)),m.validate(x,base))

    def test_legacy_and_missing_inventory_fail(self):
        self.check_change(lambda x,b:x.update(schema='whiteboard.production.v1'),'v2 required')
        self.check_change(lambda x,b:x.pop('canvas'),'canvas inventory')
        self.check_change(lambda x,b:x['canvas']['elements'].pop(),'no inventoried')

    def test_no_auto_fill_fade_or_preset_text(self):
        for method in ['fade','auto_fill','preexisting','rect_wipe','hand_place']:
            with self.subTest(method=method):
                self.check_change(lambda x,b:x['canvas']['elements'][0]['reveal'].update(method=method),'no fade')
        def legacy(x,b):
            payload=json.loads((b/'paths.json').read_text());payload['scene']['title']='preset text'
            (b/'paths.json').write_text(json.dumps(payload))
            for el in x['canvas']['elements']:el['reveal']['program']=identity(b,'paths.json')
            for event in x['visual_events']:event['asset']=identity(b,'paths.json')
        self.check_change(legacy,'legacy fill/title forbidden')

    def test_named_entity_needs_identity_reference(self):
        def named(x,b):
            n=json.loads((b/'narration.json').read_text());n['sentences'][-1]['targets'][0].update(entity_type='named_person')
            (b/'narration.json').write_text(json.dumps(n));x['narration']=identity(b,'narration.json')
        self.check_change(named,'identity reference')
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);n=json.loads((base/'narration.json').read_text());s=n['sentences'][-1]
            s['text']='CZ speaks.';s['targets']=[{'id':'t-b2','mention':'CZ','depiction':'CZ portrait speaking','entity_type':'named_person','identity':'CZ','recognition_cues':'reference facial silhouette','reference':identity(base,'paths.json'),'source':'synthetic reference fixture'}]
            (base/'narration.json').write_text(json.dumps(n));x['narration']=identity(base,'narration.json')
            self.assertEqual(m.validate(x,base),[])
            s['targets'][0]['mention']='Someone else'
            (base/'narration.json').write_text(json.dumps(n));x['narration']=identity(base,'narration.json')
            self.assertTrue(any('quote actual sentence' in e for e in m.validate(x,base)))

    def test_collisions_and_fixed_slots_rejected(self):
        self.check_change(lambda x,b:x['canvas'].update(layout='three_slots'),'semantic_freeform')
        self.check_change(lambda x,b:x['canvas']['elements'][1].update(bounds=[0,0,80,80]),'unaccounted overlap')
        with tempfile.TemporaryDirectory() as d:
            x=fixture(Path(d));x['canvas']['elements'][1]['bounds']=[0,0,80,80]
            x['canvas']['overlaps']=[{'elements':['el-v-h1','el-v-h2'],'reason':'intentional contact, verify pixels'}]
            self.assertEqual(m.validate(x,Path(d)),[])

    def test_free_directions_and_object_counts_without_direction_quota(self):
        with tempfile.TemporaryDirectory() as d:
            x=fixture(Path(d))
            x['canvas']['camera']['keyframes']=[{'t':i*2,'x':xx,'y':yy,'scale':1} for i,(xx,yy) in enumerate([(0,0),(100,100),(200,-100),(-100,-200),(-200,200),(0,0)])]
            self.assertEqual(m.validate(x,Path(d)),[])
            # No fixed upper object count: add six meaningful elements in this declared fixture.
            base=Path(d);program=json.loads((base/'paths.json').read_text())
            layers=program['scene']['pen']['layers'];strokes=program['scene']['pen']['strokes']
            extra=[]
            for i in range(6):
                layer=f'extra-{i}';layers.append({'id':layer})
                strokes.append(dict(strokes[0],id=layer,layer=layer,start=24+i*4,end=27+i*4))
                el=copy.deepcopy(x['canvas']['elements'][-1]);el['id']=layer;el['bounds']=[700+i*100,0,80,80];el['reveal']['layer_id']=layer
                extra.append(el)
            (base/'more.json').write_text(json.dumps(program))
            x['canvas']['elements'][-1]['reveal']['program']=identity(base,'more.json')
            for el in extra:el['reveal']['program']=identity(base,'more.json')
            x['canvas']['elements'].extend(extra)
            self.assertEqual(m.validate(x,Path(d)),[])

    def test_world_reset_and_camera_cut_rejected(self):
        self.check_change(lambda x,b:x['canvas']['elements'][0].update(world_id='page2'),'one world')
        self.check_change(lambda x,b:x['canvas']['camera'].update(interpolation='slide'),'continuous camera')
        self.check_change(lambda x,b:x['canvas']['camera']['keyframes'].insert(1,{'t':0,'x':1000,'y':0,'scale':1}),'no cuts/resets')

    def test_missing_pen_layer_and_out_of_window_color_fail(self):
        self.check_change(lambda x,b:x['canvas']['elements'][0]['reveal'].update(layer_id='missing'),'missing pen layer')
        self.check_change(lambda x,b:x['canvas']['elements'][0]['reveal'].update(offset=5),'complete inside sentence')

    def test_no_uninventoried_or_reused_layers(self):
        def hidden(x,b):
            program=json.loads((b/'paths.json').read_text());program['scene']['pen']['layers'].append({'id':'hidden'})
            (b/'paths.json').write_text(json.dumps(program))
            for e in x['visual_events']: e['asset']=identity(b,'paths.json')
            for el in x['canvas']['elements']:el['reveal']['program']=identity(b,'paths.json')
        self.check_change(hidden,'uninventoried layers')
        def duplicate(x,b):
            el=copy.deepcopy(x['canvas']['elements'][0]);el['id']='duplicated';el['bounds']=[2000,2000,80,80]
            x['canvas']['elements'].append(el)
        self.check_change(duplicate,'masquerade')

    def test_third_party_image_requires_mask(self):
        self.check_change(lambda x,b:x['canvas']['elements'][0].update(role='image'),'expected pen_mask')
        with tempfile.TemporaryDirectory() as d:
            base=Path(d);x=fixture(base);program=json.loads((base/'paths.json').read_text())
            program['scene']['pen']['layers'][0]['image']={'src':'photo.png','x':0,'y':0,'width':80,'height':80}
            (base/'masked.json').write_text(json.dumps(program))
            x['canvas']['elements'][0]['role']='image'
            x['canvas']['elements'][0]['reveal'].update(method='pen_mask',program=identity(base,'masked.json'))
            x['visual_events'][0]['kind']='brush_reveal'
            self.assertEqual(m.validate(x,base),[])

if __name__=='__main__': unittest.main()
