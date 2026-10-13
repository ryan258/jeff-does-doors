"""Owner-run Hugo regressions for the review-only component catalogue."""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
PAPERWORK_COMPONENTS = ('decision-register', 'responsibility-matrix', 'site-access-plan',
                        'material-schedule', 'punch-list', 'document-register')


class GuideMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.ids = []
        self.elements = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        self.elements.append((tag, attrs))
        if 'id' in attrs:
            self.ids.append(attrs['id'])


class ComponentLibraryTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='jeff-component-tests-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name) / 'site'
        cls.root.mkdir()
        for name in ('assets', 'content', 'data', 'layouts', 'static', 'profiles'):
            shutil.copytree(ROOT / name, cls.root / name)
        shutil.copy2(ROOT / 'hugo.toml', cls.root / 'hugo.toml')
        # One additional checklist exposes repeated-instance id collisions.
        data_path = cls.root / 'data/component_library.json'
        library = json.loads(data_path.read_text())
        checklist = next(item for item in library['components'] if item['id'] == 'visit-checklist')
        second = json.loads(json.dumps(checklist))
        second.update(id='visit-checklist-second', title='Second checklist')
        second['example']['title'] = '<img src=x onerror=alert(1)>'
        library['components'].append(second)
        # Repeated native choices must not share radio names or panel IDs.
        for component_id in ('project-chooser', 'finish-selector'):
            original = next(item for item in library['components'] if item['id'] == component_id)
            repeated = json.loads(json.dumps(original))
            repeated['id'] = component_id + '-second'
            repeated['example']['options'][0]['label'] = '\"><img src=x onerror=alert(1)>'
            library['components'].append(repeated)
        # Repeat the paperwork patterns to catch heading/hint collisions. Feed
        # hostile text through every new partial, including nested record fields.
        site_data_path = cls.root / 'data/site_components.json'
        site_data = json.loads(site_data_path.read_text())
        for component_id in PAPERWORK_COMPONENTS:
            original = next(item for item in library['components'] if item['id'] == component_id)
            site_data[f'fixture-{component_id}'] = dict(
                component=component_id, page='/paperwork-fixture', eyebrow='Fixture',
                heading=original['title'], content=original['example'])
            repeated = json.loads(json.dumps(original))
            repeated['id'] += '-second'
            repeated['example']['title'] = '<img src=x onerror=alert(1)>'
            # Exercise a nested field in each pattern, not just the shared title.
            nested_fields = {
                'decision-register': ('entries', 'reason'),
                'responsibility-matrix': ('rows', 'coordination'),
                'site-access-plan': ('areas', 'detail'),
                'material-schedule': ('rows', 'selection'),
                'punch-list': ('items', 'observation'),
                'document-register': ('documents', 'detail'),
            }
            collection, field = nested_fields[component_id]
            repeated['example'][collection][0][field] = '<script>alert(1)</script>'
            if component_id == 'document-register':
                repeated['example']['documents'].extend([
                    dict(title='No label', kind='Fixture', status='Pending', detail='Plain text', href='survey/'),
                    dict(title='No destination', kind='Fixture', status='Pending', detail='Plain text', action='Open file'),
                ])
            library['components'].append(repeated)
        site_data_path.write_text(json.dumps(site_data))
        (cls.root / 'content/paperwork-fixture.md').write_text(
            '---\ntitle: Paperwork fixture\nlayout: paperwork-fixture\nreviewOnly: true\n---\n')
        (cls.root / 'layouts/_default/paperwork-fixture.html').write_text(
            '{{ define "main" }}<h1>Paperwork fixture</h1>' +
            ''.join('{{ partial "site-component.html" (dict "page" . "key" "fixture-' + name + '") }}'
                    for name in PAPERWORK_COMPONENTS) + '{{ end }}')
        cls.expected_count = len(library['components'])
        data_path.write_text(json.dumps(library))
        (cls.root / 'fixture.toml').write_text(
            '[params]\nnoindex=true\nloadWebFonts=false\n'
            '[params.features]\nsearch=true\n')
        cls.env = {k: v for k, v in os.environ.items() if not k.upper().startswith('HUGO_')}
        cls.output = cls.build('review')
        cls.html = (cls.output / 'style-guide/index.html').read_text()
        cls.markup = GuideMarkup(cls.html)

    @classmethod
    def build(cls, name):
        output = Path(cls.temp.name) / name
        result = subprocess.run(
            ['hugo', '--source', str(cls.root), '--environment', 'staging',
             '--config', 'hugo.toml,profiles/jeff-does-doors.toml,fixture.toml',
             '--baseURL', 'https://fixture-review.org/subpath/',
             '--destination', str(output), '--cacheDir', str(Path(cls.temp.name) / 'cache')],
            env=cls.env, capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        return output

    def test_catalogue_renders_all_partials_and_repeated_ids_are_unique(self):
        entries = [attrs for _, attrs in self.markup.elements if 'data-guide-entry' in attrs]
        self.assertEqual(len(entries), self.expected_count)
        self.assertEqual(len(self.markup.ids), len(set(self.markup.ids)))
        self.assertIn('specimen-visit-checklist-item-0', self.markup.ids)
        self.assertIn('specimen-visit-checklist-second-item-0', self.markup.ids)
        self.assertIn('Not reviewed', self.html)
        self.assertIn('Service locations have not been added.', self.html)

    def test_supplied_text_is_escaped_and_usage_is_rendered_as_code(self):
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', self.html)
        self.assertFalse(any('onerror' in attrs for _, attrs in self.markup.elements))
        self.assertIn('your-unique-scope-panel', self.html)
        self.assertNotIn('ZgotmplZ', self.html)

    def test_labels_and_aria_references_point_to_rendered_elements(self):
        ids = set(self.markup.ids)
        for tag, attrs in self.markup.elements:
            with self.subTest(tag=tag, attrs=attrs):
                if tag == 'label' and 'for' in attrs:
                    self.assertIn(attrs['for'], ids)
                for key in ('aria-labelledby', 'aria-describedby'):
                    for target in attrs.get(key, '').split():
                        self.assertIn(target, ids)
                if tag == 'a' and attrs.get('href', '').startswith('#'):
                    self.assertIn(attrs['href'][1:], ids)

    def test_subpath_links_script_scope_and_no_javascript_fallback(self):
        hrefs = [attrs['href'] for tag, attrs in self.markup.elements if tag == 'a']
        self.assertIn('/subpath/survey/', hrefs)
        self.assertNotIn('/survey/', hrefs)
        controls = next(attrs for _, attrs in self.markup.elements if 'data-guide-controls' in attrs)
        self.assertIn('hidden', controls)
        self.assertTrue(all('hidden' not in attrs for _, attrs in self.markup.elements if 'data-guide-entry' in attrs))
        self.assertIn('/subpath/js/style-guide.', self.html)
        self.assertNotIn('/js/style-guide.', (self.output / 'index.html').read_text())
        native_checkboxes = [attrs for tag, attrs in self.markup.elements if tag == 'input' and attrs.get('type') == 'checkbox' and attrs.get('id', '').startswith('specimen-visit-checklist')]
        self.assertEqual(len(native_checkboxes), 8)
        self.assertTrue(all('disabled' not in attrs for attrs in native_checkboxes))

    def test_noindex_guide_is_absent_from_discovery_outputs(self):
        self.assertTrue(any(tag == 'meta' and attrs.get('name') == 'robots' and 'noindex' in attrs.get('content', '') for tag, attrs in self.markup.elements))
        self.assertNotIn('/style-guide/', (self.output / 'sitemap.xml').read_text())
        search = json.loads((self.output / 'index.json').read_text())
        self.assertTrue(all('/style-guide/' not in item['url'] for item in search))

    def test_choices_keep_full_fallback_and_separate_radio_groups(self):
        controls = [attrs for _, attrs in self.markup.elements if 'data-choice-controls' in attrs]
        panels = [attrs for _, attrs in self.markup.elements if 'data-choice-panel' in attrs]
        radios = [attrs for tag, attrs in self.markup.elements if tag == 'input' and 'data-choice-input' in attrs]
        self.assertEqual(len(controls), 4)
        self.assertTrue(all('hidden' in attrs for attrs in controls))
        self.assertEqual(len(panels), 12)
        self.assertTrue(all('hidden' not in attrs for attrs in panels))
        names = {attrs['name'] for attrs in radios}
        self.assertEqual(len(names), 4)
        for name in names:
            group = [attrs for attrs in radios if attrs['name'] == name]
            self.assertEqual(len(group), 3)
            self.assertEqual(sum('checked' in attrs for attrs in group), 1)
            self.assertEqual({attrs['value'] for attrs in group}, {'0', '1', '2'})
        for attrs in radios:
            self.assertIn(attrs['aria-controls'], self.markup.ids)

    def test_choice_script_loads_once_only_on_the_guide(self):
        scripts = [attrs.get('src', '') for tag, attrs in self.markup.elements if tag == 'script']
        self.assertEqual(sum('/subpath/js/contractor-choices.' in src for src in scripts), 1)
        # The comparison page has no choices. Homepage/gallery integrations are
        # covered separately in test_site_components.py.
        self.assertNotIn('/js/contractor-choices.', (self.output / 'contact/index.html').read_text())

    def test_parody_is_disclosed_and_character_copy_is_searchable(self):
        roster = next(attrs for _, attrs in self.markup.elements if attrs.get('id') == 'component-crew-roster')
        self.assertIn('Lenny', roster['data-guide-search-text'])
        self.assertIn('Parody cast.', self.html)
        self.assertIn('Not a customer review.', self.html)
        self.assertIn('Nothing has been approved, priced, signed, or added to a project.', self.html)
        self.assertFalse(any(tag == 'form' and 'contractor' in attrs.get('class', '') for tag, attrs in self.markup.elements))

    def test_existing_non_review_guard_suppresses_guide_and_script(self):
        # Exercise the existing page visibility seam in an isolated fixture.
        # This is not a release/approval bypass in application source.
        partial = self.root / 'layouts/partials/review-mode.html'
        original = partial.read_text()
        try:
            partial.write_text('{{ return false }}')
            output = self.build('not-review')
            html = (output / 'style-guide/index.html').read_text()
            self.assertIn('Information unavailable', html)
            self.assertNotIn('data-component-guide', html)
            self.assertNotIn('/js/style-guide.', html)
            self.assertNotIn('An opening with room to move', html)
        finally:
            partial.write_text(original)

    def paperwork_preview(self, component_id):
        start = self.html.index(f'id="component-{component_id}"')
        end = self.html.index('<details class="sg-usage"', start)
        return self.html[start:end]

    def test_paperwork_patterns_are_read_only_with_visible_example_boundaries(self):
        for component_id in PAPERWORK_COMPONENTS:
            with self.subTest(component=component_id):
                html = self.paperwork_preview(component_id)
                markup = GuideMarkup(html)
                self.assertIn('contractor-note', html)
                self.assertTrue('Fictional' in html or 'Example planning prompts' in html)
                self.assertFalse(any(tag in ('form', 'input', 'button', 'select', 'textarea', 'script')
                                     for tag, _ in markup.elements))
        for component_id in ('responsibility-matrix', 'material-schedule'):
            markup = GuideMarkup(self.paperwork_preview(component_id))
            self.assertEqual(sum(tag == 'caption' for tag, _ in markup.elements), 1)
            self.assertEqual(sum(tag == 'th' and attrs.get('scope') == 'col'
                                 for tag, attrs in markup.elements), 4)
            self.assertTrue(any(tag == 'th' and attrs.get('scope') == 'row'
                                for tag, attrs in markup.elements))
            region = next(attrs for _, attrs in markup.elements if attrs.get('role') == 'region')
            self.assertEqual(region['tabindex'], '0')
            self.assertIn(region['aria-labelledby'], markup.ids)
            self.assertIn(region['aria-describedby'], markup.ids)

    def test_document_register_links_are_real_and_pending_items_have_no_actions(self):
        for component_id in ('document-register', 'document-register-second'):
            html = self.paperwork_preview(component_id)
            markup = GuideMarkup(html)
            links = [attrs for tag, attrs in markup.elements
                     if tag == 'a' and 'contractor-link' in attrs.get('class', '').split()]
            self.assertEqual({attrs['href'] for attrs in links}, {'/subpath/survey/', '/subpath/faq/'})
            self.assertEqual(len(links), 2)
            for link in links:
                path = urlsplit(link['href']).path.removeprefix('/subpath/')
                self.assertTrue((self.output / path / 'index.html').is_file())
                self.assertNotIn('download', link)

    def test_paperwork_preview_escapes_titles_and_nested_text(self):
        for component_id in PAPERWORK_COMPONENTS:
            with self.subTest(component=component_id):
                # Exclude the example JSON: its escaped copy must not conceal
                # unsafe rendering in the actual component preview.
                html = self.paperwork_preview(component_id + '-second')
                markup = GuideMarkup(html)
                self.assertIn('&lt;img src=x onerror=alert(1)&gt;', html)
                self.assertIn('&lt;script&gt;alert(1)&lt;/script&gt;', html)
                self.assertFalse(any(tag in ('img', 'script') or 'onerror' in attrs
                                     for tag, attrs in markup.elements))

    def test_paperwork_patterns_also_render_through_the_site_wrapper_without_new_scripts(self):
        html = (self.output / 'paperwork-fixture/index.html').read_text()
        markup = GuideMarkup(html)
        kinds = {attrs['data-component-kind'] for _, attrs in markup.elements
                 if 'data-site-component' in attrs}
        self.assertEqual(kinds, set(PAPERWORK_COMPONENTS))
        self.assertEqual(len(markup.ids), len(set(markup.ids)))
        self.assertNotIn('/js/contractor-choices.', html)
        self.assertNotIn('/js/style-guide.', html)
