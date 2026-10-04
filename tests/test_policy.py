"""Focused regressions. Synthetic approvals are confined to temporary fixtures."""
import copy
import datetime
import hashlib
import json
import os
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import content_policy as policy
import release_check as gate


class SourcePolicyTests(unittest.TestCase):
    def test_artifact_parser_collects_responsive_assets_and_schema(self):
        parser = gate.PageAudit()
        parser.feed('<img id="same" src="base.webp" srcset="small.webp 480w, large.webp 960w" alt=""><p id="same"></p><script type="application/ld+json">{"@type":"Service"}</script>')
        self.assertEqual(parser.duplicate_ids, {'same'})
        self.assertIn('large.webp', parser.resources)
        self.assertEqual(json.loads(parser.structured_data[0])['@type'], 'Service')

    def test_standard_yaml_and_duplicate_keys(self):
        self.assertEqual(policy.parse_yaml('note: "Line\\nTwo"\n'), {'note':'Line\nTwo'})
        with self.assertRaises(ValueError): policy.parse_yaml('verified: true\nverified: false\n')
        with self.assertRaises(ValueError): policy.parse_yaml('items: [unterminated')

    def test_approval_types_fail_closed(self):
        for value in ['false', 'true', 0, 1, None, False]:
            with self.subTest(value=value):
                data={'rows':[{'service':'Fixture','range':'Fixture','drivers':'Fixture','verified':value}]}
                self.assertTrue(policy.data_issues('data/pricing.yaml',data,True))
        data['rows'][0]['verified']=True
        self.assertEqual(policy.data_issues('data/pricing.yaml',data,True),[])

    def test_financing_and_warranty_are_structural(self):
        self.assertTrue(policy.data_issues('data/financing.yaml',{'options':[{'title':'Fixture','body':'Fixture','verified':'false'}]},True))
        for data in [{}, {'verified':False}, {'verified':'false'}, {'verified':1}]:
            self.assertTrue(policy.data_issues('data/warranty.yaml',data,True))

    def test_missing_and_empty_records_fail(self):
        for data in [None, {}, [], {'rows':[]}]:
            self.assertTrue(policy.data_issues('data/pricing.yaml',data,True))

    def test_dependency_resolution(self):
        definitions=policy.registry(ROOT)['features']
        flags={'team':True,'about':False}
        self.assertFalse(policy.enabled('team',flags,definitions))
        flags['about']=True
        self.assertTrue(policy.enabled('team',flags,definitions))
        flags['team']='true'
        self.assertFalse(policy.enabled('team',flags,definitions))

    def test_frontmatter_delimiters_and_nested_feature_ownership(self):
        with tempfile.TemporaryDirectory() as tmp:
            path = Path(tmp) / 'page.md'
            path.write_text('---\ntitle: "Before --- after"\n---\nBody\n')
            self.assertEqual(policy.frontmatter(path)['title'], 'Before --- after')
        definitions = policy.registry(ROOT)['features']
        self.assertEqual(policy.page_feature(Path('blog/nested/guide.md'), {}, definitions), 'blog')
        self.assertTrue(policy.data_issues('data/faqs.yaml', [{'category':'Fixture','items':None}], False))

    def test_evidence_binds_revision_and_calendar(self):
        with tempfile.TemporaryDirectory() as tmp:
            root=Path(tmp);(root/'data').mkdir();source=root/'copy.md';source.write_text('Fixture only')
            entry={'approved':True,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reviewer':'Synthetic test reviewer','sources':['synthetic fixture'],'reviewedOn':str(datetime.date.today()),'reviewAfter':''}
            (root/'data/evidence.json').write_text(json.dumps({'copy.md':entry}))
            self.assertEqual(policy.approval_issues(root,['copy.md']),[])
            source.write_text('Changed fixture')
            self.assertTrue(any('changed' in x for x in policy.approval_issues(root,['copy.md'])))
            entry['reviewedOn']='2099-99-99';entry['approved']='true'
            (root/'data/evidence.json').write_text(json.dumps({'copy.md':entry}))
            self.assertTrue(policy.approval_issues(root,['copy.md']))

    def test_review_dates_not_invented_and_preview_allows_unknown(self):
        data=[{'quote':'Fixture','name':'Fixture','context':'Fixture','url':'https://fixture-review.org','date':'','approved':False}]
        self.assertEqual(policy.data_issues('data/reviews.yaml',data,False),[])
        self.assertTrue(policy.data_issues('data/reviews.yaml',data,True))
        data[0].update(date='2026-99-99',approved=True)
        self.assertTrue(policy.data_issues('data/reviews.yaml',data,True))


class GeneratedArtifactTests(unittest.TestCase):
    maxDiff = None
    @classmethod
    def setUpClass(cls):
        cls.temp=tempfile.TemporaryDirectory(prefix='jeff-policy-tests-')
        cls.root=Path(cls.temp.name)/'site'
        shutil.copytree(ROOT,cls.root,ignore=shutil.ignore_patterns('.git','.venv','.cache','.attic','public','resources','__pycache__'))
        cls.original_root=gate.ROOT;cls.original_config=gate.CONFIG
        gate.ROOT=cls.root

    @classmethod
    def tearDownClass(cls):
        gate.ROOT=cls.original_root;gate.CONFIG=cls.original_config
        cls.temp.cleanup()

    def build(self, configs, environment, output):
        env = {key: value for key, value in os.environ.items() if not key.upper().startswith('HUGO_')}
        if environment == 'production':
            self.assertEqual(policy.source_issues(self.root, policy.load_config(self.root, configs), True), [])
            env['HUGO_RELEASE_GATE'] = 'source-validated-v1'
        result=subprocess.run(['hugo','--source',str(self.root),'--config',configs,'--environment',environment,'--baseURL','https://fixture-review.org/subpath/','--cacheDir',str(Path(tempfile.gettempdir())/'jeff-does-doors-hugo-cache'),'--destination',str(output),'--cleanDestinationDir'],env=env,capture_output=True,text=True)
        self.assertEqual(result.returncode,0,(result.stderr or result.stdout)[-4000:])

    def test_01_preview_routes_and_client_identity(self):
        output=Path(self.temp.name)/'preview'
        configs=policy.default_configs(self.root,staging=True)
        gate.CONFIG=policy.load_config(self.root,configs)
        self.assertEqual(policy.source_issues(self.root,gate.CONFIG,False),[])
        self.build(configs,'staging',output)
        self.assertEqual(gate.audit_build(output,'https://fixture-review.org/subpath/',True),[])
        # Selected modules render; deselected ones are absent rather than empty shells.
        for route in ('about','faq','contact','service-area','services',
                      'services/barn-door-installation','services/barn-door-adjustments',
                      'pricing','gallery','financing','equipment','careers','emergency','reviews'):
            self.assertTrue((output/route/'index.html').is_file(),route)
        for route in ('estimate','site-kit'):
            self.assertFalse((output/route/'index.html').exists(),route)
        # Search is deselected, so the generated index must stay empty.
        self.assertEqual(json.loads((output/'index.json').read_text()),[])
        home=(output/'index.html').read_text()
        self.assertIn('srcset=',home)
        self.assertIn('method=dialog',home.replace('"',''))
        self.assertIn('Choose a service, or leave unspecified',home)
        self.assertNotIn('href=""',home)
        # No inherited demonstration business may survive in a client artifact.
        for page in output.rglob('*.html'):
            text=page.read_text()
            for leak in ('Jones','Jason','Septic','septic','excavation','Berryville','Construction Website Master'):
                self.assertNotIn(leak,text,f'{page.name} leaked {leak}')

    def test_012_release_receipt_requires_a_revision(self):
        """A receipt that cannot name a commit must not record a bogus one."""
        self.assertIsNone(gate.git_value('rev-parse','definitely-not-a-ref'))

    def test_02_all_off_production_with_synthetic_approvals(self):
        definitions=policy.registry(self.root)['features']
        overlay='[params]\nproductionURL = "https://fixture-review.org/subpath/"\ncontactEmail = "review@fixture-review.org"\ncontactPhone = ""\ncoverageConfirmed = true\ncontactResponse = "Synthetic response process"\napprovalConfigFiles = ["hugo.toml", "profiles/jeff-does-doors.toml", "hugo-launch.toml", "hugo-test.toml"]\n[params.features]\n'+''.join(f'{name} = false\n' for name in definitions)
        (self.root/'hugo-test.toml').write_text(overlay)
        configs='hugo.toml,profiles/jeff-does-doors.toml,hugo-launch.toml,hugo-test.toml'
        gate.CONFIG=policy.load_config(self.root,configs)
        evidence=json.loads((self.root/'data/evidence.json').read_text())
        for name in policy.required_sources(self.root,gate.CONFIG):
            source=self.root/name
            evidence[name]={'approved':True,'sha256':hashlib.sha256(source.read_bytes()).hexdigest(),'reviewer':'Synthetic fixture reviewer','sources':['TEST ONLY: not business evidence'],'reviewedOn':str(datetime.date.today()),'reviewAfter':''}
        (self.root/'data/evidence.json').write_text(json.dumps(evidence))
        issues=policy.source_issues(self.root,gate.CONFIG,True)
        self.assertEqual(issues,[])
        output=Path(self.temp.name)/'production'
        self.build(configs,'production',output)
        self.assertEqual(gate.audit_build(output,'https://fixture-review.org/subpath/'),[])
        self.assertEqual(json.loads((output/'index.json').read_text()),[])
        for feed in output.rglob('*.xml'):
            if feed.name!='sitemap.xml': self.assertNotIn('<item>',feed.read_text())
        for route in ['faq','about','privacy','contact','service-area','terms','accessibility']:
            text=(output/route/'index.html').read_text()
            self.assertIn('Information unavailable',text)
            self.assertNotIn('application/ld+json',text)
            self.assertNotIn('property="og:image"',text)
        self.assertNotIn('/blog/',(output/'sitemap.xml').read_text())
        # Generated artifacts must retain every indexable route in the sitemap.
        sitemap = output/'sitemap.xml'
        original_sitemap = sitemap.read_text()
        from xml.etree import ElementTree
        tree = ElementTree.fromstring(original_sitemap)
        for entry in list(tree):
            if any((node.text or '').endswith('/services/barn-door-installation/') for node in entry):
                tree.remove(entry)
        sitemap.write_text(ElementTree.tostring(tree, encoding='unicode'))
        self.assertTrue(any('Indexable page missing from sitemap' in issue for issue in gate.audit_build(output,'https://fixture-review.org/subpath/')))
        sitemap.write_text(original_sitemap)
        # Former approval bypass: a shared base-template change must fail both layers.
        base = self.root/'layouts/_default/baseof.html'
        original = base.read_text()
        base.write_text(original.replace('<main id="main-content">', '<main id="main-content"><p>Unapproved fixture claim</p>'))
        self.assertTrue(any('baseof.html: content changed' in issue for issue in policy.source_issues(self.root,gate.CONFIG,True)))
        rejected = subprocess.run(['hugo','--source',str(self.root),'--config',configs,'--environment','production','--baseURL','https://fixture-review.org/subpath/','--cacheDir',str(Path(tempfile.gettempdir())/'jeff-does-doors-hugo-cache'),'--destination',str(output)],capture_output=True,text=True)
        self.assertNotEqual(rejected.returncode,0)
        self.assertIn('baseof.html',rejected.stdout+rejected.stderr)
        base.write_text(original)
        # A change after approval must block direct Hugo production too.
        source=self.root/'content/services/barn-door-installation.md';source.write_text(source.read_text()+'\nChanged fixture.\n')
        result=subprocess.run(['hugo','--source',str(self.root),'--config',configs,'--environment','production','--baseURL','https://fixture-review.org/subpath/','--cacheDir',str(Path(tempfile.gettempdir())/'jeff-does-doors-hugo-cache'),'--destination',str(output)],capture_output=True,text=True)
        self.assertNotEqual(result.returncode,0)
        self.assertIn('changed since approval',result.stdout+result.stderr)


if __name__=='__main__': unittest.main()
