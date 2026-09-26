/* Every initializer must run clean against an empty document.
   initialize() logs and swallows failures, so a scope or typo error in one
   feature is otherwise invisible until a visitor hits the broken control. */
const { test } = require('node:test');
const assert = require('node:assert/strict');
const path = require('node:path');

test('no initializer throws on a page with none of its elements', () => {
  const stub = {
    addEventListener() {}, removeAttribute() {}, setAttribute() {},
    getAttribute: () => null, querySelector: () => null, querySelectorAll: () => [],
    hidden: false, style: { setProperty() {} }, textContent: '',
  };
  global.window = { matchMedia: () => ({ matches: false }), addEventListener() {}, ConstructionBrief: {} };
  global.document = {
    querySelector: () => null, querySelectorAll: () => [], addEventListener() {},
    documentElement: stub, body: stub, createElement: () => stub,
  };
  const failures = [];
  const realError = console.error;
  console.error = (...args) => failures.push(args.map(String).join(' '));
  try {
    delete require.cache[require.resolve('../assets/js/site.js')];
    require(path.join(__dirname, '..', 'assets', 'js', 'site.js'));
  } finally {
    console.error = realError;
  }
  assert.deepEqual(failures, []);
});
