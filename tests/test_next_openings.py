"""Owner-run regressions for the homepage concept spread; no live services."""
import json
import os
from html.parser import HTMLParser
from pathlib import Path
import shutil
import subprocess
import sys
import tempfile
import unittest
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT / 'scripts'))
import content_policy as policy


class ConceptMarkup(HTMLParser):
    def __init__(self, html):
        super().__init__()
        self.inside = False
        self.elements = []
        self.text = []
        self.feed(html)

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'section' and attrs.get('id') == 'next-openings':
            self.inside = True
        if self.inside:
            self.elements.append((tag, attrs))

    def handle_endtag(self, tag):
        if tag == 'section':
            self.inside = False

    def handle_data(self, data):
        if self.inside:
            self.text.append(data)


class NextOpeningsTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp = tempfile.TemporaryDirectory(prefix='jeff-next-openings-')
        cls.addClassCleanup(cls.temp.cleanup)
        cls.root = Path(cls.temp.name) / 'source'
        cls.root.mkdir()
        for name in ('assets', 'content', 'data', 'layouts', 'static', 'profiles'):
            shutil.copytree(ROOT / name, cls.root / name)
        shutil.copy2(ROOT / 'hugo.toml', cls.root / 'hugo.toml')
        # Concepts are a separate homepage section, even with the gallery off.
        (cls.root / 'fixture.toml').write_text(
            '[params]\nnoindex=true\nloadWebFonts=false\n'
            '[params.features]\ngallery=false\n')
        cls.output = Path(cls.temp.name) / 'output'
        env = {key: value for key, value in os.environ.items()
               if not key.upper().startswith('HUGO_')}
        result = subprocess.run(
            ['hugo', '--source', str(cls.root), '--environment', 'staging',
             '--config', 'hugo.toml,profiles/jeff-does-doors.toml,fixture.toml',
             '--baseURL', 'https://fixture-review.org/subpath/',
             '--destination', str(cls.output),
             '--cacheDir', str(Path(cls.temp.name) / 'cache')],
            env=env, capture_output=True, text=True)
        if result.returncode:
            raise AssertionError(result.stdout + result.stderr)
        cls.html = (cls.output / 'index.html').read_text()
        cls.markup = ConceptMarkup(cls.html)
        cls.data = json.loads((ROOT / 'data/next_openings.json').read_text())

    def test_four_distinct_concepts_render_between_styles_and_catalog(self):
        figures = [attrs for tag, attrs in self.markup.elements if tag == 'figure']
        self.assertEqual(len(figures), 4)
        self.assertEqual({attrs['id'] for attrs in figures},
                         {'next-opening-' + item['id'] for item in self.data['items']})
        self.assertLess(self.html.index('id="styles"'), self.html.index('id="next-openings"'))
        self.assertLess(self.html.index('id="next-openings"'), self.html.index('id="catalog"'))
        self.assertFalse(any('data-gallery-open' in attrs for _, attrs in self.markup.elements))

    def test_accessible_labels_and_concept_disclosures_are_present(self):
        ids = [attrs['id'] for _, attrs in self.markup.elements if 'id' in attrs]
        self.assertEqual(len(ids), len(set(ids)))
        section = next(attrs for tag, attrs in self.markup.elements if tag == 'section')
        self.assertIn(section['aria-labelledby'], ids)
        self.assertIn(section['aria-describedby'], ids)
        text = ''.join(self.markup.text)
        self.assertIn('not completed Jeff projects or available products', text)
        flags = [attrs for tag, attrs in self.markup.elements
                 if tag == 'small' and attrs.get('class') == 'next-opening__disclosure']
        self.assertEqual(len(flags), 4)
        images = [attrs for tag, attrs in self.markup.elements if tag == 'img']
        self.assertEqual(len(images), 4)
        self.assertTrue(all(image['alt'].startswith('AI concept') for image in images))

    def test_full_image_links_and_responsive_variants_resolve_under_subpath(self):
        links = [attrs for tag, attrs in self.markup.elements
                 if tag == 'a' and attrs.get('class') == 'next-opening__image']
        images = [attrs for tag, attrs in self.markup.elements if tag == 'img']
        self.assertEqual(len(links), 4)
        for link, image, item in zip(links, images, self.data['items']):
            with self.subTest(concept=item['id']):
                self.assertEqual(link['href'], image['src'])
                self.assertIn(item['title'], link['aria-label'])
                self.assertIn('AI-generated concept', link['aria-label'])
                self.assertEqual(image['loading'], 'lazy')
                self.assertEqual(image['decoding'], 'async')
                self.assertEqual((image['width'], image['height']), ('1536', '1024'))
                self.assertIn('max-width: 760px', image['sizes'])
                variants = [part.strip().rsplit(' ', 1) for part in image['srcset'].split(',')]
                self.assertEqual([width for _, width in variants], ['480w', '960w', '1536w'])
                for url, _ in variants:
                    path = urlsplit(url).path
                    self.assertTrue(path.startswith('/subpath/images/'))
                    asset = self.output / path.removeprefix('/subpath/')
                    self.assertTrue(asset.is_file(), path)
                    content = asset.read_bytes()
                    self.assertEqual(content[:4], b'RIFF')
                    self.assertEqual(content[8:12], b'WEBP')

    def test_new_copy_and_all_image_variants_are_in_publication_inventory(self):
        config = policy.load_config(ROOT, policy.default_configs(ROOT, staging=True))
        sources = policy.required_sources(ROOT, config)
        self.assertIn('data/next_openings.json', sources)
        self.assertIn('layouts/partials/next-openings.html', sources)
        self.assertIn('assets/scss/_next-openings.scss', sources)
        for item in self.data['items']:
            for field in ('image', 'smallImage', 'mediumImage'):
                self.assertIn('static/' + item[field], sources)


if __name__ == '__main__':
    unittest.main()
