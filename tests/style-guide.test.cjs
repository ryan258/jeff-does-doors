/* Behavior regressions for the guide-only enhancement; no browser dependency. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../assets/js/style-guide.js'), 'utf8');

function element(extra = {}) {
  return Object.assign({
    hidden: false, value: '', textContent: '', dataset: {}, handlers: {},
    addEventListener(name, handler) { this.handlers[name] = handler; },
    fire(name) { return this.handlers[name]?.(); },
    focus() { this.focused = true; },
    scrollIntoView() { this.scrolled = true; },
  }, extra);
}

function fixture({ hash = '', clipboard, query = '', selectedFamily = 'all' } = {}) {
  const search = element({ value: query });
  const family = element({ value: selectedFamily });
  const count = element();
  const empty = element({ hidden: true });
  const controls = element({ hidden: true });
  const reset = element();
  const emptyReset = element();
  const status = element();
  const snippet = element({ textContent: '{{ partial "example.html" . }}' });
  const copy = element({ hidden: true, dataset: { guideCopy: 'usage-example' } });
  const entries = [
    element({ id: 'component-scope', dataset: { guideSearchText: 'Scope of work Contractor responsibilities', guideFamilyName: 'contractor' } }),
    element({ id: 'component-gallery', dataset: { guideSearchText: 'Gallery image project photographs', guideFamilyName: 'shared' } }),
    element({ id: 'component-fields', dataset: { guideSearchText: 'Form fields error states', guideFamilyName: 'foundation' } }),
  ];
  const links = entries.map((entry) => element({ getAttribute: () => `#${entry.id}` }));
  const selectors = {
    '[data-guide-search]': search, '[data-guide-family]': family,
    '[data-guide-count]': count, '[data-guide-empty]': empty,
    '[data-guide-controls]': controls, '[data-guide-reset]': reset,
    '[data-guide-empty-reset]': emptyReset, '[data-guide-copy-status]': status,
  };
  const guide = {
    querySelector: (selector) => selectors[selector] || null,
    querySelectorAll: (selector) => ({
      '[data-guide-entry]': entries, '[data-guide-copy]': [copy],
      'a[href^="#component-"]': links,
    })[selector] || [],
  };
  const selection = { removeAllRanges() {}, addRange(range) { this.range = range; } };
  const window = element({ location: { hash }, getSelection: () => selection });
  const document = {
    querySelector: () => guide,
    getElementById: (id) => id === 'usage-example' ? snippet : null,
    createRange: () => ({ selectNodeContents(node) { this.node = node; } }),
  };
  vm.runInNewContext(source, { document, window, navigator: { clipboard } });
  return { search, family, count, empty, controls, reset, emptyReset, status, snippet, copy, entries, links, window, selection };
}

test('does nothing outside the guide', () => {
  assert.doesNotThrow(() => vm.runInNewContext(source, { document: { querySelector: () => null } }));
});

test('initializes all entries and enables controls only on the guide', () => {
  const f = fixture();
  assert.equal(f.count.textContent, '3 of 3 components');
  assert.equal(f.controls.hidden, false);
  assert.equal(f.empty.hidden, true);
  assert.ok(f.entries.every((entry) => !entry.hidden));
  assert.equal(f.copy.hidden, true); // no Clipboard API
});

test('search is case-insensitive, matches every word, and combines with family', () => {
  const f = fixture();
  f.search.value = '  WORK   scope ';
  f.search.fire('input');
  assert.deepEqual(f.entries.map((entry) => entry.hidden), [false, true, true]);
  assert.equal(f.count.textContent, '1 of 3 components');
  f.family.value = 'shared';
  f.family.fire('change');
  assert.equal(f.empty.hidden, false);
  assert.equal(f.count.textContent, '0 of 3 components');
});

test('empty result recovery clears both filters and restores search focus', () => {
  const f = fixture({ query: 'nothing', selectedFamily: 'shared' });
  assert.equal(f.empty.hidden, false);
  f.emptyReset.fire('click');
  assert.equal(f.search.value, '');
  assert.equal(f.family.value, 'all');
  assert.equal(f.search.focused, true);
  assert.ok(f.entries.every((entry) => !entry.hidden));
  f.search.value = 'gallery';
  f.search.fire('input');
  f.reset.fire('click');
  assert.equal(f.count.textContent, '3 of 3 components');
});

test('deep links reveal specimens hidden by restored filter values', () => {
  const f = fixture({ hash: '#component-gallery', query: 'scope' });
  assert.equal(f.search.value, '');
  assert.equal(f.entries[1].hidden, false);
  assert.equal(f.entries[1].scrolled, true);
  f.family.value = 'foundation';
  f.family.fire('change');
  f.window.location.hash = '#component-scope';
  f.window.fire('hashchange');
  assert.equal(f.family.value, 'all');
  assert.equal(f.entries[0].hidden, false);
});

test('re-clicking a filtered current fragment reveals it without hashchange', () => {
  const f = fixture({ hash: '#component-gallery' });
  f.search.value = 'scope';
  f.search.fire('input');
  assert.equal(f.entries[1].hidden, true);
  f.links[1].fire('click');
  assert.equal(f.entries[1].hidden, false);
});

test('malformed and unknown hashes are harmless and preserve filters', () => {
  for (const hash of ['#%E0%A4%A', '#unknown', '#component-%22%5D%3Cscript%3E']) {
    const f = fixture({ hash, query: 'scope' });
    assert.equal(f.search.value, 'scope');
    assert.equal(f.count.textContent, '1 of 3 components');
  }
});

test('copy uses snippet text and reports success only after clipboard resolves', async () => {
  let written;
  const f = fixture({ clipboard: { writeText: async (text) => { written = text; } } });
  assert.equal(f.copy.hidden, false);
  await f.copy.fire('click');
  assert.equal(written, f.snippet.textContent);
  assert.equal(f.status.textContent, 'Usage snippet copied.');
});

test('clipboard rejection selects the snippet and reports the manual fallback', async () => {
  const f = fixture({ clipboard: { writeText: async () => { throw new Error('denied'); } } });
  await f.copy.fire('click');
  assert.equal(f.snippet.focused, true);
  assert.equal(f.selection.range.node, f.snippet);
  assert.match(f.status.textContent, /Clipboard unavailable/);
  assert.doesNotMatch(f.status.textContent, /snippet copied/);
});
