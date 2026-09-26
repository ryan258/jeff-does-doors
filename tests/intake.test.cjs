const test = require('node:test');
const assert = require('node:assert/strict');
const { readFileSync } = require('node:fs');
const { DatabaseSync } = require('node:sqlite');
let api, recover, deliver, core, fixture;
const originalFetch = global.fetch;
test.before(async () => {
  api = (await import('../functions/api/project-request.js')).onRequest;
  recover = (await import('../functions/api/notifications.js')).onRequest;
  deliver = (await import('../lib/notifications.mjs')).deliver;
  core = await import('../assets/js/intake-core.mjs');
});
test.after(() => { global.fetch = originalFetch; });
test.beforeEach(() => {
  const sql = new DatabaseSync(':memory:');
  sql.exec(readFileSync(require('node:path').join(__dirname, '../migrations/0001_project_requests.sql'), 'utf8'));
  const db = { prepare(query) { return { bind(...args) { return {
    async first() { return sql.prepare(query).get(...args); },
    async run() { return sql.prepare(query).run(...args); },
  }; } }; } };
  fixture = { sql, db, jobs: [], sends: [], env: { DB: db, INTAKE_ENABLED: 'true', INTAKE_ENV: 'preview',
    INTAKE_PROFILE: 'jones', INTAKE_SERVICES: '["septic","dirt-work"]', INTAKE_SUPPORTS_SMS: 'false',
    TURNSTILE_SECRET_KEY: 'fixture-secret', TURNSTILE_HOSTNAMES: 'site.test', CONSENT_VERSION: 'v1',
    CF_ACCOUNT_ID: 'a'.repeat(32), EMAIL_API_TOKEN: 'fixture-token', NOTIFICATION_FROM: 'requests@site.test',
    NOTIFICATION_TO: 'operator@site.test', OPERATOR_TOKEN: 'test-only-operator-token-32-characters' } };
  global.fetch = async (url, options) => {
    if (String(url).includes('siteverify')) return Response.json({ success: true, hostname: 'site.test', action: 'project-request' });
    fixture.sends.push(JSON.parse(options.body));
    return Response.json({ success: true, result: { queued: ['operator@site.test'] } });
  };
});
test.afterEach(async () => { await Promise.allSettled(fixture.jobs); fixture.sql.close(); });
function fields(changes = {}) {
  return { environment: 'preview', profile: 'jones', projectType: 'septic', location: 'Fixture area', details: 'Private project details',
    serviceDetails: '', timing: 'Flexible', access: 'Not sure', propertyType: 'Not specified', budget: 'Not sure yet',
    name: 'Fixture Visitor', contact: 'visitor@site.test', preferredContact: 'Email', referral: 'Not specified',
    consent: 'yes', consentVersion: 'v1', 'submission-id': crypto.randomUUID(), 'cf-turnstile-response': 'fixture-token', ...changes };
}
function req(values = fields(), changes = {}) {
  return new Request('https://site.test/api/project-request', { method: 'POST', headers: { Origin: 'https://site.test', 'Content-Type': 'application/x-www-form-urlencoded' }, body: new URLSearchParams(values), ...changes });
}
function context(request, env = fixture.env) { return { request, env, waitUntil(job) { fixture.jobs.push(job); } }; }
function row() { return fixture.sql.prepare('SELECT * FROM project_requests').get(); }
function count() { return fixture.sql.prepare('SELECT count(*) AS n FROM project_requests').get().n; }
function payload() { const all = fields(); delete all['submission-id']; delete all['cf-turnstile-response']; return all; }
function storage() { const map = new Map(); return { getItem: key => map.get(key) ?? null, setItem: (key, value) => map.set(key, value), removeItem: key => map.delete(key) }; }

test('durable receipt matches ID and complete payload hash before notification finishes', async () => {
  const values = fields(); const response = await api(context(req(values)));
  assert.equal(response.status, 200);
  assert.deepEqual(await response.json(), { status: 'accepted', id: values['submission-id'], hash: row().payload_hash });
  assert.equal(JSON.parse(row().payload_json).details, values.details);
  await Promise.all(fixture.jobs);
  assert.equal(row().notification_status, 'accepted');
  assert.equal(fixture.sends[0].reply_to, 'visitor@site.test');
  assert(!fixture.sends[0].text.includes('Private project details'));
});
test('concurrent and delayed identical retries remain one inquiry and one accepted notification', async () => {
  const values = fields();
  const results = await Promise.all([api(context(req(values))), api(context(req(values)))]);
  assert.deepEqual(await results[0].json(), await results[1].json());
  await Promise.all(fixture.jobs);
  await api(context(req(values))); await Promise.all(fixture.jobs);
  assert.equal(count(), 1); assert.equal(fixture.sends.length, 1);
});
test('same identity with changed payload conflicts; deliberate new identity saves separately', async () => {
  const values = fields(); await api(context(req(values)));
  assert.equal((await api(context(req({ ...values, details: 'Changed' })))).status, 409);
  assert.equal(JSON.parse(row().payload_json).details, values.details);
  assert.equal((await api(context(req({ ...values, 'submission-id': crypto.randomUUID() })))).status, 200);
  assert.equal(count(), 2);
});
test('committed write with lost acknowledgment resolves on identical retry', async () => {
  const db = { prepare(query) { return { bind(...args) { const statement = fixture.db.prepare(query).bind(...args); return { async first() { await statement.first(); throw new Error('lost acknowledgment'); } }; } }; } };
  const values = fields(); assert.equal((await api(context(req(values), { ...fixture.env, DB: db }))).status, 503);
  assert.equal((await api(context(req(values)))).status, 200); assert.equal(count(), 1);
});
test('database failure cannot acknowledge receipt', async () => {
  const db = { prepare() { throw new Error('unavailable'); } };
  assert.equal((await api(context(req(), { ...fixture.env, DB: db }))).status, 503); assert.equal(count(), 0);
});
for (const [label, change] of Object.entries({ emptyDetails: { details: '  ' }, invalidEmail: { contact: 'bad@' }, incompatibleReply: { preferredContact: 'Call' }, disabledSMS: { contact: '4172223333', preferredContact: 'Text' }, wrongProfile: { profile: 'other' }, wrongEnvironment: { environment: 'production' }, unknownService: { projectType: 'unapproved' }, invalidEnum: { timing: 'Whenever' }, missingConsent: { consent: '' }, staleConsent: { consentVersion: 'old' }, headerInjection: { name: 'Test\r\nBCC: x' }, tooLong: { details: 'x'.repeat(8001) } })) {
  test(`reject ${label} before any save`, async () => { assert.equal((await api(context(req(fields(change))))).status, 400); assert.equal(count(), 0); });
}
test('phone inquiry has no fabricated Reply-To email', async () => {
  await api(context(req(fields({ contact: '+1 (417) 222-3333', preferredContact: 'Call' }))));
  await Promise.all(fixture.jobs); assert(!Object.hasOwn(fixture.sends[0], 'reply_to'));
});
test('duplicate fields, files, actual oversized body and wrong methods are rejected', async () => {
  const body = new URLSearchParams(fields()); body.append('details', 'duplicate');
  assert.equal((await api(context(req(fields(), { body })))).status, 400);
  const multipart = new FormData(); multipart.set('details', new Blob(['file']), 'test.txt');
  assert.equal((await api(context(req(fields(), { body: multipart, headers: {} })))).status, 415);
  assert.equal((await api(context(req(fields(), { body: 'x'.repeat(262145) })))).status, 413);
  assert.equal((await api(context(new Request('https://site.test/api/project-request')))).status, 405);
  assert.equal(count(), 0);
});
test('runtime disabled, missing config, dummy deployment secret, and wrong origin fail closed', async () => {
  for (const change of [{ INTAKE_ENABLED: 'false' }, { INTAKE_ENV: 'production' }, { DB: null }, { INTAKE_SERVICES: 'broken' }, { TURNSTILE_SECRET_KEY: '1x0000000000000000000000000000000AA' }, { INTAKE_ENV: 'local' }]) {
    assert.equal((await api(context(req(), { ...fixture.env, ...change }))).status, 503);
  }
  assert.equal((await api(context(req(fields(), { headers: { Origin: 'https://attacker.test' } })))).status, 403);
  assert.equal(count(), 0);
});
test('wrong challenge hostname/action, spent token and provider failure cannot save', async () => {
  for (const result of [{ success: false }, { success: true, hostname: 'attacker.test', action: 'project-request' }, { success: true, hostname: 'site.test', action: 'wrong' }]) {
    global.fetch = async () => Response.json(result);
    assert.equal((await api(context(req()))).status, 403);
  }
  global.fetch = async () => { throw new Error('timeout'); };
  assert.equal((await api(context(req()))).status, 503); assert.equal(count(), 0);
});
test('failed mail preserves receipt and authenticated retry claims saved record', async () => {
  delete fixture.env.EMAIL_API_TOKEN;
  const response = await api(context(req())); assert.equal(response.status, 200);
  await Promise.all(fixture.jobs); assert.equal(row().notification_status, 'failed');
  const make = token => new Request('https://site.test/api/notifications', { method: 'POST', headers: { Authorization: token, 'Content-Type': 'application/json' }, body: JSON.stringify({ id: row().id }) });
  assert.equal((await recover({ request: make('wrong'), env: fixture.env })).status, 401);
  fixture.env.EMAIL_API_TOKEN = 'fixture-token';
  assert.equal((await recover({ request: make(`Bearer ${fixture.env.OPERATOR_TOKEN}`), env: fixture.env })).status, 200);
  assert.equal(row().notification_status, 'accepted'); assert.equal(row().notification_attempts, 2);
});
test('crashed background work is recoverable after expired lease', async () => {
  const values = fields(); await api({ request: req(values), env: fixture.env, waitUntil(job) { fixture.jobs.push(job); } }); await Promise.all(fixture.jobs);
  fixture.sql.prepare("UPDATE project_requests SET notification_status='sending', notification_lease_until=1").run();
  assert.equal((await deliver(fixture.env, row().id)).status, 'accepted');
  assert.equal((await deliver(fixture.env, row().id)).status, 'not_claimed');
});
test('client lost response retains metadata only and retries same identity after reload', async () => {
  const saved = storage(); let id;
  await assert.rejects(core.submitRequest(payload(), { storage: saved, key: 'test', token: 'one', fetcher: async (url, options) => { id = options.body.get('submission-id'); throw new Error('lost'); } }));
  assert.deepEqual(Object.keys(JSON.parse(saved.getItem('test'))).sort(), ['hash','id','state']);
  const receipt = await core.submitRequest(payload(), { storage: saved, key: 'test', token: 'two', fetcher: async (url, options) => {
    assert.equal(options.body.get('submission-id'), id);
    return Response.json({ status: 'accepted', id, hash: await core.payloadHash(payload()) });
  } });
  assert.equal(receipt.state, 'accepted');
});
test('client changed retry is blocked; wrong or malformed 2xx receipt never claims acceptance', async () => {
  const saved = storage();
  await assert.rejects(core.submitRequest(payload(), { storage: saved, key: 'test', token: 'one', fetcher: async () => Response.json({ status: 'accepted', id: crypto.randomUUID(), hash: 'wrong' }) }), /uncertain/);
  await assert.rejects(core.submitRequest({ ...payload(), details: 'Changed' }, { storage: saved, key: 'test', token: 'two', fetcher: async () => { assert.fail('must not send changed retry'); } }), /differ/);
  await assert.rejects(core.submitRequest(payload(), { storage: saved, key: 'test', token: 'two', fetcher: async () => new Response('<html>static host</html>') }), /uncertain/);
  assert.equal(core.readAttempt(saved, 'test').state, 'unknown');
});
test('client concurrent click is serialized and storage denial prevents network', async () => {
  const saved = storage(); let release; const gate = new Promise(resolve => { release = resolve; });
  const first = core.submitRequest(payload(), { storage: saved, key: 'test', token: 'one', fetcher: async () => { await gate; return Response.json({}); } });
  await assert.rejects(core.submitRequest(payload(), { storage: saved, key: 'test', token: 'two' }), /already/);
  release(); await assert.rejects(first);
  await assert.rejects(core.submitRequest(payload(), { storage: { ...saved, setItem() { throw new Error('denied'); } }, key: 'other', token: 'one', fetcher: async () => assert.fail('must not send') }), /denied/);
});
