/* Owner-run behavior checks for repeatable choice components. No DOM library. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const vm = require('node:vm');

const source = fs.readFileSync(path.join(__dirname, '../assets/js/contractor-choices.js'), 'utf8');

function choice({ selected = 0, labels = ['Oak', 'Walnut', 'Glass'] } = {}) {
  const inputs = labels.map((label, index) => ({
    value: String(index), checked: index === selected,
    dataset: { choiceLabel: label }, handlers: [],
    addEventListener(name, handler) { if (name === 'change') this.handlers.push(handler); },
  }));
  const panels = labels.map((_, index) => ({ dataset: { choicePanel: String(index) }, hidden: false }));
  const controls = { hidden: true };
  const status = { textContent: '' };
  Object.defineProperty(status, 'innerHTML', { set() { throw new Error('Do not interpret labels as markup'); } });
  const root = {
    dataset: {},
    querySelector: (selector) => ({ '[data-choice-controls]': controls, '[data-choice-status]': status })[selector] || null,
    querySelectorAll: (selector) => ({ '[data-choice-input]': inputs, '[data-choice-panel]': panels })[selector] || [],
  };
  const select = (index) => {
    inputs.forEach((input, i) => { input.checked = i === index; });
    inputs[index].handlers.forEach((handler) => handler());
  };
  return { root, inputs, panels, controls, status, select };
}

function run(...choices) {
  vm.runInNewContext(source, { document: { querySelectorAll: () => choices.map((item) => item.root) } });
}

test('pages with no choice components are unaffected', () => {
  assert.doesNotThrow(() => run());
});

test('enhancement exposes controls and selects one panel without an initial announcement', () => {
  const c = choice();
  run(c);
  assert.equal(c.controls.hidden, false);
  assert.deepEqual(c.panels.map((panel) => panel.hidden), [false, true, true]);
  assert.equal(c.status.textContent, '');
});

test('respects restored radio selection and falls back to the first option if needed', () => {
  const restored = choice({ selected: 2 });
  const unselected = choice({ selected: -1 });
  run(restored, unselected);
  assert.deepEqual(restored.panels.map((panel) => panel.hidden), [true, true, false]);
  assert.deepEqual(unselected.panels.map((panel) => panel.hidden), [false, true, true]);
  assert.equal(unselected.inputs[0].checked, true);
});

test('changing a radio reveals its local content and announces the label', () => {
  const c = choice();
  run(c);
  c.select(1);
  assert.deepEqual(c.panels.map((panel) => panel.hidden), [true, false, true]);
  assert.equal(c.status.textContent, 'Showing Walnut.');
  c.inputs[0].handlers[0](); // an unchecked radio must not replace the choice
  assert.deepEqual(c.panels.map((panel) => panel.hidden), [true, false, true]);
});

test('multiple instances remain independent even when their values overlap', () => {
  const first = choice();
  const second = choice();
  run(first, second);
  first.select(2);
  assert.deepEqual(first.panels.map((panel) => panel.hidden), [true, true, false]);
  assert.deepEqual(second.panels.map((panel) => panel.hidden), [false, true, true]);
  assert.equal(second.status.textContent, '');
});

test('invalid mappings keep the full readable fallback and hide inactive controls', () => {
  const mutations = [
    (c) => c.panels.pop(),
    (c) => { c.panels[2].dataset.choicePanel = 'unknown'; },
    (c) => { c.panels[2].dataset.choicePanel = '1'; },
    (c) => { c.inputs[2].value = '1'; },
    (c) => { c.inputs.length = 0; c.panels.length = 0; },
    (c) => { c.root.querySelector = () => null; },
  ];
  for (const mutate of mutations) {
    const c = choice();
    mutate(c);
    run(c);
    assert.equal(c.controls.hidden, true);
    assert.ok(c.panels.every((panel) => panel.hidden === false));
    assert.notEqual(c.root.dataset.choiceReady, 'true');
    assert.ok(c.inputs.every((input) => input.handlers.length === 0));
  }
});

test('an invalid instance does not block another instance', () => {
  const invalid = choice();
  invalid.panels.pop();
  const valid = choice();
  run(invalid, valid);
  assert.equal(invalid.controls.hidden, true);
  assert.equal(valid.controls.hidden, false);
});

test('including the script twice does not duplicate handlers or reset a choice', () => {
  const c = choice();
  run(c);
  c.select(1);
  run(c);
  assert.ok(c.inputs.every((input) => input.handlers.length === 1));
  assert.deepEqual(c.panels.map((panel) => panel.hidden), [true, false, true]);
});

test('option labels remain plain text in announcements', () => {
  const label = '<img src=x onerror=alert(1)>';
  const c = choice({ labels: ['Plain', label] });
  run(c);
  c.select(1);
  assert.equal(c.status.textContent, `Showing ${label}.`);
});
