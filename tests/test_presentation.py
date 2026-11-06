import importlib.util,json,tempfile,unittest
from pathlib import Path
spec=importlib.util.spec_from_file_location('presentation',Path(__file__).resolve().parents[1]/'scripts/check_presentation.py')
m=importlib.util.module_from_spec(spec); spec.loader.exec_module(m)
class Presentation(unittest.TestCase):
    def test_good_and_conflicts(self):
        with tempfile.TemporaryDirectory() as d:
            base=Path(d); (base/'logo.png').write_bytes(b'test asset')
            x={'schema':'whiteboard.presentation.v1','platform':'OpenFilm','selection_basis':'user requested','spoken_language':'en','subtitle_languages':['en'],'subtitle_authority':'OpenFilm global','duration':10,'size':[1920,1080],'layout':json.loads(m.PROFILE.read_text()),'chapters':[{'start':0,'end':10,'label':'Products must deliver'}],'logo_path':'logo.png','logo_override_basis':'test fixture','logo_only_reason':'small size'}
            self.assertEqual(m.validate(x,base),[])
            for key,value in [('platform','Remotion'),('subtitle_authority',''),('duration',12),('logo_path','missing.png'),('size',[1080,1920]),('layout',{})]:
                with self.subTest(key=key): self.assertTrue(m.validate(dict(x,**{key:value}),base))
            x.update(subtitle_languages=[],subtitle_authority='none')
            self.assertEqual(m.validate(x,base),[])
    def test_missing(self):
        self.assertTrue(m.validate({},Path('.')))
