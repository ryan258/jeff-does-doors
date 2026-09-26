"""Intake activation and source-boundary regressions; no invented production evidence."""
import copy
import json
from pathlib import Path
import sys
import unittest
ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import content_policy as policy

class IntakePolicyTests(unittest.TestCase):
    def setUp(self):
        self.config = policy.load_config(ROOT, policy.default_configs(ROOT, staging=True))

    def test_default_keeps_local_briefs_and_adapter_inactive(self):
        self.assertFalse(self.config['params']['intake']['enabled'])
        self.assertFalse(self.config['params']['formEndpoint'])
        self.assertEqual(policy.source_issues(ROOT, self.config, False), [])

    def test_enabled_adapter_extends_revision_bound_sources(self):
        self.config['params']['intake']['enabled'] = True
        sources = policy.required_sources(ROOT, self.config)
        for path in ['functions/api/project-request.js', 'lib/intake.mjs', 'lib/notifications.mjs',
                     'migrations/0001_project_requests.sql', 'data/intake-acceptance.json', 'static/_headers', 'static/_routes.json']:
            self.assertIn(path, sources)

    def test_preview_allows_configured_adapter_but_never_dummy_keys(self):
        self.config['params']['intake'].update(enabled=True, environment='preview', siteKey='fixture-real-key', consentVersion='v1', retentionNotice='Synthetic test retention notice.')
        self.assertEqual(policy.source_issues(ROOT, self.config, False), [])
        self.config['params']['intake']['siteKey'] = '1x00000000000000000000AA'
        self.assertTrue(any('test key' in issue for issue in policy.source_issues(ROOT, self.config, False)))

    def test_pending_evidence_cannot_activate_production(self):
        self.config['params']['intake'].update(enabled=True, environment='production', siteKey='fixture-real-key', consentVersion='v1', retentionNotice='Synthetic test notice.')
        self.assertTrue(any('acceptance is pending' in issue for issue in policy.source_issues(ROOT, self.config, False)))

    def test_malformed_acceptance_record_fails(self):
        import tempfile, shutil
        with tempfile.TemporaryDirectory() as tmp:
            tmp_root = Path(tmp)
            shutil.copytree(ROOT, tmp_root, dirs_exist_ok=True, ignore=shutil.ignore_patterns('.git', '.venv', 'public'))
            cfg = policy.load_config(tmp_root, policy.default_configs(tmp_root, staging=False))
            cfg['params']['intake'].update(enabled=True, environment='production', siteKey='fixture-real-key', consentVersion='v1', retentionNotice='Notice.')
            cfg['params']['productionURL'] = 'https://fixture.example.com/'
            cfg['params']['profileID'] = 'test'
            acc_file = tmp_root / 'data/intake-acceptance.json'
            # Valid shape
            valid_record = {
                'status': 'accepted', 'baseURL': 'https://fixture.example.com/',
                'profile': 'test', 'consentVersion': 'v1',
                'testedOn': '2026-09-01', 'evidence': ['test-log-ref']
            }
            # Malformed dates
            for bad_date in ['', 'not-a-date', '2099-01-01', None, 12345]:
                rec = copy.deepcopy(valid_record)
                rec['testedOn'] = bad_date
                acc_file.write_text(json.dumps(rec))
                self.assertTrue(any('acceptance is pending' in i for i in policy.source_issues(tmp_root, cfg, False)))
            # Invalid evidence shapes
            for bad_evidence in [[], '', None, [''], [123], {}]:
                rec = copy.deepcopy(valid_record)
                rec['evidence'] = bad_evidence
                acc_file.write_text(json.dumps(rec))
                self.assertTrue(any('acceptance is pending' in i for i in policy.source_issues(tmp_root, cfg, False)))

