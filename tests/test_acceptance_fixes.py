"""Production approval regressions; all approval records are disposable fixtures."""
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


class AcceptanceFixTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory(prefix='jeff-acceptance-fixes-')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name) / 'site'
        self.root.mkdir()
        for name in ('assets', 'content', 'data', 'layouts', 'static', 'scripts', 'profiles', 'functions', 'lib', 'migrations'):
            shutil.copytree(ROOT / name, self.root / name, ignore=shutil.ignore_patterns('__pycache__', '*.pyc'))
        for name in ('hugo.toml', 'hugo-staging.toml', 'hugo-launch.toml', 'site-profile.json'):
            shutil.copy2(ROOT / name, self.root / name)
        self.configs = 'hugo.toml,profiles/jeff-does-doors.toml,hugo-launch.toml,fixture.toml'
        overlay = ('[params]\nproductionURL="https://fixture-review.org/subpath/"\n'
                   'contactEmail="review@fixture-review.org"\ncontactPhone=""\n'
                   'coverageConfirmed=true\ncontactResponse="Synthetic response process"\n'
                   'approvalConfigFiles=' + json.dumps(self.configs.split(',')) + '\n[params.features]\n')
        overlay += ''.join(f'{name}=false\n' for name in policy.registry(self.root)['features'])
        (self.root / 'fixture.toml').write_text(overlay)
        # A production release receipt must name a revision, so the fixture is a
        # real repository with a real commit rather than an exemption in the gate.
        for command in (['init', '-q'],
                        ['-c', 'user.name=Fixture', '-c', 'user.email=fixture@invalid',
                         'commit', '-q', '--allow-empty', '-m', 'fixture']):
            subprocess.run(['git', *command], cwd=self.root, check=True, capture_output=True)
        self.config = policy.load_config(self.root, self.configs)
        evidence = {name: {'approved': True, 'sha256': hashlib.sha256((self.root/name).read_bytes()).hexdigest(),
                          'reviewer': 'Synthetic fixture reviewer', 'sources': ['TEST ONLY'],
                          'reviewedOn': str(datetime.date.today())}
                    for name in policy.required_sources(self.root, self.config)}
        (self.root / 'data/evidence.json').write_text(json.dumps(evidence))
        self.env = {key: value for key, value in os.environ.items() if not key.upper().startswith('HUGO_')}
        self.assertEqual(policy.source_issues(self.root, self.config, True), [])

    def hugo(self, configs=None, gate_marker=False):
        env = dict(self.env)
        if gate_marker:
            env['HUGO_RELEASE_GATE'] = 'source-validated-v1'
        return subprocess.run(['hugo', '--source', str(self.root), '--config', configs or self.configs,
                               '--environment', 'production', '--baseURL', 'https://fixture-review.org/subpath/',
                               '--cacheDir', str(Path(self.temp.name)/'cache'),
                               '--destination', str(Path(self.temp.name)/'build')],
                              env=env, capture_output=True, text=True)

    def release(self, configs=None, env=None):
        return subprocess.run([sys.executable, str(self.root/'scripts/release_check.py'),
                               '--config', configs or self.configs, '--base-url', 'https://fixture-review.org/subpath/',
                               '--destination', 'public'], env=env or self.env, capture_output=True, text=True)

    def test_direct_build_is_closed_and_release_uses_only_reviewed_configs(self):
        result = self.hugo()
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('Production builds must run scripts/release_check.py', result.stdout + result.stderr)
        (self.root/'extra.toml').write_text('[params]\ncompanyName="UNREVIEWED OVERRIDE"\n')
        result = self.hugo(self.configs + ',extra.toml')
        self.assertNotEqual(result.returncode, 0)
        result = self.release(self.configs + ',extra.toml')
        self.assertNotEqual(result.returncode, 0)
        self.assertIn('extra.toml', result.stdout)
        self.assertFalse((self.root/'public').exists())
        # Implicit config directories and environment overrides must not change
        # the explicit configuration already checked by Python.
        implicit = self.root/'config/_default'
        implicit.mkdir(parents=True)
        (implicit/'params.toml').write_text('companyName="UNREVIEWED DIRECTORY"\n')
        env = dict(self.env, HUGO_PARAMS_COMPANYNAME='UNREVIEWED ENVIRONMENT')
        result = self.release(env=env)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        home = (self.root/'public/index.html').read_text()
        self.assertNotIn('UNREVIEWED', home)
        self.assertIn('Jeff Does Doors', home)
        self.assertEqual(json.loads((self.root/'public/release.json').read_text())['status'], 'passed')

    def test_redirect_addition_and_disabled_acceptance_changes_block_both_guards(self):
        for name, text in [('static/_redirects', '/subpath/contact/ /subpath/ 302\n'),
                           ('data/intake-acceptance.json', '{"status":"accepted"}\n')]:
            with self.subTest(source=name):
                path = self.root/name
                original = path.read_bytes() if path.exists() else None
                try:
                    path.write_text(text)
                    self.assertIn(name, policy.required_sources(self.root, self.config))
                    self.assertTrue(any(name in issue for issue in policy.source_issues(self.root, self.config, True)))
                    # Even the internal Hugo invocation retains its source guard.
                    result = self.hugo(gate_marker=True)
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(name, result.stdout + result.stderr)
                    result = self.release()
                    self.assertNotEqual(result.returncode, 0)
                    self.assertIn(name, result.stdout)
                    self.assertFalse((self.root/'public').exists())
                finally:
                    if original is None: path.unlink()
                    else: path.write_bytes(original)
