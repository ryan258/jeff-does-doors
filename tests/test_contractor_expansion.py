"""Owner-run coverage for the enquiry-through-aftercare guide expansion."""
import copy
import json
import os
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest

from test_component_library import GuideMarkup

ROOT = Path(__file__).resolve().parents[1]
COMPONENT_FIELDS = {
    'enquiry-summary': ('facts', 'value'),
    'site-observations': ('observations', 'next'),
    'permission-tracker': ('items', 'check'),
    'disruption-plan': ('periods', 'arrangement'),
    'estimate-breakdown': ('rows', 'amount'),
    'payment-milestones': ('milestones', 'trigger'),
    'waste-plan': ('streams', 'route'),
    'care-guide': ('groups', 'body'),
}
EMPTY_MESSAGES = {
    'enquiry-summary': 'No preparation questions supplied.',
    'site-observations': 'No site observations supplied.',
    'permission-tracker': 'No permission checks supplied.',
    'disruption-plan': 'No disruption arrangements supplied.',
    'estimate-breakdown': 'No estimate line items supplied.',
    'payment-milestones': 'No payment milestones supplied.',
    'waste-plan': 'No removal or reuse arrangements supplied.',
    'care-guide': 'No care guidance supplied.',
}


class ContractorExpansionTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='jeff-contractor-expansion-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name) / 'site'
        cls.root.mkdir()
        for name in ('assets', 'content', 'data', 'layouts', 'static', 'profiles'):
            shutil.copytree(ROOT / name, cls.root / name)
        shutil.copy2(ROOT / 'hugo.toml', cls.root / 'hugo.toml')
        library_path = cls.root / 'data/component_library.json'
        library = json.loads(library_path.read_text())
        cls.source_entries = {
            entry['id']: entry for entry in library['components']
            if entry['id'] in COMPONENT_FIELDS
        }
        site_path = cls.root / 'data/site_components.json'
        placements = json.loads(site_path.read_text())
        for component_id, (collection, field) in COMPONENT_FIELDS.items():
            entry = cls.source_entries[component_id]
            placements['fixture-' + component_id] = dict(
                component=component_id, page='/expansion-fixture', eyebrow='Fixture',
                heading=entry['title'], content=entry['example'])
            repeated = copy.deepcopy(entry)
            repeated['id'] += '-second'
            repeated['example']['title'] = '<img src=x onerror=alert(1)>'
            repeated['example'][collection][0][field] = '<script>alert(1)</script>'
            # Paired links retain the deployment subpath. Incomplete pairs must
            # render as plain text, without pretending a resource is available.
            if component_id == 'enquiry-summary':
                repeated['example']['next'].pop('action')
            if component_id == 'care-guide':
                repeated['example']['reference'].update(href='faq/', action='Read the FAQ')
            library['components'].append(repeated)
            empty = copy.deepcopy(entry)
            empty['id'] += '-empty'
            empty['example'][collection] = []
            if component_id == 'enquiry-summary':
                empty['example']['needs'] = []
                empty['example']['next'].pop('href')
            if component_id == 'estimate-breakdown':
                empty['example']['summary'] = []
            if component_id == 'care-guide':
                empty['example']['reference']['action'] = 'Unavailable resource'
            library['components'].append(empty)
        library_path.write_text(json.dumps(library))
        site_path.write_text(json.dumps(placements))
        (cls.root / 'content/expansion-fixture.md').write_text(
            '---\ntitle: Expansion fixture\nlayout: expansion-fixture\nreviewOnly: true\n---\n')
        (cls.root / 'layouts/_default/expansion-fixture.html').write_text(
            '{{ define "main" }}<h1>Expansion fixture</h1>' + ''.join(
                '{{ partial "site-component.html" (dict "page" . "key" "fixture-' + name + '") }}'
                for name in COMPONENT_FIELDS) + '{{ end }}')
        (cls.root / 'fixture.toml').write_text('[params]\nnoindex=true\nloadWebFonts=false\n')
        cls.output = Path(cls.temp.name) / 'public'
        result = subprocess.run([
            'hugo', '--source', str(cls.root), '--environment', 'staging',
            '--config', 'hugo.toml,profiles/jeff-does-doors.toml,fixture.toml',
            '--baseURL', 'https://fixture-review.org/subpath/',
            '--destination', str(cls.output), '--cacheDir', str(Path(cls.temp.name) / 'cache')],
            env={k: v for k, v in os.environ.items() if not k.upper().startswith('HUGO_')},
            capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.html = (cls.output / 'style-guide/index.html').read_text()

    def preview(self, component_id):
        start = self.html.index(f'id="component-{component_id}"')
        return self.html[start:self.html.index('<details class="sg-usage"', start)]

    def test_each_new_component_is_searchable_with_live_usage_and_a_disclosure(self):
        markup = GuideMarkup(self.html)
        for component_id, entry in self.source_entries.items():
            with self.subTest(component=component_id):
                specimen = next(attrs for _, attrs in markup.elements
                                if attrs.get('id') == 'component-' + component_id)
                self.assertEqual(specimen['data-guide-family-name'], 'contractor')
                self.assertIn(entry['example']['title'], specimen['data-guide-search-text'])
                self.assertIn('usage-' + component_id, markup.ids)
                self.assertIn('your-unique-' + component_id, self.html)
                preview = self.preview(component_id)
                self.assertIn('Fictional', preview)
                self.assertIn('contractor-note', preview)
                self.assertFalse(any(tag in ('form', 'input', 'button', 'select', 'textarea', 'script')
                                     for tag, _ in GuideMarkup(preview).elements))

    def test_repeated_previews_escape_titles_and_nested_values(self):
        for component_id in COMPONENT_FIELDS:
            with self.subTest(component=component_id):
                html = self.preview(component_id + '-second')
                self.assertIn('&lt;img src=x onerror=alert(1)&gt;', html)
                self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
                self.assertFalse(any(tag in ('img', 'script') or 'onerror' in attrs
                                     for tag, attrs in GuideMarkup(html).elements))

    def test_empty_data_keeps_missing_information_explicit(self):
        for component_id, message in EMPTY_MESSAGES.items():
            with self.subTest(component=component_id):
                self.assertIn(message, self.preview(component_id + '-empty'))
        self.assertFalse(any(tag == 'table' for tag, _ in
                             GuideMarkup(self.preview('estimate-breakdown-empty')).elements))

    def test_repeated_ids_and_aria_references_remain_resolved(self):
        markup = GuideMarkup(self.html)
        self.assertEqual(len(markup.ids), len(set(markup.ids)))
        for _, attrs in markup.elements:
            for name in ('aria-labelledby', 'aria-describedby'):
                for target in attrs.get(name, '').split():
                    self.assertIn(target, markup.ids)

    def test_estimate_table_has_caption_headers_and_keyboard_scroll_region(self):
        for component_id in ('estimate-breakdown', 'estimate-breakdown-second'):
            markup = GuideMarkup(self.preview(component_id))
            self.assertEqual(sum(tag == 'caption' for tag, _ in markup.elements), 1)
            self.assertEqual(sum(tag == 'th' and attrs.get('scope') == 'col'
                                 for tag, attrs in markup.elements), 4)
            self.assertEqual(sum(tag == 'th' and attrs.get('scope') == 'row'
                                 for tag, attrs in markup.elements), 3)
            region = next(attrs for _, attrs in markup.elements if attrs.get('role') == 'region')
            self.assertEqual(region['tabindex'], '0')
            self.assertIn(region['aria-labelledby'], markup.ids)
            self.assertIn(region['aria-describedby'], markup.ids)
        self.assertIn('Not priced', self.preview('estimate-breakdown'))
        self.assertIn('Not established', self.preview('estimate-breakdown'))

    def test_care_disclosures_start_closed_and_payment_order_is_native(self):
        details = [attrs for tag, attrs in GuideMarkup(self.preview('care-guide')).elements
                   if tag == 'details']
        self.assertEqual(len(details), 3)
        self.assertTrue(all('open' not in attrs for attrs in details))
        self.assertTrue(any(tag == 'ol' for tag, _ in
                            GuideMarkup(self.preview('payment-milestones')).elements))

    def test_incomplete_actions_are_omitted_and_paired_links_preserve_subpaths(self):
        for component_id, hrefs in {
            'enquiry-summary': ['/subpath/survey/'], 'enquiry-summary-second': [],
            'enquiry-summary-empty': [], 'care-guide': [],
            'care-guide-second': ['/subpath/faq/'], 'care-guide-empty': [],
        }.items():
            with self.subTest(component=component_id):
                links = [attrs['href'] for tag, attrs in GuideMarkup(self.preview(component_id)).elements
                         if tag == 'a' and 'contractor-link' in attrs.get('class', '').split()]
                self.assertEqual(links, hrefs)

    def test_wrapper_reuses_all_eight_without_loading_guide_or_choice_scripts(self):
        html = (self.output / 'expansion-fixture/index.html').read_text()
        markup = GuideMarkup(html)
        kinds = [attrs['data-component-kind'] for _, attrs in markup.elements
                 if 'data-site-component' in attrs]
        self.assertEqual(set(kinds), set(COMPONENT_FIELDS))
        self.assertEqual(len(kinds), 8)
        self.assertEqual(len(markup.ids), len(set(markup.ids)))
        self.assertNotIn('/js/style-guide.', html)
        self.assertNotIn('/js/contractor-choices.', html)
