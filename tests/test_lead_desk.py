"""Operator query boundaries; no provider calls or CLI execution."""
import sys
from pathlib import Path
import unittest
sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'scripts'))
import lead_desk

class LeadDeskTests(unittest.TestCase):
    def test_receipt_and_status_cannot_inject_sql(self):
        with self.assertRaises(ValueError): lead_desk.query_for('show', "x' OR 1=1 --")
        with self.assertRaises(ValueError): lead_desk.query_for('status', '00000000-0000-4000-8000-000000000000', 'unknown')
        query = lead_desk.query_for('status', '00000000-0000-4000-8000-000000000000', 'closed')
        self.assertIn('closed_at=CURRENT_TIMESTAMP', query)
        self.assertIn('purged_at IS NULL', query)

    def test_list_omits_personal_payload_and_is_bounded(self):
        query = lead_desk.query_for('list')
        self.assertNotIn('payload_json', query)
        self.assertIn('LIMIT 50', query)

    def test_notification_origin_rejects_credentials_and_paths_before_network(self):
        for origin in ['http://site.test', 'https://token@site.test', 'https://site.test/path', 'https://site.test/?token=x']:
            with self.assertRaises(ValueError): lead_desk.retry_notification(origin, 'x'*32, '00000000-0000-4000-8000-000000000000')
