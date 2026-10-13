"""Owner-run regressions for contractor components on visitor-facing pages."""
import json
import os
from html import unescape
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import unquote, urlsplit

from test_component_library import GuideMarkup

ROOT = Path(__file__).resolve().parents[1]

# The visitor journey is intentional: catch a component silently disappearing
# from its service page or being rendered on every service by a shared template.
PAGE_COMPONENTS = {
    'index.html': {'home-start': 'project-chooser'},
    'services/barn-door-installation/index.html': {
        'installation-scope': 'scope-panel', 'installation-timeline': 'project-timeline',
        'installation-responsibilities': 'responsibility-matrix'},
    'services/barn-door-replacement/index.html': {
        'replacement-materials': 'material-comparison', 'replacement-decisions': 'decision-register'},
    'services/tracks-hardware/index.html': {
        'hardware-next-step': 'service-card', 'hardware-materials': 'material-schedule'},
    'services/barn-door-adjustments/index.html': {
        'adjustments-followup': 'follow-up-plan', 'adjustments-open-items': 'punch-list'},
    'gallery/index.html': {'gallery-finishes': 'finish-selector', 'gallery-story': 'project-story'},
    'about/index.html': {'about-crew': 'crew-roster', 'about-notes': 'field-notes',
                       'about-credentials': 'credential-list'},
    'pricing/index.html': {'pricing-packages': 'package-comparison',
                          'pricing-drivers': 'cost-drivers', 'pricing-change': 'change-summary'},
    'contact/index.html': {'contact-prep': 'visit-checklist', 'contact-access': 'site-access-plan'},
    'service-area/index.html': {'service-area-availability': 'availability-panel'},
    'faq/index.html': {'faq-handover': 'handover-pack', 'faq-documents': 'document-register'},
    'reviews/index.html': {'reviews-featured': 'featured-testimonial'},
}
FLAGS = ('about', 'team', 'credentials', 'gallery', 'pricing', 'contactPage',
         'faqPage', 'reviewsPage', 'serviceArea')


class SiteComponentTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='jeff-site-component-tests-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name) / 'site'
        cls.root.mkdir()
        for name in ('assets', 'content', 'data', 'layouts', 'static', 'profiles'):
            shutil.copytree(ROOT / name, cls.root / name)
        shutil.copy2(ROOT / 'hugo.toml', cls.root / 'hugo.toml')
        cls.env = {k: v for k, v in os.environ.items() if not k.upper().startswith('HUGO_')}
        cls.output = cls.build('enabled', dict.fromkeys(FLAGS, True))
        cls.pages = {path: (cls.output / path).read_text() for path in PAGE_COMPONENTS}
        cls.markup = {path: GuideMarkup(html) for path, html in cls.pages.items()}

        # Prove live page copy does not depend on the catalogue fixture. Also
        # exercise escaping through the new wrapper, not only directly in a guide.
        (cls.root / 'data/component_library.json').write_text('{"components": []}')
        data_path = cls.root / 'data/site_components.json'
        data = json.loads(data_path.read_text())
        data['home-start']['content']['title'] = '<img src=x onerror=alert(1)>'
        data_path.write_text(json.dumps(data))
        disabled = dict.fromkeys(FLAGS, False)
        disabled['about'] = True  # The page remains; its optional blocks must not.
        cls.disabled_output = cls.build('disabled', disabled)

    @classmethod
    def build(cls, name, flags, params=''):
        (cls.root / 'fixture.toml').write_text(
            '[params]\nnoindex=true\nloadWebFonts=false\n' + params + '\n[params.features]\n' +
            ''.join(f'{key}={str(value).lower()}\n' for key, value in flags.items()))
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

    def test_all_components_render_on_their_intended_pages(self):
        kinds = set()
        for path, expected in PAGE_COMPONENTS.items():
            with self.subTest(page=path):
                entries = [attrs for _, attrs in self.markup[path].elements
                           if 'data-site-component' in attrs]
                actual = {attrs['data-site-component']: attrs['data-component-kind'] for attrs in entries}
                self.assertEqual(actual, expected)
                self.assertEqual(len(entries), len(expected))
                kinds.update(actual.values())
        self.assertEqual(len(kinds), 24)

    def test_page_ids_and_component_heading_references_are_unique_and_resolved(self):
        for path, markup in self.markup.items():
            with self.subTest(page=path):
                self.assertEqual(len(markup.ids), len(set(markup.ids)))
                headings = {attrs['id'] for tag, attrs in markup.elements
                            if tag == 'h2' and 'id' in attrs}
                for _, attrs in markup.elements:
                    if 'data-site-component' in attrs:
                        self.assertIn(attrs['aria-labelledby'], headings)
                    if attrs.get('id', '').startswith('site-'):
                        for ref in attrs.get('aria-labelledby', '').split():
                            self.assertIn(ref, markup.ids)
                    if attrs.get('for', '').startswith('site-'):
                        self.assertIn(attrs['for'], markup.ids)

    def test_choice_script_is_loaded_once_only_where_a_selector_renders(self):
        for path, markup in self.markup.items():
            with self.subTest(page=path):
                scripts = [attrs.get('src', '') for tag, attrs in markup.elements if tag == 'script']
                expected = 1 if path in ('index.html', 'gallery/index.html') else 0
                self.assertEqual(sum('/subpath/js/contractor-choices.' in src for src in scripts), expected)
                self.assertFalse(any('/js/style-guide.' in src for src in scripts))

    def test_choices_have_readable_no_script_content_and_matching_native_radios(self):
        for path in ('index.html', 'gallery/index.html'):
            with self.subTest(page=path):
                markup = self.markup[path]
                controls = [attrs for _, attrs in markup.elements if 'data-choice-controls' in attrs]
                panels = [attrs for _, attrs in markup.elements if 'data-choice-panel' in attrs]
                radios = [attrs for tag, attrs in markup.elements
                          if tag == 'input' and 'data-choice-input' in attrs]
                self.assertEqual(len(controls), 1)
                self.assertIn('hidden', controls[0])
                self.assertEqual(len(panels), 3)
                self.assertTrue(all('hidden' not in panel for panel in panels))
                self.assertEqual(len(radios), 3)
                self.assertTrue(all(radio['type'] == 'radio' for radio in radios))
                self.assertEqual(len({radio['name'] for radio in radios}), 1)
                self.assertEqual(sum('checked' in radio for radio in radios), 1)
                self.assertEqual({radio['aria-controls'] for radio in radios},
                                 {panel['id'] for panel in panels})

    def test_component_actions_retain_subpaths_and_resolve_to_existing_routes(self):
        for path, markup in self.markup.items():
            for tag, attrs in markup.elements:
                if tag != 'a' or 'contractor-link' not in attrs.get('class', '').split():
                    continue
                with self.subTest(page=path, href=attrs['href']):
                    url = urlsplit(attrs['href'])
                    self.assertFalse(url.netloc)
                    self.assertTrue(url.path.startswith('/subpath/'))
                    target = self.output / url.path.removeprefix('/subpath/')
                    if not target.suffix:
                        target /= 'index.html'
                    self.assertTrue(target.is_file())
                    if url.fragment:
                        self.assertIn(unquote(url.fragment), GuideMarkup(target.read_text()).ids)

    def test_catalogue_links_lead_to_each_actual_component_section(self):
        guide = GuideMarkup((self.output / 'style-guide/index.html').read_text())
        links = [attrs for tag, attrs in guide.elements
                 if tag == 'a' and 'data-site-component-link' in attrs]
        self.assertEqual(len(links), 24)
        self.assertEqual({attrs['data-site-component-link'] for attrs in links},
                         {key for components in PAGE_COMPONENTS.values() for key in components})
        for attrs in links:
            url = urlsplit(attrs['href'])
            self.assertTrue(url.path.startswith('/subpath/'))
            target = self.output / url.path.removeprefix('/subpath/') / 'index.html'
            self.assertIn(url.fragment, GuideMarkup(target.read_text()).ids)

    def test_disabled_pages_and_optional_about_blocks_do_not_render_components(self):
        for route in ('gallery', 'pricing', 'contact', 'faq', 'reviews', 'service-area'):
            with self.subTest(route=route):
                html = (self.disabled_output / route / 'index.html').read_text()
                self.assertIn('Information unavailable', html)
                self.assertNotIn('data-site-component=', html)
                self.assertNotIn('/js/contractor-choices.', html)
        about = (self.disabled_output / 'about/index.html').read_text()
        self.assertNotIn('Information unavailable', about)
        self.assertNotIn('data-site-component=', about)

    def test_active_pages_do_not_depend_on_catalogue_data_or_optional_destinations(self):
        home = (self.disabled_output / 'index.html').read_text()
        self.assertIn('data-site-component="home-start"', home)
        self.assertIn('/js/contractor-choices.', home)
        self.assertIn('&lt;img src=x onerror=alert(1)&gt;', home)
        self.assertNotIn('<img src=x onerror=alert(1)>', home)
        for path in PAGE_COMPONENTS:
            if path.startswith('services/'):
                html = (self.disabled_output / path).read_text()
                for key in PAGE_COMPONENTS[path]:
                    self.assertIn(f'data-site-component="{key}"', html)
        for tag, attrs in GuideMarkup(home).elements:
            if tag == 'a' and 'contractor-link' in attrs.get('class', '').split():
                target = self.disabled_output / urlsplit(attrs['href']).path.removeprefix('/subpath/') / 'index.html'
                self.assertNotIn('Information unavailable', target.read_text())

    def test_gallery_form_and_faq_keep_their_existing_single_instances(self):
        gallery = self.markup['gallery/index.html']
        self.assertEqual(sum('data-gallery' in attrs for _, attrs in gallery.elements), 1)
        self.assertEqual(sum('data-lightbox' in attrs for _, attrs in gallery.elements), 1)
        contact = self.markup['contact/index.html']
        self.assertEqual(sum(tag == 'form' and 'data-project-form' in attrs
                             for tag, attrs in contact.elements), 1)
        self.assertIn('contact-brief-help', contact.ids)
        self.assertIn('site-contact-prep-item-0', contact.ids)
        faq = self.markup['faq/index.html']
        self.assertTrue(any('contractor-handover' in attrs.get('class', '').split()
                            for _, attrs in faq.elements))
        self.assertGreaterEqual(sum(tag == 'details' and not attrs.get('class')
                                    for tag, attrs in faq.elements), 3)

    def test_project_records_are_read_only_and_do_not_imply_completed_work(self):
        records = {
            'installation-responsibilities': ('services/barn-door-installation/index.html',
                                            'nobody is assigned'),
            'replacement-decisions': ('services/barn-door-replacement/index.html',
                                     'not a record of an actual selection'),
            'hardware-materials': ('services/tracks-hardware/index.html',
                                   'not a bill of materials'),
            'adjustments-open-items': ('services/barn-door-adjustments/index.html',
                                      'no inspection, repair, completion, or customer acceptance'),
            'contact-access': ('contact/index.html', 'does not reserve a visit'),
            'faq-documents': ('faq/index.html', 'No contract, product manual, or completion record'),
        }
        for key, (path, boundary) in records.items():
            with self.subTest(component=key):
                # Match the new card itself, so unrelated form/checklist controls
                # elsewhere on the page cannot hide an accidental approval UI.
                page = self.pages[path]
                start = page.index(f'aria-labelledby="site-{key}-title"')
                card = GuideMarkup('<section ' + page[start:page.index('</section>', start) + 10])
                self.assertIn(boundary, unescape(page[start:page.index('</section>', start)]))
                self.assertFalse(any(tag in ('input', 'button', 'form', 'select', 'textarea')
                                     for tag, _ in card.elements))
                for _, attrs in card.elements:
                    self.assertNotIn('aria-current', attrs)
                    for ref in attrs.get('aria-describedby', '').split():
                        self.assertIn(ref, card.ids)

    def test_planning_tables_keep_keyboard_scroll_regions_and_semantic_headers(self):
        for key, path in (
            ('installation-responsibilities', 'services/barn-door-installation/index.html'),
            ('hardware-materials', 'services/tracks-hardware/index.html'),
        ):
            with self.subTest(component=key):
                markup = self.markup[path]
                regions = [attrs for _, attrs in markup.elements
                           if attrs.get('role') == 'region'
                           and attrs.get('aria-labelledby') == f'site-{key}-title']
                self.assertEqual(len(regions), 1)
                self.assertEqual(regions[0].get('tabindex'), '0')
                self.assertEqual(regions[0].get('aria-describedby'), f'site-{key}-hint')
                self.assertTrue(any(tag == 'th' and attrs.get('scope') == 'row'
                                    for tag, attrs in markup.elements))

    def test_contact_access_follows_the_form_and_document_links_are_real_tools(self):
        contact = self.pages['contact/index.html']
        self.assertLess(contact.index('</form>'), contact.index('id="site-contact-access"'))
        faq = self.pages['faq/index.html']
        start = faq.index('class="contractor-card contractor-documents"')
        card = GuideMarkup('<section ' + faq[start:faq.index('</section>', start) + 10])
        links = [attrs for tag, attrs in card.elements if tag == 'a']
        self.assertEqual([attrs['href'] for attrs in links], ['/subpath/survey/'])
        self.assertFalse(any('download' in attrs for attrs in links))

    def test_parody_and_unresolved_terms_remain_explicit(self):
        self.assertIn('Parody cast:', self.pages['about/index.html'])
        self.assertIn('Parody, not a customer review.', self.pages['reviews/index.html'])
        self.assertIn('Fictional design study', self.pages['gallery/index.html'])
        self.assertIn('No approval recorded', self.pages['pricing/index.html'])
        timeline = self.pages['services/barn-door-installation/index.html']
        self.assertNotIn('aria-current="step"', timeline)
        self.assertNotIn('contractor-timeline__step--complete', timeline)

    def test_faq_uses_shared_product_specific_clearance_guidance(self):
        html = unescape(self.pages['faq/index.html'])
        guidance = json.loads((ROOT / 'data/door-guidance.json').read_text())
        for check in guidance['checks']:
            with self.subTest(check=check['id']):
                # One answer and one measuring-guide card use the same copy.
                self.assertEqual(html.count(check['body']), 2)
        for outdated in ('at least 6 inches', 'plus 2 to 4 inches',
                         '3/8 to 1/2 inch', 'roughly a 3/8 inch gap'):
            self.assertNotIn(outdated, html)

    def test_faq_and_brief_delivery_help_follow_the_selected_configuration(self):
        local = 'this site currently cannot deliver your brief to Jeff'
        self.assertIn(local, self.pages['index.html'])
        self.assertIn(local, self.pages['faq/index.html'])
        cases = (
            ('contact-delivery', 'contactEmail="fixture@example.org"\n',
             'use a contact option to send it through your own messaging app'),
            ('online-delivery', '[params.intake]\nenabled=true\nenvironment="preview"\n',
             'Only a confirmed receipt means the request was saved'),
        )
        for name, params, message in cases:
            output = self.build(name, dict.fromkeys(FLAGS, True), params)
            for route in ('index.html', 'contact/index.html', 'faq/index.html'):
                with self.subTest(configuration=name, route=route):
                    html = (output / route).read_text()
                    self.assertIn(message, html)
                    self.assertNotIn(local, html)

    def test_easter_eggs_are_closed_native_disclosures_in_only_three_places(self):
        expected = {'index.html': 'lenny', 'gallery/index.html': 'jeff',
                    'about/index.html': 'doreen'}
        for path, markup in self.markup.items():
            with self.subTest(page=path):
                eggs = [(tag, attrs) for tag, attrs in markup.elements
                        if 'data-easter-egg' in attrs]
                self.assertEqual(len(eggs), 1 if path in expected else 0)
                for tag, attrs in eggs:
                    self.assertEqual(tag, 'details')
                    self.assertEqual(attrs['data-easter-egg'], expected[path])
                    self.assertNotIn('open', attrs)
                    self.assertNotIn('hidden', attrs)
                    self.assertNotIn('tabindex', attrs)
        for path in ('survey/index.html', 'privacy/index.html', '404.html'):
            self.assertNotIn('data-easter-egg=', (self.output / path).read_text())

    def test_optional_crew_and_gallery_flags_also_hide_their_easter_eggs(self):
        for path in ('index.html', 'about/index.html', 'gallery/index.html'):
            with self.subTest(page=path):
                self.assertNotIn('data-easter-egg=', (self.disabled_output / path).read_text())
        for output, expected in ((self.output, {'egg-lenny', 'egg-jeff', 'egg-doreen'}),
                                 (self.disabled_output, set())):
            guide = GuideMarkup((output / 'style-guide/index.html').read_text())
            links = [attrs['href'] for tag, attrs in guide.elements
                     if tag == 'a' and '#egg-' in attrs.get('href', '')]
            self.assertEqual({urlsplit(href).fragment for href in links}, expected)
            for href in links:
                url = urlsplit(href)
                self.assertTrue(url.path.startswith('/subpath/'))
                target = output / url.path.removeprefix('/subpath/') / 'index.html'
                self.assertIn(url.fragment, GuideMarkup(target.read_text()).ids)

    def test_site_copy_is_in_the_publication_source_inventory(self):
        sys.path.insert(0, str(ROOT / 'scripts'))
        try:
            import content_policy as policy
        finally:
            sys.path.pop(0)
        config = policy.load_config(ROOT, 'hugo.toml,profiles/jeff-does-doors.toml,hugo-staging.toml')
        sources = policy.required_sources(ROOT, config)
        self.assertIn('data/site_components.json', sources)
        self.assertIn('layouts/partials/site-component.html', sources)
        self.assertIn('static/images/barn-door-walnut.webp', sources)
