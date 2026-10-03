const test = require('node:test');
const assert = require('node:assert/strict');
let core;
test.before(async () => { core = await import('../assets/js/survey-core.mjs'); });
test('measurements accept shop fractions without evaluating expressions or guessing units', () => {
  assert.equal(core.measurement('36 1/2'), 36.5);
  assert.equal(core.measurement('3/8'), .375);
  assert.equal(core.measurement('900.5', 'mm'), 900.5);
  assert.equal(core.measurement(''), null);
  for (const value of ['1/0', '-1', '12 inches', '1e3', '2+3', 'Infinity', '36;alert(1)']) assert.throws(() => core.measurement(value));
  assert.throws(() => core.measurement('3/8','mm'));
});
test('packet import round trips notes, checks and literal markup without interpreting it', () => {
  const p = {...core.emptyPacket(), job:'Bath 1', widthTop:'36 1/2', scope:'<script>alert(1)</script>', startingPoint: 'unexpected'};
  assert.throws(() => core.encodePacket(p), /unknown fields/);
  delete p.startingPoint;
  assert.deepEqual(core.decodePacket(core.encodePacket(p)), p);
  assert.match(core.packetText(p), /<script>alert\(1\)<\/script>/);
  assert.match(core.packetText(p), /Not checked/);
  assert.throws(() => core.decodePacket(JSON.stringify({format:'jeff-door-survey', version:2, fields:p})), /version/);
  assert.throws(() => core.decodePacket('x'.repeat(100001)), /100 KB/);
  assert.throws(() => core.validatePacket({...p, scope:'x'.repeat(3001)}), /oversized/);
  assert.throws(() => core.validatePacket({...p, surveyDate:'2026-02-30'}), /valid date/);
});
test('missing dimensions stay unresolved and non-single layouts disable arithmetic', () => {
  const p = core.emptyPacket();
  assert(core.observations(p).some(line => line.includes('unresolved')));
  assert(core.packetText(p).includes('manual and reviewer/date are not both recorded'));
  p.configuration = 'Pair / bypass / other — specialist review';
  assert.equal(core.observations(p).length, 1);
  assert.match(core.observations(p)[0], /disabled/);
});
test('packet reports insufficient entered geometry and capacity without claiming fit', () => {
  const p = {...core.emptyPacket(), widthTop:'36',widthMiddle:'36 1/2',widthBottom:'36',overlapLeft:'1',overlapRight:'1',doorWidth:'38',ceiling:'90',doorHeight:'84',floorGap:'1/2',headroom:'6',weight:'210',capacity:'200'};
  const text = core.observations(p).join('\n');
  assert.match(text, /38.5 in/); assert.match(text, /smaller/);
  assert.match(text, /5.5 in/); assert.match(text, /Insufficient/); assert.match(text, /Exceeds/);
  assert.match(text, /professional review/);
});
