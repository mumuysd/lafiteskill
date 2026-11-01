"""Offline synthetic-input regressions; no image generation or likeness assertion."""
import copy,hashlib,importlib.util,json,subprocess,sys,tempfile,unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
spec=importlib.util.spec_from_file_location('assemble',ROOT/'scripts/assemble_character.py')
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)
read=lambda p:json.loads(p.read_text())

class PackageTests(unittest.TestCase):
    def setUp(self):
        self.tmp=tempfile.TemporaryDirectory(prefix='lafite-regression-')
        self.base=Path(self.tmp.name).resolve()
        # Byte fixture checks local file/hash handling, not pet identity or image quality.
        self.image=self.base/'identity.ppm'
        self.image.write_bytes(b'P6\n1 1\n255\n\x80\x80\x80')
        self.profile=read(ROOT/'style_profile.json')
        self.plan=read(ROOT/'tests/fixtures/cat-plan.json')
        self.comp=read(ROOT/'tests/fixtures/cat-composition.json')
        self.plan['reference_inputs']=[{'role':'identity','path':'identity.ppm','sha256':hashlib.sha256(self.image.read_bytes()).hexdigest()}]
    def tearDown(self):self.tmp.cleanup()
    def assemble(self):return module.assemble(self.plan,self.comp,self.profile,self.base)
    def test_cat_plan(self):
        prompt,trace=self.assemble()
        self.assertEqual(trace['request']['referenced_image_paths'],[str(self.image)])
        self.assertEqual(prompt.count(self.profile['generation_instructions']['style_prompt']),1)
        self.assertFalse(trace['generated'])
    def test_dog_plan(self):
        refs=self.plan['reference_inputs']
        self.plan=read(ROOT/'tests/fixtures/dog-plan.json')
        self.plan['reference_inputs']=refs
        self.comp=read(ROOT/'tests/fixtures/dog-composition.json')
        self.assertIn('dog',self.assemble()[0].lower())
    def test_version_mismatch(self):
        self.plan['profile_version']='old'
        with self.assertRaises(ValueError):self.assemble()
    def test_hash_mismatch(self):
        self.plan['reference_inputs'][0]['sha256']='0'*64
        with self.assertRaises(ValueError):self.assemble()
    def test_missing_identity(self):
        self.plan['reference_inputs']=[]
        with self.assertRaises(ValueError):self.assemble()
    def test_duplicate_reference(self):
        self.plan['reference_inputs'].append(dict(self.plan['reference_inputs'][0],role='quality'))
        with self.assertRaises(ValueError):self.assemble()
    def test_invalid_role(self):
        self.plan['reference_inputs'][0]['role']='mood'
        with self.assertRaises(ValueError):self.assemble()
    def test_uncertain_structure(self):
        struct=self.base/'structure.ppm';struct.write_bytes(self.image.read_bytes())
        self.plan['reference_inputs'].append({'role':'structure','path':'structure.ppm','sha256':hashlib.sha256(struct.read_bytes()).hexdigest()})
        self.plan['design_review']['structure_status']='uncertain'
        with self.assertRaises(ValueError):self.assemble()
    def test_unreviewed_design(self):
        self.plan['design_review']['status']='draft'
        with self.assertRaises(ValueError):self.assemble()
    def test_gaze_mismatch(self):
        self.comp['viewer_relationship']='viewer'
        with self.assertRaises(ValueError):self.assemble()
    def test_uncompared_clothing(self):
        self.plan['clothing_options']=[]
        with self.assertRaises(ValueError):self.assemble()
    def test_explicit_no_clothing_closed_eyes(self):
        self.plan.update(clothing_options=[],clothing_override='User explicitly requests no clothes',clothing_response='Unclothed body follows a resting pose.',clothing_choice_reason='Follow user request.',gaze_mode='closed',gaze='Eyes closed while resting, not looking at the viewer.')
        self.comp['viewer_relationship']='closed'
        self.assertIn('Eyes closed',self.assemble()[0])
    def test_example_from_other_working_directory(self):
        args=[sys.executable,str(ROOT/'scripts/assemble_character.py'),'--plan',str(ROOT/'examples/character-plan.json'),'--composition',str(ROOT/'examples/composition-intent.json'),'--profile',str(ROOT/'style_profile.json'),'--prompt',str(self.base/'prompt.txt'),'--trace',str(self.base/'trace.json'),'--request',str(self.base/'request.json')]
        subprocess.run(args,cwd=self.base,check=True,capture_output=True,text=True)
        req=read(self.base/'request.json')
        self.assertEqual(req['referenced_image_paths'],[str(ROOT/'assets/approved/lafite-approved.png')])
        self.assertIn('Image 1 is ONLY a painting-quality reference',req['prompt'])
        self.assertNotIn('Image 2',req['prompt'])
    def test_local_install_and_no_overwrite(self):
        target=self.base/'installed/lafiteskill'
        args=[sys.executable,str(ROOT/'scripts/install_local.py'),'--target',str(target)]
        subprocess.run(args,check=True,capture_output=True,text=True)
        self.assertEqual((ROOT/'SKILL.md').read_bytes(),(target/'SKILL.md').read_bytes())
        self.assertNotEqual(subprocess.run(args,capture_output=True).returncode,0)
        subprocess.run([sys.executable,str(target/'scripts/check_package.py')],cwd=self.base,check=True,capture_output=True)
        subprocess.run([sys.executable,str(target/'scripts/assemble_character.py'),'--plan',str(target/'examples/character-plan.json'),'--composition',str(target/'examples/composition-intent.json'),'--profile',str(target/'style_profile.json'),'--prompt',str(self.base/'installed-prompt.txt'),'--trace',str(self.base/'installed-trace.json')],cwd=self.base,check=True,capture_output=True)

if __name__=='__main__':unittest.main()
