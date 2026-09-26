const test = require('node:test');
const assert = require('node:assert/strict');
const vm = require('node:vm');
const fs = require('node:fs');
const path = require('node:path');
let core;
test.before(async () => { core = await import('../assets/js/intake-core.mjs'); });
class Element {
  constructor() { this.listeners = {}; this.hidden = false; this.disabled = false; this.textContent = ''; this.checked = false; this.value = ''; this.parentElement = { hidden: true }; }
  addEventListener(name, fn) { this.listeners[name] = fn; }
  click() { return this.listeners.click(); }
  focus() { this.focused = true; }
  closest() { return null; }
}
function setup(fetcher) {
  const names = ['send-request', 'retry-request', 'new-request', 'request-status', 'request-revision', 'request-consent', 'request-challenge', 'challenge-status'];
  const nodes = Object.fromEntries(names.map(name => [name, new Element()]));
  const values = { projectType: '', location: 'Fixture area', details: 'Original details', serviceDetails: '', timing: 'Flexible', access: 'Not sure', propertyType: 'Not specified', budget: 'Not sure yet', name: '', contact: 'visitor@site.test', preferredContact: 'Email', referral: 'Not specified' };
  const fields = Object.fromEntries(Object.entries(values).map(([name, value]) => { const e = new Element(); e.value = value; return [name, e]; }));
  fields.projectType.options = [{ dataset: { serviceId: '' } }, { dataset: { serviceId: 'septic' } }];
  fields.projectType.selectedOptions = [fields.projectType.options[0]];
  const panel = { dataset: { environment: 'preview', siteKey: 'fixture', consentVersion: 'v1' }, querySelector: selector => nodes[selector.slice(6,-1)] };
  const form = { dataset: { profileId: 'jones', draftScope: '/', supportsSms: 'false' }, elements: { namedItem: name => fields[name] }, querySelector: () => panel, dispatchEvent() {} };
  const map = new Map(); const storage = { getItem: k => map.get(k) ?? null, setItem: (k,v) => map.set(k,v), removeItem: k => map.delete(k) };
  let callbacks;
  const window = { sessionStorage: storage, confirm: () => true, turnstile: { render(node, options) { callbacks = options; options.callback('fixture-token'); return 'widget'; }, reset() { callbacks.callback('fresh-token'); } } };
  const script = fs.readFileSync(path.join(__dirname, '../assets/js/intake.js'), 'utf8').replace(/^import .*;\n/, '');
  vm.runInNewContext(script, { ...core, submitRequest: (payload, options) => core.submitRequest(payload, { ...options, fetcher }), window, document: { querySelectorAll: () => [form] }, CustomEvent: class {}, setTimeout, clearTimeout });
  return { nodes, fields, storage, callbacks: () => callbacks };
}
async function receipt(url, options) {
  const payload = Object.fromEntries([...options.body].filter(([k]) => Object.hasOwn(core.LIMITS, k)));
  return Response.json({ status: 'accepted', id: options.body.get('submission-id'), hash: await core.payloadHash(payload) });
}
test('online validation checks current edits and requires consent separately from local draft', async () => {
  let calls = 0; const ui = setup(async (...args) => { calls++; return receipt(...args); });
  ui.fields.details.value = ' ';
  await ui.nodes['send-request'].click();
  assert.match(ui.nodes['request-status'].textContent, /complete details/); assert(ui.fields.details.focused);
  ui.fields.details.value = 'Restored';
  await ui.nodes['send-request'].click();
  assert.match(ui.nodes['request-status'].textContent, /agree/); assert.equal(calls, 0);
});
test('receipt remains visible after challenge expiry; accepted request needs deliberate new action', async () => {
  const ui = setup(receipt); ui.nodes['request-consent'].checked = true;
  await ui.nodes['send-request'].click();
  assert.match(ui.nodes['request-status'].textContent, /Saved successfully/);
  assert(ui.nodes['send-request'].disabled);
  ui.callbacks()['expired-callback']();
  assert.match(ui.nodes['request-status'].textContent, /Saved successfully/);
  await ui.nodes['new-request'].click();
  assert(!ui.nodes['send-request'].disabled); assert(!ui.nodes['request-consent'].checked);
});
test('uncertain send keeps original revision and retry ignores edits to the current draft', async () => {
  const sent = []; let first = true;
  const ui = setup(async (url, options) => {
    sent.push(Object.fromEntries(options.body));
    if (first) { first = false; throw new Error('lost response'); }
    return receipt(url, options);
  });
  ui.nodes['request-consent'].checked = true;
  await ui.nodes['send-request'].click();
  ui.fields.details.value = 'Changed later';
  await ui.nodes['send-request'].click();
  assert.match(ui.nodes['request-status'].textContent, /differ/);
  assert.equal(sent.length, 1);
  await ui.nodes['retry-request'].click();
  assert.equal(sent[1].details, 'Original details');
  assert.equal(sent[1]['submission-id'], sent[0]['submission-id']);
  assert.match(ui.nodes['request-status'].textContent, /Saved successfully/);
});

test('missing metadata requires explicit restart and displays the new submitted revision', async () => {
  const sent = [];
  const ui = setup(async (url, options) => {
    sent.push(Object.fromEntries(options.body));
    if (sent.length === 1) throw new Error('lost response');
    return receipt(url, options);
  });
  ui.nodes['request-consent'].checked = true;
  await ui.nodes['send-request'].click();
  ui.storage.removeItem('construction-submission:v1:jones:/');
  ui.fields.details.value = 'New request details';
  await ui.nodes['send-request'].click();
  assert.equal(sent.length, 1);
  assert.match(ui.nodes['request-status'].textContent, /identity is missing/);
  assert(!ui.nodes['new-request'].hidden);
  await ui.nodes['retry-request'].click();
  assert.equal(sent.length, 1);
  await ui.nodes['new-request'].click();
  assert(!ui.nodes['request-consent'].checked);
  ui.nodes['request-consent'].checked = true;
  await ui.nodes['send-request'].click();
  assert.equal(sent.length, 2);
  assert.notEqual(sent[0]['submission-id'], sent[1]['submission-id']);
  assert.equal(sent[1].details, 'New request details');
  assert.match(ui.nodes['request-revision'].textContent, /details: New request details/);
  assert.doesNotMatch(ui.nodes['request-revision'].textContent, /Original details/);
  assert.match(ui.nodes['request-status'].textContent, /Saved successfully/);
});
